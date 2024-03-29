import collections
import copy
import datetime
import gc
import time
import sys
# import torch
import numpy as np
from contextlib import contextmanager
import pandas as pd
from .logconf import logging
import os
import random

log = logging.getLogger(__name__)
# log.setLevel(logging.WARN)
# log.setLevel(logging.INFO)
log.setLevel(logging.DEBUG)

def seed_everything(seed: int=42):
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)


def reduce_mem_usage(df):
    """iterate through all the columns of a dataframe and modify the data type
    to reduce memory usage.
    """
    start_mem = df.memory_usage().sum() / 1024**2
    print("Memory usage of dataframe is {:.2f} MB".format(start_mem))

    for col in df.columns:
        col_type = df[col].dtype

        if col_type != object:
            c_min = df[col].min()
            c_max = df[col].max()
            if str(col_type)[:3] == "int":
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
                elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                    df[col] = df[col].astype(np.int64)
            else:
                if (
                    c_min > np.finfo(np.float16).min
                    and c_max < np.finfo(np.float16).max
                ):
                    df[col] = df[col].astype(np.float16)
                elif (
                    c_min > np.finfo(np.float32).min
                    and c_max < np.finfo(np.float32).max
                ):
                    df[col] = df[col].astype(np.float32)
                else:
                    df[col] = df[col].astype(np.float64)
        else:
            df[col] = df[col].astype("category")

    end_mem = df.memory_usage().sum() / 1024**2
    print("Memory usage after optimization is: {:.2f} MB".format(end_mem))
    print("Decreased by {:.1f}%".format(100 * (start_mem - end_mem) / start_mem))

    return df


@contextmanager
def show_more_rows(new=sys.maxsize):
    old_max = pd.options.display.max_rows
    old_min = pd.options.display.min_rows
    try:
        pd.set_option("display.max_rows", new)
        pd.set_option("display.min_rows", new)
        yield old_max
    finally:
        pd.options.display.max_rows = old_max
        pd.options.display.min_rows = old_min


def is_contained(df, special_value):
    # import pandas as pd
    try:
        if type(df).__name__ == "DataFrame":
            indices = (df == special_value).any(axis=1)
            return len(df[indices]) > 0
        else:
            return (df == special_value).any()
    except:
        return True

def ivmax(l):
    max_value = -sys.maxsize
    index = 0
    for i, v in enumerate(l):
        if v > max_value:
            max_value = v
            index = i
    return index, max_value


def ivmin(l):
    """
    Finds the index and minimum value in a list.

    Parameters:
        l (list): List of numeric values.

    Returns:
        tuple: Index of the minimum value and the minimum value itself.
    """
    min_value = sys.maxsize
    index = 0
    for i, v in enumerate(l):
        if v < min_value:
            min_value = v
            index = i
    return index, min_value


def importstr(module_str, from_=None):
    """0
    >>> importstr('os')
    <module 'os' from '.../os.pyc'>
    >>> importstr('math', 'fabs')
    <built-in function fabs>
    """
    if from_ is None and ":" in module_str:
        module_str, from_ = module_str.rsplit(":")

    module = __import__(module_str)
    for sub_str in module_str.split(".")[1:]:
        module = getattr(module, sub_str)

    if from_:
        try:
            return getattr(module, from_)
        except:
            raise ImportError("{}.{}".format(module_str, from_))
    return module


def prhist(ary, prefix_str=None, **kwargs):
    if prefix_str is None:
        prefix_str = ""
    else:
        prefix_str += " "

    count_ary, bins_ary = np.histogram(ary, **kwargs)
    for i in range(count_ary.shape[0]):
        print(
            "{}{:-8.2f}".format(prefix_str, bins_ary[i]), "{:-10}".format(count_ary[i])
        )
    print("{}{:-8.2f}".format(prefix_str, bins_ary[-1]))


def enumerateWithEstimate(
    iter,
    desc_str,
    start_ndx=0,
    print_ndx=4,
    backoff=None,
    iter_len=None,
):
    """
    In terms of behavior, `enumerateWithEstimate` is almost identical
    to the standard `enumerate` (the differences are things like how
    our function returns a generator, while `enumerate` returns a
    specialized `<enumerate object at 0x...>`).

    However, the side effects (logging, specifically) are what make the
    function interesting.

    :param iter: `iter` is the iterable that will be passed into
        `enumerate`. Required.

    :param desc_str: This is a human-readable string that describes
        what the loop is doing. The value is arbitrary, but should be
        kept reasonably short. Things like `"epoch 4 training"` or
        `"deleting temp files"` or similar would all make sense.

    :param start_ndx: This parameter defines how many iterations of the
        loop should be skipped before timing actually starts. Skipping
        a few iterations can be useful if there are startup costs like
        caching that are only paid early on, resulting in a skewed
        average when those early iterations dominate the average time
        per iteration.

        NOTE: Using `start_ndx` to skip some iterations makes the time
        spent performing those iterations not be included in the
        displayed duration. Please account for this if you use the
        displayed duration for anything formal.

        This parameter defaults to `0`.

    :param print_ndx: determines which loop interation that the timing
        logging will start on. The intent is that we don't start
        logging until we've given the loop a few iterations to let the
        average time-per-iteration a chance to stablize a bit. We
        require that `print_ndx` not be less than `start_ndx` times
        `backoff`, since `start_ndx` greater than `0` implies that the
        early N iterations are unstable from a timing perspective.

        `print_ndx` defaults to `4`.

    :param backoff: This is used to how many iterations to skip before
        logging again. Frequent logging is less interesting later on,
        so by default we double the gap between logging messages each
        time after the first.

        `backoff` defaults to `2` unless iter_len is > 1000, in which
        case it defaults to `4`.

    :param iter_len: Since we need to know the number of items to
        estimate when the loop will finish, that can be provided by
        passing in a value for `iter_len`. If a value isn't provided,
        then it will be set by using the value of `len(iter)`.

    :return:
    """
    if iter_len is None:
        iter_len = len(iter)

    if backoff is None:
        backoff = 2
        while backoff**7 < iter_len:
            backoff *= 2

    assert backoff >= 2
    while print_ndx < start_ndx * backoff:
        print_ndx *= backoff

    log.info(
        "{} ----/{}, starting".format(
            desc_str,
            iter_len,
        )
    )
    start_ts = time.time()
    for current_ndx, item in enumerate(iter):
        yield (current_ndx, item)
        if current_ndx == print_ndx:
            # ... <1>
            duration_sec = (
                (time.time() - start_ts)
                / (current_ndx - start_ndx + 1)
                * (iter_len - start_ndx)
            )

            done_dt = datetime.datetime.fromtimestamp(start_ts + duration_sec)
            done_td = datetime.timedelta(seconds=duration_sec)

            log.info(
                "{} {:-4}/{}, done at {}, {}".format(
                    desc_str,
                    current_ndx,
                    iter_len,
                    str(done_dt).rsplit(".", 1)[0],
                    str(done_td).rsplit(".", 1)[0],
                )
            )

            print_ndx *= backoff

        if current_ndx + 1 == start_ndx:
            start_ts = time.time()

    log.info(
        "{} {}/{}, done at {}".format(
            desc_str,
            iter_len,
            iter_len,
            str(datetime.datetime.now()).rsplit(".", 1)[0],
        )
    )
