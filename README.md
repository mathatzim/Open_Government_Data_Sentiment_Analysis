# NLP Sentiment Modeling on OpenGov.gr (Greek e-Government)

This repository contains the code and supporting files for the MSc project:
**“Natural Language Processing tools in e-Government: Comparative Sentiment Modeling on OpenGov.gr”**.

## Repository purpose
- Scrape and structure public consultation comments from OpenGov.gr.
- Train and benchmark supervised sentiment models (binary **P/N**).
- Compare model performance and export scored outputs.

## Project snapshot
- **Comments in labeled corpus:** 14,953
- **Unique consultations represented:** 57
- **Class distribution:** {'N': 12281, 'P': 2672}
- **Validation split:** 90/10 stratified

## Best validation result (from included metrics)
| Model | Threshold | Accuracy | Macro-F1 | F1 (N) | F1 (P) |
|---|---:|---:|---:|---:|---:|
| Logistic Regression | 0.60 | 0.888 | 0.799 | 0.933 | 0.664 |
| Linear SVM (calibrated) | 0.44 | 0.892 | 0.788 | 0.936 | 0.640 |
| Random Forest | 0.27 | 0.859 | 0.772 | 0.913 | 0.632 |

## Folder structure
```text
.
├─ data/
│  ├─ raw/
│  │  ├─ consultations_index.xlsx
│  │  └─ comments_sample_anonymized.xlsx
│  └─ processed/
├─ docs/
│  └─ Report.docx
├─ notebooks/
├─ outputs/
│  ├─ metrics/
│  │  ├─ validation_metrics.xlsx
│  │  ├─ model_validation_metrics.xlsx
│  │  └─ model_comparison.csv
│  └─ predictions/
│     └─ comments_with_predictions_sample.xlsx
├─ scripts/
│  └─ create_public_sample.py
└─ src/
   ├─ data_collection/
   │  └─ extract_opengov_comments.py
   └─ modeling/
      └─ train_and_evaluate.py
```

## Quick start
### 1) Create environment
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Train + evaluate models
Place the full labeled file as `Comments(1st code).xlsx` in the repository root (or edit paths in `src/modeling/train_and_evaluate.py`), then run:

```bash
python src/modeling/train_and_evaluate.py
```

This script:
- cleans text,
- builds dual TF-IDF features (word 1–2 grams + char 3–5 grams),
- trains Logistic Regression, calibrated Linear SVM, and Random Forest,
- tunes threshold on validation macro-F1,
- writes metrics tables and confusion matrices.

### 3) Scrape comments (collector)
```bash
python src/data_collection/extract_opengov_comments.py
```
