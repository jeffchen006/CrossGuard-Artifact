# labelPackage

This folder holds the labeling data we use to categorize contracts and transactions. Think of it as the static knowledge base for the labeling stage.

## How these labels are used

- The labeling scripts load these files to decide which category a contract or transaction belongs to.
- The analysis code treats these labels as inputs, not outputs, so changing them can change downstream results.

## What is in here

- `combinedAllLabels.json`: the merged label set used by most scripts.
- `etherScanLabels.json`: labels scraped from Etherscan metadata.
- `contractAddresses.md` and `contractLabels.md`: the base address list and its labels.
- `contractAddresses2.md` and `contractLabels2.md`: extended address list and its labels.
- `contractsInHistory2Label.md`: historical mapping of contracts to labels.
- `toLabels2_extraPostStudy.md`: extra labels added after the main study.
- `readLabels.py`: loader/helper used by labeling scripts.

## Notes

- If you edit any of the label files, re-run the labeling step before regenerating results.
- The JSON and markdown files are deliberately simple so they can be reviewed or edited by hand.
