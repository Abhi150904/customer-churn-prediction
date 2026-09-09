"""
campaign_planner.py
===================
Cost-sensitive retention campaign planning utilities.

The model produces churn probabilities, but retention teams usually
need a business decision: who should we contact, what threshold should
we use, and what is the expected value after outreach costs? This
module keeps those calculations outside the Streamlit presentation
layer so they can be tested and reused.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd


PROBABILITY_COL = "Churn Probability"
MONTHLY_CHARGE_COL = "Monthly Charges"
ACTUAL_CHURN_COL = "Actual Churn"


@dataclass(frozen=True)
class CampaignAssumptions:
    """Business assumptions used to estimate campaign value."""

    retention_months: int = 12
    save_rate: float = 0.25
    contact_cost: float = 15.0
    incentive_cost: float = 50.0

    @property
    def cost_per_customer(self) -> float:
        return self.contact_cost + self.incentive_cost


def _validate_inputs(df: pd.DataFrame, assumptions: CampaignAssumptions) -> None:
    missing = {PROBABILITY_COL, MONTHLY_CHARGE_COL} - set(df.columns)
    if missing:
        raise ValueError(f"Dataframe is missing required columns: {sorted(missing)}")
    if assumptions.retention_months <= 0:
        raise ValueError("retention_months must be greater than 0.")
    if not 0 <= assumptions.save_rate <= 1:
        raise ValueError("save_rate must be between 0 and 1.")
    if assumptions.contact_cost < 0 or assumptions.incentive_cost < 0:
        raise ValueError("campaign costs cannot be negative.")


def add_campaign_value(
    df: pd.DataFrame,
    assumptions: CampaignAssumptions,
) -> pd.DataFrame:
    """
    Add per-customer expected value fields used by the campaign planner.

    Expected gross value is probability-weighted revenue saved:
    churn probability * monthly charge * retention months * save rate.
    Net value subtracts the per-customer outreach and incentive cost.
    """
    _validate_inputs(df, assumptions)
    out = df.copy()
    out["Expected Revenue Saved"] = (
        out[PROBABILITY_COL]
        * out[MONTHLY_CHARGE_COL]
        * assumptions.retention_months
        * assumptions.save_rate
    )
    out["Campaign Cost"] = assumptions.cost_per_customer
    out["Expected Net Value"] = out["Expected Revenue Saved"] - out["Campaign Cost"]
    return out


def select_campaign_customers(
    df: pd.DataFrame,
    threshold: float,
    assumptions: CampaignAssumptions,
    max_customers: int | None = None,
) -> pd.DataFrame:
    """Return customers at or above the threshold, ranked by expected net value."""
    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be between 0 and 1.")
    if max_customers is not None and max_customers < 0:
        raise ValueError("max_customers cannot be negative.")

    valued = add_campaign_value(df, assumptions)
    selected = valued[valued[PROBABILITY_COL] >= threshold].sort_values(
        by=["Expected Net Value", PROBABILITY_COL],
        ascending=[False, False],
    )
    if max_customers is not None:
        selected = selected.head(max_customers)
    return selected.reset_index(drop=True)


def estimate_campaign_impact(
    df: pd.DataFrame,
    threshold: float,
    assumptions: CampaignAssumptions,
    max_customers: int | None = None,
) -> dict:
    """Summarize expected value and, when available, historical precision/recall."""
    selected = select_campaign_customers(df, threshold, assumptions, max_customers=max_customers)
    targeted_count = int(len(selected))

    impact = {
        "threshold": float(threshold),
        "targeted_customers": targeted_count,
        "expected_revenue_saved": float(selected["Expected Revenue Saved"].sum()),
        "campaign_cost": float(selected["Campaign Cost"].sum()),
        "expected_net_value": float(selected["Expected Net Value"].sum()),
        "avg_targeted_churn_probability": (
            float(selected[PROBABILITY_COL].mean()) if targeted_count else 0.0
        ),
        "monthly_revenue_targeted": float(selected[MONTHLY_CHARGE_COL].sum()),
    }

    if ACTUAL_CHURN_COL in df.columns and df[ACTUAL_CHURN_COL].notna().any():
        actual = df[ACTUAL_CHURN_COL].fillna(0).astype(int)
        predicted_positive = df[PROBABILITY_COL] >= threshold
        true_positive = int((predicted_positive & (actual == 1)).sum())
        false_positive = int((predicted_positive & (actual == 0)).sum())
        false_negative = int((~predicted_positive & (actual == 1)).sum())
        precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0
        recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0
        impact.update(
            {
                "historical_precision": float(precision),
                "historical_recall": float(recall),
                "true_positive": true_positive,
                "false_positive": false_positive,
                "false_negative": false_negative,
            }
        )

    return impact


def threshold_sweep(
    df: pd.DataFrame,
    assumptions: CampaignAssumptions,
    thresholds: Iterable[float] | None = None,
    max_customers: int | None = None,
) -> pd.DataFrame:
    """Evaluate campaign impact over a grid of candidate thresholds."""
    if thresholds is None:
        thresholds = np.round(np.arange(0.05, 0.96, 0.05), 2)
    rows = [
        estimate_campaign_impact(df, threshold, assumptions, max_customers=max_customers)
        for threshold in thresholds
    ]
    return pd.DataFrame(rows)


def find_optimal_threshold(
    df: pd.DataFrame,
    assumptions: CampaignAssumptions,
    thresholds: Iterable[float] | None = None,
    max_customers: int | None = None,
) -> dict:
    """Return the threshold with the highest expected net value."""
    sweep = threshold_sweep(df, assumptions, thresholds=thresholds, max_customers=max_customers)
    if sweep.empty:
        raise ValueError("No thresholds were supplied.")
    return sweep.sort_values(
        by=["expected_net_value", "targeted_customers"],
        ascending=[False, False],
    ).iloc[0].to_dict()
