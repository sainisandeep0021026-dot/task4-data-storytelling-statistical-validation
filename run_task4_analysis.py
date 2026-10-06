from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
TASK3_ENRICHED_PATH = PROJECT_ROOT / "task3_deep_dive_interactive_dashboard" / "output" / "enriched_transactions.csv"
TASK3_SEGMENT_PATH = PROJECT_ROOT / "task3_deep_dive_interactive_dashboard" / "output" / "segment_summary.csv"
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

LOCAL_DATA_PATH = DATA_DIR / "enriched_transactions.csv"
SEGMENT_SUMMARY_PATH = DATA_DIR / "segment_summary.csv"
TEST_RESULTS_PATH = OUTPUT_DIR / "statistical_test_results.csv"
HYPOTHESIS_SUMMARY_PATH = OUTPUT_DIR / "hypothesis_testing_summary.md"
STORY_REPORT_PATH = OUTPUT_DIR / "storytelling_report.md"
PRESENTATION_DATA_PATH = OUTPUT_DIR / "presentation_data.json"


def ensure_dirs() -> None:
    for path in (DATA_DIR, OUTPUT_DIR):
        path.mkdir(parents=True, exist_ok=True)


def normal_cdf(value: float) -> float:
    return 0.5 * (1 + math.erf(value / math.sqrt(2)))


def money(value: float) -> str:
    return f"{value:,.2f}"


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    def fmt(value: object) -> str:
        if pd.isna(value):
            return ""
        if isinstance(value, float):
            return f"{value:.4f}" if abs(value) < 1 else f"{value:.2f}"
        return str(value)

    prepared = [[fmt(value) for value in row] for row in rows]
    widths = [len(header) for header in headers]
    for row in prepared:
        widths = [max(width, len(value)) for width, value in zip(widths, row)]

    header_line = "| " + " | ".join(header.ljust(width) for header, width in zip(headers, widths)) + " |"
    divider = "| " + " | ".join("-" * width for width in widths) + " |"
    body = ["| " + " | ".join(value.ljust(width) for value, width in zip(row, widths)) + " |" for row in prepared]
    return "\n".join([header_line, divider, *body])


def clean_json_value(value: object) -> object:
    if isinstance(value, dict):
        return {key: clean_json_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [clean_json_value(item) for item in value]
    if pd.isna(value):
        return None
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.bool_):
        return bool(value)
    return value


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not TASK3_ENRICHED_PATH.exists():
        raise FileNotFoundError(f"Missing Task 3 enriched dataset: {TASK3_ENRICHED_PATH}")

    df = pd.read_csv(TASK3_ENRICHED_PATH)
    df.to_csv(LOCAL_DATA_PATH, index=False)

    if TASK3_SEGMENT_PATH.exists():
        segments = pd.read_csv(TASK3_SEGMENT_PATH)
        segments.to_csv(SEGMENT_SUMMARY_PATH, index=False)
    else:
        segments = (
            df.groupby("segment")
            .agg(customers=("customer_id", "nunique"), total_orders=("transaction_id", "count"), realized_sales=("realized_sales", "sum"))
            .reset_index()
        )
        segments.to_csv(SEGMENT_SUMMARY_PATH, index=False)

    return df, segments


def two_proportion_z_test(success_a: int, total_a: int, success_b: int, total_b: int) -> dict[str, float]:
    p_a = success_a / total_a
    p_b = success_b / total_b
    diff = p_a - p_b
    pooled = (success_a + success_b) / (total_a + total_b)
    se_pooled = math.sqrt(pooled * (1 - pooled) * (1 / total_a + 1 / total_b))
    z_score = diff / se_pooled
    p_value = 2 * (1 - normal_cdf(abs(z_score)))
    se_unpooled = math.sqrt((p_a * (1 - p_a) / total_a) + (p_b * (1 - p_b) / total_b))
    ci_low = diff - 1.96 * se_unpooled
    ci_high = diff + 1.96 * se_unpooled
    return {
        "rate_a": p_a,
        "rate_b": p_b,
        "difference": diff,
        "pooled_rate": pooled,
        "standard_error": se_pooled,
        "z_score": z_score,
        "p_value": p_value,
        "ci_low": ci_low,
        "ci_high": ci_high,
    }


