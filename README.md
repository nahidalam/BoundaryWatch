# BoundaryWatch: Oversight Under Partial Visibility

Multi-agent evaluation for distinguishing safe adaptation from direct or coordinated policy bypass under partial message visibility.

## Run

Requires Python 3.10 or later.

Install Matplotlib:

```sh
python -m pip install -r requirements.txt
```

Run the offline experiment with the mock provider:

```sh
LLM_PROVIDER=mock python -m boundarywatch.run
```

The default experiment runs 3 scenarios x 3 visibility conditions x 5 repetitions (45 traces, 90 monitor evaluations). Use `--repetitions 1` for a quick smoke run and `--latency` to evaluate visible-message prefixes for detection latency.

Outputs are written to `results/`: `runs.jsonl` contains monitor evaluations, `traces.jsonl` keeps the full audit traces separate from monitor inputs, `summary.csv` contains grouped metrics, and `viewer.html` is a standalone run inspector. Charts are in `results/charts/`; the measured report is `REPORT.md`.

## Providers

`LLM_PROVIDER=mock` is the deterministic, fully offline default. The provider interface can also use any OpenAI-compatible chat-completions endpoint:

```sh
LLM_PROVIDER=openai-compatible \
INFERENCE_BASE_URL=https://api.vultrinference.com/v1 \
INFERENCE_API_KEY=... \
INFERENCE_MODEL=glm-5.3-flash \
python -m boundarywatch.run
```

The adapter also accepts `LLM_PROVIDER=vultr` with `VULTR_INFERENCE_BASE_URL`, `VULTR_INFERENCE_API_KEY`, and `VULTR_MODEL`. Credentials are read from the environment and never written to result artifacts. Both message rendering and LLM monitoring use the selected provider; rule monitoring and metric calculations do not.

## Tests

```sh
python -m unittest discover -v
```