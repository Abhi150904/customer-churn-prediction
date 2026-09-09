import pandas as pd

from src.feature_engineering import add_business_features


def test_add_business_features_calculates_dashboard_segments():
    df = pd.DataFrame(
        {
            "Tenure Months": [0, 24, 36],
            "Total Charges": [0.0, 1200.0, 3600.0],
            "Monthly Charges": [30.0, 70.0, 90.0],
            "Phone Service": ["Yes", "No", "Yes"],
            "Multiple Lines": ["No", "No", "Yes"],
            "Online Security": ["Yes", "No", "No internet service"],
            "Online Backup": ["No", "Yes", "No internet service"],
            "Device Protection": ["No", "Yes", "No internet service"],
            "Tech Support": ["Yes", "No", "No internet service"],
            "Streaming TV": ["No", "Yes", "No internet service"],
            "Streaming Movies": ["No", "No", "No internet service"],
            "Internet Service": ["DSL", "Fiber optic", "No"],
            "Partner": ["Yes", "No", "Yes"],
            "Dependents": ["No", "Yes", "Yes"],
        }
    )

    out = add_business_features(df)

    assert list(out["Avg Monthly Spend"]) == [0.0, 50.0, 100.0]
    assert list(out["Long Term Customer"]) == [0, 1, 1]
    assert list(out["High Monthly Bill"]) == [0, 0, 1]
    assert list(out["Total Services"]) == [3, 3, 2]
    assert list(out["Has Internet"]) == [1, 1, 0]
    assert list(out["Family Size"]) == [1, 1, 2]


def test_add_business_features_preserves_existing_columns_and_input_frame():
    df = pd.DataFrame(
        {
            "Tenure Months": [10],
            "Total Charges": [500.0],
            "Monthly Charges": [50.0],
        }
    )

    out = add_business_features(df)

    assert "Avg Monthly Spend" not in df.columns
    assert "Avg Monthly Spend" in out.columns
    assert out.loc[0, "Tenure Months"] == 10
    assert out.loc[0, "Monthly Charges"] == 50.0


def test_add_business_features_skips_missing_source_columns_gracefully():
    df = pd.DataFrame({"Monthly Charges": [40.0, 60.0]})

    out = add_business_features(df)

    assert list(out["High Monthly Bill"]) == [0, 1]
    assert "Avg Monthly Spend" not in out.columns
    assert "Total Services" not in out.columns
    assert "Has Internet" not in out.columns
    assert "Family Size" not in out.columns
