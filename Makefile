PROJECT = marrow.mongo
USE = development,logger

.PHONY: all develop clean veryclean test release

all: clean develop test

develop: ${PROJECT}.egg-info/PKG-INFO

clean:
	find . -name __pycache__ -exec rm -rfv {} +
	find . -iname \*.pyc -exec rm -fv {} +
	find . -iname \*.pyo -exec rm -fv {} +
	rm -rvf build htmlcov

veryclean: clean
	rm -rvf *.egg-info .packaging/*

test: develop
	@clear
	@pytest

release:
	./setup.py register sdist bdist_wheel upload ${RELEASE_OPTIONS}
	@echo -e "\nView online at: https://pypi.python.org/pypi/${PROJECT} or https://pypi.org/project/${PROJECT}/"
	@echo -e "Remember to make a release announcement and upload contents of .packaging/release/ folder as a Release on GitHub.\n"

${PROJECT}.egg-info/PKG-INFO: setup.py setup.cfg marrow/mongo/core/release.py
	@mkdir -p ${VIRTUAL_ENV}/lib/pip-cache
	pip install --cache-dir "${VIRTUAL_ENV}/lib/pip-cache" -Ue ".[${USE}]"
