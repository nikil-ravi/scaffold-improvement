import argparse
from typing import Optional
from .utils import setup_docker, apply_patch, get_logs
from .agent import Agent
from .evaluate import run_swe_eval
from prompts.improve import DIAGNOSE_PROMPT, IMPROVE_PROMPT
import os
import json


def self_improve(entry: str, model: str) -> None:
    """Perform self-improvement on a SWE-bench entry."""
    agent = Agent(model)

    # Step 1: Eval current code
    os.makedirs("output/baseline", exist_ok=True)
    with open("current_patch.diff", "w") as f:
        f.write("")  # Empty initial patch for baseline
    eval_results = run_swe_eval("current_patch.diff", "baseline")
    logs = get_logs(eval_results)

    print("Logs: ", logs)

    # Step 2: Diagnose
    diagnose_prompt = DIAGNOSE_PROMPT.format(entry=entry, logs=logs)
    problem = agent.chat(diagnose_prompt)

    # Step 3: Improve
    improve_prompt = IMPROVE_PROMPT.format(problem=problem)
    new_code = agent.chat(improve_prompt)  # Assume outputs patch

    # Save new patch
    with open("new_patch.diff", "w") as f:
        f.write(new_code)

    # Apply in Docker
    container = setup_docker()
    apply_patch(container, new_code)
    container.stop()
    container.remove()

    # Step 4: Re-eval
    new_results = run_swe_eval("new_patch.diff", "improved")
    print(json.dumps(new_results, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--entry", required=True, help="SWE-bench entry ID")
    parser.add_argument("--model", default="gpt-4o")
    args = parser.parse_args()
    self_improve(args.entry, args.model)
