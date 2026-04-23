#
# Copyright 2026 Marek Forkasiewicz
#

"""Live JSON writer for kiosk-style WeeWX dashboards."""

import datetime
import json
import logging
import os
import tempfile

import weewx
from weewx.engine import StdService
from weewx.units import to_METRICWX

log = logging.getLogger(__name__)

VERSION = "0.1.0"


def _to_float(value, digits=1):
    if value is None:
        return None
    return round(float(value), digits)


class WeatherCloudLive(StdService):
    """Write the latest loop packet to a small JSON file for live dashboards."""

    def __init__(self, engine, config_dict):
        super(WeatherCloudLive, self).__init__(engine, config_dict)

        self.live_config = config_dict.get("WeatherCloudLive", {})
        self.report_config = config_dict.get("StdReport", {}).get("WeatherCloudLive", {})
        self.output_path = self._resolve_output_path(config_dict)
        self.bind(weewx.NEW_LOOP_PACKET, self.new_loop_packet)

        log.info("weathercloudlive %s writing live data to %s", VERSION, self.output_path)

    def _resolve_output_path(self, config_dict):
        weewx_root = config_dict.get("WEEWX_ROOT", ".")
        html_root = self.report_config.get(
            "HTML_ROOT",
            self.live_config.get("html_root", "public_html/weathercloudlive"),
        )
        filename = self.live_config.get("live_json_filename", "live.json")
        return os.path.abspath(os.path.join(weewx_root, html_root, filename))

    def _build_payload(self, packet):
        packet_metricwx = to_METRICWX(dict(packet))

        wind_ms = packet_metricwx.get("windSpeed")
        payload = {
            "source_ip": packet.get("weathercloud_source_ip") or packet.get("source_ip"),
            "wid": packet.get("weathercloud_wid") or packet.get("wid"),
            "updated_at": None,
            "temperature_c": _to_float(packet_metricwx.get("outTemp"), 1),
            "humidity_pct": _to_float(packet_metricwx.get("outHumidity"), 0),
            "pressure_hpa": _to_float(
                packet_metricwx.get("barometer", packet_metricwx.get("pressure")), 1
            ),
            "wind_ms": _to_float(wind_ms, 1),
            "wind_kmh": _to_float(wind_ms * 3.6, 1) if wind_ms is not None else None,
            "wind_dir_deg": _to_float(packet_metricwx.get("windDir"), 0),
            "rain_mm": _to_float(packet_metricwx.get("rain"), 1),
            "rainrate_mm_h": _to_float(packet_metricwx.get("rainRate"), 1),
            "uv_index": _to_float(packet_metricwx.get("UV"), 1),
            "solar_wm2": _to_float(packet_metricwx.get("radiation"), 0),
            "dewpoint_c": _to_float(packet_metricwx.get("dewpoint"), 1),
            "heat_index_c": _to_float(packet_metricwx.get("heatindex"), 1),
        }

        timestamp = packet_metricwx.get("dateTime")
        if timestamp is not None:
            payload["updated_at"] = datetime.datetime.fromtimestamp(
                timestamp, tz=datetime.timezone.utc
            ).isoformat()

        return payload

    def _write_atomic_json(self, payload):
        directory = os.path.dirname(self.output_path)
        os.makedirs(directory, exist_ok=True)

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=directory,
            delete=False,
        ) as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            temp_path = handle.name

        os.replace(temp_path, self.output_path)

    def new_loop_packet(self, event):
        try:
            payload = self._build_payload(event.packet)
            self._write_atomic_json(payload)
        except Exception as exc:
            log.error("weathercloudlive failed to write live.json: %s", exc, exc_info=True)
