from logging import Logger
from re import M
from typing import Dict

from sqlalchemy.orm import session
from config.celery import celery_app
from config.database import db_session
from core.module.registry import Registry
from core.module.parser import TfVariables, TfOutputs
from schemas.module import ModuleInDB, ModuleState
from models.module import Module
from utils.logger import getLogger

from shutil import rmtree
from os import listdir, path

logger = getLogger(__name__)


@celery_app.task(name="fetch_module", bind=True)
def build_module_meta_data(self, module: Dict) -> bool:
    module_name = module["name"]
    module_source = module["source"]

    logger.info(f"Processing module {module_name}")

    module_dir = Registry.load(module_name, module_source)
    if module_dir is not None:
        tf_files = files = [
            path.join(module_dir, f)
            for f in listdir(module_dir)
            if path.isfile(path.join(module_dir, f)) and f.endswith(".tf")
        ]

        try:
            builder = TfVariables(module_name, tf_files)
            builder.build()
            vars_meta = builder.to_dict()
        except Exception as e:
            vars_meta = None
            logger.exception(f"An exception occured during parsing variables {e}")
            return False
        try:
            output_builder = TfOutputs(tf_files)
            output_builder.build()
            outputs_meta = output_builder.to_dict()
        except Exception as e:
            outputs_meta = None
            logger.exception(f"An exception occured during parsing outputs {e}")
            return False

        session = next(db_session())
        module_obj = session.query(Module).filter(Module.id == module["id"]).first()

        if vars_meta == None or outputs_meta == None:
            module_obj.state = ModuleState.FAILED
        else:
            module_obj.state = ModuleState.CREATED
            module_obj.variables = vars_meta
            module_obj.outputs = outputs_meta

        session.commit()
        logger.info(f"Successfully updated module {module_name}")

        try:
            rmtree(module_dir)
        except Exception as e:
            logger.error(f"Could not delete module tmp dir {e}")

        return True

    logger.error(f"Could not fetch module from {module_source}")
    return False
