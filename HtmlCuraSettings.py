# Copyright (c) 2020 5axes
# Initial Source from Johnny Matthews https://github.com/johnnygizmo/CuraSettingsWriter 
# The HTML plugin is released under the terms of the AGPLv3 or higher.
# Version 1.0.3 : simplify the source code with WriteTd
#               : Export also the meshfix paramater section by extruder and complementary information on extruder for machine definition
import os
import platform

from datetime import datetime
from cura.CuraApplication import CuraApplication
from UM.Workspace.WorkspaceWriter import WorkspaceWriter

from cura.CuraVersion import CuraVersion  # type: ignore

from UM.i18n import i18nCatalog
catalog = i18nCatalog("cura")

from UM.Logger import Logger
from UM.Message import Message


class HtmlCuraSettings(WorkspaceWriter):

        
    def write(self, stream, nodes, mode):
    
        # Current File path
        Logger.log("d", "stream = %s", os.path.abspath(stream.name))
        
        stream.write("<!DOCTYPE html>")
        stream.write("<meta charset=""UTF-8"">")
        stream.write("<html>")
        stream.write("<head>")
        stream.write("<title>Cura Settings Export</title>")
        stream.write("</head>")
        stream.write("<style>")
        stream.write(" .category { font-size:1.1em; background-color:rgb(142,170,219); } ")
        stream.write(" .off { background-color:grey; } ")
        stream.write(" .valueCol { width:200px;text-align:right }")
        stream.write("</style>")
        stream.write("<body lang=EN>")
        
        machine_manager = CuraApplication.getInstance().getMachineManager()        
        stack = CuraApplication.getInstance().getGlobalContainerStack()

        global_stack = machine_manager.activeMachine

        # Script        
        stream.write("<script src='https://code.jquery.com/jquery-3.3.1.slim.min.js'></script>\n")
        stream.write("""<script>
                            $(document).ready(function(){
                                    $("#enabled").on("click",toggleDisabled);
                            });

                            function toggleDisabled(){
                                    $("tr.disabled").toggle();
                            }
                        </script>
                        <h1>Cura Settings Export</h1>
                        <button id='enabled'>Disabled parameters</button><P>""")

        #Get extruder count
        extruder_count=stack.getProperty("machine_extruder_count", "value")
        print_information = CuraApplication.getInstance().getPrintInformation()
        
        stream.write("<table width=50% border=1 cellpadding=3>")
        # Job
        self._WriteTd(stream,"Job Name",print_information.jobName)
        
        # File
        # self._WriteTd(stream,"File",os.path.abspath(stream.name))
        # Date
        self._WriteTd(stream,"Date",datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        # platform
        self._WriteTd(stream,"Os",str(platform.system()) + " " + str(platform.version()))
       
        # Version  
        self._WriteTd(stream,"Cura Version",CuraVersion)
            
        # Profile
        P_Name = global_stack.qualityChanges.getMetaData().get("name", "")
        self._WriteTd(stream,"Profile",P_Name)
        # Quality
        Q_Name = global_stack.quality.getMetaData().get("name", "")
        self._WriteTd(stream,"Quality",Q_Name)
                
        # Material
        extruders = list(global_stack.extruders.values())
        i=0
        for Extrud in list(global_stack.extruders.values()):
            i += 1
            M_Name = Extrud.material.getMetaData().get("material", "")
            MaterialStr="Material Extruder : %d"%i
            self._WriteTd(stream,MaterialStr,M_Name)
  
        MAterial=0
        #   materialWeights
        for Mat in list(print_information.materialWeights):
            MAterial=MAterial+Mat
        if MAterial>0:
            M_Weight= "{:.1f} g".format(MAterial).rstrip("0").rstrip(".")
            self._WriteTd(stream,"Material Weights",M_Weight)            
            
            #   Print time
            P_Time = "%d d %d h %d mn"%(print_information.currentPrintTime.days,print_information.currentPrintTime.hours,print_information.currentPrintTime.minutes)
            self._WriteTd(stream,"Print Time",P_Time)   
            
        # Define every section to get the same order as in the Cura Interface
        # Modification from global_stack to extruders[0]
        i=0
        for Extrud in list(global_stack.extruders.values()):
            i += 1
            self._doTree(Extrud,"resolution",stream,0,i,True)
            self._doTree(Extrud,"shell",stream,0,i,True)
            self._doTree(Extrud,"infill",stream,0,i,True)
            self._doTree(Extrud,"material",stream,0,i,True)
            self._doTree(Extrud,"speed",stream,0,i,True)
            self._doTree(Extrud,"travel",stream,0,i,True)
            self._doTree(Extrud,"cooling",stream,0,i,True)

            # If single extruder doesn't export the data
            if extruder_count>1 :
                self._doTree(Extrud,"dual",stream,0,i,True)

        self._doTree(extruders[0],"support",stream,0,0,True)
        self._doTree(extruders[0],"platform_adhesion",stream,0,0,True)
        i=0
        for Extrud in list(global_stack.extruders.values()):
            i += 1
            self._doTree(Extrud,"meshfix",stream,0,i,True)
        self._doTree(extruders[0],"blackmagic",stream,0,0,True)
        self._doTree(extruders[0],"experimental",stream,0,0,True)
        self._doTree(extruders[0],"machine_settings",stream,0,0,True)
        i=0
        for Extrud in list(global_stack.extruders.values()):
            i += 1
            self._doTree(Extrud,"machine_settings",stream,0,i,False)

        # This Method is smarter but unfortunatly settings are not in the same ordrer as the Cura interface
        # for key in global_stack.getAllKeys():
        #     if global_stack.getProperty(key,"enabled") == True:
        #         if global_stack.getProperty(key,"type") == "category":
        #             self._doTree(global_stack,key,stream,0)

        stream.write("</table>")
        stream.write("</body>")
        stream.write("</html>")
        return True

    def _WriteTd(self,stream,Key,ValStr):

        stream.write("<tr>")
        stream.write("<td class='ok' style='width:50%;padding-left:25'>" + Key + "</td>")
        stream.write("<td class='ok' colspan=2>" + str(ValStr) + "</td>")
        stream.write("</tr>\n")
            
               
    def _doTree(self,stack,key,stream,depth,extrud,Full):   
        #output node
        Info_Extrud=""
        
        if stack.getProperty(key,"type") == "category":
            stream.write("<tr>")
            if extrud>0:
                Info_Extrud="Extruder : %d %s"%(extrud,stack.getProperty(key,"label"))
            else:
                Info_Extrud=str(stack.getProperty(key,"label"))
            stream.write("<td class=category colspan=3>" + str(Info_Extrud) + "</td>")
            #stream.write("<td class=category>" + str(key) + "</td>")
            stream.write("</tr>\n")
        else:
            style = "ok"    
            if stack.getProperty(key,"enabled") == False:
                style = "off"
                stream.write("<tr class=disabled>")
            else:
                stream.write("<tr>")
            
            definition_key=key + " label" 
            # untranslated_label=stack.getProperty(key,"label").capitalize()
            untranslated_label=stack.getProperty(key,"label")
            # translated_label=catalog.i18nc(definition_key, untranslated_label)  
            translated_label=catalog.i18nc("@label", untranslated_label)
            
            stream.write("<td class="+style+" style='width:70%;padding-left:"+str(depth*25)+"'>" + str(translated_label) + "</td>")
            
            GetType=stack.getProperty(key,"type")
            GetVal=stack.getProperty(key,"value")
            if str(GetType)=='float':
                # GelValStr="{:.2f}".format(GetVal).replace(".00", "")  # Formatage
                GelValStr="{:.4f}".format(GetVal).rstrip("0").rstrip(".") # Formatage thanks to r_moeller
            else:
                GelValStr=str(GetVal)
                
            stream.write("<td class='"+style+" valueCol'>" + GelValStr + "</td>")
            
            stream.write("<td class="+style+" style='width:10%'>" + str(stack.getProperty(key,"unit")) + "</td>")
            stream.write("</tr>\n")

        #look for children
        if Full == True:
            if len(CuraApplication.getInstance().getGlobalContainerStack().getSettingDefinition(key).children) > 0:
                for i in CuraApplication.getInstance().getGlobalContainerStack().getSettingDefinition(key).children:       
                    self._doTree(stack,i.key,stream,depth+1,extrud,Full)
        else:
            if len(stack.getSettingDefinition(key).children) > 0:
                for i in stack.getSettingDefinition(key).children:       
                    self._doTree(stack,i.key,stream,depth+1,extrud,Full)                  

                    
 