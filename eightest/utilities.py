import os
import multiprocess

from datetime import datetime

DOTENV_PATH = os.path.join(os.getcwd(), 'config.env')
env = os.environ


def get_time() -> datetime:
    return datetime.strftime(datetime.now(), '%Y-%m-%d__%H-%M-%S')


def set_cpu_count() -> None:
    cpu_count = str(multiprocess.cpu_count())
    env.update({"CPU_COUNT": cpu_count})


def load_env_file(override=False) -> None:
    try:
        with open(DOTENV_PATH) as file_obj:
            lines = file_obj.read().splitlines()

    except FileNotFoundError:
        raise FileNotFoundError('Could not config.env file.')

    dotenv_vars = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", maxsplit=1)
        dotenv_vars.setdefault(key.strip(), value.strip())
        print(dotenv_vars)

    if override:
        env.update(dotenv_vars)
    else:
        for key, value in dotenv_vars.items():
            env.setdefault(key, value)
