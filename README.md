![Banner](banner.png)

# Code Obfuscation Analyzer

A command line wrapper that runs established Python analysis tools over a directory of Python code and logs their output in one place. Despite the repository name, the code contains no obfuscation specific detection of its own: it delegates all analysis to Bandit, Flake8, Pylint and Pyre, which the user selects with flags.

## Requirements

- Python 3 (main.py uses only the standard library)
- At least one of the external tools you plan to run: Bandit, Flake8, Pylint, Pyre (installed by `pip install -r requirements.txt`, or individually)

## Install

```
git clone https://github.com/ShadowGuardAI/codeintel-code-obfuscation-analyzer.git
cd codeintel-code-obfuscation-analyzer
pip install -r requirements.txt
```

## Usage

```
python main.py <directory> [--bandit] [--flake8] [--pylint] [--pyre]
python main.py --help
python main.py --version
```

- `directory` (required, positional): directory containing the code to analyze. The program exits with status 1 if it does not exist.
- `--bandit`: run `bandit -r <directory>`
- `--flake8`: run `flake8 <directory>`
- `--pylint`: run `pylint <directory>`
- `--pyre`: run `pyre check` with the target directory as the working directory. Pyre needs its own project configuration in that directory.
- `--version`: print `main.py 1.0.0` and exit

If no tool flag is given, the program warns that no analysis tools were selected and exits with status 0 without analyzing anything.

## Example

```
python main.py /path/to/code --bandit --flake8
```

Verified behavior on a sample file that passes user input to `os.system`: Bandit findings (including B605, start process with a shell) are printed in the log output, and the program then continues and exits with status 0.

## Output and limitations

- Results are written to the log output (stdout and stderr) only. The tool does not write a report file.
- Bandit, Flake8 and Pylint exit with a non-zero status when they find issues. This wrapper logs that status and continues with the remaining tools instead of aborting. It exits with status 0 when every selected tool could be started, and status 1 when the directory does not exist or a selected tool is not installed or not on PATH.
- A selected tool that is not installed produces an error naming the tool, for example `Tool not found: bandit is not installed or not on PATH`, and the program exits with status 1.
- What each tool reports is entirely determined by that tool. This wrapper adds no checks, scoring or deobfuscation of its own.

## License

See LICENSE in this repository.
