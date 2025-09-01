import argparse
from .utils import setup_docker, apply_patch, get_logs
from .agent import Agent
from .evaluate import run_swe_eval
from prompts.improve import DIAGNOSE_PROMPT, IMPROVE_PROMPT
import os
import json

def validate_patch(patch_content: str) -> bool:
    """Validate that a patch has proper format and context."""
    if not patch_content.strip():
        return False
    lines = patch_content.split('\n')
    has_diff_header = any(line.startswith('diff --git') for line in lines)
    has_hunk = any(line.startswith('@@') for line in lines)
    has_file_markers = any(line.startswith('---') for line in lines) and \
                       any(line.startswith('+++') for line in lines)
    return has_diff_header and has_hunk and has_file_markers



def self_improve(entry: str, model: str) -> None:
    """Perform self-improvement on a SWE-bench entry."""
    agent = Agent(model)

    # Step 1: Eval current code
    os.makedirs("output/baseline", exist_ok=True)
    with open("current_patch.diff", "w") as f:
        f.write("")  # Empty initial patch for baseline
    eval_results = run_swe_eval("current_patch.diff", "baseline", num_evals=10)
    logs = get_logs(eval_results)

    print("Logs: ", logs)

    # Step 2: Diagnose
    diagnose_prompt = DIAGNOSE_PROMPT.format(entry=entry, logs=logs)
    problem = agent.chat(diagnose_prompt)

    # Step 3: Improve
    improve_prompt = IMPROVE_PROMPT.format(problem=problem)
    new_code = agent.chat(improve_prompt)  # Assume outputs patch
    
    # Validate patch format before saving
    if not validate_patch(new_code):
        print("Warning: Generated patch failed validation. Attempting to continue...")
        # Log the invalid patch for debugging
        with open("invalid_patch.diff", "w") as f:
            f.write(new_code)

    # Save new patch
    with open("new_patch.diff", "w") as f:
        f.write(new_code)

    # Apply in Docker
    container = setup_docker()
    apply_patch(container, new_code)
    container.stop()
    container.remove()

    # Step 4: Re-eval
    new_results = run_swe_eval("new_patch.diff", "improved", num_evals=10)
    print(json.dumps(new_results, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--entry", required=True, help="SWE-bench entry ID")
    parser.add_argument("--model", default="gpt-4o")
    args = parser.parse_args()
    self_improve(args.entry, args.model)
