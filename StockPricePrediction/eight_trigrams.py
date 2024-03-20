import pandas as pd
import numpy as np
def create_trigrams(df, high="High", low="Low", close="Close", prefix="", suffix=""):
    """
    Takes input high/low/close features and creates the 8-trigram scheme ☰ ☱ ☲ ☳ ☴ ☵ ☶ ☷

    Parameters:
        df (DataFrame): Input DataFrame containing financial data.
        high (str): Column name for the high prices. Default is "High".
        low (str): Column name for the low prices. Default is "Low".
        close (str): Column name for the close prices. Default is "Close".
        prefix (str): Prefix to be appended to the trigram column names. Default is an empty string.
        suffix (str): Suffix to be appended to the trigram column names. Default is an empty string.

    Returns:
        DataFrame: DataFrame containing binary indicators for each trigram pattern.
    """

    # If prefix or suffix is provided, adjust them
    if len(prefix) > 0:
        prefix = prefix + "_"
    if len(suffix) > 0:
        suffix = "_" + suffix

    # Create a DataFrame to store trigram indicators, indexed with the same index as the input DataFrame
    traigram_df = pd.DataFrame(index=df.index)

    # Calculate trigram components: Upper, Middle, and Lower
    traigram_df["Upper"] = df[high] > df[high].shift(1)
    traigram_df["Middle"] = df[close] > df[close].shift(1)
    traigram_df["Lower"] = df[low] > df[low].shift(1)

    # Define patterns for each trigram along with corresponding lambda functions
    trigram_patterns = {
        #  ["⚋", "⚊", "⚊"]:  # "BullishHarami" ☱
        f"{prefix}BullishHarami{suffix}": lambda df: (
            (df["Upper"] == False) & (df["Middle"] == True) & (df["Lower"] == True)
        ),
        #  ["⚊", "⚊", "⚋"]:  # "BullishHorn" ☴
        f"{prefix}BullishHorn{suffix}": lambda df: (
            (df["Upper"] == True) & (df["Middle"] == True) & (df["Lower"] == False)
        ),
        #  ["⚊", "⚊", "⚊"]:  # "BullishHigh" ☰
        f"{prefix}BullishHigh{suffix}": lambda df: (
            (df["Upper"] == True) & (df["Middle"] == True) & (df["Lower"] == True)
        ),
        #  ["⚋", "⚊", "⚋"]:  # "BullishLow" ☵
        f"{prefix}BullishLow{suffix}": lambda df: (
            (df["Upper"] == False) & (df["Middle"] == True) & (df["Lower"] == False)
        ),
        #  ["⚋", "⚋", "⚊"]:  # "BearHarami" ☳
        f"{prefix}BearHarami{suffix}": lambda df: (
            (df["Upper"] == False) & (df["Middle"] == False) & (df["Lower"] == True)
        ),
        #  ["⚊", "⚋", "⚋"]:  # "BearHorn" ☶
        f"{prefix}BearHorn{suffix}": lambda df: (
            (df["Upper"] == True) & (df["Middle"] == False) & (df["Lower"] == False)
        ),
        #  ["⚊", "⚋", "⚊"]:  # "BearHigh" ☲
        f"{prefix}BearHigh{suffix}": lambda df: (
            (df["Upper"] == True) & (df["Middle"] == False) & (df["Lower"] == True)
        ),
        #  ["⚋", "⚋", "⚋"]:  # "BearLow" ☷
        f"{prefix}BearLow{suffix}": lambda df: (
            (df["Upper"] == False) & (df["Middle"] == False) & (df["Lower"] == False)
        ),
    }

    # Iterate over trigram patterns
    for trigram in trigram_patterns:
        # Calculate trigram indicators using corresponding lambda function
        traigram_df[trigram] = trigram_patterns[trigram](traigram_df)
        # Map True/False to 1/0 in the trigram indicators
        traigram_df[trigram] = traigram_df[trigram].map({True: 1, False: 0})

    # Set the first row of trigram indicators to NaN since they cannot be determined for the first row
    traigram_df.iloc[0, -8:] = np.nan

    # Return trigram DataFrame containing binary indicators for each trigram pattern
    return traigram_df[list(trigram_patterns.keys())]
