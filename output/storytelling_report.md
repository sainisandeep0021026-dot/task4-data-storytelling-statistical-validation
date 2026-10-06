# Task 4 Data Storytelling Report

## Story Objective

This report synthesizes Tasks 1-3 into a business narrative and validates one key finding with a statistical test.

## Narrative

The analysis began with a cleaned sales transaction dataset and moved through EDA, SQL analysis, customer segmentation, and an interactive dashboard. The central business issue is not raw order volume; it is the gap between booked sales and realized revenue.

## Evidence From Prior Tasks

- Total orders analyzed: 138
- Booked net sales: 630,195.86
- Realized sales from delivered orders: 320,834.34
- Delivery rate: 43.5%
- Return/cancel rate: 56.5%
- Strongest month: 2025-02 with realized sales of 95,133.33
- Leading category: Home & Kitchen with realized sales of 181,891.18
- Highest value segment: At-Risk / Recovery with realized sales of 130,146.17
- Highest risk segment: At-Risk / Recovery with average return/cancel rate of 78.0%

## Statistical Validation

The hypothesis test checked whether delivery rate differs between online and offline orders.

- Online delivery rate: 46.3%
- Offline delivery rate: 41.7%
- Difference: 4.6%
- 95% confidence interval: -12.3% to 21.6%
- p-value: 0.592
- Decision: Fail to reject H0

## Recommendation

The business should prioritize realized revenue recovery. Channel performance should continue to be monitored, but the test does not support channel as the main statistically validated driver. The recommended actions are:

1. Protect Champion Customers with loyalty and priority support.
2. Launch recovery actions for At-Risk / Recovery customers.
3. Track delivery rate, return/cancel rate, repeat customer rate, and realized sales in every review.
4. Investigate operational causes behind returns and cancellations before shifting channel strategy.
