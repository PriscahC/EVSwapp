import json
import numpy as np

with open('data/processed/nairobi_stop_frequency.geojson') as f:
    geo = json.load(f)

anchors_hours = [7.5, 12.0, 17.5]  # AM peak, midday, PM peak
anchor_cols = ['vph_am_peak', 'vph_midday', 'vph_pm_peak']
sample_hours = np.arange(6, 21.5, 1.0)  # 6:00 to 21:00, hourly

# collect all interpolated vph values first, then pick a percentile-based threshold
all_vph = []
for feature in geo['features']:
    props = feature['properties']
    anchor_vals = [props.get(c) for c in ['vph_am_peak', 'vph_midday', 'vph_pm_peak']]
    if any(v is None for v in anchor_vals):
        continue
    all_vph.extend(np.interp(sample_hours, anchors_hours, anchor_vals))

VPH_THRESHOLD = np.percentile(all_vph, 85)  # top ~15% busiest stop-hours
print(f"Using data-derived threshold: {VPH_THRESHOLD:.1f} vph")

melted_features = []
for feature in geo['features']:
    props = feature['properties']
    anchor_vals = [props.get(c) for c in anchor_cols]
    if any(v is None for v in anchor_vals):
        continue
    interp_vph = np.interp(sample_hours, anchors_hours, anchor_vals)

    for hour, vph in zip(sample_hours, interp_vph):
        if vph < VPH_THRESHOLD:
            continue  # <- key change: skip this row entirely for this hour
        h = int(hour)
        m = int(round((hour - h) * 60))
        timestamp = f"2026-08-30T{h:02d}:{m:02d}:00"
        new_props = {k: v for k, v in props.items() if k not in anchor_cols}
        new_props['time_stamp'] = timestamp
        new_props['vph'] = round(float(vph), 1)
        melted_features.append({
            "type": "Feature",
            "geometry": feature['geometry'],
            "properties": new_props,
        })

with open('data/processed/transit_bands_melted.geojson', 'w') as f:
    json.dump({"type": "FeatureCollection", "features": melted_features}, f)

print(f"Wrote {len(melted_features)} features (threshold={VPH_THRESHOLD} vph)")