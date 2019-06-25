image = $(shell sudo docker images "data_marketplace*" -q)
container = $(shell sudo docker ps -aq -f name="data_marketplace")
cd := $(shell pwd)
test: 
	pipenv run python run_pytest.py
generate_test:
	pipenv run python ./tests/generate_test.py
remove-test:
	rm tests/test_aes*
build-image:
	pipenv lock -r > requirements.txt  && pipenv lock -r --dev >> requirements.txt
	sudo docker build -t data_marketplace:latest .
save-image:
	sudo docker save data_marketplace:latest -o data_marketplace.tar
load-image:
	sudo docker loads
clean-image:
	rm data_marketplace.tar
	sudo docker rmi $(image)
remove-container:
	sudo docker stop $(container) && sudo docker rm $(container)
run-server:
	sudo docker run -it -d --name=data_marketplace -p 6562:6562 -v $(cd):/root/data_marketplace --entrypoint "python" $(image) /root/data_marketplace/run_server.py
rerun-server:
	make remove-container
	make run-server
run-test:
	sudo docker run -it -d --name=data_marketplace -v $(cd):/root/data_marketplace --entrypoint "python" $(image) /root/data_marketplace/run_pytest.py
watch-docker-logs:
	sudo docker logs -f $(container)
