import os
import sys
import torch
import random
import pandas as pd
import numpy as np
from datetime import datetime
import yfinance as yfin
from collections import namedtuple

tick_data_info = namedtuple("tick_data_info", "idx symbol sector tick_data")

# logging
sys.path.append("../")
from MyPyUtil.logconf import logging

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

"""
**download stocks list from ftp://ftp.nasdaqtrader.com/symboldirectory**  
[**reference: nasdaqtrader**](https://www.nasdaqtrader.com/trader.aspx?id=symboldirdefs)

- **Market Category:** The category assigned to the issue by NASDAQ based on Listing Requirements. Values:  
   Q = NASDAQ Global Select MarketSM  
   G = NASDAQ Global MarketSM  
   S = NASDAQ Capital Market

- **Test Issue:** Indicates whether or not the security is a test security. Values:  
   Y = yes, it is a test issue.  
   N = no, it is not a test issue.

- **Financial Status:** Indicates when an issuer has failed to submit its regulatory filings on a timely basis, has failed to meet NASDAQ's continuing listing standards, and/or has filed for bankruptcy. Values include:
  D = Deficient: Issuer Failed to Meet NASDAQ Continued Listing Requirements  
  E = Delinquent: Issuer Missed Regulatory Filing Deadline  
  Q = Bankrupt: Issuer Has Filed for Bankruptcy  
  N = Normal (Default): Issuer Is NOT Deficient, Delinquent, or Bankrupt.  
  G = Deficient and Bankrupt  
  H = Deficient and Delinquent  
  J = Delinquent and Bankrupt  
  K = Deficient, Delinquent, and Bankrupt

"""
def download_stocks_list():
    from ftplib import FTP

    # Connect to the FTP server
    ftp = FTP("ftp.nasdaqtrader.com")
    ftp.login(user="anonymous", passwd="aaa@aaa.com")

    # Change to the desired directory
    ftp.cwd("symboldirectory")

    # Download a file (e.g., 'example.txt') to the local machine
    with open("nasdaqlisted.txt", "wb") as local_file:
        ftp.retrbinary("RETR nasdaqlisted.txt", local_file.write)

    # Close the FTP connection
    ftp.quit()

    stocks_list = pd.read_csv("nasdaqlisted.txt", delimiter="|")
    stocks_list.drop(index=stocks_list.index[-1], axis=0, inplace=True)
    stocks_list = stocks_list[
        (stocks_list["Test Issue"] == "N")
        & (stocks_list["ETF"] == "N")
        & (stocks_list["Financial Status"] == "N")
    ]

    NaN_symbol = stocks_list[stocks_list["Symbol"].isnull()]
    log.debug(f"empty count:{stocks_list.isnull().sum()}")
    log.debug(f"NaN Symbol:{NaN_symbol}")

    stocks_list.drop(NaN_symbol.index, inplace=True)
    log.info(stocks_list)
    log.info(stocks_list.groupby("Market Category").count()["Symbol"])

    return stocks_list

def retrieve_sectors_from_yfinance(symbols):
    from tqdm import tqdm
    sectors_data = []
    for _, symbol in enumerate(tqdm(symbols, desc="yfin.Ticker")):
        # Retrieving ticker information for each symbol and appending to list
        info = yfin.Ticker(symbol).info
        sectors_data.append(info["sector"] if "sector" in info.keys() else "")

    # Creating DataFrame to store symbol and corresponding sector information
    retrived_sectors = pd.DataFrame(
        data={
            "Symbol": symbols,
            "Sector": sectors_data,
        }
    )
    return retrived_sectors


