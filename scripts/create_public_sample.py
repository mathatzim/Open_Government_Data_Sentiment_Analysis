"""Create an anonymized public sample from the full comments file.

Usage:
    python scripts/create_public_sample.py --input "Comments(1st code).xlsx" --output "data/raw/comments_sample_anonymized.xlsx"
"""

import argparse
import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-per-class", type=int, default=500)
    args = parser.parse_args()

    df = pd.read_excel(args.input)
    if "User_Name" in df.columns:
        df["User_Name"] = "ANONYMIZED"

    if "Comment_Sentiment" in df.columns:
        parts = []
        for _, grp in df.groupby("Comment_Sentiment", dropna=False):
            parts.append(grp.head(args.max_per_class))
        out = pd.concat(parts).reset_index(drop=True)
    else:
        out = df.head(args.max_per_class * 2)

    out.to_excel(args.output, index=False)
    print(f"Saved: {args.output} ({len(out)} rows)")


if __name__ == "__main__":
    main()
