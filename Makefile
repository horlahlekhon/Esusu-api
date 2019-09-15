clean:
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.log' -delete

install:
	pip3 install -r requirements.txt

test:
	./manage.py test

run:
	./manage.py runserver

db:
	./manage.py makemigrations
	./manage.py migrate

all: clean install db test run

serve:
	python manage.py collectstatic
	/etc/init.d/nginx restart
	uwsgi --socket api.sock --ini uwsgi.ini --chmod-socket=777

build:
	# ./manage.py collectstatic
	docker build -t esusu-api .

contain:
	docker run -p 8001:8001 --name esusu -v /data/esusu/api/media/:/app/api/media \
	-v /tmp:/data/esusu \
	-v /data/esusu/api/static/:/app/api/static esusu-api

build-and-contain: build contain
