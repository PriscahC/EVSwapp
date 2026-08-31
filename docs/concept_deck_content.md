# Nairobi E-Mobility Need-Analysis — 20-Slide Concept Deck Content
*Draft copy for each slide: headline, key content, and speaker notes. Visuals/layout come later — this is the argument, in your own numbers.*

---

## 1. Title
**Headline:** [Working name — e.g. "GridShift" / "AsiliMove" / TBD] — AI-Guided E-Mobility Siting for African Cities
**Content:** One-line pitch: "Where should Nairobi put its next charging station? We built a pipeline that answers this with data, not guesswork — and any city can run it."
**Speaker note:** Set the tone immediately: this is a working tool with real Nairobi output, not a concept sketch.

## 2. The Problem
**Content:**
- Nairobi's e-mobility sector (matatus, e-bikes, boda-bodas) is growing faster than infrastructure planning can track
- Charging/swap stations are being sited by private operators' commercial logic (retail forecourts, CBD visibility), not by where transport demand and population actually concentrate
- Result: a citywide infrastructure map that no single city planning body currently holds
**Speaker note:** This is the gap your pipeline fills — not "no infrastructure exists," but "no one has unified view of where it exists vs. where it's needed."

## 3. Context — Why Nairobi
**Content:**
- ~4.6M residents (WorldPop 2020, verified in this project), highly informal transit system
- Matatu network: 136 routes, 4,284 stops, no fixed timetable — headway-based frequency
- Nairobi is a representative "high-informality, high-growth" African city — the hard case, on purpose
**Speaker note:** Framing Nairobi as the hard test case supports your replicability claim later — if it works here, it generalizes.

## 4. Framework Alignment — Avoid-Shift-Improve
**Content:**
- Solution explicitly prioritizes: 1) Public buses, 2) E-bikes/motorcycles, 3) Private car charging (lowest priority)
- Every infrastructure site in the analysis is weighted by this hierarchy (priority_weight: 3/2/1)
- Directly operationalizes C40 and I4C's Avoid-Shift-Improve guidance into a scoring formula, not just a slide statement
**Speaker note:** This slide is what makes the C40/I4C alignment substantive rather than decorative — you're not citing ASI, you're computing with it.

## 5. Solution Overview
**Content:** One end-to-end diagram: Raw city data → H3 tessellation → AI-assisted need scoring → Growth-adjusted phasing → Ranked, siteable recommendations → Interactive decision-support app
**Speaker note:** This is the "one slide that explains everything" — build the diagram after the visualization exists, so it's a real screenshot-derived graphic, not an abstract box diagram.

## 6. Methodology Pipeline
**Content:**
- Roads: OpenStreetMap
- Population: WorldPop 100m constrained gridded population
- Transit: Digital Matatus GTFS (136 routes, 3 time-bands: AM peak/midday/PM peak)
- Tessellation: H3 resolution-8 (865 hexagons, ~0.7km² each)
- Existing infrastructure: 29-site verified dataset (operator, type, coordinates, source)
**Speaker note:** Every layer here is open data — reinforces feasibility and replicability without needing proprietary feeds.

## 7. AI Integration 1 — Multi-Criteria Need-Analysis Model
**Content:**
- Composite scoring model: 60% population density + 40% peak transit demand, discounted by existing priority-weighted infrastructure coverage
- Formula shown on-slide (demand_score, need_score) — real, auditable math, not a black box
- Output: every one of Nairobi's 865 hexagons ranked by e-mobility infrastructure need
**Speaker note:** Be precise in language here: this is a transparent, explainable multi-criteria decision model — a form of applied AI/decision-support, not deep learning, and that's a feature (auditable by city officials) not a limitation.

## 8. AI Integration 2 — Growth-Forecasting & Phased Recommendations
**Content:**
- Per-hexagon population growth forecast (WorldPop 2015→2020 CAGR, extrapolated to pilot window)
- Combines *current* need with *predicted* growth to produce a 3-phase, 6-month pilot rollout (Phase 1: needed now / Phase 2: compounding demand / Phase 3: get ahead of growth)
- Real output: 289 hexagons flagged Phase 1, 51 Phase 2, 2 Phase 3
**Speaker note:** This is what turns a static map into a decision tool a pilot budget can actually be built around.

## 9. AI Integration 3 — Live Decision-Support Insights (LLM Layer)
**Content:**
- [Build pending] Each recommended site's stats (population, transit frequency, need score, growth trend, priority tier) are passed to an LLM, which generates a plain-language justification in the app in real time
- Turns a ranked spreadsheet into something a non-technical planning committee can read and defend
**Speaker note:** Mark this slide as depending on the viz build — we'll fill in a real screenshot once it exists, don't present this as built until it is.

## 10. AI Integration 4 — The Pipeline Itself Is AI-Replicable
**Content:**
- Every step is a documented, sequential script (data pull → tessellation → scoring → phasing → export)
- Designed so another city's planning team can hand this exact sequence to an LLM coding assistant and reproduce the analysis for their own city — swapping in local OSM/GTFS/population data — without a specialist GIS team
- This is the core of the "replicability" ask in the brief, made concrete
**Speaker note:** This is arguably your strongest, most honest AI claim — lead with it if judges push on "where's the AI."

