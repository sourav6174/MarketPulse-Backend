# app/services/metals_service.py

import time
import logging
import threading

import yfinance as yf

from app.config.metals import (
    METALS_CONFIG,
    USD_INR_SYMBOL,
    TROY_OUNCE_IN_GRAMS,
    POUND_IN_KG
)


logger = logging.getLogger(__name__)

# --------------------------------------------------
# CACHE CONFIGURATION
# --------------------------------------------------

CACHE_DURATION = 60

_metals_cache = None
_cache_timestamp = 0

_cache_lock = threading.Lock()


# --------------------------------------------------
# FETCH HISTORICAL DATA
# --------------------------------------------------

def fetch_history(symbol):
    """
    Fetch the latest available daily historical data
    for a Yahoo Finance ticker.
    """

    try:
        ticker = yf.Ticker(symbol)

        history = ticker.history(
            period="5d",
            interval="1d",
            auto_adjust=False
        )

        if history.empty:
            logger.warning("No historical data received for %s", symbol)
            return None

        history = history.dropna(subset=["Close"])

        if history.empty:
            return None

        return history

    except Exception as error:
        logger.exception(
            "Error fetching Yahoo Finance data for %s: %s",
            symbol,
            error
        )

        return None


# --------------------------------------------------
# GET USD TO INR EXCHANGE RATE
# --------------------------------------------------

def get_usd_inr_rate():
    """
    Fetch the latest available USD/INR exchange rate.
    """

    history = fetch_history(USD_INR_SYMBOL)

    if history is None or len(history) == 0:
        raise ValueError("Unable to fetch USD/INR exchange rate")

    latest_rate = float(history["Close"].iloc[-1])

    if latest_rate <= 0:
        raise ValueError("Invalid USD/INR exchange rate")

    return latest_rate


# --------------------------------------------------
# PRICE CONVERSION
# --------------------------------------------------

def convert_price_to_inr(price_usd, conversion_type, usd_inr):
    """
    Convert the source commodity price into the
    required INR display unit.

    Gold/Silver/Platinum:
        USD per troy ounce -> INR per 10 grams

    Copper:
        USD per pound -> INR per kilogram
    """

    if conversion_type == "troy_ounce":

        price_per_gram_usd = (
            price_usd / TROY_OUNCE_IN_GRAMS
        )

        price_per_10g_inr = (
            price_per_gram_usd * 10 * usd_inr
        )

        return price_per_10g_inr

    elif conversion_type == "pound":

        price_per_kg_usd = (
            price_usd / POUND_IN_KG
        )

        price_per_kg_inr = (
            price_per_kg_usd * usd_inr
        )

        return price_per_kg_inr

    return None


# --------------------------------------------------
# GET INDIVIDUAL METAL DATA
# --------------------------------------------------

def get_metal_data(metal_id, config, usd_inr):
    """
    Fetch and process market data for one metal.
    """

    symbol = config["symbol"]

    history = fetch_history(symbol)

    if history is None or len(history) == 0:

        return {
            "id": metal_id,
            "name": config["name"],
            "symbol": symbol,
            "status": "failed",
            "error": "No market data available"
        }

    try:

        latest_row = history.iloc[-1]

        latest_source_price = float(latest_row["Close"])

        previous_source_price = None

        if len(history) >= 2:
            previous_source_price = float(
                history["Close"].iloc[-2]
            )

        if latest_source_price <= 0:
            raise ValueError("Invalid market price")

        conversion_type = config["conversion_type"]

        # Convert latest price into INR
        latest_price = convert_price_to_inr(
            latest_source_price,
            conversion_type,
            usd_inr
        )

        # Convert previous closing price into INR
        previous_price = None

        if previous_source_price is not None:

            previous_price = convert_price_to_inr(
                previous_source_price,
                conversion_type,
                usd_inr
            )

        # Calculate price movement
        change = None
        change_percent = None

        if previous_price is not None and previous_price != 0:

            change = latest_price - previous_price

            change_percent = (
                (change / previous_price) * 100
            )

        result = {
            "id": metal_id,
            "name": config["name"],
            "symbol": symbol,

            "price": round(latest_price, 2),

            "previousPrice": (
                round(previous_price, 2)
                if previous_price is not None
                else None
            ),

            "change": (
                round(change, 2)
                if change is not None
                else None
            ),

            "changePercent": (
                round(change_percent, 2)
                if change_percent is not None
                else None
            ),

            "unit": config["display_unit"],

            "sourcePrice": round(latest_source_price, 4),

            "sourceUnit": config["source_unit"],

            "currency": "INR",

            "marketTimestamp": history.index[-1].isoformat(),

            "status": "success"
        }

        # Additional 22K gold calculation
        if metal_id == "gold":

            result["price24k"] = round(latest_price, 2)

            result["price22k"] = round(
                latest_price * (22 / 24),
                2
            )

            if previous_price is not None:

                result["previousPrice24k"] = round(
                    previous_price,
                    2
                )

                result["previousPrice22k"] = round(
                    previous_price * (22 / 24),
                    2
                )

            if change is not None:

                result["change22k"] = round(
                    change * (22 / 24),
                    2
                )

        return result

    except Exception as error:

        logger.exception(
            "Error processing %s data: %s",
            metal_id,
            error
        )

        return {
            "id": metal_id,
            "name": config["name"],
            "symbol": symbol,
            "status": "failed",
            "error": str(error)
        }


# --------------------------------------------------
# GET ALL METALS DATA
# --------------------------------------------------

def fetch_all_metals():

    global _metals_cache
    global _cache_timestamp

    current_time = time.time()

    # Check cache first
    with _cache_lock:

        if (
            _metals_cache is not None
            and current_time - _cache_timestamp < CACHE_DURATION
        ):

            return _metals_cache

    metals_data = []

    try:

        # Fetch USD/INR once and reuse it
        usd_inr = get_usd_inr_rate()

        for metal_id, config in METALS_CONFIG.items():

            metal_data = get_metal_data(
                metal_id,
                config,
                usd_inr
            )

            metals_data.append(metal_data)

    except Exception as error:

        logger.exception("Unable to process metals data: %s", error)

        # Return individual failures if exchange-rate
        # data is unavailable.
        metals_data = [
            {
                "id": metal_id,
                "name": config["name"],
                "symbol": config["symbol"],
                "status": "failed",
                "error": "Unable to fetch USD/INR exchange rate"
            }
            for metal_id, config in METALS_CONFIG.items()
        ]

    successful_count = sum(
        1 for item in metals_data
        if item["status"] == "success"
    )

    failed_count = len(metals_data) - successful_count

    response = {
        "count": len(metals_data),
        "successfulCount": successful_count,
        "failedCount": failed_count,
        "currency": "INR",
        "usdInrRate": (
            round(usd_inr, 4)
            if "usd_inr" in locals()
            else None
        ),
        "data": metals_data
    }

    # Update cache
    with _cache_lock:

        _metals_cache = response
        _cache_timestamp = time.time()

    return response


# --------------------------------------------------
# FORCE REFRESH
# --------------------------------------------------

def clear_metals_cache():

    global _metals_cache
    global _cache_timestamp

    with _cache_lock:

        _metals_cache = None
        _cache_timestamp = 0