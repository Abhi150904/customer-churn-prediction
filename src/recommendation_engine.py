"""
recommendation_engine.py
=========================
Rule-based retention actions keyed off risk level, contract type,
monthly charges, tenure, service mix, support coverage, payment method,
and customer support needs.

This is intentionally a simple, auditable rule table rather than a
second model — for a retention program, "why did the model say to
call this customer" needs to be answerable in one sentence to a
non-technical stakeholder.
"""

from __future__ import annotations

import pandas as pd

from src.utils import get_logger

logger = get_logger(__name__)

MONTHLY_CHARGE_HIGH_THRESHOLD = 80
NEW_CUSTOMER_TENURE_MONTHS = 6
LOW_SERVICE_COUNT_THRESHOLD = 2


def _value(row: pd.Series, column: str, default=None):
    """Return a row value with a safe fallback for optional dashboard fields."""
    value = row.get(column, default)
    if pd.isna(value):
        return default
    return value


def _is_yes(row: pd.Series, column: str) -> bool:
    return _value(row, column, "No") == "Yes"


def _has_no_support_coverage(row: pd.Series) -> bool:
    return _value(row, "Tech Support", "Yes") == "No" or _value(row, "Online Security", "Yes") == "No"


def recommend_action(row: pd.Series) -> str:
    """
    Return a retention action for a single customer row.

    Expects the row to contain 'Risk Level', 'Contract', and
    'Monthly Charges'. Additional customer attributes are used when
    present, with safe fallbacks for older dashboard datasets.
    """
    risk = row["Risk Level"]
    contract = row["Contract"]
    monthly = row["Monthly Charges"]
    tenure = _value(row, "Tenure Months")
    internet_service = _value(row, "Internet Service")
    payment_method = _value(row, "Payment Method")
    total_services = _value(row, "Total Services")
    is_senior = _is_yes(row, "Senior Citizen")
    new_customer = tenure is not None and tenure <= NEW_CUSTOMER_TENURE_MONTHS
    low_service_depth = total_services is not None and total_services <= LOW_SERVICE_COUNT_THRESHOLD

    if risk == "Critical":
        if is_senior:
            return "Priority human support outreach + retention specialist follow-up"
        if contract == "Month-to-month":
            return "Immediate retention call + annual contract upgrade incentive"
        elif _has_no_support_coverage(row):
            return "Priority retention call + support/security bundle review"
        elif monthly > MONTHLY_CHARGE_HIGH_THRESHOLD:
            return "Priority retention call + loyalty pricing review"
        else:
            return "Priority retention call + Loyalty reward"

    elif risk == "High":
        if new_customer:
            return "Onboarding rescue call + first-bill review"
        elif internet_service == "Fiber optic":
            return "Service quality review + personalized retention offer"
        elif _has_no_support_coverage(row):
            return "Offer premium support/security bundle"
        elif payment_method == "Electronic check":
            return "Autopay migration incentive + billing support"
        elif monthly > MONTHLY_CHARGE_HIGH_THRESHOLD:
            return "Loyalty pricing review for high-value account"
        elif low_service_depth:
            return "Service-fit check-in + targeted bundle offer"
        else:
            return "Offer premium support"

    elif risk == "Medium":
        if contract == "Month-to-month":
            return "Contract upgrade email + annual plan incentive"
        elif payment_method == "Electronic check":
            return "Autopay migration email + small incentive"
        else:
            return "Targeted nurture email with service check-in"

    else:
        return "No action required"


def apply_recommendations(df: pd.DataFrame) -> pd.DataFrame:
    """Add a 'Recommendation' column to df by applying recommend_action row-wise."""
    required = {"Risk Level", "Contract", "Monthly Charges"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Dataframe is missing required columns: {missing}")

    out = df.copy()
    out["Recommendation"] = out.apply(recommend_action, axis=1)

    logger.info("Generated recommendations: %s", out["Recommendation"].value_counts().to_dict())
    return out
