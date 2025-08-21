# Diagnosis prompt template
DIAGNOSE_PROMPT = (
    "You are an expert software engineer and debugger. Analyze the evaluation logs and propose the minimal fix.\n"
    "\n"
    "ENTRY: {entry}\n"
    "EVAL_LOGS (JSON):\n{logs}\n"
    "\n"
    "Output the following sections ONLY (no extra commentary):\n"
    "- PROBLEM: One-sentence root cause in plain English.\n"
    "- EVIDENCE: 2-5 bullet points quoting key log lines (tests, tracebacks, assertions).\n"
    "- FIX_PLAN: 2-6 ordered steps describing minimal code edits; include file paths and where to change.\n"
    "- PATCH_SCOPE: List the exact files that will be touched (tests included if needed).\n"
)

# Improvement prompt template
IMPROVE_PROMPT = (
    "You will now implement the fix as a unified diff.\n"
    "\n"
    "Problem to fix:\n{problem}\n"
    "\n"
    "Requirements:\n"
    "- Output ONLY a valid unified diff, no explanations or markdown fences.\n"
    "- Start each file change with 'diff --git a/<path> b/<path>' and include '---', '+++' and '@@' hunks.\n"
    "- Paths must be relative to the repo root. Use 'a/' and 'b/' prefixes.\n"
    "- Keep the patch minimal and self-contained. Do not refactor unrelated code.\n"
    "- If adding a new file, use '--- /dev/null' and '+++ b/<path>'.\n"
    "- If tests are required, include them in the same patch (e.g., under tests/).\n"
    "- Ensure the patch can be applied with 'git apply -p0' in /app and is syntactically correct.\n"
    "- Do NOT include tool calls, reasoning text, or any content outside of the diff.\n"
)