FROM python

RUN pip install boto3 redis

WORKDIR /app

COPY * /app/
