# Self-Improver Agent Benchmark
A simple repo for LLM-based self-improvement of code agents, evaluated on SWE-bench.
## Setup
Set env vars: `export ANTHROPIC_API_KEY=...` or `OPENAI_API_KEY=...`.
Build Docker: `docker build -t self-improve-agent .`.
Run container: `docker run -it -v $(pwd):/app self-improve-agent`.
## Usage
Self-improve and eval: `python src/self_improve.py --entry django__django-XXXX --model claude-3-5-sonnet-20240620`.
Eval only: `python src/evaluate.py --patch_path model_patch.diff --model_name test_model`.
Uses SWE-bench subsets (small/medium/big) for evaluation with the official harness.


# The full pipeline involves:
1. Baseline Evaluation (run_swe_eval in src/evaluate.py):

- Creates an empty `current_patch.diff` for the baseline run.
- Invokes the SWE-bench evaluation harness on the first 10 instances listed in `small.json` (or other subset files).
- Produces a real evaluation report saved under `output/<model_name>/`.


2. Diagnosis (Agent.chat in src/agent.py):

- Uses an LLM (e.g., claude-3-5-sonnet-20240620) to analyze evaluation logs.
- Applies DIAGNOSE_PROMPT from prompts/improve.py to generate a problem statement describing issues (e.g., why a task failed).


3. Improvement (Agent.chat in src/agent.py):

- Uses the LLM with IMPROVE_PROMPT to generate a Git patch addressing the diagnosed problem.
- Ensures patches are valid (correct diff format, existing files, no trailing whitespace).
- Saves the patch to new_patch.diff.

4. Re-evaluation (run_swe_eval in src/evaluate.py):

- Runs the harness again with the generated patch on the same SWE-bench instances.
- Saves results to `output/<model_name>/` and logs them.
