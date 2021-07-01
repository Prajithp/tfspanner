from abc import ABC, abstractmethod
from typing import Optional
from tempfile import mkdtemp
from core.module.registry import Registry


class ModuleLoader(ABC):
    def __init__(self) -> None:
        Registry.register(self)

    def load(self, module_name: str, module_source: str) -> str:
        if not self._is_matching_loader(module_source):
            return None
        tmp_dir = f"{mkdtemp()}/{module_name}"
        return self._load_module(tmp_dir, module_name, module_source)

    @abstractmethod
    def _is_matching_loader(self, module_source: str) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def _load_module(self, tmp_dir: str, module_name: str, module_source: str):
        raise NotImplementedError()
