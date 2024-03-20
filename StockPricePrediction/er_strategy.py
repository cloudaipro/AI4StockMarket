import pandas as pd
import pandas_ta
import numpy as np
import gc
'''
https://www.whselfinvest.com/en-be/trading-platform/free-trading-strategies/tradingsystem/33-kaufman-efficiency-ratio
'''
def create_buy_sell_signals(df, close, prefix="", suffix=""):

    # If prefix or suffix is provided, adjust them
    if len(prefix) > 0:
        prefix = prefix + "_"
    if len(suffix) > 0:
        suffix = "_" + suffix

    # Create a DataFrame to store calculated values
    data = pd.DataFrame(index=df.index)
    data["er"] = df.ta.er(close=close)
    data["p_er"] = data["er"].shift(1)
    data["ER_BULL"] = 0
    data["ER_BEAR"] = 0

    data.loc[
        (data["er"] > 0.6)
        & (data["p_er"] <= 0.6),
        "ER_BULL"
    ] = 1
    data.loc[
        (data["er"] < -0.6)
        & (data["p_er"] >= -0.6),
        "ER_BEAR"
    ] = 1
    data = data.dropna()

    buy_sell_signals = pd.DataFrame(index=df.index)
    buy_sell_signals[f"{prefix}ER_BULL{suffix}"] = data["ER_BULL"]
    buy_sell_signals[f"{prefix}ER_BEAR{suffix}"] = data["ER_BEAR"]

    del data
    gc.collect()

    return buy_sell_signals
