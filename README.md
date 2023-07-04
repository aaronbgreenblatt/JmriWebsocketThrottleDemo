# Automation Scripts for JMRI
These scripts call the JMRI REST API

## Running
These scripts use Poetry for package management

1. Install poetry via `brew install poetry`. As of 7/2/2023, the Poetry installer script from their website fails on MacOS.

2. Install dependencies with `poetry install`

3. Run `poetry run python3 automationRwc/main.py`

## JMRI Setup
See the [JMRI Documentation](https://www.jmri.org/help/en/html/web/JsonServlet.shtml) for instructions on enabling the REST API server
