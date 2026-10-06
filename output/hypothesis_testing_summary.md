# Task 4 Hypothesis Testing Summary

## Business Hypothesis

Sales channel may influence whether an order becomes realized revenue. If one channel has a meaningfully higher delivery rate, the business could prioritize that channel or investigate operational differences.

## Statistical Test

| Item                     | Value                                            |
| ------------------------ | ------------------------------------------------ |
| Null hypothesis          | Online and offline delivery rates are equal.     |
| Alternative hypothesis   | Online and offline delivery rates are different. |
| Test selected            | Two-proportion z-test for delivery success rate. |
| Online delivery rate     | 46.3%                                            |
| Offline delivery rate    | 41.7%                                            |
| Difference               | 4.6%                                             |
| 95% confidence interval  | -12.3% to 21.6%                                  |
| z-score                  | 0.535                                            |
| p-value                  | 0.592                                            |
| Decision at alpha = 0.05 | Fail to reject H0                                |

## Interpretation

The p-value is above 0.05, so the analysis does not find statistically significant evidence that delivery success differs by sales channel. The observed online advantage is small and the confidence interval crosses zero. Business action should focus on customer segments and order-quality recovery rather than assuming one channel is the cause.

## Business Conclusion

Channel alone is not statistically validated as the main driver of order success. The stronger story from Tasks 2 and 3 is that realized revenue is leaking through returns and cancellations, especially in high-risk customer segments. Management should track realized sales, delivery rate, repeat customer rate, and segment-level recovery actions.
