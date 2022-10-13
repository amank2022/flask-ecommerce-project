FROM python:3.8-slim-buster

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

# ENV EMAIL_USER=akushwaha@deqode.com
# ENV EMAIL_PASS=

# CMD [ "python3", "-m" , "flask", "--app", "run", "run", "--host=0.0.0.0"]