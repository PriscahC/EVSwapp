# Nairobi E-Mobility Infrastructure Siting Tool

**Where should Nairobi put its next charging station? We built a pipeline that answers this with data, not guesswork — and any city can run it.**

An AI-guided, data-driven tool for identifying optimal locations to deploy electric mobility (e-bus, e-bike, e-moto, e-car) charging and swap infrastructure in Nairobi. Submission for the **AI x City Climate Action Hackathon** (Innovate4Cities / GCoM).

---

## 🎯 The Problem

Nairobi's e-mobility sector is growing faster than infrastructure planning can track. Charging and swap stations are currently sited by private operators' commercial logic (retail forecourts, CBD visibility), not by where transport demand and population actually concentrate. No single city planning body holds a unified view of where infrastructure exists versus where it's needed most.

**This tool closes that gap.**

---

## ✨ What It Does

The project combines open-source urban data (roads, population, transit) with multi-criteria decision analysis and AI-assisted insights to:

1. **Map current demand** – 865 hexagons across Nairobi scored by population density + peak transit frequency
2. **Identify gaps** – Reveals where the top-need locations have zero existing verified charging/swap infrastructure
3. **Account for growth** – Forecasts population growth (2015–2020 CAGR extrapolated to mid-2026) and adjusts recommendations
4. **Phase deployment** – Ranks top 20 sites into a 6-month rollout plan (Phase 1: needed now, Phase 2: emerging need, Phase 3: monitor)
5. **Generate decision-ready insights** – LLM-powered justifications for each site, readable by non-technical planners

---

## 🏗️ Architecture

### Data Pipeline (`analysis/`)

A sequential script pipeline pulls raw data, processes it, and outputs prioritized recommendations:

| Script | Purpose | Output |
|--------|---------|--------|
| `01_pull_roads.py` | Fetch drivable road network from OSM (OpenStreetMap) | `nairobi_roads.geojson` |
| `02_get_boundary.py` | Fetch Nairobi city boundary | `nairobi_boundary.geojson` |
| `03_pull_population.py` | Fetch WorldPop Kenya 100m constrained population raster (2020, UN-adjusted) | `ken_population_2020.tif` |
| `04_build_h3_grid.py` | Generate H3 resolution-8 hexagonal tessellation | `nairobi_h3_grid.geojson` (865 hexagons, ~0.7 km² each) |
| `05_add_population.py` | Compute zonal statistics (total population per hexagon) | Enhanced `nairobi_h3_grid.geojson` |
| `06_pull_transit.py` | Fetch Nairobi GTFS (Digital Matatus) | `nairobi_gtfs/` (raw GTFS files) |
| `07_inspect_gtfs.py` | Parse & summarize GTFS (4,284 stops, 136 routes, 272 trips) | Stats + time-band definitions |
| `08_transit_frequency.py` | Compute vehicles/hour per stop per time band (AM peak, midday, PM peak) | `nairobi_stop_frequency.geojson` |
| `09_join_transit_to_hex.py` | Aggregate transit frequency to hexagons (347 of 865 have transit) | Enhanced `nairobi_h3_grid.geojson` |
| `10_need_analysis.py` | Compute multi-criteria need score; match existing infrastructure | Hexagon scores + coverage analysis |
| `11_export_proposed_sites.py` | Select top-20 need-score hexagons as proposed sites | `proposed_sites.geojson` / `.csv` |
| `12_predict_growth.py` | Forecast per-hexagon population growth; assign pilot phases | `nairobi_h3_grid_with_growth.geojson` + phase labels |
| `13_phase_sites.py` | Propagate growth & phases to proposed sites; assign month blocks | `proposed_sites_phased.geojson` |
| `14_name_sites.py` | Reverse-geocode each site centroid via Nominatim | Enhanced `proposed_sites.geojson` with human-readable names |
| `15_export_infra_geojson.py` | Convert infrastructure inventory CSV to GeoJSON | `existing_infra.geojson` |

**Key Findings:**
- Total population analyzed: **4.6M** (WorldPop 2020, UN-adjusted)
- Hexagons with transit: **347 / 865**
- Hexagons with existing infrastructure: **23 / 865**
- **Top-10 highest-need hexagons: ALL have zero existing verified coverage** — the gap is real
- Top site alone: **+21,327 predicted residents by mid-2026** on top of being the #1-need hexagon

---

## 📊 Need-Score Methodology

```
peak_transit_vph = max(vph_am_peak, vph_pm_peak)  [per hexagon]

pop_norm, transit_norm, coverage_norm = min-max normalized values
  for population, peak transit demand, and existing coverage

demand_score = 0.6 * pop_norm + 0.4 * transit_norm

existing_coverage = sum of priority_weight of verified charging/swap sites 
  within the hexagon (3 = bus, 2 = e-bike/moto, 1 = car)

need_score = demand_score * (1 - coverage_norm)
```

