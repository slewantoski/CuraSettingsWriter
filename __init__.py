# Copyright (c) 2020 5axes, modified to TXT by slewantoski
# The HtmlCuraSettings plugin is released under the terms of the AGPLv3 or higher.

from . import TXTCuraSettings

from UM.i18n import i18nCatalog
catalog = i18nCatalog("cura")

def getMetaData():
    return {
        "workspace_writer": { 
            "output": [{
                "extension": "txt",
                "description": catalog.i18nc("@item:inlistbox", "Cura Settings Documentation"),
                "mime_type": "text/plain"
            }]
        }
    }

def register(app):
    return { "workspace_writer": TXTCuraSettings.TXTCuraSettings() }
