help:
	@echo "Query Parser"
	@echo "============"
	@cat makefile

# Virtual Environment

clean:
	rm -fr venv dist .tox .pytest_cache
	find . -name '*.egg-info' -exec rm -fr {} \;

venv:
	python3.10 -m venv venv

requirements: venv
	venv/bin/python -m pip install --upgrade -r test_requirements.txt

test: 
	venv/bin/pytest -v

coverage: 
	venv/bin/pytest -v --cov=qparser --cov=tests --cov=tests --cov-report=term-missing --cov-fail-under=100

mutations: 
	rm -f .mutmut-cache
	venv/bin/mutmut run || echo "Mutations failed"

results:
	venv/bin/mutmut results

tox: 
	venv/bin/tox -p

build: 
	rm -fr dist
	find . -depth -name '*.egg-info' -exec rm -fr {} \;
	venv/bin/python -m build

pypi-test: build
	venv/bin/python -m twine upload --repository testpypi dist/*

pypi: build
	venv/bin/python -m twine upload dist/*
