import pandas as pd
import talib as ta
import numpy as np
from itertools import compress
from candle_rankings import (
    candle_rankings,
)  # Importing candle_rankings module for ranking candlestick patterns
from sklearn.preprocessing import OneHotEncoder
from MyPyUtil.util import ivmin
import gc

def create_candle_signals(
    df, open="Open", high="High", low="Low", close="Close", prefix="", suffix=""
):
    """
    Creates candlestick signals based on the input DataFrame.

    Parameters:
        df (DataFrame): Input DataFrame containing OHLC (Open, High, Low, Close) data.
        open (str): Name of the column containing opening prices.
        high (str): Name of the column containing high prices.
        low (str): Name of the column containing low prices.
        close (str): Name of the column containing closing prices.
        prefix (str): Prefix to be added to the transformed column names.
        suffix (str): Suffix to be added to the transformed column names.

    Returns:
        DataFrame: Transformed DataFrame with one-hot encoded candlestick patterns.
    """

    # If prefix or suffix is provided, adjust them
    if len(prefix) > 0:
        prefix = prefix + "_"
    if len(suffix) > 0:
        suffix = "_" + suffix

    # Get list of candlestick pattern names
    candle_names = ta.get_function_groups()["Pattern Recognition"]

    op = df[open]
    hi = df[high]
    lo = df[low]
    cl = df[close]

    # Initialize DataFrame for storing candlestick values
    candle_values = pd.DataFrame(index=df.index)
    for candle in candle_names:
        # Calculate candlestick values using TA-Lib functions
        candle_values[candle] = getattr(ta, candle)(op, hi, lo, cl)

    # Initialize column for storing detected candlestick patterns
    candle_values["candlestick_pattern"] = np.nan
    # Initialize column for storing the count of matched patterns
    candle_values["candlestick_match_count"] = np.nan

    # Define a lambda function to determine candlestick pattern name based on bullish or bearish signal
    to_pattern_name = lambda row, signal_name: signal_name + (
        "_BULL" if row[signal_name] > 0 else "_BEAR"
    )
    for index, row in candle_values.iterrows():
        # Check if each candlestick pattern is detected
        candle_signals = row[candle_names].values != 0
        # Count the number of detected patterns
        found_pattern = sum(candle_signals)

        # If no pattern is found in the row
        if found_pattern == 0:
            candle_values.loc[index, "candlestick_pattern"] = (
                "NO_PATTERN"  # Mark as no pattern found
            )
            candle_values.loc[index, "candlestick_match_count"] = 0
        # If a single pattern is found
        elif found_pattern == 1:
            # Get the name of the detected pattern
            signal_name = list(compress(row[candle_names].keys(), candle_signals))[0]
            candle_values.loc[index, "candlestick_pattern"] = to_pattern_name(
                row, signal_name
            )
            # Set candlestick pattern name based on the detected pattern
            candle_values.loc[index, "candlestick_match_count"] = 1
        # If multiple patterns are matched, select the best performance
        else:
            # filter out pattern names from bool list of values
            # Get names of detected patterns
            signals_name = list(compress(row[candle_names].keys(), candle_signals))
            # Determine candlestick pattern names
            patterns_name = [
                to_pattern_name(row, signal_name) for signal_name in signals_name
            ]  
            # Retrieve ranking of detected patterns
            ranks_list = [
                candle_rankings[pattern_name] for pattern_name in patterns_name
            ]  
            # Get index of the best-performing pattern
            rank_index_best, _ = ivmin(
                ranks_list
            )  
            # Set the best-performing pattern
            candle_values.loc[index, "candlestick_pattern"] = patterns_name[
                rank_index_best
            ]  
            candle_values.loc[index, "candlestick_match_count"] = len(patterns_name)

    # Define categories for one-hot encoding
    ohe_categories = [list(candle_rankings.keys())]
    ohe_columns = ["candlestick_pattern"]
    # Initialize OneHotEncoder
    enc = OneHotEncoder(
        sparse_output=False,
        categories=ohe_categories,
        handle_unknown="ignore",
        dtype=int,
    )
    # Convert the encoded features to a DataFrame
    transformed_df = pd.DataFrame(
        enc.fit_transform(
            candle_values[ohe_columns]
        ),  # Fit and transform the candlestick pattern column
        columns=enc.get_feature_names_out(),
        index=candle_values.index,
    )
    # Position to start extracting column names
    start_pos = len("candlestick_pattern") + 1
    # Rename columns with prefix and suffix
    transformed_df.columns = [
        f"{prefix}{name[start_pos:]}{suffix}" for name in transformed_df.columns
    ]

    del candle_values
    gc.collect()
    
    return transformed_df
