# installer for weathercloudlive
# Copyright 2026 Marek Forkasiewicz

from io import StringIO

import configobj

from weecfg.extension import ExtensionInstaller


def loader():
    return WeatherCloudLiveInstaller()


WEATHERCLOUDLIVE_CONFIG = """
[WeatherCloudLive]
    live_json_filename = live.json
    stale_after_seconds = 20

[StdReport]

    [[WeatherCloudLive]]
        skin = WeatherCloudLive
        enable = True
        HTML_ROOT = weathercloudlive
        lang = pl
        unit_system = METRICWX
"""

weathercloudlive_dict = configobj.ConfigObj(StringIO(WEATHERCLOUDLIVE_CONFIG))


class WeatherCloudLiveInstaller(ExtensionInstaller):
    def __init__(self):
        super(WeatherCloudLiveInstaller, self).__init__(
            version="0.1.0",
            name="weathercloudlive",
            description="Live kiosk dashboard and JSON writer for Weathercloud-style live packets.",
            author="Marek Forkasiewicz",
            author_email="marek@efork.pl",
            process_services="user.weathercloudlive.WeatherCloudLive",
            config=weathercloudlive_dict,
            files=[
                ("bin/user", [
                    "bin/user/weathercloudlive.py",
                ]),
                ("skins/WeatherCloudLive", [
                    "skins/WeatherCloudLive/index.html.tmpl",
                    "skins/WeatherCloudLive/app.css",
                    "skins/WeatherCloudLive/app.js",
                    "skins/WeatherCloudLive/skin.conf",
                    "skins/WeatherCloudLive/lang/pl.conf",
                ]),
            ],
        )
