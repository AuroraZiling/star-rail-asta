import os
import shutil
import subprocess

import requests
from PySide6.QtWidgets import QApplication

from ...constant import GITHUB_RELEASE_URL, UPDATE_SCRIPT_MODEL
from ..Utils.tools import Tools

utils = Tools()


def cleanUpdateZip():
    if os.path.exists(f"{utils.workingDir}/temp"):
        shutil.rmtree(f"{utils.workingDir}/temp")
    os.mkdir(f"{utils.workingDir}/temp")


def installUpdate():
    if not os.listdir(f"{utils.workingDir}/temp"):
        return
    if os.path.exists(f"{utils.workingDir}/asta.py"):
        return
    with open('temp/update.bat', 'w') as f:
        f.write(UPDATE_SCRIPT_MODEL.format(filename=os.listdir(f"{utils.workingDir}/temp")[0]))

    subprocess.Popen(
        [
            "start",
            "update.bat"
        ],
        cwd='temp',
        stdout=subprocess.PIPE,
        shell=True
    )
    QApplication.quit()


def findLatestVersion():
    try:
        return requests.get(GITHUB_RELEASE_URL).json()
    except ValueError:
        return None


def isNeedUpdate(appVersion):
    tag = findLatestVersion()
    try:
        if not appVersion == tag["tag_name"]:
            return tag
    except KeyError:
        error = requests.get(GITHUB_RELEASE_URL)
        if error.json()["message"] == "Not Found":
            return None
        return "limit", error.headers
    return None
