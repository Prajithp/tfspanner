from http import HTTPStatus
import requests
from zipfile import ZipFile
from io import BytesIO

from core.module.loader import ModuleLoader


class HTTPLoader(ModuleLoader):
    def __init__(self) -> None:
        super().__init__()

    def _is_matching_loader(self, source: str) -> bool:
        if source.startswith("http") or source.startswith("https") and "zip" in source:
            return True
        return False

    def _load_module(self, tmp_dir: str, name: str, source: str) -> str:
        r = requests.get(url=source)
        if r.status_code != HTTPStatus.OK and r.status_code != HTTPStatus.NO_CONTENT:
            return None
        z = ZipFile(BytesIO(r.content))
        z.extractall(tmp_dir)

        return tmp_dir


loader = HTTPLoader()
