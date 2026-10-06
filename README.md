# Task 4: Data Storytelling and Statistical Validation

This project completes Task 4 from the internship PDF.

## Task Objective

Synthesize the work from Tasks 1-3 into a business narrative and validate one key finding with a statistical test.

## Files

- `run_task4_analysis.py` - creates the hypothesis test outputs and deck data
- `data/enriched_transactions.csv` - Task 3 enriched dataset used for storytelling and testing
- `data/segment_summary.csv` - Task 3 customer segment summary
- `output/hypothesis_testing_summary.md` - statistical test summary
- `output/storytelling_report.md` - business narrative report
- `output/statistical_test_results.csv` - numeric test output
- `output/task4_final_presentation.pptx` - final PowerPoint deck

## Hypothesis Tested

Null hypothesis: online and offline delivery rates are equal.

Alternative hypothesis: online and offline delivery rates are different.

Test used: two-proportion z-test.

## How To Run

From the main project folder:

```powershell
& "C:\Users\kashy\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" "task4_data_storytelling_statistical_validation\run_task4_analysis.py"
```

The PowerPoint deck is generated separately by the deck builder after the analysis output is created.

```powershell
cd "C:\Users\kashy\OneDrive\Documents\New project\task4_data_storytelling_statistical_validation"
& "C:\Users\kashy\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe" "build_task4_deck.mjs"
```

## Submission Checklist

- Upload this full project folder to GitHub.
- Submit the final presentation deck and hypothesis testing summary.
- Record a 7-10 minute LinkedIn stakeholder-style presentation of insights.
