<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

const weather = ref(null)
const error = ref('')
const now = ref(new Date())

let clockTimer = null
let refreshTimer = null

function fmt(value, digits = 1, suffix = '') {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return '--' + suffix
  }
  return `${Number(value).toFixed(digits)}${suffix}`
}

async function fetchLive() {
  try {
    const response = await fetch(`live.json?_=${Date.now()}`, {
      cache: 'no-store'
    })
    if (!response.ok) {
      throw new Error('Brak odpowiedzi live.json')
    }

    weather.value = await response.json()
    error.value = ''
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Błąd pobierania danych'
  }
}

const updatedAt = computed(() => {
  if (!weather.value?.updated_at) return null
  return new Date(weather.value.updated_at)
})

const ageSeconds = computed(() => {
  if (!updatedAt.value) return Infinity
  return Math.round((now.value.getTime() - updatedAt.value.getTime()) / 1000)
})

const isStale = computed(() => ageSeconds.value > 20)

const statusText = computed(() => {
  if (error.value) return 'Brak danych live'
  if (!weather.value) return 'Oczekiwanie na pierwszy pakiet'
  if (isStale.value) return `Brak świeżego pakietu od ${ageSeconds.value} s`
  return `Połączenie aktywne z ${weather.value.source_ip || 'nadajnikiem'}`
})

const updatedText = computed(() => {
  if (!updatedAt.value) return 'Brak znacznika czasu'
  return `Ostatni pakiet: ${updatedAt.value.toLocaleString('pl-PL')}`
})

const footerText = computed(() => {
  if (!updatedAt.value) return 'Dashboard czeka na pakiet ze stacji'
  return `Pakiet sprzed ${ageSeconds.value} s`
})

const clockTime = computed(() =>
  now.value.toLocaleTimeString('pl-PL', {
    hour: '2-digit',
    minute: '2-digit'
  })
)

