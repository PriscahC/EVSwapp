require("dotenv").config();
const fs = require("fs");
const Groq = require("groq-sdk");

const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });

function buildPrompt(p) {
  return `You are advising Nairobi city planners on e-mobility charging infrastructure siting. Given this data for one proposed site, write a 2-3 sentence plain-language justification a planning committee could read directly. Be specific and reference the actual numbers. Do not invent facts not given below. Keep your entire response under 80 words.

Site data:
- Recommended infrastructure: ${p.recommended_infrastructure}
- Population in this hexagon: ${Math.round(p.population).toLocaleString()}
- Peak transit frequency: ${p.peak_transit_vph} vehicles/hour
- Existing charging/swap coverage: ${p.existing_coverage} (priority-weighted score)
- Need score (0-1 scale, higher = more urgent): ${Number(p.need_score).toFixed(3)}
- Predicted population growth by mid-2026: +${Math.round(p.growth_delta).toLocaleString()}
- Pilot phase: ${p.pilot_phase}

Write the justification now, no preamble:`;
}

async function getInsight(p, attempt = 1) {
  try {
    const completion = await groq.chat.completions.create({
      model: "openai/gpt-oss-120b",
      messages: [{ role: "user", content: buildPrompt(p) }],
      temperature: 0.4,
      max_tokens: 500,
      reasoning_effort: "low",
    });
    const text = completion.choices[0].message.content?.trim() || "";
    if (!text) throw new Error("empty content");
    return text;
  } catch (err) {
    if (attempt < 3) {
      console.warn(`  retry ${attempt} (${err.message})`);
      await new Promise(r => setTimeout(r, 1500 * attempt));
      return getInsight(p, attempt + 1);
    }
    throw err;
  }
}

async function main() {
//   const raw = JSON.parse(fs.readFileSync("../data/processed/proposed_sites_phased.geojson", "utf8"));
    const raw = JSON.parse(fs.readFileSync("../../data/processed/proposed_sites_phased.geojson", "utf8"));
  const cache = {};

  for (const [i, feature] of raw.features.entries()) {
    const p = feature.properties;
    const key = p.site_name || `site_${i}`;
    console.log(`[${i + 1}/${raw.features.length}] ${key}`);
    const insight = await getInsight(p);
    cache[key] = insight;
    feature.properties.ai_insight = insight;
    await new Promise(r => setTimeout(r, 500)); // gentle pacing
  }

    fs.writeFileSync("../../data/processed/site_insights.json", JSON.stringify(cache, null, 2));
    fs.writeFileSync("../../data/processed/proposed_sites_with_insights.geojson", JSON.stringify(raw, null, 2));
  console.log("Done: site_insights.json + proposed_sites_with_insights.geojson");
}

main().catch(err => { console.error("Batch failed:", err); process.exit(1); });