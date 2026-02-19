# -*- coding: utf-8 -*-
"""
Created on Sun Nov 16 21:44:11 2025

@author: mathaios
"""

import re
import numpy as np
import pandas as pd
from scipy.sparse import hstack
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix,
    accuracy_score, f1_score
)

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap

# ============ FILES ============
INPUT_XLSX  = "Comments(1st code).xlsx"   # change if needed
OUTPUT_XLSX = "Comments_scored.xlsx"
METRICS_XLSX = "validation_metrics.xlsx"

# ============ COLUMN RESOLUTION ============
POSSIBLE_TEXT_COLS  = ["Comment_Text", "Comment", "Text", "Comment text", "comment_text"]
POSSIBLE_LABEL_COLS = ["Comment_Sentiment", "Comment sentiment", "Sentiment", "Label", "Actual_Sentiment"]

def _norm(s: str) -> str:
    return re.sub(r"[ _\-]+", "", s.strip().lower())

def resolve_col(possible, df_cols):
    norm_map = {_norm(c): c for c in df_cols}
    for name in possible:
        n = _norm(name)
        if n in norm_map:
            return norm_map[n]
    raise ValueError(f"Could not find any of {possible} in columns: {list(df_cols)}")

# ============ LOAD ============
df = pd.read_excel(INPUT_XLSX)
text_col  = resolve_col(POSSIBLE_TEXT_COLS,  df.columns)
label_col = resolve_col(POSSIBLE_LABEL_COLS, df.columns)
print(f"Using text column:  {text_col}")
print(f"Using label column: {label_col}")

# ============ CLEAN TEXT ============
def clean_text(s: str) -> str:
    if not isinstance(s, str):
        return ""
    t = s.strip()
    t = re.sub(r"https?://\S+|www\.\S+", " ", t)  # URLs
    t = re.sub(r"\s+", " ", t)                    # collapse whitespace
    return t.lower()

df["_clean"] = df[text_col].astype(str).apply(clean_text)

# ============ LABELS: expect only P/N; others => unlabeled ============
def normalize_bin(lbl):
    if pd.isna(lbl): return np.nan
    s = str(lbl).strip().upper()
    if s in {"P", "N"}: return s
    return np.nan

df["_label_bin"] = df[label_col].apply(normalize_bin)
print("\nLabel distribution (raw):")
print(df[label_col].astype(str).str.upper().value_counts(dropna=False))

labeled_mask = df["_label_bin"].notna()
df_l = df.loc[labeled_mask].copy()
if df_l.empty or df_l["_label_bin"].nunique() < 2:
    raise RuntimeError("Need labeled rows with both 'P' and 'N' to train.")

# ============ TRAIN/VAL SPLIT ============
X_text = df_l["_clean"].values
y       = df_l["_label_bin"].map({"N":0, "P":1}).values
X_tr_txt, X_va_txt, y_tr, y_va = train_test_split(
    X_text, y, test_size=0.1, random_state=42, stratify=y
)

# ============ TF-IDF FEATURES (shared across models) ============
tfidf_word = TfidfVectorizer(analyzer="word", ngram_range=(1,2), min_df=2, max_features=100_000)
tfidf_char = TfidfVectorizer(analyzer="char", ngram_range=(3,5), min_df=2, max_features=50_000)

X_tr = hstack([tfidf_word.fit_transform(X_tr_txt),
               tfidf_char.fit_transform(X_tr_txt)]).tocsr()
X_va = hstack([tfidf_word.transform(X_va_txt),
               tfidf_char.transform(X_va_txt)]).tocsr()

# ============ HELPERS ============
def tune_threshold(proba, y_true):
    # scan thresholds to maximize macro-F1
    best_t, best_f1 = 0.5, -1.0
    for i in range(20, 81):  # 0.20..0.80
        t = i / 100.0
        yhat = (proba >= t).astype(int)
        f1 = f1_score(y_true, yhat, average="macro")
        if f1 > best_f1:
            best_f1, best_t = f1, t
    return best_t, best_f1