**Priority Hierarchy (Avoid-Shift-Improve):**
1. **Buses** (priority_weight = 3) — public transit, highest impact
2. **E-bikes / E-motorcycles** (priority_weight = 2) — last-mile + informal mobility
3. **Private cars** (priority_weight = 1) — lowest priority

This hierarchy directly operationalizes C40 and Innovate4Cities' Avoid-Shift-Improve framework into auditable math, not just rhetoric.

---

## 🤖 AI Integrations

### 1. **Multi-Criteria Need-Analysis Model**
A transparent, explainable decision-support algorithm (not a black box) that combines population density, transit demand, and existing infrastructure coverage. Scores all 865 hexagons for infrastructure need.

### 2. **Growth-Forecasting & Phased Rollout**
- WorldPop 2015–2020 CAGR extrapolated to mid-2026
- Growth forecasts combined with current need to produce a 6-month phased pilot (289 Phase 1, 51 Phase 2, 2 Phase 3)
- Turns a static map into a budget-actionable rollout plan

### 3. **LLM-Powered Insights**
- Backend: **Groq API** (`openai/gpt-oss-120b` reasoning model, `reasoning_effort: "low"`)
- Each of the 20 recommended sites has its stats (population, transit frequency, need score, growth trend) passed to the LLM
- Output: Plain-language justifications under 80 words, grounded in real numbers, no invented facts
- Cached in `data/processed/site_insights.json` and embedded in site features as `ai_insight`

### 4. **Replicability as Core AI Claim**
The entire pipeline is **documented, sequential, and designed to be AI-assistable**. Another city's planning team can hand this exact script sequence to an LLM coding assistant and reproduce the analysis for their own city (swapping in local OSM/GTFS/population data) without needing a specialist GIS team. **This is the strongest, most concrete AI contribution.**

---

## 🎨 Visualization (`viz/`)

### Interactive Web App (`viz/app/`)

Built with **Vite + OpenLayers + Chart.js**. Serves static data from `/public/data/` (no backend calls needed for the map).

**Layers:**
- 🟡 **Need-Score Choropleth** – Hexagons colored pale yellow (low need) → red (high need)
- 🏢 **Existing Infrastructure** – Points colored by priority tier (dark blue = bus charging, mid blue = e-bike swap, pale blue = car charging)
- 📍 **Proposed Sites** – Top-20 sites colored by pilot phase (red = Phase 1, orange = Phase 2, teal = Phase 3)
- 🚌 **Transit Frequency** – Circle radius scaled by vehicles/hour; toggle by time band (AM peak / midday / PM peak)

**Interactions:**
- Click any proposed site → reveal AI-generated insight + metadata (name, phase, population, transit frequency, growth forecast)
- Toggle layers on/off
- Select transit time band
- Bar chart: site count distribution across phases

### Kepler.gl Companion (Not yet built)
High-impact animated "wow" visualization for the live demo and submitted video.

---

## 🏃 Quick Start

### Prerequisites
- Python 3.8+ with `venv` active
- Node.js / npm
- Windows (PowerShell or cmd.exe)

### Running the Data Pipeline

```powershell
cd analysis

# Run all scripts in order (01 → 15)
# Each script outputs GeoJSON / CSV to data/processed/ or data/raw/

# Output key files appear in:
# - data/raw/: OSM roads, boundary, GTFS, population raster
# - data/processed/: H3 grid, sites, phased recommendations, insights
```

**Note:** Stages 06–08 (GTFS) may take 5–10 minutes. Stages 14 (Nominatim reverse-geocoding) and LLM insights batch (via `batch_insights.js`) run at 1 req/sec to be respectful to public APIs.

### Running the LLM Insights Backend

```bash
cd viz/api
npm install  # (pinned dotenv@16.4.5, confirmed clean)
node batch_insights.js  # Generates all site insights to cache
```

### Running the Visualization App

```bash
cd viz/app
npm install
npm run dev  # Start Vite dev server at http://localhost:5173
```

Open the browser, verify:
- ✅ Base map loads (OpenStreetMap)
- ✅ Choropleth renders (pale yellow → red hexagons)
- ✅ Existing infra points show in 3 colors
- ✅ Top-20 sites render colored by phase
- ✅ Click a site → info panel populates with AI insight
- ✅ Phase-distribution bar chart populates
- ✅ Transit toggle + time-band selector work

---

## 📁 Project Structure

