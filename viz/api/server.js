require("dotenv").config();
const express = require("express");
const cors = require("cors");
const Groq = require("groq-sdk");

const app = express();
app.use(cors());
app.use(express.json());

const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });

app.post("/api/insight", async (req, res) => {
  const {
    site_name,
    population,
    peak_transit_vph,
    existing_coverage,
    need_score,
    growth_delta,
    pilot_phase,
    recommended_infrastructure,
  } = req.body;

  const prompt = `You are advising Nairobi city planners on e-mobility charging infrastructure siting. Given this data for one proposed site, write a 2-3 sentence plain-language justification a planning committee could read directly. Be specific and reference the actual numbers. Do not invent facts not given below.

Site data:
- Recommended infrastructure: ${recommended_infrastructure}
- Population in this hexagon: ${Math.round(population).toLocaleString()}
- Peak transit frequency: ${peak_transit_vph} vehicles/hour
- Existing charging/swap coverage: ${existing_coverage} (priority-weighted score)
- Need score (0-1 scale, higher = more urgent): ${Number(need_score).toFixed(3)}
- Predicted population growth by mid-2026: +${Math.round(growth_delta).toLocaleString()}
- Pilot phase: ${pilot_phase}
- Keep your entire response under 80 words.

Write the justification now, no preamble:`;

  try {
    const completion = await groq.chat.completions.create({
        model: "openai/gpt-oss-120b",
        messages: [{ role: "user", content: prompt }],
        temperature: 0.4,
        max_tokens: 500,
        reasoning_effort: "low",   // cuts down reasoning-token spend
    });

    res.json({ insight: completion.choices[0].message.content.trim() });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Failed to generate insight" });
  }
});

const PORT = 3001;
app.listen(PORT, () => console.log(`Insights API running on http://localhost:${PORT}`));