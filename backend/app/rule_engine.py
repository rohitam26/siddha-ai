"""
RULE ENGINE — explicit, human-readable observation rules.
--------------------------------------------------------
Deterministic IF/THEN observations derived directly from measured physical parameters.
These rules describe physical/visual observations without making unverified clinical diagnoses.
"""

from typing import Dict, List, Any


def generate_observations(f: Dict[str, Any]) -> List[str]:
    """Produces human-interpretable observation statements from physical measurements."""
    obs = []

    # --- Urine physical observations (Neerkuri) ---
    foam_pct = float(f.get("foam_percentage", 0))
    if foam_pct > 40:
        obs.append("High foam coverage observed on the urine surface (suggests increased surface tension).")
    elif foam_pct > 15:
        obs.append("Moderate foam coverage observed on sample surface.")
    else:
        obs.append("Minimal foam observed on surface meniscus.")

    sediment_pct = float(f.get("sediment_percentage", 0))
    if sediment_pct > 25:
        obs.append("Significant sediment precipitate visible in lower sample layer.")
    elif sediment_pct > 8:
        obs.append("Slight sediment deposit visible.")
    else:
        obs.append("No notable particulate sediment observed.")

    transparency = float(f.get("transparency_score", 5))
    if transparency < 4:
        obs.append("Sample appears turbid / low transparency (optical scatter detected).")
    elif transparency > 8:
        obs.append("Sample appears clear and homogeneous.")

    color = str(f.get("urine_color", "Yellow"))
    if color in ["Dark Amber", "Reddish", "Brownish"]:
        obs.append(f"Urine colour categorized as '{color}', deviating from typical pale-yellow baseline.")
    else:
        obs.append(f"Urine colour categorized as '{color}'.")

    odor = float(f.get("odor_score", 3))
    if odor > 7:
        obs.append("Odour intensity recorded as pungent/strong (proxy intensity score).")

    # --- Neikuri oil-spread pattern observations ---
    branch_count = int(f.get("branch_count", 0))
    circularity = float(f.get("circularity", 0.5))
    if branch_count > 6 and circularity < 0.5:
        obs.append("Highly branched, irregular oil-spread perimeter detected.")
    elif branch_count > 3:
        obs.append("Moderately branched oil-spread pattern with minor peripheral projections.")
    else:
        obs.append("Oil spread boundary is smooth with minimal branching.")

    if circularity > 0.8:
        obs.append("Oil drop demonstrates high radial circularity and regular spreading.")
    elif circularity < 0.4:
        obs.append("Oil drop exhibits an asymmetrical, irregular boundary morphology.")

    speed = float(f.get("oil_spread_speed", 5))
    if speed < 3.0:
        obs.append("Slow expansion velocity across the urine surface.")
    elif speed > 7.0:
        obs.append("Rapid surface expansion velocity observed.")

    roughness = float(f.get("edge_roughness", 3))
    if roughness > 6:
        obs.append("Contour boundary exhibits high edge roughness / micro-indentations.")

    shape = str(f.get("oil_shape", "Circular"))
    obs.append(f"Overall Neikuri morphological pattern classified as '{shape}'.")

    return obs


def rule_based_flags(f: Dict[str, Any]) -> Dict[str, bool]:
    """Boolean alert flags for practitioner quality assurance."""
    return {
        "high_foam": float(f.get("foam_percentage", 0)) > 40,
        "high_sediment": float(f.get("sediment_percentage", 0)) > 25,
        "irregular_oil_pattern": int(f.get("branch_count", 0)) > 6 and float(f.get("circularity", 1.0)) < 0.5,
        "turbid_sample": float(f.get("transparency_score", 10)) < 4.0,
        "high_edge_roughness": float(f.get("edge_roughness", 0)) > 6.0,
    }
