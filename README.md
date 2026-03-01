# epexprijzen.nl – Home Assistant custom component

A Home Assistant custom integration that fetches Dutch dynamic energy prices from [epexprijzen.nl](https://epexprijzen.nl). It supports all major Dutch energy providers and provides hourly or quarterly price data as sensors.

## Features

- Current energy price sensor (with full `today` / `tomorrow` price lists as attributes)
- Lowest, highest and average price sensors for today and tomorrow
- Supports 18 Dutch energy providers
- Hourly or quarterly (15-minute) price intervals
- Configurable via the Home Assistant UI (no YAML required)
- Compatible with [apexcharts-card](https://github.com/RomRider/apexcharts-card) for price charts

## Installation

### HACS (recommended)

1. Open HACS in Home Assistant.
2. Go to **Integrations** → click the three dots menu → **Custom repositories**.
3. Add this repository URL and select category **Integration**.
4. Search for **epexprijzen.nl** and install it.
5. Restart Home Assistant.

### Manual

1. Copy the `custom_components/epexprijzen` folder into your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.

## Configuration

1. Go to **Settings → Integrations → Add integration**.
2. Search for **epexprijzen.nl**.
3. Select your energy provider and price interval (hourly or quarterly).
4. Click **Submit**.

You can add multiple entries if you want to compare prices across providers.

## Sensors

Each configured entry creates the following sensors:

| Sensor | Description | Extra attributes |
|--------|-------------|-----------------|
| **Huidige prijs** | Price for the current period | `today`, `tomorrow`, `energy_tax`, `provider_charge`, `current_period` |
| **Laagste prijs vandaag** | Lowest price today | `timestamp`, `local_time` |
| **Hoogste prijs vandaag** | Highest price today | `timestamp`, `local_time` |
| **Gemiddelde prijs vandaag** | Average price today | – |
| **Laagste prijs morgen** | Lowest price tomorrow (available ~13:00) | `timestamp`, `local_time` |
| **Hoogste prijs morgen** | Highest price tomorrow | `timestamp`, `local_time` |
| **Gemiddelde prijs morgen** | Average price tomorrow | – |

All prices are in **€/kWh** and include applicable taxes and provider surcharges.

## Dashboard example

After installing [apexcharts-card](https://github.com/RomRider/apexcharts-card), use the following card configuration to display today's and tomorrow's prices:

```yaml
type: custom:apexcharts-card
graph_span: 48h
span:
  start: day
now:
  show: true
  label: Nu
header:
  show: true
  title: Elektriciteitsprijzen (€/kWh)
yaxis:
  - decimals: 2
    min: ~0
    max: "|+0.05|"
series:
  - entity: sensor.engie_hourly_huidige_prijs
    stroke_width: 2
    name: Vandaag
    float_precision: 4
    type: line
    curve: stepline
    data_generator: |
      return entity.attributes.today.map((item) => [item.t, item.price]);
  - entity: sensor.engie_hourly_huidige_prijs
    stroke_width: 2
    name: Morgen
    float_precision: 4
    type: line
    curve: stepline
    opacity: 0.5
    color: grey
    data_generator: |
      return (entity.attributes.tomorrow || []).map((item) => [item.t, item.price]);
```

## Supported providers

| Provider | API slug |
|----------|----------|
| ANWB Energie | `anwb-energie` |
| Atoom Alliantie | `atoom-alliantie` |
| Budget Energie | `budget-energie` |
| Coolblue Energie | `coolblue-energie` |
| easyEnergy | `easyenergy` |
| Eneco | `eneco` |
| Energie VanOns | `energie-vanons` |
| EnergyZero | `energyzero` |
| Engie | `engie` |
| Frank Energie | `frank-energie` |
| Frank Energie (Slim terugleveren) | `frank-energie-slim` |
| Hegg | `hegg` |
| Innova | `innova` |
| NextEnergy | `nextenergy` |
| SamSam | `samsam` |
| Tibber | `tibber` |
| VandeBron | `vandebron` |
| Zonneplan | `zonneplan` |

## Data source

Prices are fetched from [epexprijzen.nl](https://epexprijzen.nl), which publishes EPEX SPOT day-ahead prices including energy tax and provider surcharges. Tomorrow's prices are typically available around **13:00**. The integration polls the API every **30 minutes**.

## License

MIT
