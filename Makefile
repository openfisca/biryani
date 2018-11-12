all: check test

install:
	pip install --upgrade pip
	pip install --editable .[bsonconv] --upgrade
	pip install --editable .[datetimeconv] --upgrade
	pip install --editable .[jwtconv] --upgrade
	pip install --editable .[netconv] --upgrade
	pip install --editable .[webobconv] --upgrade
	pip install --editable .[dev] --upgrade

clean:
	rm -rf dist build
	find . -name '*.pyc' -exec rm \{\} \;

check-style: clean
	flake8 `git ls-files | grep "\.py$$"`

compile-catalog:
	python setup.py compile_catalog

ctags:
	ctags --recurse=yes --exclude=build --exclude=docs --exclude=dist .

dist: compile-catalog
	python setup.py sdist bdist_wheel

publish: compile-catalog
	python setup.py sdist bdist_wheel upload -r pypi

publish-to-test: compile-catalog
	python setup.py sdist bdist_wheel upload -r testpypi

test:
	pytest
	compile-catalog
	python setup.py build_sphinx -b doctest

update-i18n:
	python setup.py extract_messages update_catalog
