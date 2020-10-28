FROM python:3.8-alpine3.11
ADD ./api /app
WORKDIR /app
ADD requirements.txt /
RUN apk add --no-cache git
RUN pip install -r /requirements.txt

EXPOSE 8080
CMD ["gunicorn", "-b", "0.0.0.0:8080", "wsgi:app", "--access-logfile", "-" ]
