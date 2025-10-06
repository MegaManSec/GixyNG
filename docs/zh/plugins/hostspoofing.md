# [host_spoofing] 伪造请求的 Host 头

位于 Nginx 后的应用经常依赖正确的 `Host` 头来生成 URL（重定向、资源、邮件中的链接等）。
伪造该请求头可能引发多种问题，从钓鱼到 SSRF 不等。

> 注意：你的应用也可能使用 `X-Forwarded-Host` 请求头来实现此功能。
> 这种情况下必须确保该请求头被正确设置。

## 如何发现？
多数情况下，问题源于使用了 `$http_host` 而不是 `$host`。

两者差异如下：
- `$host`：按以下优先级确定的主机名：请求行中的主机名，或 `Host` 请求头中的主机名，或与请求匹配的 `server_name`；
- `$http_host`：即 `Host` 请求头的原始值。

配置示例：
```nginx
location @app {
  proxy_set_header Host $http_host;
  # 其他代理参数
  proxy_pass http://backend;
}
```

## 如何规避？
所幸结论十分直接：
- 在 `server_name` 指令中列出所有合法的服务器名称；
- 始终使用 `$host`，不要使用 `$http_host`。

## 更多资料
- [Host of Troubles Vulnerabilities](https://hostoftroubles.com/)
- [Practical HTTP Host header attacks](http://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html)

--8<-- "zh/snippets/nginx-extras-cta.md"
