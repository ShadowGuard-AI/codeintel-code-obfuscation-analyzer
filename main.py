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

def run_tool(command):
    """
    Runs a given shell command and logs the output.

    Args:
        command (list): The command to run as a list of strings.

    Raises:
        RuntimeError: If the command execution fails.
    """
    try:
        logger.info("Running command: %s", " ".join(command))
        result = subprocess.run(
            command, check=True, capture_output=True, text=True
        )
        logger.info("Command output:\n%s", result.stdout)
    except subprocess.CalledProcessError as e:
        logger.error("Command failed with error:\n%s", e.stderr)
        raise RuntimeError(f"Error running command: {' '.join(command)}") from e

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

    # Run tools based on arguments
    if use_bandit:
        run_tool(["bandit", "-r", directory])
    if use_flake8:
        run_tool(["flake8", directory])
    if use_pylint:
        run_tool(["pylint", directory])
    if use_pyre:
        run_tool(["pyre", "check"])

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