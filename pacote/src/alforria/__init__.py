"""Pacote Alforria"""

__version__ = "0.2"

from . import main


def set_config_path(path: str):
    main._PATHS_PATH = path + "/paths.cnf"
    main._ALFCFG_PATH = path + "/alforria.cnf"
    main._CONST_PATH = path + "/con stantes.cnf"
