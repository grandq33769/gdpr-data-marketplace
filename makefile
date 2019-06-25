image = $(shell sudo docker images "data_marketplace*" -q)
cd := $(shell pwd)
test: 
	pipenv run python run_pytest.py
generate_test:
	pipenv run python ./tests/generate_test.py
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
run-image:
	sudo docker run -it -d --name=data_marketplace -p 6562:6562 -v $(cd):/root/data_marketplace $(image)
