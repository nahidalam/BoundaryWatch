from __future__ import annotations

import argparse
import os
from pathlib import Path

from boundarywatch.artifacts import generate_charts, generate_report, generate_viewer
from boundarywatch.experiment import REPETITIONS, run_experiment, write_outputs
from boundarywatch.providers import provider_from_env


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the BoundaryWatch partial-visibility evaluation.")
    parser.add_argument("--repetitions", type=int, default=REPETITIONS, help="runs per scenario/visibility cell (default: 5)")
    parser.add_argument("--latency", action="store_true", help="measure first correct BYPASS prediction over visible-message prefixes")
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    args = parser.parse_args()
    provider = provider_from_env()
    provider_name = os.environ.get("LLM_PROVIDER", "mock").strip().lower()
    rows, traces = run_experiment(provider, repetitions=args.repetitions, measure_latency=args.latency)
    write_outputs(rows, traces, args.output_dir)
    chart_paths = generate_charts(rows, args.output_dir)
    report_path = generate_report(rows, args.repetitions, provider_name, args.output_dir, getattr(provider, "model", None))
    viewer_path = generate_viewer(rows, traces, args.output_dir)
    print(f"Completed {len(traces)} traces and {len(rows)} monitor evaluations using {provider_name}.")
    print(f"Summary: {args.output_dir / 'summary.csv'}")
    print(f"Report: {report_path}")
    print(f"Viewer: {viewer_path}")
    for path in chart_paths:
        print(f"Chart: {path}")


if __name__ == "__main__":
    main()