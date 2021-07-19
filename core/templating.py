from os import path, listdir
from shutil import rmtree
from tempfile import mkdtemp
import json
from typing import Any, Dict, Tuple
from jinja2.environment import Template
from pydantic.types import UUID4
from utils.logger import getLogger
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from jinja2.exceptions import TemplateNotFound, TemplateSyntaxError, UndefinedError
from schemas.resource import ResourceInDB
from config.settings import settings


def to_hcl(data: Any) -> str:
    """
    Helper function to convert python type to hcl value.
    if a value starts with 'module.' usually it should be a reference to other resource.
    """
    if isinstance(data, str) and data.startswith("module."):
        return data

    return json.dumps(data)


class Renderer:
    def __init__(self, resource_id: str) -> None:
        self._context = {}
        self._template_dir = path.join(settings.BASE_DIR, "templates")
        self.tmpdir = mkdtemp(prefix=str(resource_id))
        self.logger = getLogger(__name__)
        self._env = self.init_engine()

    def init_engine(self):
        env = Environment(
            undefined=StrictUndefined, loader=FileSystemLoader([self._template_dir])
        )
        env.filters["to_hcl"] = to_hcl
        return env

    @property
    def context(self) -> Dict:
        return self._context

    @context.setter
    def context(self, property: ResourceInDB) -> None:
        workspace_id = property.workspace_id
        backend_address = f"{settings.BASE_URL}/states/remote/workspace/{workspace_id}"

        state = {
            "backend_adress": f"{backend_address}",
            "lock_address": f"{backend_address}/lock",
            "unlock_address": f"{backend_address}/unlock",
            "lock_method": "POST",
            "unlock_method": "DELETE",
        }
        self._context = {
            "name": property.name,
            "module": property.module.dict(),
            "workspace": property.workspace.dict(),
            "variables": property.variables,
            "outputs": property.module.outputs,
            "state": state,
        }

    def __enter__(self) -> None:
        return self

    def __exit__(self, exc_type, value, traceback) -> None:
        try:
            rmtree(self.tmpdir)
        except Exception as e:
            self.logger.exception(f"An error while removing tmp dir {self.tmpdir}")

    def render(self) -> Tuple:
        template_dir = self._template_dir
        tf_files = files = [
            f
            for f in listdir(template_dir)
            if path.isfile(path.join(template_dir, f)) and f.endswith(".j2")
        ]

        context = self._context
        renderd = []
        for tf_file in tf_files:
            try:
                self.logger.debug(f"Processing template file {tf_file}")
                template = self._env.get_template(tf_file)
                new_name = tf_file.replace(".j2", "")
                tf_path = path.join(self.tmpdir, new_name)

                with open(tf_path, "w") as fh:
                    fh.write(template.render(**context))
                renderd.append(tf_path)
            except Exception as e:
                self.logger.exception(e)
                raise RuntimeError(e)

        return (renderd, self.tmpdir)
