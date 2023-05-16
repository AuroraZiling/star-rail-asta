from enum import Enum

from qfluentwidgets import getIconColor, Theme, FluentIconBase

from ..Utils import config_utils

utils = config_utils.ConfigUtils()


class MyFluentIcon(FluentIconBase, Enum):
    """ Custom icons """

    USER = "User"
    GACHA_REPORT = "GachaReport"
    DATA = "Data"
    ANNOUNCEMENT = "Announcement"
    PLUGIN = "Plugin"
    ABOUT = "About"
    DELETE = "Delete"
    GITHUB = "Github"

    def path(self, theme=Theme.AUTO):
        if theme == Theme.AUTO:
            c = getIconColor()
        else:
            c = "white" if theme == Theme.DARK else "black"

        return f'{utils.workingDir}/assets/icons/{self.value}_{c}.svg'