const clockDate = computed(() =>
  now.value.toLocaleDateString('pl-PL', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
)

const tiles = computed(() => [
  {
    label: 'Wilgotność',
    value: fmt(weather.value?.humidity_pct, 0, '%'),
    sub: 'warunki otoczenia'
  },
  {
    label: 'Punkt rosy',
    value: fmt(weather.value?.dewpoint_c, 1, '°C'),
    sub: 'temperatura kondensacji'
  },
  {
    label: 'Ciśnienie',
    value: fmt(weather.value?.pressure_hpa, 1, ' hPa'),
    sub: 'barometr stacji'
  },
  {
    label: 'Odczuwalna',
    value: fmt(weather.value?.heat_index_c, 1, '°C'),
    sub: 'heat index'
  }
])

const sideCards = computed(() => [
  {
    label: 'Wiatr',
    value: fmt(weather.value?.wind_kmh, 1, ' km/h'),
    sub: `kierunek ${fmt(weather.value?.wind_dir_deg, 0, '°')}`
  },
  {
    label: 'Deszcz dzisiaj',
    value: fmt(weather.value?.rain_mm, 1, ' mm'),
    sub: `opad chwilowy ${fmt(weather.value?.rainrate_mm_h, 1, ' mm/h')}`
  },
  {
    label: 'Nasłonecznienie',
    value: fmt(weather.value?.solar_wm2, 0, ' W/m²'),
    sub: `UV ${fmt(weather.value?.uv_index, 1, '')}`
  }
])

const stats = computed(() => [
  {
    label: 'Źródło danych',
    value: weather.value?.source_ip || '--',
    sub: 'adres IP nadajnika'
  },
  {
    label: 'ID stacji',
    value: weather.value?.wid || '--',
    sub: 'identyfikator Weathercloud'
  },
  {
    label: 'Ostatni pakiet',
    value: updatedAt.value ? updatedAt.value.toLocaleTimeString('pl-PL') : '--:--:--',
    sub: 'czas lokalny'
  },
  {
    label: 'Odświeżanie',
    value: '5 s',
    sub: 'frontend Vue 3'
  }
])

onMounted(() => {
  fetchLive()
  clockTimer = window.setInterval(() => {
    now.value = new Date()
  }, 1000)
  refreshTimer = window.setInterval(fetchLive, 5000)
})

onBeforeUnmount(() => {
  if (clockTimer) window.clearInterval(clockTimer)
  if (refreshTimer) window.clearInterval(refreshTimer)
})
</script>

<template>
  <div class="shell">
    <div class="topbar">
      <div class="brand">
        <h1>VEVOR Live</h1>
        <p>{{ updatedText }}</p>
      </div>

      <div class="top-actions">
        <div class="clock-box">
          <div class="time">{{ clockTime }}</div>
          <div class="date">{{ clockDate }}</div>
        </div>

        <div :class="['status', { stale: isStale || !!error }]">
          <span class="status-dot"></span>
          <span>{{ statusText }}</span>
        </div>

        <div class="links">
          <a href="../index.html">Raport WeeWX</a>
          <a href="../telemetry.html">Telemetry</a>
        </div>
      </div>
    </div>

    <div class="hero">
      <div class="panel hero-main">
        <div class="now-block">
          <div>
            <div class="eyebrow">Aktualna pogoda</div>
            <div class="temperature-row">
              <div class="value">{{ fmt(weather?.temperature_c, 1, '') }}</div>
              <div class="unit">°C</div>
            </div>
          </div>

          <div class="conditions">
            <div v-for="tile in tiles" :key="tile.label" class="mini">
              <div class="label">{{ tile.label }}</div>
              <div class="val">{{ tile.value }}</div>
              <div class="sub">{{ tile.sub }}</div>
            </div>
          </div>
        </div>

        <div class="hero-side">
          <div v-for="card in sideCards" :key="card.label" class="card">
            <div class="label">{{ card.label }}</div>
            <div class="val">{{ card.value }}</div>
            <div class="sub">{{ card.sub }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="stats">
      <div v-for="stat in stats" :key="stat.label" class="panel stat-card">
        <div class="label">{{ stat.label }}</div>
        <div class="val">{{ stat.value }}</div>
        <div class="sub">{{ stat.sub }}</div>
      </div>
    </div>

    <div class="footer">
      <div><strong>RPi3 kiosk:</strong> Vue 3, duży zegar i dane pogodowe na jednym ekranie.</div>
      <div>{{ footerText }}</div>
    </div>
  </div>
</template>

<style>
:root {
  --bg-top: #edf4ee;
  --bg-bottom: #d8e7dd;
  --panel: rgba(255, 255, 255, 0.88);
  --panel-strong: rgba(255, 255, 255, 0.96);
  --line: rgba(22, 58, 42, 0.08);
  --text: #16362b;
  --muted: #5f7a6f;
  --accent: #22744e;
  --accent-soft: #dff2e6;
  --warn: #b6721b;
  --shadow: 0 18px 60px rgba(32, 60, 46, 0.12);
}

* {
  box-sizing: border-box;
}

html, body, #app {
  margin: 0;
  min-height: 100%;
  font-family: 'Trebuchet MS', 'Segoe UI', sans-serif;
  color: var(--text);
  background:
    radial-gradient(circle at top right, rgba(255, 222, 153, 0.35), transparent 26%),
    radial-gradient(circle at top left, rgba(112, 180, 143, 0.22), transparent 24%),
    linear-gradient(180deg, var(--bg-top) 0%, var(--bg-bottom) 100%);
}

body {
  overflow-x: hidden;
}

.shell {
  min-height: 100vh;
  padding: 24px;
  display: grid;
  grid-template-rows: auto auto 1fr;
  gap: 18px;
}

.topbar {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: flex-start;
}

.brand h1 {
  margin: 0;
  font-size: 38px;
  line-height: 0.95;
  letter-spacing: -0.04em;
  font-weight: 800;
}

.brand p {
  margin: 10px 0 0;
  color: var(--muted);
  font-size: 15px;
}

.top-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
}

