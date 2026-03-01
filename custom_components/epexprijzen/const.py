"""Constants for the epexprijzen.nl integration."""

DOMAIN = "epexprijzen"

CONF_PROVIDER = "provider"
CONF_INTERVAL = "price_interval"

INTERVAL_HOURLY = "hourly"
INTERVAL_QUARTERLY = "quarterly"

DEFAULT_SCAN_INTERVAL = 1800  # 30 minutes

API_URL = "https://epexprijzen.nl/api/v1/prices/{provider}/{interval}"

PROVIDERS: dict[str, str] = {
    "anwb-energie": "ANWB Energie",
    "atoom-alliantie": "Atoom Alliantie",
    "budget-energie": "Budget Energie",
    "coolblue-energie": "Coolblue Energie",
    "easyenergy": "easyEnergy",
    "eneco": "Eneco",
    "energie-vanons": "Energie VanOns",
    "energyzero": "EnergyZero",
    "engie": "Engie",
    "frank-energie": "Frank Energie",
    "frank-energie-slim": "Frank Energie (Slim terugleveren)",
    "hegg": "Hegg",
    "innova": "Innova",
    "nextenergy": "NextEnergy",
    "samsam": "SamSam",
    "tibber": "Tibber",
    "vandebron": "VandeBron",
    "zonneplan": "Zonneplan",
}
