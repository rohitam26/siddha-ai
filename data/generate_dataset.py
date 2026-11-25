"""
SYNTHETIC DATA GENERATOR
------------------------
Generates a FAKE, internally-consistent dataset "inspired by" published
descriptions of Siddha Neerkuri (urine exam) and Neikuri (oil-drop) methods.

*** THIS IS NOT REAL PATIENT DATA. ***
It is produced purely for an academic ML demonstration and must never be
represented as clinical / diagnostic data.

Design idea: we first sample a hidden "risk_latent" score per patient, then
sample every observable feature as a noisy function of that latent risk plus
the chosen predominant humor. This creates the realistic correlations the
brief asks for (high foam + high sediment + irregular oil + high branching
-> higher risk; circular oil + low foam + clear urine -> lower risk).
"""

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
N = 500

COLORS = ["Pale Yellow", "Yellow", "Amber", "Dark Amber", "Reddish", "Brownish"]
OIL_SHAPES = ["Circular", "Ring", "Snake", "Pearl", "Lotus", "Branched", "Spiral", "Irregular"]
HUMORS = ["Vatham", "Pitham", "Kabham", "Vatha-Pitha", "Pitha-Kabha", "Vatha-Kabha"]

# oil shapes considered "clean" vs "concerning" for risk shaping only
LOW_RISK_SHAPES = ["Circular", "Ring", "Pearl"]
MID_RISK_SHAPES = ["Lotus", "Spiral", "Snake"]
HIGH_RISK_SHAPES = ["Branched", "Irregular"]

def clip(x, lo, hi):
    return np.clip(x, lo, hi)

