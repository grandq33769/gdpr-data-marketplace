FROM python:3.6

COPY . /root/data_marketplace

WORKDIR /root/data_marketplace

RUN pip install -r requirements.txt

EXPOSE 6562

ENTRYPOINT [ "bash" ]
