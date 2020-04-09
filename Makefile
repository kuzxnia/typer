MODULE := typer
BLUE='\033[0;34m'
NC='\033[0m' # No Color

run:
	@pipenv run python3 -m $(MODULE)

test:
	@pipenv run python3 -m pytest

lint:
	@echo "\n${BLUE}Running Pylint against source and test files...${NC}\n"
	@pipenv run pylint --rcfile=.pylintrc **/*.py
	@echo "\n${BLUE}Running Flake8 against source and test files...${NC}\n"
	@pipenv run flake8

clean:
	rm -rf .pytest_cache .coverage .pytest_cache coverage.xml

.PHONY: clean test
