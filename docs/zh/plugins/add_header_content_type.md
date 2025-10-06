# 使用 `add_header` 设置 `Content-Type`

## 不佳示例

```nginx
add_header Content-Type text/plain;
```
如果后端也设置了 `Content-Type`，这可能导致产生重复的 `Content-Type` 响应头。

## 更佳示例

```nginx
default_type text/plain;
```

## 例外情况

当与任意 `*_hide_header Content-Type` 指令结合使用时，`add_header Content-Type` 是安全的，不会触发该检查：

```nginx
proxy_hide_header Content-Type;
add_header Content-Type "application/octet-stream";
```

此模式是有效的，因为 `*_hide_header`（例如 `proxy_hide_header`、`fastcgi_hide_header`、`uwsgi_hide_header`、`scgi_hide_header` 或 `grpc_hide_header`）会阻止后端返回的 `Content-Type` 透传，然后由 `add_header` 重新设置一个新的，从而避免重复响应头。

--8<-- "zh/snippets/nginx-extras-cta.md"
