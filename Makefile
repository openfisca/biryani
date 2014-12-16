.PHONY: check pep8 pyflakes

all: check

check: pep8 pyflakes

pep8:
	pep8 --exclude=.git,cache,docs --ignore=E251 --max-line-length  120 .

pyflakes:
	rm -Rf cache/templates*/
	pyflakes .

distfile:
	python setup.py sdist bdist_wheel

test_publish:
	python setup.py sdist bdist_wheel upload -r testpypi

publish:
	python setup.py sdist bdist_wheel upload -r pypi

clean:
	rm -f dist/*
	rm -rf build/*

test:
	python setup.py build_sphinx -b doctest