# Load stock data
def load_stock_data(sectors, stk_symbols, start, end, empty_vol_threshold, data_dir):
    from MyPyUtil.util import is_contained
    from tqdm import tqdm
    ticks_data = []

    error_download = []
    error_sector_not_found = []
    error_numerical = []
    error_volumn = []
    error_empty = []
    for idx, symbol in enumerate(tqdm(stk_symbols)):
        if sectors.loc[symbol].Sector == "":
            log.warning(f"{symbol}: Its sector cannot be found")
            error_sector_not_found.append(symbol)
            continue

        stk_file = f"{data_dir}{symbol}_{start.strftime('%Y%m%d')}-{end.strftime('%Y%m%d')}.csv"
        bLoad = False
        if os.path.isfile(stk_file):
            try:
                _stk_data = pd.read_csv(stk_file).set_index("Date")
                bLoad = True
                log.info(f"read {stk_file} completely!")
            except:
                None
        if bLoad == False:
            # _stk_data = web.get_data_yahoo(stk_tickers, start, end)
            try:
                _stk_data = yfin.download([symbol], start, end).dropna()
                _stk_data.to_csv(stk_file)
                log.info(
                    f"download {symbol} from yfin and write to {stk_file} completely!"
                )
            except:
                error_download.append(symbol)
                continue
        statistics = _stk_data.describe()
        if is_contained(statistics, 0):
            if is_contained(
                statistics.loc[:, ["Open", "High", "Low", "Close", "Adj Close"]], 0
            ) or is_contained(statistics.loc["std"], 0):
                log.warning(f"{symbol}: contains numerical errors. Ignore it.")
                error_numerical.append(symbol)
                continue
            else:
                empty_vol_index = _stk_data[_stk_data["Volume"] == 0].index
                if len(empty_vol_index) > empty_vol_threshold:
                    log.warning(
                        f"The total volume with a value of zero ({len(empty_vol_index)}) is greater than the threshold({empty_vol_threshold}). Ignore it."
                    )
                    error_volumn.append(symbol)
                    continue
                log.info(
                    f"A total of {len(empty_vol_index)} volume values ​​are zero. Delete these data."
                )

                cleaned_data = _stk_data.drop(empty_vol_index)
                log.info(
                    f"The cleaned data size is {len(cleaned_data)}. The original data size is {len(_stk_data)}."
                )
                if len(cleaned_data) == 0:
                    error_empty.append(symbol)
                    log.warning(f"The cleaned data size is {len(cleaned_data)}.")
                    continue
                _stk_data = cleaned_data

        ticks_data.append(
            tick_data_info(idx, symbol, sectors.loc[symbol].Sector, _stk_data)
        )
        log.info(f"{symbol}, size:{len(_stk_data)}")
    return ticks_data, (
        error_download,
        error_sector_not_found,
        error_numerical,
        error_volumn,
        error_empty,
    )


def get_sectors_data(stocks_list, resources_dir):
    sectors_file = f"{resources_dir}/sectors.csv"
    if os.path.exists(sectors_file):
        sectors = pd.read_csv(sectors_file).fillna("")
        sectors.drop(columns=sectors.columns[0], axis=1, inplace=True)
        log.info(sectors.groupby("Sector").count())
    else:
        sectors = pd.DataFrame(columns=["Symbol", "Sector"])

    tmp_list = stocks_list.merge(sectors, how="left", on="Symbol")
    stocks_without_sector = tmp_list[tmp_list.Sector.isna()]
    if len(stocks_without_sector) == 0:
        return sectors

    retrived_sectors = retrieve_sectors_from_yfinance(
        stocks_without_sector.Symbol.values
    )
    log.debug(retrived_sectors)

    new_sectors = retrived_sectors.merge(sectors, on=["Symbol", "Sector"], how="outer")
    new_sectors.to_csv(sectors_file)
    log.info(new_sectors)

    return new_sectors


def build_stocks_data(
    start, end, empty_vol_threshold, data_dir, resources_dir, drop_empty_sectors=True
):
    stocks_list = download_stocks_list()
    sectors = get_sectors_data(stocks_list, resources_dir)
    stocks_list = stocks_list.merge(sectors, how="left", on="Symbol")

    log.info(stocks_list)
    log.info(stocks_list.groupby("Sector").Symbol.count())

    if drop_empty_sectors:
        stocks_with_empty_sector = stocks_list[stocks_list.Sector == ""]
        stocks_list.drop(stocks_with_empty_sector.index, inplace=True)
        log.info(f"new stocks_list after dropping empty sectors:\n{stocks_list}")

    stks_data, (
        error_download,
        error_sector_not_found,
        error_numerical,
        error_volumn,
        error_empty,
    ) = load_stock_data(
        sectors.set_index("Symbol"),
        stocks_list.Symbol.values,
        start,
        end,
        empty_vol_threshold,
        data_dir,
    )

    return stks_data
