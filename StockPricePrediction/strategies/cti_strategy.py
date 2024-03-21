import pandas as pd
import pandas_ta
import numpy as np
import gc


def create_buy_sell_signals(df, close, fast, slow, prefix="", suffix=""):

    # If prefix or suffix is provided, adjust them
    if len(prefix) > 0:
        prefix = prefix + "_"
    if len(suffix) > 0:
        suffix = "_" + suffix

    # Create a DataFrame to store calculated values
    data = pd.DataFrame(index=df.index)
    data["fast"] = df.ta.cti(close=close, length=fast)
    data["slow"] = df.ta.cti(close=close, length=slow)
    data["p_fast"] = data["fast"].shift(1)
    data["p_slow"] = data["slow"].shift(1)

    data["CTI_BULL"] = 0
    data["CTI_BEAR"] = 0

    data.loc[
        (data["fast"] < -0.5)
        & (data["slow"] < -0.5)
        & (data["fast"] > data["slow"])
        & (data["p_fast"] < data["p_slow"]),
        "CTI_BULL",
    ] = 1
    data.loc[
        (data["fast"] > 0.5)
        & (data["slow"] > 0.5)
        & (data["fast"] < data["slow"])
        & (data["p_fast"] > data["p_slow"]),
        "CTI_BEAR",
    ] = 1

    data = data.dropna()

    buy_sell_signals = pd.DataFrame(index=df.index)
    buy_sell_signals[f"{prefix}CTI_BULL{suffix}"] = data["CTI_BULL"]
    buy_sell_signals[f"{prefix}CTI_BEAR{suffix}"] = data["CTI_BEAR"]

    del data
    gc.collect()

    return buy_sell_signals
