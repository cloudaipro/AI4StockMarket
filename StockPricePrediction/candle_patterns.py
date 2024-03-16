import os
import pandas as pd
import numpy as np
import talib as ta

cs_patterns_rest = {
    "shortLineCdl": lambda openP, high, low, close: ta.CDLSHORTLINE(
        openP, high, low, close
    ),
    "longLineCdl": lambda openP, high, low, close: ta.CDLLONGLINE(
        openP, high, low, close
    ),
    "spinningTop": lambda openP, high, low, close: ta.CDLSPINNINGTOP(
        openP, high, low, close
    ),
    "closingMarubozu": lambda openP, high, low, close: ta.CDLCLOSINGMARUBOZU(
        openP, high, low, close
    ),
    # "hammer": lambda openP, high, low, close: ta.CDLHAMMER(openP, high, low, close),
    # "doji": lambda openP, high, low, close: ta.CDLDOJI(openP, high, low, close),
    # "engulfing": lambda openP, high, low, close: ta.CDLENGULFING(
    #     openP, high, low, close
    # ),
    # "hangingMan": lambda openP, high, low, close: ta.CDLHANGINGMAN(
    #     openP, high, low, close
    # ),
    # "hammer": lambda openP, high, low, close: ta.CDLHAMMER(openP, high, low, close),
    # "invertedHammer": lambda openP, high, low, close: ta.CDLINVERTEDHAMMER(
    #     openP, high, low, close
    # ),
    # "marubozu": lambda openP, high, low, close: ta.CDLMARUBOZU(openP, high, low, close),
    # "beltHold": lambda openP, high, low, close: ta.CDLBELTHOLD(openP, high, low, close),
    # "breakaway": lambda openP, high, low, close: ta.CDLBREAKAWAY(
    #     openP, high, low, close
    # ),
    # "inNeck": lambda openP, high, low, close: ta.CDLINNECK(openP, high, low, close),
    # "kicking": lambda openP, high, low, close: ta.CDLKICKING(openP, high, low, close),
    # "kickingByLength": lambda openP, high, low, close: ta.CDLKICKINGBYLENGTH(
    #     openP, high, low, close
    # ),
    # "ladderBottom": lambda openP, high, low, close: ta.CDLLADDERBOTTOM(
    #     openP, high, low, close
    # ),
    # "longLeggedDoji": lambda openP, high, low, close: ta.CDLLONGLEGGEDDOJI(
    #     openP, high, low, close
    # ),
    # "rickShawMan": lambda openP, high, low, close: ta.CDLRICKSHAWMAN(
    #     openP, high, low, close
    # ),
    # "stalled": lambda openP, high, low, close: ta.CDLSTALLEDPATTERN(
    #     openP, high, low, close
    # ),
    # "stickSandwhich": lambda openP, high, low, close: ta.CDLSTICKSANDWICH(
    #     openP, high, low, close
    # ),
    # "takuri": lambda openP, high, low, close: ta.CDLTAKURI(openP, high, low, close),
    # "tasukiGap": lambda openP, high, low, close: ta.CDLTASUKIGAP(
    #     openP, high, low, close
    # ),
    # "stalled": lambda openP, high, low, close: ta.CDLSTALLEDPATTERN(
    #     openP, high, low, close
    # ),
    # "thrusting": lambda openP, high, low, close: ta.CDLTHRUSTING(
    #     openP, high, low, close
    # ),
}
