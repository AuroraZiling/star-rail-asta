from enum import Enum

from qfluentwidgets import getIconColor, Theme, FluentIconBase

from ..Utils import tools

utils = tools.Tools()


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

        return f'{utils.working_dir}/assets/icons/{self.value}_{c}.svg'
