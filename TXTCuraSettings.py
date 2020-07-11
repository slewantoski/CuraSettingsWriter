# Copyright (c) 2020 5axes, modified to TXT by slewantoski
# Initial Source from Johnny Matthews https://github.com/johnnygizmo/CuraSettingsWriter 
# The HTML plugin is released under the terms of the AGPLv3 or higher.
# Version 1.0.3 : simplify the source code with WriteTd
#               : Export also the meshfix paramater section by extruder and complementary information on extruder for machine definition
# Version 1.0.4 : html cleanup, no jquery dependency  thanks to https://github.com/etet100
#  
import os
import platform

from datetime import datetime
from cura.CuraApplication import CuraApplication
from UM.Workspace.WorkspaceWriter import WorkspaceWriter

from cura.CuraVersion import CuraVersion  # type: ignore

from UM.i18n import i18nCatalog
i18n_cura_catalog = i18nCatalog("cura")
i18n_catalog = i18nCatalog("fdmprinter.def.json")
i18n_extrud_catalog = i18nCatalog("fdmextruder.def.json")

from UM.Logger import Logger
from UM.Message import Message

class TXTCuraSettings(WorkspaceWriter):

    def write(self, stream, nodes, mode):
    
        # Current File path
        Logger.log("d", "stream = %s", os.path.abspath(stream.name))
        
        machine_manager = CuraApplication.getInstance().getMachineManager()        
        stack = CuraApplication.getInstance().getGlobalContainerStack()

        global_stack = machine_manager.activeMachine

        TitleTxt =i18n_cura_catalog.i18nc("@label","Print settings")

        stream.write(TitleTxt+ "\n")

        #Get extruder count
        extruder_count=stack.getProperty("machine_extruder_count", "value")
        print_information = CuraApplication.getInstance().getPrintInformation()
        
        #   ####stream.write("<table width='50%' border='1' cellpadding='3'>")
        # Job
        self._WriteTd(stream,i18n_cura_catalog.i18nc("@label","Job Name"),print_information.jobName)
        
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
        self._WriteTd(stream,i18n_cura_catalog.i18nc("@label","Profile"),P_Name)
        # Quality
        Q_Name = global_stack.quality.getMetaData().get("name", "")
        self._WriteTd(stream,i18n_cura_catalog.i18nc("@label:table_header","Quality"),Q_Name)
                
        # Material
        extruders = list(global_stack.extruders.values())      
        i=0
        for Extrud in list(global_stack.extruders.values()):
            i += 1
            M_Name = Extrud.material.getMetaData().get("material", "")
            MaterialStr="%s %s : %d"%(i18n_cura_catalog.i18nc("@label", "Material"),i18n_cura_catalog.i18nc("@label", "Extruder"),i)
            self._WriteTd(stream,MaterialStr,M_Name)
  
        MAterial=0
        #   materialWeights
        for Mat in list(print_information.materialWeights):
            MAterial=MAterial+Mat
        if MAterial>0:
            M_Weight= "{:.1f} g".format(MAterial).rstrip("0").rstrip(".")
            self._WriteTd(stream,i18n_cura_catalog.i18nc("@label","Material estimation"),M_Weight)            
            
            #   Print time
            P_Time = "%d d %d h %d mn"%(print_information.currentPrintTime.days,print_information.currentPrintTime.hours,print_information.currentPrintTime.minutes)
            self._WriteTd(stream,i18n_cura_catalog.i18nc("@label","Printing Time"),P_Time)   
            
        # Define every section to get the same order as in the Cura Interface
        # Modification from global_stack to extruders[0]
        i=0
        for Extrud in list(global_stack.extruders.values()):
            i += 1
            self._doTree(Extrud,"resolution",stream,0,i)
            self._doTree(Extrud,"shell",stream,0,i)
            self._doTree(Extrud,"infill",stream,0,i)
            self._doTree(Extrud,"material",stream,0,i)
            self._doTree(Extrud,"speed",stream,0,i)
            self._doTree(Extrud,"travel",stream,0,i)
            self._doTree(Extrud,"cooling",stream,0,i)

            # If single extruder doesn't export the data
            if extruder_count>1 :
                self._doTree(Extrud,"dual",stream,0,i)

        self._doTree(extruders[0],"support",stream,0,0)
        self._doTree(extruders[0],"platform_adhesion",stream,0,0)
        i=0
        for Extrud in list(global_stack.extruders.values()):
            i += 1
            self._doTree(Extrud,"meshfix",stream,0,i)
        self._doTree(extruders[0],"blackmagic",stream,0,0)
        self._doTree(extruders[0],"experimental",stream,0,0)
        self._doTree(extruders[0],"machine_settings",stream,0,0)
        i=0
        for Extrud in list(global_stack.extruders.values()):
            i += 1
            self._doTreeExtrud(Extrud,"machine_settings",stream,0,i)

        # This Method is smarter but unfortunatly settings are not in the same ordrer as the Cura interface
        # for key in global_stack.getAllKeys():
        #     if global_stack.getProperty(key,"enabled") == True:
        #         if global_stack.getProperty(key,"type") == "category":
        #             self._doTree(global_stack,key,stream,0)

        return True

    def _WriteTd(self,stream,Key,ValStr):

        stream.write(Key + ": ")
        stream.write(str(ValStr) + "\n")
            
               
    def _doTree(self,stack,key,stream,depth,extrud):   
        #output node
        Info_Extrud=""
        definition_key=key + " label"
        ExtruderStrg = i18n_cura_catalog.i18nc("@label", "Extruder")
        
        if stack.getProperty(key,"type") == "category":
            if extrud>0:
                untranslated_label=stack.getProperty(key,"label")
                translated_label=i18n_catalog.i18nc(definition_key, untranslated_label)
                Info_Extrud="%s : %d %s"%(ExtruderStrg,extrud,translated_label)
            else:
                untranslated_label=stack.getProperty(key,"label")
                translated_label=i18n_catalog.i18nc(definition_key, untranslated_label)
                Info_Extrud=str(translated_label)
                stream.write(str(Info_Extrud) + "\n")
        else:
            # untranslated_label=stack.getProperty(key,"label").capitalize()
            untranslated_label=stack.getProperty(key,"label")           
            translated_label=i18n_catalog.i18nc(definition_key, untranslated_label)
            
            stream.write(str(translated_label) + ": ")
            
            GetType=stack.getProperty(key,"type")
            GetVal=stack.getProperty(key,"value")
            if str(GetType)=='float':
                # GelValStr="{:.2f}".format(GetVal).replace(".00", "")  # Formatage
                GelValStr="{:.4f}".format(GetVal).rstrip("0").rstrip(".") # Formatage thanks to r_moeller
            else:
                GelValStr=str(GetVal)
                
            stream.write(GelValStr)
            
            stream.write(str(stack.getProperty(key,"unit")) + "\n")

            depth += 1

        #look for children
        if len(CuraApplication.getInstance().getGlobalContainerStack().getSettingDefinition(key).children) > 0:
            for i in CuraApplication.getInstance().getGlobalContainerStack().getSettingDefinition(key).children:       
                self._doTree(stack,i.key,stream,depth,extrud)                
    
    def _doTreeExtrud(self,stack,key,stream,depth,extrud):   
        #output node
        Info_Extrud=""
        definition_key=key + " label"
        ExtruderStrg = i18n_cura_catalog.i18nc("@label", "Extruder")
        
        if stack.getProperty(key,"type") == "category":
            if extrud>0:
                untranslated_label=stack.getProperty(key,"label")
                translated_label=i18n_extrud_catalog.i18nc(definition_key, untranslated_label)
                Info_Extrud="%s : %d %s"%(ExtruderStrg,extrud,translated_label)
            else:
                untranslated_label=stack.getProperty(key,"label")
                translated_label=i18n_extrud_catalog.i18nc(definition_key, untranslated_label)
                Info_Extrud=str(translated_label)
            stream.write(str(Info_Extrud) + "\n")
        else:
            # untranslated_label=stack.getProperty(key,"label").capitalize()
            untranslated_label=stack.getProperty(key,"label")           
            translated_label=i18n_extrud_catalog.i18nc(definition_key, untranslated_label)
            
            stream.write(str(translated_label) + ": ")
            
            GetType=stack.getProperty(key,"type")
            GetVal=stack.getProperty(key,"value")
            if str(GetType)=='float':
                # GelValStr="{:.2f}".format(GetVal).replace(".00", "")  # Formatage
                GelValStr="{:.4f}".format(GetVal).rstrip("0").rstrip(".") # Formatage thanks to r_moeller
            else:
                GelValStr=str(GetVal)
                
            stream.write(GelValStr)
            
            stream.write(str(stack.getProperty(key,"unit")) + "\n")

            depth += 1

        #look for children
        if len(stack.getSettingDefinition(key).children) > 0:
            for i in stack.getSettingDefinition(key).children:       
                self._doTreeExtrud(stack,i.key,stream,depth,extrud)  