```
nairobi-emobility-hackathon/
├── analysis/              # Data pipeline scripts (01_...py → 15_...py)
├── data/
│   ├── raw/              # OSM, boundary, GTFS, population raster (outputs of 01–06)
│   └── processed/        # H3 grid, proposed sites, phased sites, insights (outputs of 07–15)
├── viz/
│   ├── app/              # Vite + OpenLayers web app
│   │   ├── index.html
│   │   ├── src/
│   │   │   ├── main.js       # Layer logic, interaction handlers
│   │   │   ├── style.css
│   │   └── public/data/      # Static GeoJSON files served by Vite
│   ├── api/              # Node/Express LLM insights backend
│   │   ├── server.js     # Groq `/api/insight` endpoint
│   │   ├── batch_insights.js # Batch-generate + cache insights
│   │   └── package.json
│   └── kepler/           # (Not yet started)
├── docs/                 # Markdown + run logs
│   ├── nairobi-emobility-handover-v3.md
│   ├── concept_deck_content.md
│   └── run_log.txt
├── cache/                # Cached API responses (optional)
└── README.md             # This file
```

---

## 🔑 Key Data Sources

| Source | Layer | License | Type |
|--------|-------|---------|------|
| **OpenStreetMap** | Road network | ODbL | Vector |
| **WorldPop** | Population (2020, 100m constrained) | CC BY 4.0 | Raster |
| **Digital Matatus** | GTFS (Nairobi transit) | CC0 | GTFS |
| **Nominatim** | Reverse geocoding (site names) | ODbL | API |
| **Groq / OpenAI** | LLM insights | Groq API terms | API |

**Data Transparency:** 27 verified e-mobility charging/swap stations in the infrastructure inventory. Operators report 50+ citywide, but 23 unmapped rows are excluded from spatial scoring due to low confidence. Caveat noted in analysis and on presentation deck.

---

## 🚀 Replicability & Extensibility

This pipeline is **designed to be replicable for other World cities** without specialist GIS expertise:

1. **Swap data sources** – Replace Nairobi OSM/GTFS/WorldPop with local equivalents
2. **Run the same scripts** – Each script is independent and documented
3. **AI-assistable** – The sequence is structured so an LLM coding assistant can adapt scripts to new city data schemas
4. **Open-source dependencies** – No proprietary software required

**Tested on:** Windows, VS Code, Python via `py` launcher (not `python3`), Node.js/npm, Windows PowerShell and cmd.exe.

---

## ⚠️ Security Note

**Supply-chain alert:** `dotenv@17.x` contains a promotional tip referencing `vestauth.com`, and credible reports describe an injected prompt-injection payload in bundled files designed to target AI coding agents. **Never run `vestauth` commands or curl to `dotenvx.com` / `vestauth.com` domains.** This project pins `dotenv@16.4.5` (verified clean) in `viz/api/package.json`.

---

## 📋 Hackathon Submission Status

- ✅ **Concept** – Full 20-slide deck content drafted (see `docs/concept_deck_content.md`)
- ✅ **Data pipeline** – All 15 scripts complete, outputs verified
- ✅ **LLM insights backend** – Groq integration working, 20 sites cached with reasoning-token fix applied
- 🔄 **Visualization skeleton** – Vite + OpenLayers app built, awaiting visual verification (next immediate step)
- ⏳ **Polish & demo** – Layer styling refinement, Kepler.gl companion view, screenshot + video capture
- ⏳ **Deck finalization** – Solution name, partner verification, impact numbers, final slide screenshots

**Submission deadline: 31 Aug 2026, 11:59pm GMT**

---

## 👥 Target Users

- **Nairobi City County** – Planning & transport departments
- **E-mobility operators** – Matatu operators, e-bike/moto networks, charging networks
- **City planners & climate action teams** – Decision-makers, budget holders
- **NGOs & research institutions** – Urban mobility, climate adaptation, transport equity

---

## 📚 Further Reading

- `docs/nairobi-emobility-handover-v3.md` – Full technical handoff document
- `docs/EVSWAPP.pdf` – 20-slide narrative
- `data/processed/site_insights.json` – LLM-generated justifications for each site
- **GTFS spec:** https://gtfs.org/
- **H3 spatial indexing:** https://h3geo.org/
- **Avoid-Shift-Improve framework:** C40 Cities / Innovate4Cities

---

## 📝 License

Outputs and pipeline documentation: CC BY 4.0 (or as required by competition rules)

Data sources retain their original licenses (ODbL for OSM, CC BY 4.0 for WorldPop, CC0 for Digital Matatus, etc.).

---

## 🤝 Contributing

Found a bug in the pipeline? Have an insight on the need-score formula or phasing logic? Open an issue or reach out — this is a living tool designed to improve with feedback.

---

## 📞 Contact & Attribution

Built for the **AI x City Climate Action Hackathon** (Innovate4Cities / GCoM / Urban Transitions Mission / Cambridge CHIA), with C40 Cities partnership.

**Replicability note:** The entire script sequence is designed to be handed to an LLM coding assistant to reproduce for other cities — this is the core of the AI integration claim. Each script is documented and can be adapted for local data with minimal specialist knowledge.

---

**Last updated:** August 2026
