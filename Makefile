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
	uwsgi --ini uwsgi.ini

build:
	docker-compose build 

contain:
	docker-compose up
	docker-compose run /app/api/manage.py migrate
	docker-compose run /app/api/manage.py collectstatic

build-and-contain: build contain
