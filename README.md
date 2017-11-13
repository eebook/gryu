# Gryu
![](./gryu关羽.jpg)

## Developers need to know
[git-flow](http://nvie.com/posts/a-successful-git-branching-model/)

## DB

`create database gryu`

TODO: use python
    
```
python manage.py db migrate
python manage.py db upgrade
python manage.py db --help
```

### Drop resource key. Executed in the database container


## init config

### environment

```
$ cp .env.back .env
$ mkdir envs; touch envs/local.env
$ docker-compose -f docker-compose.dev.yaml up
```

### log file path

mkdir -p /var/log/eebook/

## TODO

* 利用 redis 做 token 的 cache 过期
* 更新登录时间

## License

[AGPLv3](https://www.gnu.org/licenses/agpl-3.0.en.html)
