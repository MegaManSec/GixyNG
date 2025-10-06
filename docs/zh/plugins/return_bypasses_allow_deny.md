# [return_bypasses_allow_deny] `return` 可能绕过 allow/deny

当 `return` 出现在应用 `allow/deny` 的上层上下文时，可能在未触发访问控制的情况下直接返回，从而绕过了 `allow/deny`。

## 错误示例

```nginx
server {
    allow 10.0.0.0/8;
    deny all;

    location /healthz {
        return 200 "ok";
    }
}
```

在某些结构下，`return` 可能在访问控制之前生效，导致未授权访问得以返回。

## 更安全的做法

- 将 `allow/deny` 放置在更靠近实际匹配的上下文，或在需要的 `location` 内重复设置；
- 若必须使用 `return`，确保它处于同一受控上下文，否则显式在该位置添加相同的访问控制；
- 通过 `satisfy` 与 `auth_*` 等机制组合时，确认短路顺序不会绕过安全检查。

--8<-- "zh/snippets/nginx-extras-cta.md"
