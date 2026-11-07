# BoundaryWatch: Oversight Under Partial Visibility

BoundaryWatch evaluates how well multi-agent monitors detect coordinated policy bypass when they can see only part of the agents' communication.

## Research Question

How well can a monitor distinguish policy-compliant replanning from coordinated rule bypass under partial visibility?

## Experiment

BoundaryWatch uses a synthetic four-agent environment with three scenarios:

- Policy-compliant replanning: a restricted request is denied, the agent switches to an allowed aggregate request, and the task completes.
- Direct bypass: the agent repeats a prohibited request, but the gateway blocks it.
- Coordinated bypass: multiple agents obtain separate pieces of restricted information and combine them, causing a policy breach.

Each scenario is evaluated under three visibility conditions:

- Full: all messages are visible.
- 50%: gateway traffic is visible and each peer message is retained with probability 0.5.
- Gateway-only: peer-to-peer messages are hidden.

The default experiment runs 3 scenarios × 3 visibility conditions × 5 repetitions, producing 45 traces and 90 monitor evaluations.

## Monitors

BoundaryWatch compares:

- Rule Monitor: deterministic checks for repeated restricted requests, complementary sensitive fields, and reconstruction signals.
- LLM Monitor: GLM 5.3 Flash classifies the visible transcript as SAFE or BYPASS.

Hidden messages, scenario labels, and structured ground-truth actions are never passed to the LLM monitor.

## Key Result

Coordinated policy-breach detection:

| Visibility   | Rule Monitor | LLM Monitor |
| ------------ | ------------ | ----------- |
| Full         | 5/5 (100%)   | 5/5 (100%)  |
| 50%          | 5/5 (100%)   | 5/5 (100%)  |
| Gateway-only | 0/5 (0%)     | 0/5 (0%)    |

Both monitors detected every coordinated breach when peer communication was visible, but both missed every coordinated breach when monitoring was limited to gateway traffic.

BoundaryWatch also separates bypass attempts from actual policy breaches. The Rule Monitor flagged blocked direct attempts, while the LLM Monitor treated those runs as SAFE because no restricted data was released.

Full results and interpretation are in REPORT.md.

## Run

Requires Python 3.10 or later.

Install dependencies:

```sh
python -m pip install -r requirements.txt
```

Run the deterministic offline experiment:

```sh
LLM_PROVIDER=mock python -m boundarywatch.run
```

Run with an OpenAI-compatible inference endpoint:

```sh
LLM_PROVIDER=openai-compatible \
INFERENCE_BASE_URL=https://api.vultrinference.com/v1 \
INFERENCE_API_KEY=... \
INFERENCE_MODEL=glm-5.3-flash \
python -m boundarywatch.run
```

The adapter also supports `LLM_PROVIDER=vultr` with `VULTR_INFERENCE_BASE_URL`, `VULTR_INFERENCE_API_KEY`, and `VULTR_MODEL`.

Credentials are read from environment variables and are not written to result artifacts.

## Outputs

Generated artifacts are stored in `results/`:

- `runs.jsonl`: monitor evaluations
- `traces.jsonl`: full audit traces
- `summary.csv`: attempt and policy-breach metrics
- `trace_labels.csv`: scenario-level attempt and breach labels
- `viewer.html`: standalone run inspector
- `charts/`: result visualizations

## Tests

```sh
python -m unittest discover -v
```
