FROM python:alpine
MAINTAINER Alex Recker <alex@reckerfamily.com>
WORKDIR /usr/src/app
COPY . .
CMD [ "python", "main.py" ]
