import pandas as pd
import pandas_ta
import numpy as np
import gc
"""
https://www.whselfinvest.com/en-be/trading-platform/free-trading-signals/15-dr-alexander-elder-ray-bull-power-bear-power
"""
def create_buy_sell_signals(df, high, low, close, length, prefix="", suffix=""):
    """
    Create buy and sell signals based on the ERI strategy.

    Args:
        df (pandas.DataFrame): The input DataFrame containing the stock market data.
        high (str): The column name for the high prices.
        low (str): The column name for the low prices.
        close (str): The column name for the closing prices.
        length (int): The length parameter for the ERI indicator.
        prefix (str, optional): The prefix to be added to the signal column names. Defaults to "".
        suffix (str, optional): The suffix to be added to the signal column names. Defaults to "".

    Returns:
        pandas.DataFrame: A DataFrame containing the buy and sell signals.

    """
    # If prefix or suffix is provided, adjust them
    if len(prefix) > 0:
        prefix = prefix + "_"
    if len(suffix) > 0:
        suffix = "_" + suffix

    # Create a DataFrame to store calculated values
    data = pd.DataFrame(index=df.index)
    data["close"] = df[close]
    data["p_close"] = data["close"].shift(1)
    data[["bull", "bear"]] = df.ta.eri(high=high, low=low, close=close, length=length)
    data["ema"] = df.ta.ema(close=close, length=length)
    data["p_ema"] = data["ema"].shift(1)
    data["p_bull"] = data["bull"].shift(1)
    data["p_bear"] = data["bear"].shift(1)

    data["ERI_BULL"] = 0
    data["ERI_BEAR"] = 0

    """
    The market price (EMA) is going up.
    The Bear Power is negative (below zero), but going up.
    The current Bull Power bar is higher than the previous bar.
    The Bear Power indicator shows a bullish divergence with the market price. This means the indicator goes up and the price down.
    """
    data.loc[
        (data["ema"] > data["p_ema"])
        & (data["bear"] < 0)
        & (data["bear"] > data["p_bear"])
        & (data["bull"] > data["p_bull"])
        & (data["close"] < data["p_close"]),
        "ERI_BULL",
    ] = 1
    """
    The market price (EMA) is going up.
    The Bull Power is positive (above zero), but going down.
    The current Bear Power bar is lower than the previous bar.
    The Bull Power shows a bearish divergence with the market price. This means the indicator goes down and the market price goes up
    """
    data.loc[
        (data["ema"] > data["p_ema"])
        & (data["bull"] > 0)
        & (data["bull"] < data["p_bull"])
        & (data["bear"] < data["p_bear"])
        & (data["close"] > data["p_close"]),
        "ERI_BEAR",
    ] = 1
    data = data.dropna()

    buy_sell_signals = pd.DataFrame(index=df.index)
    buy_sell_signals[f"{prefix}ERI_BULL{suffix}"] = data["ERI_BULL"]
    buy_sell_signals[f"{prefix}ERI_BEAR{suffix}"] = data["ERI_BEAR"]

    del data
    gc.collect()

    return buy_sell_signals
