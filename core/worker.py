import subprocess
from typing import Any, Dict, List, Union
from python_terraform import Terraform, IsFlagged
from sqlalchemy.dialects.postgresql import json
import json
from utils.logger import getLogger

_MAPPING = {
    "init": {"input": False},
    "plan": {"input": False},
    "apply": {"input": False, "auto_approve": True},
    "destroy": {"input": False, "auto_approve": True},
}


class TerrformInitFailed(Exception):
    def __init__(self, rc=1) -> None:
        self.r_value = rc
        self.message = "Failed to initialize terraform"
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"{self.r_value} - {self.message}"


class TfWorker:
    def __init__(self, workspace: str) -> None:
        self.workspace = workspace
        self.logger = getLogger(__name__)
        self.tf = Terraform(working_dir=workspace)
        self._stream = None
        self._env = {}

    @property
    def stream(self) -> Any:
        return self._stream

    @stream.setter
    def stream(self, handler: Any) -> None:
        if not callable(handler):
            raise IOError("handler is not a callable function")
        self._stream = handler

    def __getattr__(self, item) -> Any:
        def wrapper(*args, **kwargs):
            if self._stream is not None:
                kwargs.update({"synchronous": False})

            kwargs.update({"no_color": IsFlagged})

            if item in _MAPPING:
                kwargs.update(_MAPPING[item])

            if not self._stream:
                rc, stdout, stderr = self.tf.cmd(item, *args, **kwargs)
                return rc, stdout.strip(), stderr.strip()
            else:
                p, _, _ = self.tf.cmd(item, *args, **kwargs)
                while p.poll() == None:
                    stdout = p.stdout.readline().decode("utf-8").strip()
                    stderr = p.stderr.readline().decode("utf-8").strip()
                    self.publish(stdout, stderr)
                rc = p.poll()
                stdout, stderr = p.communicate()
                self.publish(stdout, stderr)
                return rc, None, None

        return wrapper

    def publish(self, stdout: bytes, stderr: bytes) -> None:
        try:
            if stdout:
                self.stream(stdout)
            if stderr:
                self.stream(stderr)
        except Exception as e:
            self.logger.error(f"Failed to publish output {e}")

    def output_dict(self) -> Dict:
        r_code, raw_data, stderr = self.tf.cmd("output", json=IsFlagged)
        if r_code == 0:
            return json.loads(raw_data)
        return None

    def __enter__(self) -> None:
        r_code, _, _ = self.init()
        if r_code >= 1:
            raise (TerrformInitFailed(r_code))
        return self

    def __exit__(self, exc_type, value, traceback) -> None:
        pass
