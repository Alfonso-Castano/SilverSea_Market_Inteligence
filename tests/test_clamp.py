import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.analyst import _clamp_opportunity_scores, _SCORE_DIMENSIONS


def _make_opp(scores=None):
    return {"title": "Test opportunity", "scores": scores or {}}


def test_out_of_range_dimensions_are_clamped():
    opp = _make_opp({
        "strategic_fit": 9,
        "revenue_potential": -3,
        "win_probability": 3,
        "urgency": 100,
        "intelligence_quality": 5,
    })
    result = _clamp_opportunity_scores([opp])[0]
    assert result["scores"]["strategic_fit"] == 5
    assert result["scores"]["revenue_potential"] == 1
    assert result["scores"]["win_probability"] == 3
    assert result["scores"]["urgency"] == 5
    assert result["scores"]["intelligence_quality"] == 5
    assert result["total_score"] == 19  # 5 + 1 + 3 + 5 + 5


def test_negative_and_non_numeric_values_default_to_one():
    opp = _make_opp({
        "strategic_fit": -5,
        "revenue_potential": "high",
        "win_probability": None,
        "urgency": 3,
        "intelligence_quality": 4,
    })
    result = _clamp_opportunity_scores([opp])[0]
    assert result["scores"]["strategic_fit"] == 1
    assert result["scores"]["revenue_potential"] == 1
    assert result["scores"]["win_probability"] == 1
    assert result["scores"]["urgency"] == 3
    assert result["scores"]["intelligence_quality"] == 4
    assert result["total_score"] == 10


def test_missing_dimensions_default_to_one():
    opp = _make_opp({"strategic_fit": 4})  # other four dims absent entirely
    result = _clamp_opportunity_scores([opp])[0]
    for dim in _SCORE_DIMENSIONS:
        assert dim in result["scores"]
    assert result["scores"]["strategic_fit"] == 4
    assert result["scores"]["revenue_potential"] == 1
    assert result["scores"]["win_probability"] == 1
    assert result["scores"]["urgency"] == 1
    assert result["scores"]["intelligence_quality"] == 1
    assert result["total_score"] == 8


def test_missing_scores_key_entirely_defaults_all_to_one():
    opp = {"title": "No scores field at all"}
    result = _clamp_opportunity_scores([opp])[0]
    assert result["total_score"] == 5  # 1 * 5 dimensions
    assert all(v == 1 for v in result["scores"].values())


def test_llm_supplied_bogus_total_score_is_overridden():
    opp = _make_opp({
        "strategic_fit": 5,
        "revenue_potential": 5,
        "win_probability": 5,
        "urgency": 5,
        "intelligence_quality": 5,
    })
    opp["total_score"] = 999  # LLM hallucinated an out-of-range total
    result = _clamp_opportunity_scores([opp])[0]
    assert result["total_score"] == 25  # recomputed from clamped dims, not trusted from input


def test_multiple_opportunities_are_each_clamped_independently():
    opps = [
        _make_opp({"strategic_fit": 10, "revenue_potential": 1, "win_probability": 1, "urgency": 1, "intelligence_quality": 1}),
        _make_opp({"strategic_fit": 1, "revenue_potential": 1, "win_probability": 1, "urgency": 1, "intelligence_quality": 1}),
    ]
    result = _clamp_opportunity_scores(opps)
    assert result[0]["total_score"] == 9   # 5+1+1+1+1
    assert result[1]["total_score"] == 5   # 1+1+1+1+1
