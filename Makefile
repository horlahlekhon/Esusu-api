clean:
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.log' -delete

install:
	cd ../ && python virtualenv python3 .
	cd api
	pip3 install -r requirements.txt
	./manage.py migrate

test:
	./manage.py test

run:
	./manage.py runserver

db:
	./manage.py makemigrations
	./manage.py migrate

all: clean install test run

serve:
	./manage.py collectstatic
	/etc/init.d/nginx restart
	uwsgi --ini uwsgi.ini

build:
	docker-compose build 

contain:
	sudo mkdir -p /data/esusu/nginx/
	sudo cp nginx/conf.d /data/esusu/nginx/
	sudo mkdir -p /data/esusu/conf
	sudo cp conf/config.toml /data/esusu/conf
	sudo mkdir -p /data/esusu/logs/nginx/
	sudo mkdir /data/esusu/logs/esusu
	sudo cp uwsgi_params /data/esusu/

	docker-compose up &
	docker-compose run /app/api/manage.py migrate
	docker-compose run /app/api/manage.py collectstatic

build-and-contain: build contain
