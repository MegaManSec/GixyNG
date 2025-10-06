# Использование `add_header` для установки `Content-Type`

## Плохой пример

```nginx
add_header Content-Type text/plain;
```
Это может привести к дублированию заголовка `Content-Type`, если его выставляет бэкенд.

## Хороший пример

```nginx
default_type text/plain;
```

## Исключение

Комбинация `add_header Content-Type` с любой директивой `*_hide_header Content-Type` безопасна и не вызывает данную проверку:

```nginx
proxy_hide_header Content-Type;
add_header Content-Type "application/octet-stream";
```

Этот паттерн корректен, потому что `*_hide_header` (например, `proxy_hide_header`, `fastcgi_hide_header`, `uwsgi_hide_header`, `scgi_hide_header`, `grpc_hide_header`) блокирует прохождение `Content-Type` от бэкенда, а `add_header` затем устанавливает новый, избегая дублей.

--8<-- "ru/snippets/nginx-extras-cta.md"
