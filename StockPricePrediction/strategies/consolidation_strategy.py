import pandas as pd


def detectx(
    df, high, low, close, volume, length=10, std=2.0, scalar=1.2, prefix="", suffix=""
):
    # If prefix or suffix is provided, adjust them
    if len(prefix) > 0:
        prefix = prefix + "_"
    if len(suffix) > 0:
        suffix = "_" + suffix

    # Create a DataFrame to store calculated values
    data = pd.DataFrame(index=df.index)

    data["SMA"] = df[close].rolling(window=length).mean()
    data["stdev"] = df[close].rolling(window=length).std()
    data["Lower_Bollinger"] = data["SMA"] - (std * data["stdev"])
    data["Upper_Bollinger"] = data["SMA"] + (std * data["stdev"])
    data["TR"] = abs(df[high] - df[low])
    data["ATR"] = data["TR"].rolling(window=length).mean()
    data["Upper_KC"] = data["SMA"] + (scalar * data["ATR"])
    data["Lower_KC"] = data["SMA"] - (scalar * data["ATR"])
    data[volume] = df[volume]
    data["MeanVolume"] = df[volume].rolling(window=length).mean()
    data["LowVolume"] = data[volume] < data["MeanVolume"]
    print(data)
    data["consolidation"] = 0
    data.loc[
        (data["Lower_Bollinger"] > data["Lower_KC"])
        & (data["Upper_Bollinger"] < data["Upper_KC"]) & (data["LowVolume"])
    , "consolidation"] = 1
    # def in_consolidation(row):
    #     return (
    #         row["Lower_Bollinger"] > row["Lower_KC"]
    #         and row["Upper_Bollinger"] < row["Upper_KC"] & row["LowVolume"]
    #     )

    # data["consolidation"] = df.apply(in_consolidation, axis=1)

    return data
