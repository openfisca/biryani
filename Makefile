all: check test

check: flake8

clean: clean-pyc
	rm -f dist/*
	rm -rf build/*

clean-pyc:
	find -name '*.pyc' -exec rm \{\} \;

compile-catalog:
	python setup.py compile_catalog

ctags:
	ctags --recurse=yes --exclude=build --exclude=docs --exclude=dist .

distfile: compile-catalog
	python setup.py sdist bdist_wheel

flake8: clean-pyc
	python setup.py flake8

publish: compile-catalog
	python setup.py sdist bdist_wheel upload -r pypi

test-publish: compile-catalog
	python setup.py sdist bdist_wheel upload -r testpypi

test: compile-catalog
	python setup.py build_sphinx -b doctest

update-i18n:
	python setup.py extract_messages update_catalog
