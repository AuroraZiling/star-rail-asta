import os

import requests
from PySide6.QtCore import Signal, QThread

from ...constant import GITHUB_RELEASE_URL


class UpdateThread(QThread):
    trigger = Signal(int, str)

    def __init__(self, info, downloadWay, parent=None):
        super(UpdateThread, self).__init__(parent)
        self.info = info
        self.downloadWay = downloadWay

    def run(self):
        self.trigger.emit(0, f"正在从 {self.downloadWay} 获取更新")
        if "Github" in self.downloadWay:
            try:
                compressed_url = self.info['assets'][0]['browser_download_url']
                file_name = self.info['assets'][0]['name']
            except ConnectionError:
                self.trigger.emit(1, "更新失败")
                return
            except requests.exceptions.SSLError:
                self.trigger.emit(1, "更新失败")
                return
            url = compressed_url
        else:
            url = f"https://sangonomiya-generic.pkg.coding.net/asta/release/[{self.info['tag_name']}]Asta.zip"
            file_name = f"Asta.zip"
        if not os.path.exists('temp'):
            os.mkdir('temp')
        resp = requests.get(url, stream=True)
        count = resp.headers.get('content-length')
        with open(f'temp/{file_name}', 'wb') as f:
            for chunk in resp.iter_content(chunk_size=2048):
                if chunk:
                    f.write(chunk)
                    self.trigger.emit(0, f"正在下载: {f.tell()} 字节/{count} 字节")
        self.trigger.emit(2, "更新下载完毕")