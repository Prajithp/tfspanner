from pathlib import Path
from typing import Callable, Optional, List, Optional
from utils.logger import getLogger

logger = getLogger(__name__)


class ModuleRegistry:
    loaders: List = []

    def __init__(self) -> None:
        self.failed_urls = set()

    def load(self, module_name: str, module_source: str) -> Optional[str]:
        logger.info(f"Evaluating plugin for {module_name}")
        if module_source in self.failed_urls:
            return None

        for loader in self.loaders:
            module_path = loader.load(module_name, module_source)
            if module_path is None:
                self.failed_urls.add(module_source)
            if module_path and Path(module_path).is_dir():
                break
        return module_path

    def register(self, module: Callable) -> None:
        self.loaders.append(module)


Registry = ModuleRegistry()
