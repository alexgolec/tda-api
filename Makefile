test:
	python3 -m nose $(NOSE_ARGS)

fix:
	autopep8 --in-place -r -a tda
	autopep8 --in-place -r -a tests
	autopep8 --in-place -r -a examples

coverage:
	python3 -m coverage run --source=tda -m nose
	python3 -m coverage html

dist: clean
	python3 setup.py sdist bdist_wheel

release: clean test dist
	python3 -m twine upload dist/*

clean:
	rm -rf build dist docs-build tda_api.egg-info __pycache__ htmlcov
