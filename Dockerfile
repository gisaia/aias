FROM ubuntu:22.10

RUN apt-get update -y && \
    apt-get install -y curl python3-pip python3-dev libgeos-dev gdal-bin libgdal-dev

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY ./aeoprs /app/aeoprs
COPY ./conf /app/conf
COPY ./start.sh /app/
COPY ./aeoprs.py /app/

EXPOSE 8000
ENTRYPOINT ["./start.sh"]
