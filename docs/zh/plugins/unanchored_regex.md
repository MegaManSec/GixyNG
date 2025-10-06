# [unanchored_regex] 未加锚点的正则

在 NGINX 中，使用正则定义 `location` 时，建议至少对字符串开头或结尾加锚点。
否则，该正则会匹配字符串的任意部分，可能导致意外行为或性能下降。

例如，以下 `location` 会匹配任何包含 `/v1/` 的 URL：

```nginx
location ~ /v1/ {
    # ...
}
```

它会匹配：

- `/v1/`
- `/v1/foo`
- `/foo/v1/bar`
- `/foo/v1/`

若只希望匹配以 `/v1/` 开头的 URL，应加上锚点：

```nginx
location ~ ^/v1/ {
    # ...
}
```

这样，正则仅匹配以 `/v1/` 开头的 URL。

匹配文件扩展名（如 PHP 文件）时，正则应锚定到字符串结尾。

错误示例：

```nginx
location ~ \.php {
    # ...
}
```

它会匹配任何包含 `.php` 的 URL：`/foo.php`、`/foo.phpanything`，这是不正确的。

正确示例：

```nginx
location ~ \.php$ {
    # ...
}
```

这样才能只匹配以 `.php` 结尾的 URL。

--8<-- "zh/snippets/nginx-extras-cta.md"
