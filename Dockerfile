FROM python:3

RUN apt-get update
RUN apt-get install -y python3-pip git
RUN git clone https://github.com/jacobthebanana/mcgill-course-map.git
WORKDIR mcgill-course-map
RUN pip install -r requirements.txt

CMD ["python", "app.py"]