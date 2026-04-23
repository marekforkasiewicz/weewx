# WeatherCloudLive

`weathercloudlive` to szkic rozszerzenia WeeWX do dwóch zadań:

- zapisywanie ostatniego pakietu loop jako `live.json`
- serwowanie lekkiego ekranu kiosku z dużym zegarem i danymi pogodowymi

To nie jest pełny driver Weathercloud. Rozszerzenie zakłada, że pakiet loop trafia już do WeeWX
inną drogą, na przykład przez własny bridge HTTP.

## Co zawiera

- `bin/user/weathercloudlive.py`
  - `StdService`, który nasłuchuje `NEW_LOOP_PACKET`
  - normalizuje dane do `METRICWX`
  - zapisuje atomowo `live.json`
- `skins/WeatherCloudLive`
  - prosty ekran kiosk
  - `live.css`
  - `live.js`

## Instalacja

Przykładowo:

```bash
cd ~/weewx-data/examples/weathercloudlive
weectl extension install .
```

Po instalacji w `weewx.conf` pojawią się:

```ini
[WeatherCloudLive]
    live_json_filename = live.json
    stale_after_seconds = 20

[StdReport]
    [[WeatherCloudLive]]
        skin = WeatherCloudLive
        enable = true
        HTML_ROOT = weathercloudlive
        lang = pl
        unit_system = METRICWX
```

## Gdzie trafiają pliki

Rozszerzenie zapisuje:

- `index.html`
- `live.css`
- `live.js`
- `live.json`

do katalogu raportu `StdReport/WeatherCloudLive/HTML_ROOT`.

## Dalszy kierunek

Ten scaffold jest przygotowany pod dalsze spięcie z naszym lokalnym bridge:

- przejęcie `api.weathercloud.net`
- mapowanie requestów HTTP do pakietu loop
- pełny dashboard pod ekran RPi3