def evaluate_model(name, proba, y_true):
    t, _ = tune_threshold(proba, y_true)
    yhat = (proba >= t).astype(int)
    acc  = accuracy_score(y_true, yhat)
    macf = f1_score(y_true, yhat, average="macro")
    cm   = confusion_matrix(y_true, yhat, labels=[0,1])
    # report as dict for tables
    rep  = classification_report(y_true, yhat, target_names=["N","P"], output_dict=True)
    print(f"\n=== {name} ===")
    print(f"Chosen threshold: {t:.2f}")
    print(f"Accuracy: {acc:.3f} | Macro-F1: {macf:.3f}")
    print("Confusion Matrix:\n", cm)
    print("Classification Report:\n", classification_report(y_true, yhat, target_names=["N","P"]))
    return {"name": name, "threshold": t, "macro_f1": macf, "acc": acc, "cm": cm, "report": rep}

# nice white→light-blue colormap
white_to_blue = LinearSegmentedColormap.from_list("white_to_blue", ["#ffffff", "#cfe8ff", "#7fb3ff", "#3d8bff"])

def save_cm_heatmap(cm, title, fname):
    plt.figure(figsize=(4.2, 3.8))
    sns.heatmap(cm, annot=True, fmt="d", cmap=white_to_blue, cbar=True,
                xticklabels=["Pred N","Pred P"], yticklabels=["True N","True P"])
    plt.title(title)
    plt.tight_layout()
    plt.savefig(fname, dpi=200, bbox_inches="tight")
    plt.close()

def report_to_df(report_dict, accuracy_value):
    # Convert classification_report dict to a tidy DataFrame + accuracy row
    df_rep = pd.DataFrame(report_dict).T[["precision","recall","f1-score","support"]]
    # Ensure consistent order if present
    desired = [r for r in ["N","P","macro avg","weighted avg"] if r in df_rep.index]
    df_rep = df_rep.loc[desired]
    # Append accuracy as a single-row table
    acc_df = pd.DataFrame({"precision":[np.nan], "recall":[np.nan], "f1-score":[accuracy_value], "support":[df_rep["support"].sum()]}, index=["accuracy"])
    return pd.concat([df_rep, acc_df], axis=0)

# ============ MODEL 1: LOGISTIC REGRESSION ============
logreg = LogisticRegression(max_iter=4000, class_weight="balanced", solver="liblinear", random_state=42)
logreg.fit(X_tr, y_tr)
proba_lr = logreg.predict_proba(X_va)[:, 1]
res_lr = evaluate_model("LogisticRegression", proba_lr, y_va)
save_cm_heatmap(res_lr["cm"], "Logistic Regression — Confusion Matrix", "cm_logreg.png")

# ============ MODEL 2: LINEAR SVM (CALIBRATED) ============
svm_raw = LinearSVC(C=1.0, class_weight="balanced", random_state=42)
svm = CalibratedClassifierCV(svm_raw, method="sigmoid", cv=3)  # gives predict_proba
svm.fit(X_tr, y_tr)
proba_svm = svm.predict_proba(X_va)[:, 1]
res_svm = evaluate_model("LinearSVM (calibrated)", proba_svm, y_va)
save_cm_heatmap(res_svm["cm"], "Linear SVM (calibrated) — Confusion Matrix", "cm_svm.png")

# ============ MODEL 3: RANDOM FOREST ============
rf = RandomForestClassifier(
    n_estimators=300,
    max_depth=None,
    max_features="sqrt",
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)
rf.fit(X_tr, y_tr)
proba_rf = rf.predict_proba(X_va)[:, 1]
res_rf = evaluate_model("RandomForest", proba_rf, y_va)
save_cm_heatmap(res_rf["cm"], "Random Forest — Confusion Matrix", "cm_rf.png")

# ============ BUILD & SAVE TABLES ============
results = [res_lr, res_svm, res_rf]

