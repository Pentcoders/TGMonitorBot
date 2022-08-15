FROM python:3.10-alpine

ENV PYTHONUNBUFFERED 1

RUN mkdir /dj_admin

COPY pipfile.txt . 
RUN apk update && apk add python3-dev \
                          gcc libc-dev libffi-dev libpq-dev

RUN python3 -m pip install --upgrade pip
RUN pip3 install --no-cache-dir --requirement pipfile.txt

# copy entrypoint.sh
COPY ./entrypoint.sh /dj_admin
RUN sed -i 's/\r$//g' dj_admin/entrypoint.sh
RUN chmod +x dj_admin/entrypoint.sh

# copy project
COPY . /dj_admin
WORKDIR /dj_admin

RUN mkdir /staticfiles
RUN python manage.py collectstatic --noinput
# run entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
