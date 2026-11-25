"""
Unit tests for Siddha Deterministic Rule Engine.
"""

from app.rule_engine import generate_observations, rule_based_flags


def test_rule_engine_high_foam():
    """Verify high foam flags and observation text."""
    sample = {
        "foam_percentage": 55.0,
        "sediment_percentage": 5.0,
        "transparency_score": 9.0,
        "urine_color": "Yellow",
        "branch_count": 1,
        "circularity": 0.85,
        "oil_spread_speed": 5.0,
        "edge_roughness": 2.0,
        "oil_shape": "Circular",
    }
    obs = generate_observations(sample)
    flags = rule_based_flags(sample)
    assert flags["high_foam"] is True
    assert any("High foam" in o for o in obs)


def test_rule_engine_irregular_oil_pattern():
    """Verify irregular Neikuri oil spread flags."""
    sample = {
        "foam_percentage": 10.0,
        "sediment_percentage": 30.0,
        "transparency_score": 3.0,
        "urine_color": "Dark Amber",
        "branch_count": 8,
        "circularity": 0.35,
        "oil_spread_speed": 2.0,
        "edge_roughness": 7.5,
        "oil_shape": "Branched",
    }
    obs = generate_observations(sample)
    flags = rule_based_flags(sample)
    assert flags["irregular_oil_pattern"] is True
    assert flags["turbid_sample"] is True
    assert flags["high_sediment"] is True
    assert any("Branched" in o for o in obs)
