# app/config/metals.py

METALS_CONFIG = {
    "gold": {
        "name": "Gold",
        "symbol": "GC=F",
        "source_unit": "USD per troy ounce",
        "display_unit": "10 grams",
        "conversion_type": "troy_ounce",
        "featured": True
    },

    "silver": {
        "name": "Silver",
        "symbol": "SI=F",
        "source_unit": "USD per troy ounce",
        "display_unit": "1 kilogram",
        "conversion_type": "troy_ounce",
        "featured": True
    },

    "copper": {
        "name": "Copper",
        "symbol": "HG=F",
        "source_unit": "USD per pound",
        "display_unit": "1 kilogram",
        "conversion_type": "pound",
        "featured": True
    },

    "platinum": {
        "name": "Platinum",
        "symbol": "PL=F",
        "source_unit": "USD per troy ounce",
        "display_unit": "10 grams",
        "conversion_type": "troy_ounce",
        "featured": True
    }
}

USD_INR_SYMBOL = "USDINR=X"

# Unit conversion constants
TROY_OUNCE_IN_GRAMS = 31.1034768
POUND_IN_KG = 0.45359237