# Per-model metrics sheets + confusion matrices as tables
with pd.ExcelWriter(METRICS_XLSX, engine="openpyxl") as writer:
    comp_rows = []
    for res in results:
        # metrics table
        df_metrics = report_to_df(res["report"], res["acc"])
        df_metrics.to_excel(writer, sheet_name=res["name"][:31])  # Excel sheet name limit
        # confusion matrix as a 2x2 table
        df_cm = pd.DataFrame(res["cm"], index=["True N","True P"], columns=["Pred N","Pred P"])
        df_cm.to_excel(writer, sheet_name=(res["name"][:27] + " CM"))
        # collect comparison row
        comp_rows.append({
            "Model": res["name"],
            "Threshold": round(res["threshold"], 2),
            "Accuracy": round(res["acc"], 3),
            "Macro-F1": round(res["macro_f1"], 3),
            "F1 (N)": round(res["report"]["N"]["f1-score"], 3) if "N" in res["report"] else np.nan,
            "F1 (P)": round(res["report"]["P"]["f1-score"], 3) if "P" in res["report"] else np.nan,
            "Precision (P)": round(res["report"]["P"]["precision"], 3) if "P" in res["report"] else np.nan,
            "Recall (P)": round(res["report"]["P"]["recall"], 3) if "P" in res["report"] else np.nan,
        })
    pd.DataFrame(comp_rows).to_excel(writer, sheet_name="Comparison", index=False)

print(f"\nSaved validation tables ➜ {METRICS_XLSX}")
print("Saved CM images: cm_logreg.png, cm_svm.png, cm_rf.png")

# ============ PICK BEST BY MACRO-F1 ============
best = max(results, key=lambda r: r["macro_f1"])
print(f"\n>>> Best model: {best['name']} (Macro-F1={best['macro_f1']:.3f}, thr={best['threshold']:.2f})")

# ============ RETRAIN BEST ON ALL LABELED, THEN SCORE UNLABELED ============
# Refit vectorizers on ALL labeled text
tfidf_word_full = TfidfVectorizer(analyzer="word", ngram_range=(1,2), min_df=2, max_features=100_000)
tfidf_char_full = TfidfVectorizer(analyzer="char", ngram_range=(3,5), min_df=2, max_features=50_000)
X_all_l = hstack([
    tfidf_word_full.fit_transform(df_l["_clean"].values),
    tfidf_char_full.fit_transform(df_l["_clean"].values)
]).tocsr()
y_all_l = df_l["_label_bin"].map({"N":0, "P":1}).values

def build_model(name):
    if name == "LogisticRegression":
        m = LogisticRegression(max_iter=4000, class_weight="balanced", solver="liblinear", random_state=42)
    elif name == "LinearSVM (calibrated)":
        m = CalibratedClassifierCV(LinearSVC(C=1.0, class_weight="balanced", random_state=42),
                                   method="sigmoid", cv=3)
    elif name == "RandomForest":
        m = RandomForestClassifier(
            n_estimators=300, max_depth=None, max_features="sqrt",
            class_weight="balanced", random_state=42, n_jobs=-1
        )
    else:
        raise ValueError(name)
    return m

best_model = build_model(best["name"])
best_model.fit(X_all_l, y_all_l)
best_thr = best["threshold"]

# Predict unlabeled rows (if any)
unlabeled_mask = df["_label_bin"].isna()
if unlabeled_mask.any():
    Xu = hstack([
        tfidf_word_full.transform(df.loc[unlabeled_mask, "_clean"].values),
        tfidf_char_full.transform(df.loc[unlabeled_mask, "_clean"].values)
    ]).tocsr()

    if hasattr(best_model, "predict_proba"):
        pu = best_model.predict_proba(Xu)[:, 1]
    else:
        pu = best_model.decision_function(Xu)
        pu = 1 / (1 + np.exp(-pu))  # sigmoid

    yu = np.where(pu >= best_thr, "P", "N")
    df.loc[unlabeled_mask, label_col] = yu
    print(f"\nFilled {unlabeled_mask.sum()} previously unlabeled rows using {best['name']} (thr={best_thr:.2f}).")
else:
    print("\nNo unlabeled rows detected—nothing to fill.")

# ============ SAVE ============
to_save = df.drop(columns=[c for c in df.columns if c.startswith("_")], errors="ignore")
to_save.to_excel(OUTPUT_XLSX, index=False)
print(f"\nSaved scored file ➜ {OUTPUT_XLSX}")
print("\nFinal sentiment distribution in saved file:")
print(to_save[label_col].value_counts(dropna=False))