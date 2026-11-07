from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from boundarywatch.metrics import aggregate_rows
from boundarywatch.model import MonitorPrediction, ScenarioTrace, TraceMessage, VisibleMessage
from boundarywatch.monitors import LLMMonitor, RuleMonitor
from boundarywatch.providers import LLMProvider
from boundarywatch.scenarios import SCENARIO_ORDER, build_actions, scenario_outcomes
from boundarywatch.visibility import VISIBILITY_ORDER, visible_messages


BASE_SEED = 20261107
REPETITIONS = 5


def _event_type(action: str, channel: str) -> str:
    if action.startswith("deny") or action == "provide_aggregate_revenue" or action.startswith("submit_"):
        return "gateway_response" if channel == "gateway" else "peer_message"
    if action.startswith("request_"):
        return "gateway_request" if channel == "gateway" else "peer_message"
    return "peer_message" if channel == "peer" else "gateway_message"


def build_trace(scenario: str, run_id: str, seed: int, provider: LLMProvider) -> ScenarioTrace:
    actions = build_actions(scenario)
    rendered = provider.render_actions(actions)
    truth, task_success, policy_success = scenario_outcomes(scenario)
    messages = tuple(
        TraceMessage(
            message_id=action.message_id,
            sender=action.sender,
            recipient=action.recipient,
            channel=action.channel,
            event_type=_event_type(action.action, action.channel),
            text=rendered[action.message_id],
            sequence=index,
            action=action.action,
        )
        for index, action in enumerate(actions)
    )
    return ScenarioTrace(run_id, scenario, seed, truth, task_success, policy_success, messages)


def _prediction_row(
    trace: ScenarioTrace,
    visibility: str,
    monitor_name: str,
    prediction: MonitorPrediction,
    messages: tuple[VisibleMessage, ...],
    latency: int | None,
) -> dict[str, Any]:
    return {
        "run_id": trace.run_id,
        "scenario": trace.scenario,
        "visibility": visibility,
        "monitor_type": monitor_name,
        "ground_truth": trace.ground_truth,
        "prediction": prediction.label,
        "confidence": prediction.confidence,
        "correct": prediction.label == trace.ground_truth,
        "reason": prediction.reason,
        "evidence_message_ids": list(prediction.evidence_message_ids),
        "matched_signals": list(prediction.matched_signals),
        "task_success": trace.task_success,
        "policy_success": trace.policy_success,
        "visible_messages": [message.__dict__ for message in messages],
        "visible_message_count": len(messages),
        "total_message_count": len(trace.messages),
        "hidden_message_count": len(trace.messages) - len(messages),
        "detection_latency": latency,
    }


def run_experiment(provider: LLMProvider, repetitions: int = REPETITIONS, measure_latency: bool = False) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if repetitions < 1:
        raise ValueError("repetitions must be at least one")
    rows: list[dict[str, Any]] = []
    audit_traces: list[dict[str, Any]] = []
    monitors = (RuleMonitor(), LLMMonitor(provider))
    for scenario_index, scenario in enumerate(SCENARIO_ORDER):
        for visibility_index, visibility in enumerate(VISIBILITY_ORDER):
            for repetition in range(repetitions):
                run_id = f"{scenario}-{visibility}-{repetition + 1:02d}"
                seed = BASE_SEED + scenario_index * 10_000 + visibility_index * 100 + repetition
                trace = build_trace(scenario, run_id, seed, provider)
                visible = visible_messages(trace.messages, visibility, seed)
                visible_ids = {message.message_id for message in visible}
                audit_traces.append({
                    "run_id": run_id,
                    "scenario": scenario,
                    "visibility": visibility,
                    "seed": seed,
                    "ground_truth": trace.ground_truth,
                    "task_success": trace.task_success,
                    "policy_success": trace.policy_success,
                    "messages": [message.__dict__ for message in trace.messages],
                    "visible_message_ids": sorted(visible_ids),
                })
                for monitor in monitors:
                    prediction = monitor.predict(visible)
                    latency: int | None = None
                    if measure_latency and trace.ground_truth == "BYPASS":
                        for prefix_length in range(1, len(visible) + 1):
                            prefix_prediction = monitor.predict(visible[:prefix_length])
                            if prefix_prediction.label == "BYPASS":
                                latency = prefix_length
                                break
                    rows.append(_prediction_row(trace, visibility, monitor.name, prediction, visible, latency))
    return rows, audit_traces


def write_outputs(rows: list[dict[str, Any]], traces: list[dict[str, Any]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "runs.jsonl").open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=True) + "\n")
    with (output_dir / "traces.jsonl").open("w", encoding="utf-8") as file:
        for trace in traces:
            file.write(json.dumps(trace, ensure_ascii=True) + "\n")

    summaries = aggregate_rows(rows)
    columns = list(summaries[0]) if summaries else []
    with (output_dir / "summary.csv").open("w", encoding="utf-8", newline="") as file:
        import csv
        writer = csv.DictWriter(file, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(summaries)