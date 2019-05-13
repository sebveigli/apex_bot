import argparse
import logging
import os
import sys
import time

from pymongo import MongoClient

logger = logging.getLogger(__name__)

SEVERITIES = {'debug': logging.DEBUG, 'info': logging.INFO, 'warning': logging.WARNING, 'error': logging.ERROR, 'critical': logging.CRITICAL}
ENVS = ['dev', 'prod']

def bootstrap_app(**kwargs):
    _set_cwd()
    
    args = _get_args()
    
    _set_env(args.env, kwargs.get('env'))
    _add_config_to_path()
    _start_loggers(SEVERITIES[args.file_severity], SEVERITIES[args.console_severity])
    _check_db_connection()


    logger.info("App bootstrapped")

def start_discord():
    from client.discord_client import DiscordClient

    import config

    d = DiscordClient()
    d.run(config.DISCORD_BOT_TOKEN)

def _set_cwd():
    if os.path.split(os.getcwd())[1] != 'src':
        os.chdir(os.path.join(os.getcwd(), 'src'))

def _get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--env', '--e', default='dev', required=False, choices=ENVS)
    parser.add_argument('--file_severity', '--f', default='info', required=False, choices=[severity for severity in SEVERITIES])
    parser.add_argument('--console_severity', '--c', default='debug', required=False, choices=[severity for severity in SEVERITIES])

    return parser.parse_args()

def _set_env(env, override):
    if override and override in ENVS:
        os.environ['env'] = override
        return
    
    os.environ['env'] = env

def _add_config_to_path():
    sys.path.append(os.path.join(os.getcwd(), 'envs', os.environ['env']))

def _start_loggers(f_severity, c_severity):
    import config
    
    skipped = ['websockets']

    for s in skipped:
        l = logging.getLogger(s)
        l.setLevel(logging.CRITICAL)

    l = logging.getLogger()
    l.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%d/%m %H:%M:%S")

    """ File Logger """
    log_dir = os.path.join(os.getcwd(), "..", "logs")
    log_path = os.path.join(log_dir, config.LOG_NAME)

    try:
        os.mkdir(log_dir)
    except FileExistsError:
        pass

    try:
        os.remove(log_path)
    except Exception:
        pass

    fh = logging.FileHandler(log_path)
    fh.setLevel(f_severity)
    fh.setFormatter(formatter)

    ch = logging.StreamHandler()
    ch.setLevel(c_severity)
    ch.setFormatter(formatter)

    l.addHandler(fh)
    l.addHandler(ch)

def _check_db_connection():
    import config

    logger.debug("Checking DB connection to Mongo")

    try:
        mc = MongoClient(host=config.MONGO['host'], port=config.MONGO['port'], serverSelectionTimeoutMS=100)
        mc.admin.command('ismaster')
    except Exception as e:
        logger.critical("MongoDB does not seem to be running on your host. Please start the service, and try loading the bot again.")
        sys.exit(-1)
