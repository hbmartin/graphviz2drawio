help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "install - install the package to the active Python's site-packages"

pipenv:
	pip install pipenv
	pipenv install --dev

tests:
	pipenv run flake8
	pipenv run black graphviz2drawio --check
	pipenv run black test --check
#	pipenv run mypy graphviz2drawio
	pipenv run pytest test/ --cov-report term-missing --cov=graphviz2drawio

ci: pipenv tests

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name '*.DS_Store' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	find . -name '.pytest_cache' -exec rm -fr {} +
	find . -name '.mypy_cache' -exec rm -fr {} +

install: clean
	python setup.py install

package: clean-build
	pipenv run python setup.py sdist bdist_wheel

upload:
	twine upload dist/*

tag:
	git diff-index --quiet HEAD --  # checks for unstaged/uncomitted files
	git tag "v`pipenv run python graphviz2drawio/version.py`"
	git push --tags

release: clean tag package upload
