FROM python:3.12-alpine3.21

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN pip3 install --no-cache-dir gunicorn==23.0.0

COPY requirements.txt /usr/src/app/
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

EXPOSE 8080
ENV WORKERS=4

CMD gunicorn -w $WORKERS -b 0.0.0.0:8080 -k uvicorn.workers.UvicornWorker 'awm.__main__:create_app()'
