# Original User Request

## Initial Request — 2026-06-15T23:30:19+05:30

# Teamwork Project Prompt — Draft

> Status: Launched
> Goal: Craft prompt → get user approval → delegate to teamwork_preview

Enhance over 2,000 markdown files in the VAPT repository by adding detailed explanations, preserving existing structure, adding practical use cases, and including comprehensive command lists with sample outputs.

Working directory: /home/sanchit/Notes/VAPT
Integrity mode: demo

## Requirements

### R1. Content Enhancement
Every markdown file must be expanded to include detailed explanations, practical use cases, comprehensive lists of all relevant commands, and sample outputs. The existing structure and formatting must be maintained.

### R2. In-Place Modification
The original markdown files must be overwritten in-place with the newly enhanced content.

### R3. Processing Order & Sizing
The team must process the files in ascending order of their current size, starting with the smallest files first (you can reference the `file_stats.md` list we generated earlier located at `/home/sanchit/.gemini/antigravity-cli/brain/77399aa3-cb2f-4b0e-8289-c2d532a5d414/file_stats.md`). The goal is to expand the smaller files so that all files eventually reach a consistently high level of depth, detail, and size.

### R4. Strict Quality Control
The expansions must be meaningful, highly technical, and high-quality. Do not pad files with redundant or filler information just to increase their character count. The quality of the existing notes must not degrade.

## Acceptance Criteria

### Programmatic Verification
- [ ] A verification script successfully runs and confirms that every `.md` file in the repository contains the required sections (e.g., "Use Cases", "Commands", "Sample Output").
- [ ] A script verifies that the newly expanded files have significantly increased in size to match the desired baseline without losing original content.

### Agent-as-Judge Verification
- [ ] An independent evaluation agent reviews a random sample of 10 enhanced files and passes them based on a grading rubric checking for explanation depth, structural integrity, usefulness of sample outputs, and absence of generic filler content.


## Follow-up — 2026-06-15T18:18:07Z

The user has requested some mid-flight adjustments to the project:
1. Please scale up the number of concurrent worker subagents to process the files more quickly.
2. Ensure that every single file change is committed to git individually as soon as it is enhanced and verified.


## Follow-up — 2026-06-15T18:33:17Z

The user has granted permanent permission to run git commands (manual approval timeouts are resolved for git operations). The orchestrator or its workers should retry the git commit process for the 10 pilot files, and then proceed with mass processing.


## Follow-up — 2026-06-15T18:34:01Z

The user has requested to add beginner-level explanations, use cases, and categories. As the workers expand files, they must explicitly add "Beginner" level content. If they see an opportunity to generate new beginner-level markdown files to balance out the advanced content, they should create those as well.

## Relaunch — 2026-06-16T04:32:00Z

# Teamwork Project Prompt — Draft

> Status: Relaunched
> Goal: Craft prompt → get user approval → delegate to teamwork_preview

Enhance over 2,000 markdown files in the VAPT repository by adding detailed explanations, preserving existing structure, adding practical use cases, and including comprehensive command lists with sample outputs.

Working directory: /home/sanchit/Notes/VAPT
Integrity mode: demo

## Requirements

### R1. Content Enhancement
Every markdown file must be expanded to include detailed explanations, practical use cases, comprehensive lists of all relevant commands, and sample outputs. The existing structure and formatting must be maintained. 
*CRITICAL*: You must explicitly add "Beginner" level explanations, use cases, and categories to make the content accessible. If appropriate, generate new beginner-focused modules/files to balance the content.

### R2. In-Place Modification
The original markdown files must be overwritten in-place with the newly enhanced content.

### R3. Processing Order & Sizing
The team must process the files in ascending order of their current size, starting with the smallest files first (you can reference the `file_stats.md` list we generated earlier located at `/home/sanchit/.gemini/antigravity-cli/brain/77399aa3-cb2f-4b0e-8289-c2d532a5d414/file_stats.md`). The goal is to expand the smaller files so that all files eventually reach a consistently high level of depth, detail, and size.

### R4. Strict Quality Control
The expansions must be meaningful, highly technical, and high-quality. Do not pad files with redundant or filler information just to increase their character count. The quality of the existing notes must not degrade.

## Acceptance Criteria

### Programmatic Verification
- [ ] A verification script successfully runs and confirms that every `.md` file in the repository contains the required sections (e.g., "Use Cases", "Commands", "Sample Output").
- [ ] A script verifies that the newly expanded files have significantly increased in size to match the desired baseline without losing original content.

### Agent-as-Judge Verification
- [ ] An independent evaluation agent reviews a random sample of 10 enhanced files and passes them based on a grading rubric checking for explanation depth, structural integrity, usefulness of sample outputs, inclusion of beginner content, and absence of generic filler content.
