---

# Python Virtual Environment Policy

For all Python projects, always use a dedicated virtual environment.

## Requirements

- Before installing any Python package, check whether a virtual environment already exists in the project directory.
- If a virtual environment does not exist, create one in the project root before installing any dependencies.
- Never install project-specific packages globally unless explicitly instructed to do so.
- Activate the virtual environment before running any installation, testing, or execution commands.
- Install all project dependencies inside the virtual environment.
- Keep project dependencies isolated from the system Python installation.
- If a `requirements.txt`, `pyproject.toml`, or equivalent dependency file exists, install dependencies from it rather than installing packages individually.
- When new dependencies are added, update the project's dependency file (`requirements.txt`, `pyproject.toml`, or equivalent) so the environment can be reproduced.
- Ensure the virtual environment directory is excluded from version control using `.gitignore` (for example, `.venv/`, `venv/`, or the project's chosen environment directory).
- Prefer naming the virtual environment `.venv` unless the project already follows a different convention.
- Verify that all installation commands are executed within the active virtual environment.

## Standard Workflow

1. Check for an existing virtual environment.
2. If none exists, create one in the project root (preferably named `.venv`).
3. Activate the virtual environment.
4. Upgrade `pip` if appropriate.
5. Install all required dependencies.
6. Update the project's dependency file if new packages were introduced.
7. Execute all Python commands using the virtual environment's interpreter.

This policy is mandatory for every Python project unless explicitly instructed otherwise.
