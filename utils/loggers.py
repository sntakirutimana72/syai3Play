from os import path
from datetime import datetime
from utils.app_envs import appDataDir
from logging import basicConfig, DEBUG, getLogger

logger = None


def _setup_logging():
    global logger

    logfile_name = datetime.now().strftime('%B-%Y')
    basicConfig(filename=path.join(appDataDir(), 'resources', 'logs', logfile_name + '.log'),
                format='%(asctime)s :: %(levelname)s :: %(name)s :: %(message)s')
    logger = getLogger('syaiV3play')
    logger.setLevel(DEBUG)


def inform_(info):
    logger.info(info)


def alert_(err):
    logger.error(err)


_setup_logging()
