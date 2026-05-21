import os
import subprocess
import sys


def get_changed_files():
    """Gets the list of files changed in the most recent commit."""
    try:
        # Get files changed in the last commit
        result = subprocess.run(
            ['git', 'diff', '--name-only', 'HEAD~1', 'HEAD'],
            capture_output=True, text=True, check=True
        )
        return [line.strip() for line in result.stdout.split('\n') if line.strip()]
    except subprocess.CalledProcessError:
        print("Warning: Could not determine changed files (might be the first commit).")
        return []

def check_documentation_drift(changed_files):
    """
    Checks if significant code changes were made without corresponding doc updates.
    """
    code_changes = []
    doc_changes = []

    # Define what we consider 'core code' and 'core docs' for this project
    core_code_prefixes = ('scripts/', 'skills/', '.cursor/rules/')
    core_doc_prefixes = ('docs/', 'rules/', 'README.md')

    for file in changed_files:
        if file.startswith(core_code_prefixes):
            code_changes.append(file)
        elif file.startswith(core_doc_prefixes):
            doc_changes.append(file)

    if code_changes and not doc_changes:
        print("\n" + "="*60)
        print("⚠️  DOCUMENTATION DRIFT WARNING ⚠️")
        print("="*60)
        print("You modified core infrastructure or skills, but did not update any documentation.")
        print("\nFiles changed:")
        for cf in code_changes[:5]:
            print(f"  - {cf}")
        if len(code_changes) > 5:
            print(f"  - ... and {len(code_changes) - 5} more.")

        print("\nConsider checking if the following core docs need updates:")
        print("  - docs/dev-guide.md (Technical architecture & extension points)")
        print("  - docs/agent-environment.md (API/MCP tool map for agents)")
        print("  - docs/project-context.md (High-level project status & timeline)")
        print("  - docs/admin-guide.md (API keys & environment setup)")
        print("  - docs/user-guide.md (End-user instructions & workflows)")
        print("="*60 + "\n")

        # Returning a non-zero exit code will mark the GitHub Action step as "failed"
        # (which serves as an alert), but because of our "continue-on-error" YAML setup,
        # it won't block any of your workflow.
        sys.exit(1)
    else:
        print("✅ No obvious documentation drift detected.")
        sys.exit(0)

if __name__ == "__main__":
    # Ensure we are in a git repository
    if not os.path.exists('.git'):
        print("Not a git repository, skipping drift check.")
        sys.exit(0)

    changed = get_changed_files()
    if changed:
        check_documentation_drift(changed)
    else:
        print("No files changed or unable to read history.")
