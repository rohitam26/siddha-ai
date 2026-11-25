"""
RULE ENGINE — explicit, human-readable observation rules.

This sits ALONGSIDE the ML model, not inside it. The goal is transparency:
every observation string below is produced by a plain IF/THEN condition on
measured features, not learned from data. This is what lets the system say
"we measured X and Y, and by definition that means Z" instead of "the model
decided this," which is a much easier claim to defend academically.

IMPORTANT: these rules describe visual/physical OBSERVATIONS ONLY
(e.g. "high foam", "branched oil spread"). They intentionally do NOT map
any observation to a named disease — there is no established clinical
evidence for that mapping, and asserting one would be scientifically
dishonest. Clinical interpretation is left to a qualified practitioner.
"""

from typing import Dict, List


def generate_observations(f: Dict) -> List[str]:
    """f is a dict of the same features used for ML prediction."""
    obs = []

    # --- Urine-level observations ---
    if f["foam_percentage"] > 40:
        obs.append("High foam coverage observed on the urine surface.")
    elif f["foam_percentage"] > 15:
        obs.append("Moderate foam coverage observed.")
    else:
        obs.append("Minimal foam observed.")

    if f["sediment_percentage"] > 25:
        obs.append("Significant sediment deposit visible.")
    elif f["sediment_percentage"] > 8:
        obs.append("Slight sediment deposit visible.")

    if f["transparency_score"] < 4:
        obs.append("Urine sample appears turbid / low transparency.")
    elif f["transparency_score"] > 8:
        obs.append("Urine sample appears clear.")

    if f["urine_color"] in ["Dark Amber", "Reddish", "Brownish"]:
        obs.append(f"Urine colour recorded as {f['urine_color'].lower()}, darker than typical pale-yellow baseline.")

    if f["odor_score"] > 7:
        obs.append("Odour intensity recorded as strong (proxy score).")

    # --- Neikuri oil-spread observations ---
    if f["branch_count"] > 8 and f["circularity"] < 0.5:
        obs.append("Highly branched, irregular oil-spread pattern.")
    elif f["branch_count"] > 4:
        obs.append("Moderately branched oil-spread pattern.")
    else:
        obs.append("Oil spread largely unbranched / smooth.")

    if f["circularity"] > 0.8:
        obs.append("Oil spread is highly circular and symmetric.")
    elif f["circularity"] < 0.4:
        obs.append("Oil spread shows an irregular, asymmetric boundary.")

    if f["oil_spread_speed"] < 3:
        obs.append("Oil spread slowly across the surface (low expansion velocity).")
    elif f["oil_spread_speed"] > 7:
        obs.append("Oil spread rapidly across the surface.")

    if f["edge_roughness"] > 6:
        obs.append("Oil-spread boundary edge is rough / jagged.")

    if f["oil_shape"] in ["Branched", "Irregular"]:
        obs.append(f"Overall Neikuri pattern classified visually as '{f['oil_shape']}'.")

    return obs


def rule_based_flags(f: Dict) -> Dict[str, bool]:
    """Boolean flags used for dashboard badges / QA, independent of the ML model."""
    return {
        "high_foam": f["foam_percentage"] > 40,
        "high_sediment": f["sediment_percentage"] > 25,
        "irregular_oil_pattern": f["branch_count"] > 8 and f["circularity"] < 0.5,
        "turbid_sample": f["transparency_score"] < 4,
    }
