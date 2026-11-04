# Screenshot inventory

All **11 original Workato screenshots** are included in this package, organized with short consistent file names. Links are already embedded in the root and case-study READMEs; no separate Markdown paste is required.

## 01 — API consolidation (7 screenshots)

| Filename | Evidence |
|---|---|
| `01-http-baseline-top.png` | Baseline beginning: scheduler, HTTP, IF and retry handling |
| `02-http-baseline-middle.png` | Baseline middle: monitoring and HTTP actions |
| `03-http-baseline-lower-middle.png` | Baseline additional monitoring branches |
| `04-http-baseline-bottom.png` | Baseline ending |
| `05-python-optimized.png` | Optimized one-action Python recipe |
| `06-http-job-result.png` | Successful baseline job: 5 tasks, 910 ms |
| `07-python-job-result.png` | Successful optimized job: 1 task, 897 ms |

## 02 — Native formula (4 screenshots)

| Filename | Evidence |
|---|---|
| `01-python-baseline.png` | Baseline: two Python actions |
| `02-native-formula-optimized.png` | Optimized: one Python action with `.to_json.encode_base64` formula |
| `03-python-encoding-result.png` | Baseline encoder output |
| `04-native-encoding-input.png` | Formula-generated encoded input to optimized decoder |

The Base64 example screenshots do not establish the final decoder output or exact billed task difference; those are future test evidence.

## Publication safety

The screenshots show a personal Workato development workspace, recipe and job metadata, sample test data, and example outputs. Before publishing publicly, verify the workspace identifiers, URLs, and job identifiers are appropriate to share. No passwords or API keys were apparent in these screenshots, but that is not a guarantee that other project artifacts are free of secrets.

## GitHub

Upload everything **inside** this `02-recipe-optimization` folder into `projects/02-recipe-optimization/` of the existing portfolio repository. Avoid creating `projects/02-recipe-optimization/02-recipe-optimization/`.
