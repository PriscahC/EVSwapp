import 'ol/ol.css';
import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import OSM from 'ol/source/OSM';
import GeoJSON from 'ol/format/GeoJSON';
import { Style, Fill, Stroke, Circle as CircleStyle } from 'ol/style';
import { fromLonLat } from 'ol/proj';
import Chart from 'chart.js/auto';

const map = new Map({
  target: 'map',
  layers: [new TileLayer({ source: new OSM() })],
  view: new View({ center: fromLonLat([36.82, -1.29]), zoom: 11 }),
});

// ---- colour helpers ----
function needColor(score) {
  // low->high: pale yellow to deep red
  const t = Math.max(0, Math.min(1, score));
  const r = 255, g = Math.round(230 - t * 180), b = Math.round(180 - t * 180);
  return `rgba(${r},${g},${b},0.65)`;
}
const phaseColor = {
  'Phase 1: needed now': '#e63946',
  'Phase 2: emerging need': '#f4a261',
  'Phase 3: monitor': '#2a9d8f',
};
const infraColor = { 3: '#1d3557', 2: '#457b9d', 1: '#a8dadc' }; // priority_weight 3/2/1

// ---- layer builders ----
function geojsonLayer(url, styleFn) {
  return new VectorLayer({
    source: new VectorSource({
      url,
      format: new GeoJSON(),
    }),
    style: styleFn,
  });
}

const infraLayer = geojsonLayer('/data/existing_infra.geojson', (f) => new Style({
  image: new CircleStyle({
    radius: 5,
    fill: new Fill({ color: infraColor[f.get('priority_weight')] || '#999' }),
    stroke: new Stroke({ color: '#fff', width: 1 }),
  }),
}));

const needLayer = geojsonLayer('/data/nairobi_h3_grid_with_growth.geojson', (f) => new Style({
  fill: new Fill({ color: needColor(f.get('need_score') || 0) }),
  stroke: new Stroke({ color: 'rgba(0,0,0,0.15)', width: 0.5 }),
}));

const sitesLayer = geojsonLayer('/data/proposed_sites_with_insights.geojson', (f) => new Style({
  image: new CircleStyle({
    radius: 8,
    fill: new Fill({ color: phaseColor[f.get('pilot_phase')] || '#333' }),
    stroke: new Stroke({ color: '#fff', width: 2 }),
  }),
}));

let currentBand = 'vph_am_peak';
function transitStyle(f) {
  const v = f.get(currentBand) || 0;
  return new Style({
    image: new CircleStyle({
      radius: Math.min(12, 3 + v / 4),
      fill: new Fill({ color: 'rgba(106,90,205,0.55)' }),
      stroke: new Stroke({ color: '#fff', width: 1 }),
    }),
  });
}
const transitLayer = geojsonLayer('/data/nairobi_stop_frequency.geojson', transitStyle);
transitLayer.setVisible(false);

map.addLayer(needLayer);
map.addLayer(infraLayer);
map.addLayer(transitLayer);
map.addLayer(sitesLayer); // sites on top

// ---- toggles ----
document.getElementById('toggle-infra').addEventListener('change', e => infraLayer.setVisible(e.target.checked));
document.getElementById('toggle-need').addEventListener('change', e => needLayer.setVisible(e.target.checked));
document.getElementById('toggle-sites').addEventListener('change', e => sitesLayer.setVisible(e.target.checked));
document.getElementById('toggle-transit').addEventListener('change', e => {
  transitLayer.setVisible(e.target.checked);
  document.getElementById('transit-band').style.display = e.target.checked ? 'block' : 'none';
});
document.getElementById('transit-select').addEventListener('change', e => {
  currentBand = e.target.value;
  transitLayer.setStyle(transitStyle);
});

// ---- click -> AI insight panel ----
const infoPanel = document.getElementById('info-panel');
map.on('click', (evt) => {
  let shown = false;
  map.forEachFeatureAtPixel(evt.pixel, (feature, layer) => {
    if (layer === sitesLayer && !shown) {
      shown = true;
      const p = feature.getProperties();
      infoPanel.innerHTML = `
        <strong>${p.site_name || 'Proposed site'}</strong><br/>
        <em>${p.recommended_infrastructure || ''}</em> · ${p.pilot_phase || ''}<br/><br/>
        ${p.ai_insight || '<span class="hint">No insight cached for this site.</span>'}
        <div class="stat-row" style="margin-top:8px;opacity:0.75;font-size:11px;">
          need score: ${p.need_score?.toFixed(3) ?? '—'} · pop: ${p.population != null ? Number(p.population).toLocaleString() : '—'}
        </div>
      `;
    }
  });
});

// ---- phase distribution chart ----
fetch('/data/proposed_sites_with_insights.geojson')
  .then(r => r.json())
  .then(geo => {
    const counts = {};
    geo.features.forEach(f => {
      const ph = f.properties.pilot_phase || 'Unphased';
      counts[ph] = (counts[ph] || 0) + 1;
    });
    new Chart(document.getElementById('phase-chart'), {
      type: 'bar',
      data: {
        labels: Object.keys(counts),
        datasets: [{ label: 'Proposed sites', data: Object.values(counts),
          backgroundColor: Object.keys(counts).map(k => phaseColor[k] || '#999') }],
      },
      options: {
        plugins: { legend: { display: false } },
        scales: { x: { ticks: { color: '#ccc' } }, y: { ticks: { color: '#ccc' } } },
      },
    });
  });