rows = []
for i in range(1, N + 1):
    age = int(clip(rng.normal(45, 15), 12, 90))
    gender = rng.choice(["Male", "Female"], p=[0.52, 0.48])

    # hidden latent risk in [0,1] - drives everything else
    risk_latent = clip(rng.beta(2, 3), 0, 1)  # skewed toward lower risk, realistic class balance

    humor = rng.choice(HUMORS, p=[0.18, 0.18, 0.18, 0.16, 0.15, 0.15])

    # ---- urine color: darker / redder colors correlate with higher risk ----
    color_probs_low = np.array([0.35, 0.30, 0.20, 0.08, 0.04, 0.03])
    color_probs_high = np.array([0.03, 0.10, 0.20, 0.27, 0.20, 0.20])
    color_probs = color_probs_low * (1 - risk_latent) + color_probs_high * risk_latent
    color_probs = color_probs / color_probs.sum()
    urine_color = rng.choice(COLORS, p=color_probs)

    # HSV approximations tied to color + risk (darker/more saturated with risk)
    base_hue = {"Pale Yellow": 55, "Yellow": 48, "Amber": 38, "Dark Amber": 30,
                "Reddish": 10, "Brownish": 20}[urine_color]
    HSV_H = clip(rng.normal(base_hue, 4), 0, 60)
    HSV_S = clip(rng.normal(40 + 50 * risk_latent, 8), 10, 100)
    HSV_V = clip(rng.normal(85 - 30 * risk_latent, 8), 20, 100)

    transparency_score = clip(rng.normal(8 - 5 * risk_latent, 1.2), 1, 10)  # 10=very clear
    foam_percentage = clip(rng.normal(10 + 55 * risk_latent, 10), 0, 100)
    foam_bubble_count = int(clip(rng.normal(20 + 150 * risk_latent, 25), 0, 250))
    sediment_percentage = clip(rng.normal(5 + 40 * risk_latent, 8), 0, 100)
    odor_score = clip(rng.normal(2 + 6 * risk_latent, 1.2), 1, 10)  # 1=mild,10=strong

    oil_spread_diameter_mm = clip(rng.normal(25 - 12 * risk_latent, 4), 3, 30)
    oil_spread_speed = clip(rng.normal(7 - 4 * risk_latent, 1.3), 0.5, 10)  # slower spread -> higher risk

    shape_probs_low = np.array([0.30, 0.20, 0.10, 0.20, 0.10, 0.05, 0.03, 0.02])
    shape_probs_high = np.array([0.03, 0.05, 0.12, 0.05, 0.10, 0.25, 0.15, 0.25])
    shape_probs = shape_probs_low * (1 - risk_latent) + shape_probs_high * risk_latent
    shape_probs = shape_probs / shape_probs.sum()
    oil_shape = rng.choice(OIL_SHAPES, p=shape_probs)

    branch_count = int(clip(rng.normal(1 + 9 * risk_latent, 2), 0, 12))
    circularity = clip(rng.normal(0.9 - 0.6 * risk_latent, 0.08), 0.1, 1.0)
    symmetry_score = clip(rng.normal(9 - 5 * risk_latent, 1.2), 1, 10)
    edge_roughness = clip(rng.normal(1 + 7 * risk_latent, 1.3), 0, 10)
    fractal_dimension = clip(rng.normal(1.05 + 0.55 * risk_latent, 0.08), 1.0, 2.0)

    # tridosha scores (sum ~ 100), predominant humor nudges its own score up
    base = rng.dirichlet(alpha=[3, 3, 3]) * 100
    vatham_score, pitham_score, kabham_score = base
    if "Vatha" in humor: vatham_score += 15
    if "Pitha" in humor or humor == "Pitham": pitham_score += 15
    if "Kabha" in humor or humor == "Kabham": kabham_score += 15
    total = vatham_score + pitham_score + kabham_score
    vatham_score, pitham_score, kabham_score = (
        round(100 * vatham_score / total, 1),
        round(100 * pitham_score / total, 1),
        round(100 * kabham_score / total, 1),
    )

    # ---- final composite risk score used to derive the label ----
    shape_penalty = {"Circular": -0.10, "Ring": -0.07, "Pearl": -0.08, "Lotus": -0.02,
                     "Spiral": 0.03, "Snake": 0.02, "Branched": 0.10, "Irregular": 0.12}[oil_shape]
    composite = (
        0.30 * risk_latent
        + 0.15 * (foam_percentage / 100)
        + 0.15 * (sediment_percentage / 100)
        + 0.10 * (branch_count / 12)
        + 0.10 * (1 - circularity)
        + 0.10 * (edge_roughness / 10)
        + shape_penalty
        + rng.normal(0, 0.05)
    )
    composite = clip(composite, 0, 1)

    if composite < 0.32:
        prototype_risk = "Low"
    elif composite < 0.50:
        prototype_risk = "Moderate"
    else:
        prototype_risk = "High"

    rows.append(dict(
        patient_id=f"SYN-{i:04d}",
        age=age,
        gender=gender,
        urine_color=urine_color,
        HSV_H=round(HSV_H, 1),
        HSV_S=round(HSV_S, 1),
        HSV_V=round(HSV_V, 1),
        transparency_score=round(transparency_score, 1),
        foam_percentage=round(foam_percentage, 1),
        foam_bubble_count=foam_bubble_count,
        sediment_percentage=round(sediment_percentage, 1),
        odor_score=round(odor_score, 1),
        oil_spread_diameter_mm=round(oil_spread_diameter_mm, 1),
        oil_spread_speed=round(oil_spread_speed, 2),
        oil_shape=oil_shape,
        branch_count=branch_count,
        circularity=round(circularity, 2),
        symmetry_score=round(symmetry_score, 1),
        edge_roughness=round(edge_roughness, 1),
        fractal_dimension=round(fractal_dimension, 2),
        vatham_score=vatham_score,
        pitham_score=pitham_score,
        kabham_score=kabham_score,
        predominant_humor=humor,
        prototype_risk=prototype_risk,
    ))

df = pd.DataFrame(rows)
df.to_csv("/home/claude/siddha_ai/data/siddha_synthetic_dataset.csv", index=False)
print(df["prototype_risk"].value_counts())
print(df.shape)
print("Saved to siddha_synthetic_dataset.csv")
