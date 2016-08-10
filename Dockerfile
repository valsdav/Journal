FROM  python:3.5

MAINTAINER valsdav valsdav@wikitolearn.org

ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true

COPY requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt

COPY journal.py .
COPY journal/ journal/
RUN echo 'DB_HOST = "mongo"' > journal/config.py


ENTRYPOINT ["python"]
CMD ["journal.py"]
