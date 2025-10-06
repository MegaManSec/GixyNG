# `allow` 未配套 `deny`

当某个配置块包含 `allow` 指令（指定某个 IP 或网段）时，通常也应该包含 `deny all;` 指令（或在其他位置进行强制）。
**否则，基本上就没有任何访问限制。**

## 错误示例

```nginx
location / {
      root /var/www/;
      allow 10.0.0.0/8;
      . . .
}
```

--8<-- "zh/snippets/nginx-extras-cta.md"

## 正确示例

```nginx
location / {
      root /var/www/;
      allow 10.0.0.0/8;
      deny all;
      . . .
}
```
