import argparse
import logging
import subprocess
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Tool version
VERSION = "1.0.0"

def setup_argparse():
    """
    Sets up command-line argument parsing for the tool.

    Returns:
        argparse.ArgumentParser: Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        description="Code Obfuscation Analyzer: Analyze obfuscated code to identify potential vulnerabilities."
    )
    parser.add_argument(
        "directory",
        type=str,
        help="Directory containing the code to analyze."
    )
    parser.add_argument(
        "--bandit",
        action="store_true",
        help="Run Bandit for static security analysis."
    )
    parser.add_argument(
        "--flake8",
        action="store_true",
        help="Run Flake8 for code quality checks."
    )
    parser.add_argument(
        "--pylint",
        action="store_true",
        help="Run Pylint for detailed code analysis."
    )
    parser.add_argument(
        "--pyre",
        action="store_true",
        help="Run Pyre-Check for type checking and potential issues."
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}",
        help="Show the version of the tool and exit."
    )
    return parser

def run_tool(command, cwd=None):
    """
    Runs a given command and logs the output.

    Bandit, Flake8 and Pylint exit with a non-zero status when they find
    issues. That is a result, not a failure, so the output is logged and
    the exit status is reported without raising. Only a tool that cannot
    be started at all (for example because it is not installed) raises.

    Args:
        command (list): The command to run as a list of strings.
        cwd (str): Optional working directory for the command.

    Raises:
        RuntimeError: If the command cannot be started.
    """
    try:
        # I log the joined command for reading, but the list form is
        # what actually runs. A path with spaces prints as if it were
        # several arguments while the tool still receives it as one.
        logger.info("Running command: %s", " ".join(command))
        result = subprocess.run(
            command, check=False, capture_output=True, text=True, cwd=cwd
        )
    except FileNotFoundError as e:
        raise RuntimeError(
            f"Tool not found: {command[0]} is not installed or not on PATH"
        ) from e
    if result.stdout:
        logger.info("Command output:\n%s", result.stdout)
    if result.stderr:
        logger.info("Command stderr:\n%s", result.stderr)
    logger.info("Command exited with status %s", result.returncode)
    # I hand the result back and nobody above me reads its code.
    # A run where every tool reports pages of findings still ends
    # with this program exiting 0, as long as the tools started.
    return result

def analyze_code(directory, use_bandit, use_flake8, use_pylint, use_pyre):
    """
    Analyzes the code in the specified directory using selected tools.

    Args:
        directory (str): Path to the directory containing code.
        use_bandit (bool): Whether to run Bandit.
        use_flake8 (bool): Whether to run Flake8.
        use_pylint (bool): Whether to run Pylint.
        use_pyre (bool): Whether to run Pyre-Check.
    """
    # Ensure the directory exists
    path = Path(directory)
    if not path.is_dir():
        logger.error("Directory does not exist: %s", directory)
        raise FileNotFoundError(f"Directory not found: {directory}")

    # I warn and return here rather than failing. That makes a run
    # with no tool flags look like a finished analysis in a script
    # that only checks the exit code, which is a trap I know about.
    if not (use_bandit or use_flake8 or use_pylint or use_pyre):
        logger.warning(
            "No analysis tools selected. "
            "Pass at least one of --bandit, --flake8, --pylint or --pyre."
        )
        return

    # Each tool gets the directory as a single argv item in list
    # form, so a target path containing spaces is passed to the tool
    # as one argument and is never reinterpreted by a shell.
    if use_bandit:
        run_tool(["bandit", "-r", directory])
    if use_flake8:
        run_tool(["flake8", directory])
    if use_pylint:
        run_tool(["pylint", directory])
    if use_pyre:
        # Pyre checks the project in its working directory, so run it
        # inside the target directory instead of the caller's directory.
        run_tool(["pyre", "check"], cwd=directory)

def main():
    """
    Main entry point for the tool. Parses arguments and runs the analysis.

    Example:
        python main.py /path/to/code --bandit --flake8 --pylint
    """
    parser = setup_argparse()
    args = parser.parse_args()

    try:
        analyze_code(
            args.directory,
            use_bandit=args.bandit,
            use_flake8=args.flake8,
            use_pylint=args.pylint,
            use_pyre=args.pyre
        )
    except Exception as e:
        logger.error("An error occurred: %s", e)
        sys.exit(1)

if __name__ == "__main__":
    main()