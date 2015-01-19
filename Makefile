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

dist: compile-catalog
	python setup.py sdist bdist_wheel

flake8: clean-pyc
	flake8

publish: compile-catalog
	python setup.py sdist bdist_wheel upload -r pypi

publish-to-test: compile-catalog
	python setup.py sdist bdist_wheel upload -r testpypi

test: compile-catalog
	python setup.py build_sphinx -b doctest

update-i18n:
	python setup.py extract_messages update_catalog
