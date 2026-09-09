import pandas as pd

from src.recommendation_engine import apply_recommendations, recommend_action


def test_critical_month_to_month():
    row = pd.Series({"Risk Level": "Critical", "Contract": "Month-to-month", "Monthly Charges": 50})
    assert recommend_action(row) == "Immediate retention call + annual contract upgrade incentive"


def test_critical_long_term_contract():
    row = pd.Series({"Risk Level": "Critical", "Contract": "Two year", "Monthly Charges": 50})
    assert recommend_action(row) == "Priority retention call + Loyalty reward"


def test_critical_senior_customer_gets_human_support_priority():
    row = pd.Series(
        {
            "Risk Level": "Critical",
            "Contract": "Month-to-month",
            "Monthly Charges": 90,
            "Senior Citizen": "Yes",
        }
    )
    assert recommend_action(row) == "Priority human support outreach + retention specialist follow-up"


def test_critical_missing_support_coverage():
    row = pd.Series(
        {
            "Risk Level": "Critical",
            "Contract": "One year",
            "Monthly Charges": 70,
            "Tech Support": "No",
            "Online Security": "Yes",
        }
    )
    assert recommend_action(row) == "Priority retention call + support/security bundle review"


def test_high_risk_high_bill():
    row = pd.Series(
        {
            "Risk Level": "High",
            "Contract": "One year",
            "Monthly Charges": 90,
            "Tenure Months": 18,
            "Internet Service": "DSL",
            "Tech Support": "Yes",
            "Online Security": "Yes",
        }
    )
    assert recommend_action(row) == "Loyalty pricing review for high-value account"


def test_high_risk_low_bill():
    row = pd.Series(
        {
            "Risk Level": "High",
            "Contract": "One year",
            "Monthly Charges": 50,
            "Tenure Months": 18,
            "Internet Service": "DSL",
            "Tech Support": "Yes",
            "Online Security": "Yes",
        }
    )
    assert recommend_action(row) == "Offer premium support"


def test_high_risk_new_customer_gets_onboarding_recovery():
    row = pd.Series(
        {
            "Risk Level": "High",
            "Contract": "Month-to-month",
            "Monthly Charges": 65,
            "Tenure Months": 3,
        }
    )
    assert recommend_action(row) == "Onboarding rescue call + first-bill review"


def test_high_risk_fiber_customer_gets_service_quality_review():
    row = pd.Series(
        {
            "Risk Level": "High",
            "Contract": "One year",
            "Monthly Charges": 70,
            "Tenure Months": 18,
            "Internet Service": "Fiber optic",
        }
    )
    assert recommend_action(row) == "Service quality review + personalized retention offer"


def test_high_risk_without_support_gets_bundle_offer():
    row = pd.Series(
        {
            "Risk Level": "High",
            "Contract": "One year",
            "Monthly Charges": 70,
            "Tenure Months": 18,
            "Internet Service": "DSL",
            "Tech Support": "No",
            "Online Security": "Yes",
        }
    )
    assert recommend_action(row) == "Offer premium support/security bundle"


def test_high_risk_electronic_check_gets_autopay_offer():
    row = pd.Series(
        {
            "Risk Level": "High",
            "Contract": "One year",
            "Monthly Charges": 70,
            "Tenure Months": 18,
            "Internet Service": "DSL",
            "Tech Support": "Yes",
            "Online Security": "Yes",
            "Payment Method": "Electronic check",
        }
    )
    assert recommend_action(row) == "Autopay migration incentive + billing support"


def test_medium_risk():
    row = pd.Series({"Risk Level": "Medium", "Contract": "One year", "Monthly Charges": 50})
    assert recommend_action(row) == "Targeted nurture email with service check-in"


def test_medium_month_to_month_gets_contract_upgrade_email():
    row = pd.Series({"Risk Level": "Medium", "Contract": "Month-to-month", "Monthly Charges": 50})
    assert recommend_action(row) == "Contract upgrade email + annual plan incentive"


def test_low_risk():
    row = pd.Series({"Risk Level": "Low", "Contract": "Two year", "Monthly Charges": 50})
    assert recommend_action(row) == "No action required"


def test_apply_recommendations_on_dataframe(sample_customers):
    out = apply_recommendations(sample_customers)
    assert "Recommendation" in out.columns
    assert len(out) == len(sample_customers)
    assert out["Recommendation"].notna().all()
