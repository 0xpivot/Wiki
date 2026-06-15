# Project Context & Requirements

## Objectives
- Enhance over 2,000 markdown files in the VAPT repository.
- Each enhanced file must contain:
  - Detailed explanations of the topic
  - Practical use cases
  - Comprehensive lists of all relevant commands
  - Sample outputs
- Maintain existing structure and formatting.
- Overwrite original markdown files in-place.
- Process files in ascending order of their size (smallest files first), using `/home/sanchit/.gemini/antigravity-cli/brain/77399aa3-cb2f-4b0e-8289-c2d532a5d414/file_stats.md` as the baseline.
- Ensure strict quality control (no redundant or filler content).

## Acceptance Criteria
- **Programmatic Verification**:
  - A verification script runs and confirms that every `.md` file contains the required sections ("Use Cases", "Commands", "Sample Output").
  - A script verifies that the newly expanded files have significantly increased in size relative to the baseline without losing original content.
- **Agent-as-Judge Verification**:
  - An independent evaluation agent reviews a random sample of 10 enhanced files and passes them based on a grading rubric checking for explanation depth, structural integrity, usefulness of sample outputs, and absence of generic filler content.

## Environment Details
- **OS**: Linux
- **Workspace Directory**: `/home/sanchit/Notes/VAPT`
- **Metadata Folder**: `/home/sanchit/Notes/VAPT/.agents/orchestrator`
- **Network Mode**: `CODE_ONLY` (no internet access, no external HTTP clients targeting external URLs).
- **Subagent Limit**: 128 total spawns.
- **Succession Limit**: 16 spawns per orchestrator generation.

## Key Constraints
- Never write, modify, or create source code files directly.
- Never run build/test commands yourself — require workers to do so.
- File-editing tools can only be used for metadata/state files (.md) in your `.agents/` folder.
- Never reuse a subagent after it has delivered its handoff — always spawn fresh.
