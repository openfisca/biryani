all: check test

check: flake8

clean: clean-pyc
	rm -f dist/*
	rm -rf build/*

clean-pyc:
	find -name '*.pyc' -exec rm \{\} \;

flake8: clean-pyc
	python setup.py flake8

distfile:
	python setup.py sdist bdist_wheel

test_publish:
	python setup.py sdist bdist_wheel upload -r testpypi

publish:
	python setup.py sdist bdist_wheel upload -r pypi

test:
	python setup.py build_sphinx -b doctest
