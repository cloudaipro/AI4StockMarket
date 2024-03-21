import pandas as pd
import pandas_ta
import numpy as np
import gc


"""
https://school.stockcharts.com/doku.php?id=technical_indicators:accumulation_distribution_line
"""
def create_signals(df, high, low, close, volume, prefix="", suffix=""):

    # If prefix or suffix is provided, adjust them
    if len(prefix) > 0:
        prefix = prefix + "_"
    if len(suffix) > 0:
        suffix = "_" + suffix

    # Create a DataFrame to store calculated values
    data = pd.DataFrame(index=df.index)
    data["close"] = df[close]
    data["sma20"] = df.ta.sma(close=close, length=20)
    data["sma65"] = df.ta.sma(close=close, length=65)
    data["ad"] = df.ta.ad(high=high, low=low, close=close, volume=volume)
    data["obv"] = df.ta.obv(close=close, volume=volume)
    data["ad20"] = data.ta.sma(close="ad", length=20)
    data["ad65"] = data.ta.sma(close="ad", length=65)
    data["obv20"] = data.ta.sma(close="obv", length=20)
    data["obv65"] = data.ta.sma(close="obv", length=65)

    data["OBV_ADL_BULL_DIVERGENCE"] = 0
    data["OBV_ADL_BEAR_DIVERGENCE"] = 0

    """
    [Daily Close < Daily SMA(65,Daily Close)] 
    AND [Daily AccDist > Daily AccDist Signal (65)] 
    AND [Daily OBV > Daily OBV Signal(65)] 
    AND [Daily Close < Daily SMA(20,Daily Close)] 
    AND [Daily AccDist > Daily AccDist Signal (20)] 
    AND [Daily OBV > Daily OBV Signal(20)]
    """
    data.loc[
        (data["close"] < data["sma65"])
        & (data["ad"] > data["ad65"])
        & (data["obv"] > data["obv65"])
        & (data["close"] < data["sma20"])
        & (data["ad"] > data["ad20"])
        & (data["obv"] > data["obv20"]),
        "OBV_ADL_BULL_DIVERGENCE",
    ] = 1

    """
    [Daily Close > Daily SMA(65,Daily Close)] 
    AND [Daily AccDist < Daily AccDist Signal (65)] 
    AND [Daily OBV < Daily OBV Signal(65)] 
    AND [Daily Close > Daily SMA(20,Daily Close)] 
    AND [Daily AccDist < Daily AccDist Signal (20)] 
    AND [Daily OBV < Daily OBV Signal(20)]
    """
    data.loc[
        (data["close"] > data["sma65"])
        & (data["ad"] < data["ad65"])
        & (data["obv"] < data["obv65"])
        & (data["close"] > data["sma20"])
        & (data["ad"] < data["ad20"])
        & (data["obv"] < data["obv20"]),
        "OBV_ADL_BEAR_DIVERGENCE",
    ] = 1

    data = data.dropna()

    buy_sell_signals = pd.DataFrame(index=df.index)
    buy_sell_signals[f"{prefix}OBV_ADL_BULL_DIVERGENCE{suffix}"] = data[
        "OBV_ADL_BULL_DIVERGENCE"
    ]
    buy_sell_signals[f"{prefix}OBV_ADL_BEAR_DIVERGENCE{suffix}"] = data[
        "OBV_ADL_BEAR_DIVERGENCE"
    ]

    del data
    gc.collect()

    return buy_sell_signals
