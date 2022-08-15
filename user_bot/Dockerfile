FROM python:3.10-alpine

RUN mkdir /user_bot

COPY pipfile.txt . 
# RUN apk update && apk add python3-dev \
#                           gcc libc-dev libffi-dev 
RUN pip3 install --upgrade pip && pip3 install --no-cache-dir --requirement pipfile.txt

RUN apk --update --no-cache add curl

COPY . /user_bot
WORKDIR /user_bot
