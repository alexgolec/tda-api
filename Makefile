test:
	python -m nose $(NOSE_ARGS)

fix:
	autopep8 --in-place -r -a tda
	autopep8 --in-place -r -a tests
	autopep8 --in-place -r -a examples

coverage:
	python -m coverage run --source=tda -m nose
	python -m coverage html

dist:
	python setup.py sdist bdist_wheel

release:
	python3 -m twine upload dist/*
