# Project: VAPT Notes Enhancement (Adjusted)

## Architecture
- The project involves modifying in-place 2,158 markdown files in the VAPT repository.
- The files are organized in an Obsidian vault across 15 domain subdirectories.
- A programmatic verification script `verify_enhancement.py` validates file enhancements.
- Multiple concurrent worker subagents will process files in parallel batches, sorted in ascending order of file size using `file_stats.md` as the baseline.
- For each file, the worker must:
  1. Generate enhanced content.
  2. Overwrite the file in-place.
  3. Verify the file using `verify_enhancement.py`.
  4. Commit the file individually to git (with retry logic to handle concurrent locks).

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Environment Inspection & Tooling | Identify local LLM availability and build verification script | None | DONE |
| 2 | Pilot Batch & Git Integration | Enhance and verify a pilot batch of 10 smallest files, committing each individually to git | M1 | DONE |
| 3 | Concurrent Mass Processing | Process all remaining files in parallel size-sorted batches with individual commits | M2 | IN_PROGRESS |
| 4 | Final Verification & Audit | Run verification script, evaluation agent, and Forensic Audit | M3 | PLANNED |

## Code Layout
- `.agents/orchestrator/` — Orchestrator planning and progress metadata.
- `verify_enhancement.py` — Verification script for checking enhanced markdown files.
- Domain folders (e.g., `Network Security`, `Active Directory`, etc.) — Location of the markdown notes to be enhanced.
