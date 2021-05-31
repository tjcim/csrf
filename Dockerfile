FROM python:3-alpine

RUN apk add --no-cache gcc musl-dev g++

RUN adduser -D microblog

WORKDIR /code

COPY requirements.txt /code/requirements.txt
RUN python -m venv /code/venv
RUN /code/venv/bin/pip install --upgrade pip && \
  /code/venv/bin/pip install -r /code/requirements.txt
RUN /code/venv/bin/pip install gunicorn pymysql

COPY app /code/app
COPY migrations /code/migrations
COPY microblog.py config.py boot.sh /code/
RUN chmod +x /code/boot.sh

ENV FLASK_APP /code/microblog.py

RUN chown -R microblog:microblog /code/
USER microblog

EXPOSE 5000
ENTRYPOINT ["/code/boot.sh"]
