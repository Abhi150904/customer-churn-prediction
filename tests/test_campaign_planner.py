import pandas as pd
import pytest

from src.campaign_planner import (
    CampaignAssumptions,
    estimate_campaign_impact,
    find_optimal_threshold,
    select_campaign_customers,
    threshold_sweep,
)


@pytest.fixture
def campaign_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Customer ID": ["A", "B", "C"],
            "Churn Probability": [0.9, 0.6, 0.2],
            "Monthly Charges": [100.0, 50.0, 80.0],
            "Actual Churn": [1, 0, 1],
        }
    )


def test_select_campaign_customers_ranks_by_expected_net_value(campaign_df):
    assumptions = CampaignAssumptions(
        retention_months=12,
        save_rate=0.5,
        contact_cost=10,
        incentive_cost=20,
    )

    selected = select_campaign_customers(campaign_df, threshold=0.5, assumptions=assumptions)

    assert list(selected["Customer ID"]) == ["A", "B"]
    assert selected.loc[0, "Expected Revenue Saved"] == pytest.approx(540.0)
    assert selected.loc[0, "Expected Net Value"] == pytest.approx(510.0)


def test_estimate_campaign_impact_includes_value_and_historical_metrics(campaign_df):
    assumptions = CampaignAssumptions(
        retention_months=12,
        save_rate=0.5,
        contact_cost=10,
        incentive_cost=20,
    )

    impact = estimate_campaign_impact(campaign_df, threshold=0.5, assumptions=assumptions)

    assert impact["targeted_customers"] == 2
    assert impact["expected_revenue_saved"] == pytest.approx(720.0)
    assert impact["campaign_cost"] == pytest.approx(60.0)
    assert impact["expected_net_value"] == pytest.approx(660.0)
    assert impact["historical_precision"] == pytest.approx(0.5)
    assert impact["historical_recall"] == pytest.approx(0.5)


def test_threshold_sweep_and_optimal_threshold(campaign_df):
    assumptions = CampaignAssumptions(
        retention_months=12,
        save_rate=0.5,
        contact_cost=10,
        incentive_cost=20,
    )
    thresholds = [0.1, 0.5, 0.8]

    sweep = threshold_sweep(campaign_df, assumptions, thresholds=thresholds)
    optimal = find_optimal_threshold(campaign_df, assumptions, thresholds=thresholds)

    assert list(sweep["threshold"]) == thresholds
    assert optimal["threshold"] == 0.1
    assert optimal["expected_net_value"] == pytest.approx(726.0)


def test_invalid_campaign_assumptions_raise(campaign_df):
    assumptions = CampaignAssumptions(save_rate=1.5)

    with pytest.raises(ValueError, match="save_rate"):
        estimate_campaign_impact(campaign_df, threshold=0.5, assumptions=assumptions)
