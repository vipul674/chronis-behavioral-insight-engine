import argparse
import sys

from src.loader import load_data
from src.patterns import discover_patterns
from src.anomalies import detect_anomalies
from src.insights import generate_insights
from src.reporting import (
    save_insights,
    save_anomalies,
    save_assessment_summary,
    save_summary_md,
)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Chronis Behavioral Insight Engine")
    parser.add_argument(
        "--input",
        default="data/Chronis_TaskA_Synthetic_Behavioral_Data_v2-2.csv",
        help="Path to the input CSV file",
    )
    parser.add_argument(
        "--output",
        default="results",
        help="Directory to write output files",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    print("Chronis Behavioral Insight Engine")
    print("=" * 40)

    df = load_data(args.input)
    print(f"Loaded {len(df)} rows for {df['user_id'].nunique()} users.")

    patterns = discover_patterns(df)
    print(f"Discovered {len(patterns)} patterns.")

    anomalies = detect_anomalies(df)
    print(f"Detected {len(anomalies)} anomalies.")

    insights = generate_insights(df, patterns, anomalies)
    claims = [i for i in insights if i.status == "claim"]
    abstentions = [i for i in insights if i.status == "abstain"]
    print(f"Generated {len(claims)} claims and {len(abstentions)} abstentions.")

    save_insights(insights, args.output)
    save_anomalies(anomalies, args.output)
    save_assessment_summary(insights, anomalies, args.output)
    save_summary_md(insights, anomalies, df, args.output)

    print(f"\nResults written to {args.output}/")
    print(f"  - insights.json ({len(insights)} entries)")
    print(f"  - anomalies.json ({len(anomalies)} entries)")
    print(f"  - assessment_summary.json")
    print(f"  - summary.md")


if __name__ == "__main__":
    main()
