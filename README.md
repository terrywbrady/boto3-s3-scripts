# Python code for creating/reading S3

## Setup
- Clone code
- Run Redis (in Docker) on an accessible host (to your client apps)
  - `docker run -p 6379:6379 --rm -d --name redis redis`
  - Alternative
    - `docker-compose -f redis.yml up -d`
- Copy service.ini.template to service.ini
  - Configure credentials
  - Configure host and port to access Redis

## Obtain Docker image

- If published
  - `docker pull terrywbrady/my-s3-tester`
- Build locally
  - `docker-compose build`

## Run code in 2 terminals or on 2 hosts
- Load Content
  - `docker-compose run my-s3-tester python s3.py 20`
- Read Content
  - `docker-compose run my-s3-tester python reader.py`
- Clean up Content
  - `docker-compose run my-s3-tester python reader.py delete 20`
