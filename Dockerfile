FROM python

LABEL maintainer="Olalekan Adebari"

WORKDIR /app/api/
RUN pip3 install uwsgi

COPY requirements.txt /app/api/requirements.txt 

RUN pip3 install -r requirements.txt 

COPY . /app/api/


# EXPOSE 8001

CMD ["uwsgi", "--ini", "uwsgi.ini"]

