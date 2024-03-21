import pandas as pd
import pandas_ta
import numpy as np
import gc

"""
Many professional traders find the default settings (12, 26 and 9) to be too slow, causing late entry and exit to and from a trade. 
You may want to customize/format the settings and see how well they perform on a demo account. Some alternative settings to try are:
ref: https://www.dynotrading.com/10-best-macd-settings-for-effective-trading/#:~:text=Top%2010%20MACD%20settings%20for%20effective%20trading%201,may%20suit%20your%20trading%20style.%20...%20More%20items
     https://www.oanda.com/us-en/learn/indicators-oscillators/determining-entry-and-exit-points-with-macd/
8, 21, 5
3, 17, 5
3, 10, 16
"""
def create_buy_sell_signals(df, close, fast, slow, signal, prefix="", suffix=""):

    # If prefix or suffix is provided, adjust them
    if len(prefix) > 0:
        prefix = prefix + "_"
    if len(suffix) > 0:
        suffix = "_" + suffix

    # Create a DataFrame to store calculated values
    data = df.ta.macd(close=close, fast=fast, slow=slow, signal=signal)

    macd_line = data.iloc[:, 0]
    # histogram_line = data.iloc[:, 1]
    signal_line = data.iloc[:, 2]
    data["p_macd_line"] = macd_line.shift(1)
    data["p_signal_line"] = signal_line.shift(1)

    data["CORSSOVER_BULL"] = 0
    data["CORSSOVER_BEAR"] = 0
    data["ZERO_CORSSING_BULL"] = 0
    data["ZERO_CORSSING_BEAR"] = 0

    data.loc[
        (macd_line > signal_line) & (data["p_macd_line"] < data["p_signal_line"]),
        "CORSSOVER_BULL",
    ] = 1
    data.loc[
        (macd_line < signal_line) & (data["p_macd_line"] > data["p_signal_line"]),
        "CORSSOVER_BEAR",
    ] = 1
    data.loc[(macd_line > 0) & (data["p_macd_line"] < 0), "ZERO_CORSSING_BULL"] = 1
    data.loc[(macd_line < 0) & (data["p_macd_line"] > 0), "ZERO_CORSSING_BEAR"] = 1

    data = data.dropna()

    buy_sell_signals = pd.DataFrame(index=df.index)
    buy_sell_signals[f"{prefix}CORSSOVER_BULL{suffix}"] = data["CORSSOVER_BULL"]
    buy_sell_signals[f"{prefix}CORSSOVER_BEAR{suffix}"] = data["CORSSOVER_BEAR"]

    buy_sell_signals[f"{prefix}ZERO_CORSSING_BULL{suffix}"] = data["ZERO_CORSSING_BULL"]
    buy_sell_signals[f"{prefix}ZERO_CORSSING_BEAR{suffix}"] = data["ZERO_CORSSING_BEAR"]

    del data
    gc.collect()

    return buy_sell_signals
