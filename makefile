run_all_test: 
	pipenv run pytest -s --benchmark-save-data
generate_test:
	pipenv run python ./tests/generate_test.py
