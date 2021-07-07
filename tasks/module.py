from exceptions.core import CoreException
from typing import Dict
from shutil import rmtree
from os import listdir, path
from celery_singleton import Singleton
from config.celery import celery_app
from config.database import db_session_scope
from core.module.registry import Registry
from core.module.parser import TfVariables, TfOutputs
from schemas.module import ModuleInDB, ModuleState
from models.module import Module
from utils.logger import getLogger

logger = getLogger(__name__)


@celery_app.task(base=Singleton, name="fetch_module", bind=True)
def build_module_meta_data(self, module: Dict) -> bool:
    module_name = module["name"]
    module_source = module["source"]

    logger.info(f"Processing module {module_name}")

    module_dir = Registry.load(module_name, module_source)
    if module_dir is not None:
        tf_files = [
            path.join(module_dir, f)
            for f in listdir(module_dir)
            if path.isfile(path.join(module_dir, f)) and f.endswith(".tf")
        ]
        if len(tf_files) == 0:
            raise (CoreException.NotFound("Not found any valid .tf files in module"))

        try:
            vars_builder = TfVariables(module_name, tf_files)
            vars_builder.build()
            vars_meta = vars_builder.to_dict()
        except Exception as exc:
            vars_meta = None
            logger.exception(f"An exception occured when parsing variables {e}")
            raise exc

        try:
            output_builder = TfOutputs(tf_files)
            output_builder.build()
            outputs_meta = output_builder.to_dict()
        except Exception as exc:
            outputs_meta = None
            logger.exception(f"An exception occured when parsing outputs {e}")
            raise exc

        with db_session_scope() as session:
            module_obj = session.query(Module).filter(Module.id == module["id"]).first()

            if vars_meta == None or outputs_meta == None:
                module_obj.state = ModuleState.FAILED
            else:
                module_obj.state = ModuleState.CREATED
                module_obj.variables = vars_meta
                module_obj.outputs = outputs_meta

            logger.info(f"Successfully updated module {module_name}")

        try:
            rmtree(module_dir)
        except Exception as e:
            logger.error(f"Could not delete module tmp dir {e}")

        return True

    logger.error(f"Could not fetch module from {module_source}")
    return False
