[git-flow](http://nvie.com/posts/a-successful-git-branching-model/)

* cp .env.back .env
* mkdir envs; touch envs/local.env
* docker-compose -f docker-compose.dev.yaml up


## DB

create database eebook

python manage.py db migrate
python manage.py db upgrade
python manage.py db --help
