from logging import Logger
import os
from typing import Optional

from sqlalchemy import MetaData
from dbmanager.db_config import DBmanagerConfig, db_config_from_dict
from dbmanager.manager import DBmanager



def make_db_manager(config: dict|DBmanagerConfig, metadata: MetaData, *,
                    partition_size:int = 5000,
                    safe: bool = True,
                    logger: Optional[Logger] = None) -> DBmanager:
    if isinstance(config, dict):
        _config = db_config_from_dict(config)
    else:
        _config = config
    return DBmanager(_config.database, _config, metadata,
                     partition_size=partition_size,
                     logger=logger,
                     safe=safe)