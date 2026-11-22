import time
from datetime import datetime, timezone
import pandas as pd
import yfinance as yf
from app.config.indexes import INDEX_CONFIG

CACHE = {}
CACHE_DURATION = 60

def get_cached_data(key):
    cached = CACHE.get(key)
    if not cached:
        return None
    if time.time() - cached["timestamp"] > CACHE_DURATION:
        CACHE.pop(key, None)
        return None
    return cached["data"]

def set_cached_data(key, data):
    CACHE[key] = {
        "data": data,
        "timestamp": time.time()
    }

def clean_number(value):
    if pd.isna(value):
        return None
    return round(float(value), 2)

def format_timestamp(value):
    timestamp = pd.Timestamp(value)
    if timestamp.tzinfo is None:
        timestamp = timestamp.tz_localize("Asia/Kolkata")
    else:
        timestamp = timestamp.tz_convert("Asia/Kolkata")
    return timestamp.isoformat()

def fetch_single_index(index_id, config, force_refresh=False):
    cache_key = f"index_{index_id}"
    if not force_refresh:
        cached = get_cached_data(cache_key)
        if cached is not None:
            return cached
    symbol = config["symbol"]
    try:
        ticker = yf.Ticker(symbol)
        # Get daily history for the latest available
        # trading session and previous close.
        daily = ticker.history(
            period="5d",
            interval="1d",
            auto_adjust=False,
            actions=False,
            timeout=15,
            raise_errors=True
        )
        if daily.empty or "Close" not in daily.columns:
            raise ValueError("No daily closing data returned.")
        daily = daily.dropna(subset=["Close"])
        if len(daily) < 2:
            raise ValueError("Insufficient daily history.")
        latest_daily_date = pd.Timestamp(
            daily.index[-1]
        ).date()
        previous_close = float(daily["Close"].iloc[-2])
        current_value = float(daily["Close"].iloc[-1])
        timestamp = format_timestamp(daily.index[-1])
        price_type = "daily_close"

        # Try to obtain the latest intraday observation.
        try:
            intraday = ticker.history(
                period="1d",
                interval="5m",
                auto_adjust=False,
                actions=False,
                timeout=15,
                raise_errors=True
            )
            if not intraday.empty and "Close" in intraday.columns:
                intraday = intraday.dropna(subset=["Close"])
                if not intraday.empty:
                    latest = intraday.iloc[-1]
                    intraday_date = pd.Timestamp(
                        intraday.index[-1]
                    ).date()

                    # Only use intraday data when it belongs
                    # to the latest daily trading session.
                    if intraday_date == latest_daily_date:
                        current_value = float(latest["Close"])
                        timestamp = format_timestamp(
                            intraday.index[-1]
                        )
                        price_type = "intraday_5m"

        except Exception:
            # Daily closing data remains the fallback.
            pass
        if previous_close == 0:
            raise ValueError("Previous close cannot be zero.")
        change = current_value - previous_close
        change_percent = (change / previous_close) * 100
        result = {
            "id": index_id,
            "name": config["name"],
            "symbol": symbol,
            "category": config["category"],
            "featured": config["featured"],

            "value": clean_number(current_value),
            "previousClose": clean_number(previous_close),
            "change": clean_number(change),
            "changePercent": round(change_percent, 2),

            "unit": "points",
            "priceType": price_type,
            "marketTimestamp": timestamp,

            "source": "Yahoo Finance",
            "status": "success"
        }
        set_cached_data(cache_key, result)
        return result

    except Exception as error:
        return {
            "id": index_id,
            "name": config["name"],
            "symbol": symbol,
            "category": config["category"],
            "featured": config["featured"],

            "value": None,
            "previousClose": None,
            "change": None,
            "changePercent": None,

            "unit": "points",
            "priceType": None,
            "marketTimestamp": None,

            "source": "Yahoo Finance",
            "status": "error",
            "error": str(error)
        }

def fetch_all_indexes(force_refresh=False):
    results = []
    for index_id, config in INDEX_CONFIG.items():
        result = fetch_single_index(
            index_id,
            config,
            force_refresh
        )
        results.append(result)
    successful = sum(
        item["status"] == "success"
        for item in results
    )
    return {
        "success": successful > 0,
        "source": "Yahoo Finance via yfinance",
        "count": len(results),
        "successfulCount": successful,
        "failedCount": len(results) - successful,
        "fetchedAt": datetime.now(timezone.utc).isoformat(),
        "data": results
    }

def fetch_index_by_id(index_id, force_refresh=False):
    config = INDEX_CONFIG.get(index_id)
    if not config:
        return None
    return fetch_single_index(
        index_id,
        config,
        force_refresh
    )