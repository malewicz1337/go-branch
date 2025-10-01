import os
import subprocess
from datetime import datetime, timedelta
import time

# --- Configuration ---
MAIN_BRANCH = "main"
LOG_FILE = "branch.log"
START_DATE = datetime(2025, 8, 4, 9, 0, 0)
ITERATIONS = 10
# ---------------------


def run_command(command, env=None):
    """
    Executes a shell command, prints its output, and raises an exception on error.
    """
    print(f"\n> {' '.join(command)}")

    process_env = os.environ.copy()
    if env:
        print(f"  (with custom env: {env})")
        process_env.update(env)

    try:
        # Using capture_output=True to get stdout/stderr
        result = subprocess.run(
            command, check=True, text=True, capture_output=True, env=process_env
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {' '.join(command)}")
        print(f"Return Code: {e.returncode}")
        print(f"Output:\n{e.stdout}")
        print(f"Error Output:\n{e.stderr}")
        raise


def main():
    """
    Main function to orchestrate the Git workflow.
    """
    # 1. Safety Check: Ensure we are in a Git repository
    if not os.path.isdir(".git"):
        print("Error: This script must be run from the root of a Git repository.")
        return

    counter = 0
    while True:
        counter += 1
        try:
            # 2. Generate a unique branch name
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            new_branch_name = f"feature/log-update-{timestamp}"
            print(f"Creating a new branch named: {new_branch_name}")

            current_commit_date = START_DATE + timedelta(minutes=counter)
            iso_date = current_commit_date.isoformat()
            commit_env = {
                "GIT_AUTHOR_DATE": iso_date,
                "GIT_COMMITTER_DATE": iso_date,
            }

            # 3. Start from a clean slate on the main branch
            run_command(["git", "checkout", MAIN_BRANCH])
            # Optional: uncomment to ensure main is up-to-date
            # run_command(["git", "pull", "origin", MAIN_BRANCH])

            # 4. Create and switch to the new branch
            run_command(["git", "checkout", "-b", new_branch_name])

            # 5. Create or append to the log file with a new entry
            log_message = f"{datetime.now().isoformat()}: Activity recorded on branch {new_branch_name}.\n"
            with open(LOG_FILE, "a") as f:
                f.write(log_message)
            print(f"\nAppended change to '{LOG_FILE}'.")

            # 6. Stage and commit the changes
            run_command(["git", "add", LOG_FILE])
            commit_message = f"feat: Add new entry to {LOG_FILE}"
            run_command(["git", "commit", "-m", commit_message], env=commit_env)

            # 7. Switch back to the main branch
            run_command(["git", "checkout", MAIN_BRANCH])

            # 8. Merge the new branch into main
            # Using --no-ff creates a merge commit, preserving branch history
            run_command(["git", "merge", "--no-ff", new_branch_name], env=commit_env)
            print(f"\nSuccessfully merged '{new_branch_name}' into '{MAIN_BRANCH}'.")

            # 9. (Optional but recommended) Delete the feature branch
            run_command(["git", "branch", "-d", new_branch_name])
            print(f"Successfully deleted local branch '{new_branch_name}'.")

            print("\n✅ Git workflow completed successfully!")

            time.sleep(1)

            if counter >= ITERATIONS:
                print(f"\nReached the maximum of {ITERATIONS} ITERATIONS. Exiting.")
                break

        except subprocess.CalledProcessError:
            print("\n❌ An error occurred during the Git workflow.")
            print(
                "The repository may be in an intermediate state. Please check `git status`."
            )
        except Exception as e:
            print(f"\n❌ An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