## 11. Key Finding 1 — The Coverage Gap
**Content:**
- Top-10 highest-need hexagons (by population + peak transit demand): ALL show zero existing verified charging/swap infrastructure
- Existing infrastructure (23 of 865 hexagons with any coverage) clusters around the CBD and the TotalEnergies retail network — a commercial siting pattern, not a needs-based one
- Caveat stated on-slide: 27 verified physical points vs. operators' aggregate claims of 50+ stations citywide — dataset transparency gap noted honestly
**Speaker note:** This is your headline finding. State the caveat out loud — it reads as rigor, not weakness.

## 12. Key Finding 2 — Growth Will Widen the Gap
**Content:**
- The hexagons with the highest current need are also, independently, among the fastest-growing (2015-2020 CAGR ~2.2-3.1%/year)
- Top site alone (hexagon 887a6e404bfffff): +21,327 predicted residents by mid-2026 on top of already being the #1 need hexagon
- Without intervention, the gap compounds rather than closes
**Speaker note:** This is the urgency argument for funding a pilot now, not later.

## 13. Demo Walkthrough — Existing Infrastructure Layer
**Content:** [Screenshot placeholder] Map showing all 29 catalogued sites, color-coded by operator and priority tier
**Speaker note:** Fill in once the OpenLayers/Kepler build is ready.

## 14. Demo Walkthrough — Animated H3 Tessellation & Transit Patterns
**Content:** [Screenshot/GIF placeholder] AM peak / midday / PM peak animated hexagon view, sourced directly from GTFS frequency bands
**Speaker note:** Emphasize these time bands are the transit operators' own scheduled headways, not simulated.

## 15. Demo Walkthrough — Proposed Sites + Live AI Insights
**Content:** [Screenshot placeholder] Top-20 ranked sites, toggle between current need and growth-adjusted phasing, LLM-generated rationale panel
**Speaker note:** This is the slide judges will remember — make sure the LLM panel is actually live in the demo, not a static mock.

## 16. Target Users
**Content:**
- Nairobi City County planning & transport departments
- National/county e-mobility policy teams (Kenya's e-mobility policy is still forming)
- C40/I4C member cities seeking a replicable siting methodology
- E-mobility operators (Roam, BasiGo, Ampersand, ARC Ride, etc.) — investment/expansion prioritization
- Climate finance & impact investors evaluating e-mobility infrastructure deals
**Speaker note:** Naming real operators by name here (as data subjects, not partners) grounds this in the actual Nairobi ecosystem.

## 17. Impact Framing
**Content:**
- Direct link to Pilot Plan's phase counts: 289 Phase-1 hexagons represent [X]M people currently underserved by verified charging/swap access
- Framed around Avoid-Shift-Improve outcomes: enabling mode-shift from private car/petrol boda to electric bus/e-bike in the highest-need corridors first
- Explicit tie to C40's transport-emissions goals
**Speaker note:** Keep numbers to what the pipeline actually output — don't inflate with unsourced emissions-reduction estimates unless you calculate them from real trip/mode data.

## 18. Replicability as the Product
**Content:**
- Every data source is open (OSM, WorldPop, GTFS) — no proprietary feed required
- Scripts are parameterized by city name/boundary — swapping "Nairobi" for another city's GTFS feed and boundary is the only required change
- This is positioned as a methodology + toolkit, not a one-city dashboard
**Speaker note:** This slide is your answer to "how does this scale beyond Nairobi" — a judging criterion.

## 19. C40 / I4C Partner Alignment
**Content:**
- Explicit callouts: Avoid-Shift-Improve (C40), Transportation priority theme (I4C bonus criteria), Urban Transitions Mission / GCoM city networks as potential pilot-scaling partners
- [Add specific named C40/I4C Nairobi-relevant programs if identified before submission]
**Speaker note:** Verify current C40/I4C Nairobi program names before finalizing — don't guess at partner names.

## 20. Pilot Plan Summary + Call to Action
**Content:**
- 6-month phased rollout: Months 1-2 (7 sites, Phase 1 highest-need), Months 3-4 (7 sites), Months 5-6 (6 sites)
- Team structure and activities per the separate Pilot Plan document
- Ask: pilot funding/partnership to validate the top Phase-1 sites with on-ground siting surveys
**Speaker note:** End on the ask, not a recap — judges should leave knowing exactly what you want from them.

---
**Still open before this is submission-ready:**
- Slides 9 and 15 depend on the LLM insights panel actually being built
- Slide 5's pipeline diagram and slides 13-14 need real screenshots once the viz exists
- Slide 19 needs verified, current C40/I4C partner/program names (don't guess)
- Slide 1 needs a final solution name
- Slide 17 needs a real, sourced impact number (population-in-Phase-1-hexagons is easy to compute now if you want it before the viz is done)
