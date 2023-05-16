import logging
import os
import time

from ..Utils.tools import Tools

utils = Tools()


def debugWrite(content):
    logging.debug(content)


def infoWrite(content):
    logging.info(content)


def warningWrite(content):
    logging.warning(content)


def criticalWrite(content):
    logging.critical(content)


def errorWrite(content):
    logging.error(content)


if not os.path.exists(f"{utils.workingDir}/logs"):
    os.mkdir(f"{utils.workingDir}/logs")
logFileName = "Sangonomiya " + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + ".log"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename=utils.logDir + "/" + logFileName,
    filemode='w'
)
