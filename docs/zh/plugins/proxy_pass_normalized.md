# [proxy_pass_normalized] 使用带路径的 `proxy_pass` 可能解码/归一化路径

当 `proxy_pass` 使用了带路径的上游 URL 时，nginx 在代理前会对请求路径进行归一化与解码。这可能改变原始路径的语义，导致安全问题。

## 不安全示例

```nginx
# 归一化/解码可能改变语义
location /api/ {
    proxy_pass http://backend/api/;
}
```

## 更安全的替代方案

- 避免在 `proxy_pass` 中添加路径，使用无路径上游并在 `location` 中控制拼接；
- 对用户可控的路径进行严格校验与约束；
- 在上游侧实施额外的路径验证与访问控制。

## 为什么重要

路径归一化与解码可能导致绕过检查、路径混淆等问题。保持路径处理的明确性与一致性，避免在代理层引入非预期的变换。

--8<-- "zh/snippets/nginx-extras-cta.md"
