# [error_log_off] 将 `error_log` 设为 `off`

一个常见的误解是使用 `error_log off` 可以关闭错误日志。
不同于 `access_log` 指令，`error_log` 并不接受 `off` 参数。
如果在配置中写上 `error_log off`，NGINX 会在默认配置目录（通常是 `/etc/nginx`）下创建名为 “off” 的日志文件。

一般不建议关闭错误日志，因为它对定位 NGINX 问题非常重要。
但如果磁盘空间极度有限，且担心日志占满空间，可以选择关闭错误日志。可在主配置上下文中添加：

```nginx
error_log /dev/null emerg;
```

请注意，此设置仅在 NGINX 读取并验证配置文件之后才会生效。
因此，在启动或重新加载配置时，NGINX 仍可能将错误写入默认错误日志位置（通常是 `/var/log/nginx/error.log`），直到验证完成。
若要永久更改默认日志目录，可在启动 NGINX 时使用 `--error-log-path`（或 `-e`）选项。

--8<-- "zh/snippets/nginx-extras-cta.md"
