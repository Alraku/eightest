from datetime import datetime


def get_time() -> datetime:
    return datetime.strftime(datetime.now(), '%Y-%m-%d__%H-%M-%S')
