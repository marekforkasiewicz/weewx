function fmt(value, digits = 1, suffix = '') {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return '--' + suffix;
  }
  return Number(value).toFixed(digits) + suffix;
}

function tickClock() {
  const now = new Date();
  const timeNode = document.getElementById('clockTime');
  const dateNode = document.getElementById('clockDate');
  if (timeNode) {
    timeNode.textContent = now.toLocaleTimeString('pl-PL', {
      hour: '2-digit',
      minute: '2-digit'
    });
  }
  if (dateNode) {
    dateNode.textContent = now.toLocaleDateString('pl-PL', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }
}

function updateDom(data) {
  document.getElementById('temp').textContent = fmt(data.temperature_c, 1, '');
  document.getElementById('humidity').textContent = fmt(data.humidity_pct, 0, '%');
  document.getElementById('wind').textContent = fmt(data.wind_kmh, 1, ' km/h');
  document.getElementById('winddir').textContent = `kierunek ${fmt(data.wind_dir_deg, 0, '°')}`;
  document.getElementById('pressure').textContent = fmt(data.pressure_hpa, 1, ' hPa');
  document.getElementById('rain').textContent = fmt(data.rain_mm, 1, ' mm');
  document.getElementById('rainrate').textContent = `opad chwilowy ${fmt(data.rainrate_mm_h, 1, ' mm/h')}`;
  document.getElementById('solar').textContent = fmt(data.solar_wm2, 0, ' W/m²');
  document.getElementById('uv').textContent = `UV ${fmt(data.uv_index, 1, '')}`;
  document.getElementById('dew').textContent = fmt(data.dewpoint_c, 1, '°C');
  document.getElementById('srcip').textContent = data.source_ip || '--';
  document.getElementById('wid').textContent = data.wid || '--';

  const updatedAt = data.updated_at ? new Date(data.updated_at) : null;
  const now = new Date();
  const ageSeconds = updatedAt ? Math.round((now - updatedAt) / 1000) : Number.POSITIVE_INFINITY;
  document.getElementById('status').textContent = updatedAt
    ? `Ostatni pakiet sprzed ${ageSeconds} s`
    : 'Brak bieżących danych';
  document.getElementById('updated').textContent = updatedAt
    ? `Aktualizacja: ${updatedAt.toLocaleString('pl-PL')}`
    : 'Aktualizacja: brak';
}

async function refresh() {
  try {
    const response = await fetch('live.json?_=' + Date.now(), { cache: 'no-store' });
    if (!response.ok) {
      throw new Error('Brak live.json');
    }
    const data = await response.json();
    updateDom(data);
  } catch (error) {
    document.getElementById('status').textContent = 'Dashboard czeka na pakiet ze stacji';
  }
}

tickClock();
setInterval(tickClock, 1000);
refresh();
setInterval(refresh, 5000);
