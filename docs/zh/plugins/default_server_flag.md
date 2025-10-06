# [default_server_flag] 共享监听套接字缺少 default_server

当两个或更多 `server` 块共享相同的 `listen` 地址与端口时，其中一个应显式标记为 `default_server`（或 `default`）。
这样可以避免对不匹配任何 `server_name` 的请求由哪个 `server` 处理产生歧义。

## 如何发现？

如果 Gixy 发现有多个 `server` 在同一套接字上监听，但没有任何一个被标记为 `default_server`，就会报告问题。

错误示例：

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

## 如何规避？

- 在共享同一套接字的多个 `server` 中，给其中一个加上 `default_server` 标志。

正确配置示例：

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

## 参考

- NGINX `listen` 指令: https://nginx.org/en/docs/http/ngx_http_core_module.html#listen

--8<-- "zh/snippets/nginx-extras-cta.md"