def analyze(df: pd.DataFrame, segments: pd.DataFrame) -> dict[str, object]:
    df["is_delivered"] = df["order_status"].eq("Delivered")
    online = df[df["sales_channel"].eq("Online")]
    offline = df[df["sales_channel"].eq("Offline")]
    online_success = int(online["is_delivered"].sum())
    offline_success = int(offline["is_delivered"].sum())
    online_total = int(len(online))
    offline_total = int(len(offline))
    test = two_proportion_z_test(online_success, online_total, offline_success, offline_total)

    monthly = (
        df.groupby("order_month")
        .agg(orders=("transaction_id", "count"), realized_sales=("realized_sales", "sum"), booked_sales=("net_sales", "sum"))
        .reset_index()
        .round(2)
    )
    category = (
        df.groupby("product_category")
        .agg(orders=("transaction_id", "count"), realized_sales=("realized_sales", "sum"), delivery_rate=("is_delivered", "mean"))
        .reset_index()
        .sort_values("realized_sales", ascending=False)
        .round(4)
    )
    channel = (
        df.groupby("sales_channel")
        .agg(orders=("transaction_id", "count"), delivered=("is_delivered", "sum"), delivery_rate=("is_delivered", "mean"), realized_sales=("realized_sales", "sum"))
        .reset_index()
        .round(4)
    )
    risk_segment = segments.sort_values("avg_return_cancel_rate", ascending=False).iloc[0]
    value_segment = segments.sort_values("realized_sales", ascending=False).iloc[0]
    best_month = monthly.sort_values("realized_sales", ascending=False).iloc[0]
    top_category = category.iloc[0]

    total_orders = len(df)
    delivered_orders = int(df["is_delivered"].sum())
    failed_orders = total_orders - delivered_orders
    realized_sales = float(df["realized_sales"].sum())
    booked_sales = float(df["net_sales"].sum())

    result_rows = [
        {
            "test": "Two-proportion z-test",
            "hypothesis": "Online delivery rate differs from offline delivery rate",
            "online_successes": online_success,
            "online_orders": online_total,
            "online_delivery_rate": test["rate_a"],
            "offline_successes": offline_success,
            "offline_orders": offline_total,
            "offline_delivery_rate": test["rate_b"],
            "difference_online_minus_offline": test["difference"],
            "z_score": test["z_score"],
            "p_value": test["p_value"],
            "ci_95_low": test["ci_low"],
            "ci_95_high": test["ci_high"],
            "alpha": 0.05,
            "decision": "Fail to reject H0" if test["p_value"] >= 0.05 else "Reject H0",
        }
    ]
    pd.DataFrame(result_rows).to_csv(TEST_RESULTS_PATH, index=False)

    return {
        "totals": {
            "orders": total_orders,
            "deliveredOrders": delivered_orders,
            "failedOrders": failed_orders,
            "bookedSales": booked_sales,
            "realizedSales": realized_sales,
            "deliveryRate": delivered_orders / total_orders,
            "failureRate": failed_orders / total_orders,
            "avgOrderValue": float(df["net_sales"].mean()),
            "customers": int(df["customer_id"].nunique()),
        },
        "test": {
            **test,
            "onlineSuccess": online_success,
            "onlineTotal": online_total,
            "offlineSuccess": offline_success,
            "offlineTotal": offline_total,
            "decision": "Fail to reject H0" if test["p_value"] >= 0.05 else "Reject H0",
        },
        "monthly": monthly.to_dict(orient="records"),
        "category": category.to_dict(orient="records"),
        "channel": channel.to_dict(orient="records"),
        "segments": segments.to_dict(orient="records"),
        "riskSegment": risk_segment.to_dict(),
        "valueSegment": value_segment.to_dict(),
        "bestMonth": best_month.to_dict(),
        "topCategory": top_category.to_dict(),
    }


