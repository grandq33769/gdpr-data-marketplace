test: 
	pipenv run python run_pytest.py
generate_test:
	pipenv run python ./tests/generate_test.py
build-docker-image:
	pipenv lock -r > requirements.txt  && pipenv lock -r --dev >> requirements.txt
	docker build -t data_marketplace:latest .
	docker save data_marketplace:latest -o data_marketplace.tar
load-image:
	sudo docker loads
clean-image:
	rm data_marketplace.tar
	sudo docker rmi $(sudo docker images "data_marketplace*" -qs