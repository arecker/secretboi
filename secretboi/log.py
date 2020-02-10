import logging as _logging
import sys

_logging.getLogger().setLevel(_logging.INFO)


def make_logger(name):
    logger = _logging.getLogger(name)
    handler = _logging.StreamHandler(stream=sys.stderr)
    handler.setLevel(_logging.INFO)
    formatter = _logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
