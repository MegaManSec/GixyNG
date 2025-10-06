# [resolver_external] 使用外部 DNS 解析器

直接在 `resolver` 指令中使用公共 DNS 服务器，可能使 nginx 暴露于 DNS 缓存投毒与旁路响应注入风险。被伪造的 DNS 响应可能污染 nginx 的缓存，使其将请求代理到攻击者控制的主机。

## 不安全示例

```nginx
# 公共、外部解析器（不安全）
resolver 1.1.1.1 8.8.8.8;

# 基于变量的上游解析依赖 resolver
set $backend upstream.internal.example;
location / {
    proxy_pass http://$backend;
}
```

## 更安全的替代方案

- 运行本地缓存解析器，并仅指向回环地址：

```nginx
# 仅使用本地解析器
resolver 127.0.0.1 [::1] valid=10s;
resolver_timeout 5s;
```

- 尽可能使用静态上游（避免基于变量的 `proxy_pass`）
- 将 `valid` 设置较低以缩短缓存时长；确保本地解析器可信并已加固

## 为什么重要

- 外部解析器增加了响应伪造的攻击面
- 被投毒的缓存项可能悄然将流量重定向到任意上游
- 在回环地址运行本地解析器（如 `unbound`、`dnsmasq`）可以显著降低风险

--8<-- "zh/snippets/nginx-extras-cta.md"
