FROM python:3

MAINTAINER JacobTheBanana "jacob@banana.abay.cf"

RUN apt-get update -y && \
    apt-get install -y python3-pip

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app
RUN pip3 install -r requirements.txt

ARG CACHEBUST=1
COPY simple_map.py /app
ADD course_data /app/course_data
ADD graph_generator /app/graph_generator

ENTRYPOINT ["python3"]
CMD ["simple_map.py"]

EXPOSE 8000/tcp