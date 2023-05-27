# coding: utf-8
from enum import Enum
from ..Utils.tools import Tools
from qfluentwidgets import StyleSheetBase, Theme, qconfig, isDarkTheme

utils = Tools()


class StyleSheet(StyleSheetBase, Enum):
    """ Style sheet  """

    TITLE_BAR = "title_bar"
    MAIN_WINDOW = "general"
    GACHA_REPORT_FRAME = "general"
    ANNOUNCEMENT_FRAME = "general"
    LINK_FRAME = "link_frame"
    LINK_CARD = "link_card"
    HOME_FRAME = "home_frame"
    SETTING_FRAME = "setting_frame"
    ABOUT_FRAME = "general"
    METADATA_FRAME = "metadata_frame"
    GLYPHS_FRAME = "glyphs_frame"

    def path(self, theme=Theme.AUTO):
        theme = qconfig.theme if theme == Theme.AUTO else theme
        return f"{utils.working_dir}/assets/themes/{theme.value.lower()}/{theme.value.lower()}_{self.value}.qss"


def component_style_sheet(component):
    theme = "dark" if isDarkTheme() else "light"
    with open(f"{utils.working_dir}/assets/themes/{theme}/components/{component}.qss",
              encoding='utf-8') as f:
        return f.read()
