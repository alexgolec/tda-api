test:
	python -m nose 

fix:
	autopep8 --in-place -r -a tdameritrade_api
	autopep8 --in-place -r -a tests
