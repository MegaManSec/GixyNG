# [add_header_multiline] 多行响应头

应避免使用多行响应头，因为：
- 它已被弃用（见 [RFC 7230](https://tools.ietf.org/html/rfc7230#section-3.2.4)）；
- 某些 HTTP 客户端和浏览器从未支持（例如 IE/Edge/Nginx）。

## 如何发现？
错误配置示例：
```nginx
# https://nginx.org/en/docs/http/ngx_http_headers_module.html#add_header
add_header Content-Security-Policy "
    default-src: 'none';
    script-src data: https://yastatic.net;
    style-src data: https://yastatic.net;
    img-src data: https://yastatic.net;
    font-src data: https://yastatic.net;";

# https://nginx-extras.getpagespeed.com/modules/headers-more/
more_set_headers -t 'text/html text/plain'
    'X-Foo: Bar
        multiline';
```

## 如何规避？
唯一的解决方案就是不要使用多行响应头。

--8<-- "zh/snippets/nginx-extras-cta.md"
