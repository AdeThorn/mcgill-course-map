FROM python:3-alpine

LABEL maintainer="JacobTheBanana jacob@banana.abay.cf"

RUN apk add --update py3-pip
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app
RUN pip3 install --no-cache-dir -r requirements.txt

ARG CACHEBUST=1
COPY simple_map.py /app
ADD course_data /app/course_data
ADD graph_generator /app/graph_generator

ENTRYPOINT ["python3"]
CMD ["simple_map.py"]

EXPOSE 8000/tcp
