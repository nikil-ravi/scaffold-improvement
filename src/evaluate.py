import argparse
import json
import os
import sys
import tempfile
from typing import Dict, List

if sys.version_info < (3, 10):  # pragma: no cover
    raise RuntimeError(
        "The SWE-bench harness requires Python 3.10 or newer; "
        f"current version: {sys.version_info.major}.{sys.version_info.minor}"
    )

from swebench.harness.run_evaluation import main as run_harness
try:  # support running as a script
    from .utils import safe_log
except ImportError:  # pragma: no cover
    from utils import safe_log


def run_swe_eval(
    patch_path: str,
    model_name: str,
    subset: str = "small",
    num_evals: int = 10,
    max_workers: int = 5,
) -> Dict:
    """Run the official SWE-bench evaluation harness for a patch.

    Parameters
    ----------
    patch_path: str
        Path to a Git patch file.
    model_name: str
        Identifier for the current model/run.
    subset: str
        Name of JSON file listing instance IDs (e.g., "small").
    num_evals: int
        Number of instances from the subset to evaluate.
    max_workers: int
        Number of parallel workers for the harness.
    """

    with open(patch_path, "r", encoding="utf-8") as f:
        patch = f.read()

    subset_file = subset if subset.endswith(".json") else f"{subset}.json"
    with open(subset_file, "r", encoding="utf-8") as f:
        all_tasks: List[str] = json.load(f)
    tasks = all_tasks[:num_evals]

    predictions = [
        {
            "instance_id": t,
            "model_name_or_path": model_name,
            "model_patch": patch,
        }
        for t in tasks
    ]
    tmp_preds = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(predictions, tmp_preds)
    tmp_preds.close()

    output_dir = os.path.join("output", model_name)
    os.makedirs(output_dir, exist_ok=True)

    report_path = run_harness(
        dataset_name="SWE-bench/SWE-bench",
        split="test",
        instance_ids=tasks,
        predictions_path=tmp_preds.name,
        max_workers=max_workers,
        force_rebuild=False,
        cache_level="none",
        clean=False,
        open_file_limit=4096,
        run_id=model_name,
        timeout=7200,
        namespace=None,
        rewrite_reports=False,
        modal=False,
        instance_image_tag="latest",
        report_dir=output_dir,
    )

    with open(report_path, "r", encoding="utf-8") as f:
        results: Dict = json.load(f)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run SWE-bench evaluation")
    parser.add_argument("--patch_path", required=True, help="Path to patch file")
    parser.add_argument("--model_name", required=True, help="Model name for run")
    parser.add_argument(
        "--subset",
        default="small",
        choices=["small", "medium", "big"],
        help="SWE-bench subset to evaluate",
    )
    parser.add_argument("--num_evals", type=int, default=10, help="Number of evaluations")
    parser.add_argument("--max_workers", type=int, default=5, help="Max parallel workers")
    args = parser.parse_args()

    results = run_swe_eval(
        args.patch_path,
        args.model_name,
        args.subset,
        args.num_evals,
        args.max_workers,
    )
    safe_log(json.dumps(results, indent=2))
