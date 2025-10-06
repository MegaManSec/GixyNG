# `allow` без `deny`

Если в блоке конфигурации есть `allow` с IP или подсетью, как правило, должен присутствовать и `deny all;` (или это должно обеспечиваться в другом месте).
**Иначе по сути нет ограничения доступа.**

## Плохой пример

```nginx
location / {
      root /var/www/;
      allow 10.0.0.0/8;
      . . .
}
```

--8<-- "ru/snippets/nginx-extras-cta.md"

## Хороший пример

```nginx
location / {
      root /var/www/;
      allow 10.0.0.0/8;
      deny all;
      . . .
}
```
