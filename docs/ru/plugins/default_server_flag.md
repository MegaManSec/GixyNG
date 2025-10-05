# [default_server_flag] Отсутствует default_server при общем сокете listen

Когда два и более блока `server` используют один и тот же адрес и порт в директиве `listen`, один из них должен быть явно помечен как `default_server` (или `default`). Это устраняет неоднозначность в выборе блока `server` для запросов, не совпадающих по `server_name`.

## Как это найти?

Gixy сообщает о проблеме, если обнаруживает несколько блоков `server`, слушающих один и тот же сокет, и ни один из них не помечен флагом `default_server`.

Пример неверной конфигурации:

```nginx
http {
    server {
        listen 80;
        server_name a.test;
    }

    server {
        listen 80;
        server_name b.test;
    }
}
```

## Что делать?

- Добавьте флаг `default_server` одному из блоков `server`, которые слушают один и тот же сокет.

Пример корректной конфигурации:

```nginx
http {
    server {
        listen 80 default_server;
        server_name a.test;
    }

    server {
        listen 80;
        server_name b.test;
    }
}
```

## Ссылки

- Директива `listen` в NGINX: https://nginx.org/ru/docs/http/ngx_http_core_module.html#listen