def write_hypothesis_summary(results: dict[str, object]) -> None:
    test = results["test"]
    assert isinstance(test, dict)

    rows = [
        ["Null hypothesis", "Online and offline delivery rates are equal."],
        ["Alternative hypothesis", "Online and offline delivery rates are different."],
        ["Test selected", "Two-proportion z-test for delivery success rate."],
        ["Online delivery rate", pct(float(test["rate_a"]))],
        ["Offline delivery rate", pct(float(test["rate_b"]))],
        ["Difference", pct(float(test["difference"]))],
        ["95% confidence interval", f"{pct(float(test['ci_low']))} to {pct(float(test['ci_high']))}"],
        ["z-score", f"{float(test['z_score']):.3f}"],
        ["p-value", f"{float(test['p_value']):.3f}"],
        ["Decision at alpha = 0.05", str(test["decision"])],
    ]

    conclusion = (
        "The p-value is above 0.05, so the analysis does not find statistically significant evidence that delivery success differs by sales channel. "
        "The observed online advantage is small and the confidence interval crosses zero. Business action should focus on customer segments and order-quality recovery rather than assuming one channel is the cause."
    )

    text = f"""# Task 4 Hypothesis Testing Summary

## Business Hypothesis

Sales channel may influence whether an order becomes realized revenue. If one channel has a meaningfully higher delivery rate, the business could prioritize that channel or investigate operational differences.

## Statistical Test

{markdown_table(["Item", "Value"], rows)}

## Interpretation

{conclusion}

## Business Conclusion

Channel alone is not statistically validated as the main driver of order success. The stronger story from Tasks 2 and 3 is that realized revenue is leaking through returns and cancellations, especially in high-risk customer segments. Management should track realized sales, delivery rate, repeat customer rate, and segment-level recovery actions.
"""
    HYPOTHESIS_SUMMARY_PATH.write_text(text, encoding="utf-8")


def write_story_report(results: dict[str, object]) -> None:
    totals = results["totals"]
    test = results["test"]
    risk = results["riskSegment"]
    value = results["valueSegment"]
    month = results["bestMonth"]
    category = results["topCategory"]
    assert isinstance(totals, dict) and isinstance(test, dict)
    assert isinstance(risk, dict) and isinstance(value, dict) and isinstance(month, dict) and isinstance(category, dict)

    text = f"""# Task 4 Data Storytelling Report

## Story Objective

This report synthesizes Tasks 1-3 into a business narrative and validates one key finding with a statistical test.

## Narrative

The analysis began with a cleaned sales transaction dataset and moved through EDA, SQL analysis, customer segmentation, and an interactive dashboard. The central business issue is not raw order volume; it is the gap between booked sales and realized revenue.

## Evidence From Prior Tasks

- Total orders analyzed: {totals["orders"]}
- Booked net sales: {money(float(totals["bookedSales"]))}
- Realized sales from delivered orders: {money(float(totals["realizedSales"]))}
- Delivery rate: {pct(float(totals["deliveryRate"]))}
- Return/cancel rate: {pct(float(totals["failureRate"]))}
- Strongest month: {month["order_month"]} with realized sales of {money(float(month["realized_sales"]))}
- Leading category: {category["product_category"]} with realized sales of {money(float(category["realized_sales"]))}
- Highest value segment: {value["segment"]} with realized sales of {money(float(value["realized_sales"]))}
- Highest risk segment: {risk["segment"]} with average return/cancel rate of {pct(float(risk["avg_return_cancel_rate"]))}

## Statistical Validation

The hypothesis test checked whether delivery rate differs between online and offline orders.

- Online delivery rate: {pct(float(test["rate_a"]))}
- Offline delivery rate: {pct(float(test["rate_b"]))}
- Difference: {pct(float(test["difference"]))}
- 95% confidence interval: {pct(float(test["ci_low"]))} to {pct(float(test["ci_high"]))}
- p-value: {float(test["p_value"]):.3f}
- Decision: {test["decision"]}

## Recommendation

The business should prioritize realized revenue recovery. Channel performance should continue to be monitored, but the test does not support channel as the main statistically validated driver. The recommended actions are:

1. Protect Champion Customers with loyalty and priority support.
2. Launch recovery actions for At-Risk / Recovery customers.
3. Track delivery rate, return/cancel rate, repeat customer rate, and realized sales in every review.
4. Investigate operational causes behind returns and cancellations before shifting channel strategy.
"""
    STORY_REPORT_PATH.write_text(text, encoding="utf-8")


def write_presentation_data(results: dict[str, object]) -> None:
    PRESENTATION_DATA_PATH.write_text(json.dumps(clean_json_value(results), indent=2), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    df, segments = load_inputs()
    results = analyze(df, segments)
    write_hypothesis_summary(results)
    write_story_report(results)
    write_presentation_data(results)
    print(f"Copied dataset: {LOCAL_DATA_PATH}")
    print(f"Copied segment summary: {SEGMENT_SUMMARY_PATH}")
    print(f"Hypothesis summary: {HYPOTHESIS_SUMMARY_PATH}")
    print(f"Storytelling report: {STORY_REPORT_PATH}")
    print(f"Statistical results CSV: {TEST_RESULTS_PATH}")
    print(f"Presentation data: {PRESENTATION_DATA_PATH}")


if __name__ == "__main__":
    main()
