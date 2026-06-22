# Project Plan: VAPT Markdown Note Enhancement (Adjusted)

## Objectives
Enhance 2,000+ markdown files in the VAPT repository in ascending order of their size.

## Phase 1: Environment & Tooling Verification (Milestone 1) - [DONE]
- **Objective**: Identify if there are offline LLM command-line tools, local model endpoints, and create verification scripts.
- **Steps**:
  1. Check for local LLM tools (none found, must use subagent LLM contexts directly).
  2. Create verification script `verify_enhancement.py` (completed by worker_1).
  3. Establish baseline verification status (0% pass rate).

## Phase 2: Pilot Batch & Git Integration (Milestone 2) - [IN PROGRESS]
- **Objective**: Test the enhancement, verification, and git-commit pipeline on a small pilot batch of 10 files.
- **Steps**:
  1. Identify the 10 smallest files from `file_stats.md`.
  2. Spawn a worker to generate the enhanced contents for these 10 files.
  3. The worker writes a Python script `process_pilot.py` which contains the pre-generated contents, writes each file, verifies it via `verify_enhancement.py`, and commits it individually to git (with retry logic to prevent locks).
  4. Run and verify the results of the pilot batch.

## Phase 3: Scaling & Concurrent Processing (Milestone 3)
- **Objective**: Process all remaining files concurrently using multiple parallel workers.
- **Steps**:
  1. Sort all unprocessed files from `file_stats.md` in ascending size order.
  2. Partition the files into distinct, non-overlapping batches (e.g., 5-10 files per batch).
  3. Spawn multiple concurrent workers in parallel (up to 4-5 at a time) to process distinct batches.
  4. Guidelines for workers:
     - As files are expanded, explicitly add "Beginner" level explanations, use cases, and categories (along with the required sections).
     - If opportunity arises to create new beginner-level markdown files to balance the advanced content, they must do so.
  5. Each worker follows the same pattern: generates the enhanced content, writes a batch processing script, and executes it. The script writes, validates, and commits each file to git individually.
  6. Use a file-based lock or retry logic in the git commit step of the batch processing scripts to prevent concurrent commit conflicts (index.lock issues).
  7. Execute the orchestrator succession protocol when spawn counts approach 16 to clear parent/successor memory and manage resources.

## Phase 4: Final Validation & Victory Audit (Milestone 4)
- **Objective**: Verify complete repository compliance.
- **Steps**:
  1. Run the full `verify_enhancement.py` script on all 2,000+ files to ensure 100% compliance.
  2. Spawn an evaluation agent as a judge to review a random sample of 10 enhanced files.
  3. Spawn the Forensic Auditor (`teamwork_preview_auditor`) to perform integrity forensics.
  4. Compile final results and report to the user/Sentinel.
