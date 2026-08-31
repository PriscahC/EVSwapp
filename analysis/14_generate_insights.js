// analysis/14_generate_insights.js
// Run: node analysis/14_generate_insights.js
// Prereq: viz/api server must be running (node server.js) on port 3001

const fs = require("fs");
const path = require("path");

const SITES_PATH = path.join(__dirname, "..", "data", "processed", "proposed_sites_phased.geojson");
const CACHE_PATH = path.join(__dirname, "..", "data", "processed", "site_insights.json");
const API_URL = "http://localhost:3001/api/insight";
const DELAY_MS = 1500; // space out calls, be polite to Groq's rate limit

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function main() {
  const geojson = JSON.parse(fs.readFileSync(SITES_PATH, "utf8"));
  const features = geojson.features;

  // Resume support: load any existing cache so a crash/interrupt doesn't cost you re-runs
  let cache = {};
  if (fs.existsSync(CACHE_PATH)) {
    cache = JSON.parse(fs.readFileSync(CACHE_PATH, "utf8"));
    console.log(`Loaded existing cache: ${Object.keys(cache).length} sites already done`);
  }

  // Sanity check property names against what server.js expects, using site 0
  const sampleProps = features[0].properties;
  console.log("Sample site properties:", Object.keys(sampleProps));

  for (let i = 0; i < features.length; i++) {
    const f = features[i];
    const p = f.properties;
    const siteId = p.site_name || p.id || `site_${i}`;

    if (cache[siteId]) {
      console.log(`[${i + 1}/${features.length}] ${siteId} — cached, skipping`);
      continue;
    }

    const payload = {
      site_name: p.site_name,
      population: p.population,
      peak_transit_vph: p.peak_transit_vph,
      existing_coverage: p.existing_coverage,
      need_score: p.need_score,
      growth_delta: p.growth_delta,
      pilot_phase: p.pilot_phase,
      recommended_infrastructure: p.recommended_infrastructure,
    };

    // Warn (don't crash) if any expected field is undefined — property names may differ
    const missing = Object.entries(payload).filter(([, v]) => v === undefined).map(([k]) => k);
    if (missing.length) {
      console.warn(`  ⚠ ${siteId}: missing fields ${missing.join(", ")} — check property names against sampleProps above`);
    }

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();

      if (!data.insight) {
        console.error(`[${i + 1}/${features.length}] ${siteId} — empty insight, will retry next run`);
        continue;
      }

      cache[siteId] = data.insight;
      fs.writeFileSync(CACHE_PATH, JSON.stringify(cache, null, 2)); // write after every success
      console.log(`[${i + 1}/${features.length}] ${siteId} — OK`);
    } catch (err) {
      console.error(`[${i + 1}/${features.length}] ${siteId} — request failed:`, err.message);
    }

    await sleep(DELAY_MS);
  }

  console.log(`\nDone. ${Object.keys(cache).length}/${features.length} sites cached at ${CACHE_PATH}`);
}

main();