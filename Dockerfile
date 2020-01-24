FROM python

WORKDIR /app

COPY * /app/

RUN pip install boto3 redis