.clock-box {
  min-width: 270px;
  padding: 18px 22px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid var(--line);
  box-shadow: var(--shadow);
  text-align: right;
}

.clock-box .time {
  font-size: 64px;
  line-height: 0.88;
  letter-spacing: -0.06em;
  font-weight: 800;
}

.clock-box .date {
  margin-top: 10px;
  font-size: 17px;
  color: var(--muted);
  font-weight: 700;
}

.status {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--accent);
  font-weight: 700;
  font-size: 14px;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 0 0 6px rgba(34, 116, 78, 0.15);
}

.status.stale {
  background: #fff0d9;
  color: var(--warn);
}

.status.stale .status-dot {
  background: var(--warn);
  box-shadow: 0 0 0 6px rgba(182, 114, 27, 0.12);
}

.links {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.links a {
  text-decoration: none;
  color: var(--accent);
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 10px 14px;
  font-size: 14px;
  font-weight: 700;
  box-shadow: var(--shadow);
}

.hero {
  display: grid;
  grid-template-columns: 1.25fr 1fr;
  gap: 18px;
}

.panel {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 28px;
  box-shadow: var(--shadow);
  backdrop-filter: blur(10px);
}

.hero-main {
  padding: 28px;
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 18px;
  align-items: stretch;
}

.now-block {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 16px;
}

.eyebrow {
  color: var(--muted);
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-weight: 700;
}

.temperature-row {
  display: flex;
  align-items: flex-end;
  gap: 14px;
  margin-top: 4px;
}

.temperature-row .value {
  font-size: 118px;
  line-height: 0.85;
  letter-spacing: -0.07em;
  font-weight: 800;
}

.temperature-row .unit {
  font-size: 38px;
  line-height: 1.2;
  color: var(--muted);
  font-weight: 700;
  margin-bottom: 16px;
}

.conditions {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.mini {
  background: var(--panel-strong);
  border: 1px solid var(--line);
  border-radius: 20px;
  padding: 16px;
}

.mini .label,
.card .label,
.stat-card .label {
  color: var(--muted);
  font-size: 13px;
  margin-bottom: 10px;
  font-weight: 700;
}

.mini .val {
  font-size: 31px;
  line-height: 1;
  font-weight: 800;
  letter-spacing: -0.04em;
}

.mini .sub,
.card .sub,
.stat-card .sub {
  margin-top: 8px;
  color: var(--muted);
  font-size: 14px;
}

.hero-side {
  display: grid;
  gap: 14px;
}

.hero-side .card {
  background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(247, 252, 249, 0.96));
  border: 1px solid var(--line);
  border-radius: 22px;
  padding: 18px;
}

.hero-side .card .val {
  font-size: 36px;
  line-height: 1;
  font-weight: 800;
  letter-spacing: -0.04em;
}

.stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
}

.stat-card {
  padding: 18px 20px;
}

.stat-card .val {
  font-size: 40px;
  line-height: 1;
  letter-spacing: -0.05em;
  font-weight: 800;
}

.footer {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  color: var(--muted);
  font-size: 14px;
}

.footer strong {
  color: var(--text);
}

@media (max-width: 1100px) {
  .hero,
  .hero-main,
  .stats {
    grid-template-columns: 1fr;
  }

  .temperature-row .value {
    font-size: 84px;
  }
}

@media (max-width: 700px) {
  .shell {
    padding: 14px;
  }

  .topbar,
  .footer {
    flex-direction: column;
    align-items: stretch;
  }

  .top-actions,
  .links {
    align-items: flex-start;
    justify-content: flex-start;
  }

  .conditions {
    grid-template-columns: 1fr;
  }
}
</style>
