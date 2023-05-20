import json
import logging
import os
import pathlib
import shutil
import sys
import time

import win32clipboard
from PySide6.QtGui import QFont

from ...Metadata import character_list, weapon_list


class Tools:
    def __init__(self):
        self.working_dir = self.__get_working_dir()
        self.OS_name = self.__get_OS_name()
        self.log_dir = self.working_dir + "/logs"
        self.config_dir = self.working_dir + "/configs"

        self.app_version = self.__get_version("application_version")
        self.ui_version = self.__get_version("ui_version")

        self.license = self.__get_license()
        self.open_source_license = self.__get_open_source_license()

        logFileName = "Asta " + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + ".log"
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            filename=self.log_dir + "/" + logFileName,
            filemode='w',
            encoding="utf-8"
        )

    @staticmethod
    def __get_working_dir() -> str:
        """Get the working directory of the program
        :return: The working directory of the program
        """
        if sys.platform.startswith("win32"):
            return os.path.abspath(os.curdir).replace("\\", '/')
        elif sys.platform.startswith("darwin"):
            return os.path.dirname(sys.argv[0])

    def __get_version(self, version_type: str) -> str:
        """Get the version of the program
        :param version_type: The type of the version
        :return: The version of the program
        """
        if self.find_exist(f"{self.working_dir}/assets/configs/application.json"):
            with open(f"{self.working_dir}/assets/configs/application.json", 'r') as f:
                return json.load(f)[version_type]
        return ""

    @staticmethod
    def __get_OS_name() -> str:
        """Get the name of the operating system
        :return: The name of the operating system
        """
        if sys.platform.startswith("win32"):
            return "Windows"
        elif sys.platform.startswith("darwin"):
            return "macOS"
        elif sys.platform.startswith("linux"):
            return "Linux"
        else:
            return "Unknown"

    def __get_license(self) -> str:
        """Get the license of the program
        :return: The license of the program
        """
        if self.find_exist(f"{self.working_dir}/assets/configs/license"):
            with open(f"{self.working_dir}/assets/configs/license", 'r') as f:
                return f.read()
        return ""

    def __get_open_source_license(self) -> str:
        """Get the open source license of the program
        :return: The open source license of the program
        """
        if self.find_exist(f"{self.working_dir}/assets/configs/open_source"):
            with open(f"{self.working_dir}/assets/configs/open_source", 'r') as f:
                return f.read()
        return ""

    def get_font(self, size: int) -> QFont:
        """Get the font
        :param size: The size of the font
        :return: The font
        """
        if self.OS_name == "Windows":
            return QFont("Microsoft YaHei", size)
        elif self.OS_name == "macOS":
            return QFont("Microsoft YaHei", size + 6)

    def open_directory(self, path: str) -> None:
        """Open the directory
        :param path: The path of the directory
        :return: None
        """
        if self.find_exist(path):
            os.startfile(path) if self.OS_name == "Windows" else os.system(f"open {path}")
        else:
            logging.error(f"[Utils] Directory {path} not found")
        return None

    def create_directory(self, path: str) -> None:
        """Create the directory
        :param path: The path of the directory
        :return: None
        """
        if self.find_exist(path):
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)
            logging.info(f"[Utils] Directory {path} created")
        else:
            logging.warning(f"[Utils] Directory {path} has already existed")
        return None

    @staticmethod
    def find_exist(path: str) -> bool:
        """Check if the file or directory exists
        :param path: The path of the file or directory
        :return: True if the file or directory exists, False if not
        """
        return os.path.exists(path)

    def delete_directory(self, path: str, create=True) -> None:
        """Delete the directory
        :param path: The path of the directory
        :param create: Whether to create the directory after deleting
        :return: None
        """
        if self.find_exist(path):
            try:
                shutil.rmtree(path)
            except PermissionError:
                logging.warning(f"[Utils] Permission denied when deleting directory {path}")
                return None
        if create:
            os.mkdir(path)
        return None

    def get_directory_size(self, path: str) -> float:
        """Get the size of the directory
        :param path: The path of the directory
        :return: The size of the directory
        """
        if self.find_exist(path):
            size = 0
            for root, dirs, files in os.walk(path):
                size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
            return round(size / 1024 / 1024, 2)
        else:
            logging.error(f"[Utils] Directory {path} not found")
        return 0.0

    def get_log_file_amount(self) -> int:
        """Get the amount of log files
        :return: The amount of log files
        """
        if self.find_exist(self.log_dir):
            return len(os.listdir(self.log_dir))
        return 0

    def get_file_create_date(self, path: str) -> str:
        """Get the creation date of the file
        :param path: The path of the file
        :return: The creation date of the file
        """
        if self.find_exist(path):
            return time.strftime("%Y.%m.%d", time.localtime(os.stat(path).st_ctime))
        return ""

    @staticmethod
    def get_clipboard_text():
        """Get the text in the clipboard
        :return: The text in the clipboard
        """
        win32clipboard.OpenClipboard()
        try:
            return win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
        except TypeError:
            return ""

    def update_metadata(self, data_type: str, data=None) -> None:
        """Update the metadata
        :param data_type: The type of the data
        :param data: The data
        :return: None
        """
        if data_type == "character" and not data:
            data = character_list.categoryCharacterInStar()
        elif data_type == "weapon" and not data:
            data = weapon_list.categoryWeaponInStar()
        elif data_type == "permanent" and not data:
            data = character_list.getPermanentCharacter()
        if not os.path.exists(f"{self.config_dir}/metadata/"):
            os.mkdir(f"{self.config_dir}/metadata/")
        open(f"{self.config_dir}/metadata/{data_type}.json", 'w', encoding="utf-8").write(
            json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False))
        logging.info(f"[Metadata_utils] Metadata updated: {data_type}")

    def read_metadata(self, data_type: str) -> dict:
        if self.find_exist(f"{self.config_dir}/metadata/{data_type}.json"):
            return json.loads(open(f"{self.config_dir}/metadata/{data_type}.json", 'r', encoding="utf-8").read())
        return {}

    @staticmethod
    def json_validator(path, requirement=None):
        if not os.path.exists(path):
            return False
        try:
            file = json.loads(open(path, 'r', encoding="utf-8").read())
            if requirement == "uigf":
                if not file["info"]["uigf_version"] == "v2.2":
                    return False
        except json.decoder.JSONDecodeError:
            return False
        return True
