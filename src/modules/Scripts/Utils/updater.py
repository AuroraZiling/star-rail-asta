import os
import shutil
import subprocess

import requests
from PySide6.QtWidgets import QApplication

from ...constant import GITHUB_RELEASE_URL, UPDATE_SCRIPT_MODEL
from ..Utils.tools import Tools

utils = Tools()


def cleanUpdateZip():
    if os.path.exists(f"{utils.working_dir}/temp"):
        shutil.rmtree(f"{utils.working_dir}/temp")
    os.mkdir(f"{utils.working_dir}/temp")


def installUpdate():
    if not os.listdir(f"{utils.working_dir}/temp"):
        return
    if os.path.exists(f"{utils.working_dir}/asta.py"):
        return
    with open('temp/update.bat', 'w') as f:
        target = [i for i in os.listdir(f"{utils.working_dir}/temp") if ".bat" not in i]
        f.write(UPDATE_SCRIPT_MODEL.format(filename=target[0]))

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
