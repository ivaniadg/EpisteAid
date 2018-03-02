import logging
from bisect import bisect_left
from os.path import join


def timespan_from_object(object_id):
    return int(object_id[:8], 16)


def create_logger(logger_name, PATH=""):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(join(PATH, logger_name + '.log'))
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(processName)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


def binary_search(list_, item, lo=0,
                  hi=None):  # can't use a to specify default for hi
    hi = hi if hi is not None else len(list_)  # hi defaults to len(a)
    pos = bisect_left(list_, item, lo, hi)  # find insertion position
    return pos if pos != hi and list_[
                                    pos] == item else -1  # don't walk off the end
