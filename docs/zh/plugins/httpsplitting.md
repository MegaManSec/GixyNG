# [http_splitting] HTTP 拆分

HTTP 拆分是由于输入校验不当而导致的一类攻击。它通常针对位于 Nginx 之后的 Web 应用（HTTP Request Splitting），或针对其用户（HTTP Response Splitting）。

当攻击者能够将换行符 `\n` 或 `\r` 注入到请求，或由 Nginx 生成的响应中时，就会产生此漏洞。

## 如何发现？
应始终关注：
- 用于构造请求的指令中所用到的变量（这些变量可能包含 CRLF），例如 `rewrite`、`return`、`add_header`、`proxy_set_header`、`proxy_pass`；
- `$uri` 与 `$document_uri` 变量，以及它们被用于哪些指令，因为它们包含“已解码”的 URL 值；
- 由排除型范围（exclusive range）提取出的变量，例如 `(?P<myvar>[^.]+)`。

包含由排除型范围提取变量的错误配置示例：
```nginx
server {
    listen 80 default;

    location ~ /v1/((?<action>[^.]*)\.json)?$ {
        add_header X-Action $action;
        return 200 "OK";
    }
}
```

漏洞利用示例：
```http
GET /v1/see%20below%0d%0ax-crlf-header:injected.json HTTP/1.0
Host: localhost

HTTP/1.1 200 OK
Server: nginx/1.11.10
Date: Mon, 13 Mar 2017 21:21:29 GMT
Content-Type: application/octet-stream
Content-Length: 2
Connection: close
X-Action: see below
x-crlf-header:injected

OK
```

如上所示，攻击者成功向响应中添加了 `x-crlf-header: injected`。这是因为：
- `add_header` 并不会对传入的值进行编码或校验，默认假定编写者知晓后果；
- 路径在进入位置匹配前已被规范化；
- `$action` 的值来自一个包含排除范围的正则：`[^.]*`；
- 因而 `$action` 实际值可等于 `see below\r\nx-crlf-header:injected`，在被用于生成响应头时，产生了注入。

## 如何规避？
- 尽量使用更安全的变量，例如使用 `$request_uri` 替代 `$uri`；
- 在排除范围中禁止换行符，例如使用 `/some/(?<action>[^/\s]+)` 替代 `/some/(?<action>[^/]+`；
- 也可以考虑对 `$uri` 进行校验（仅在你明确了解其影响时）。

--8<-- "zh/snippets/nginx-extras-cta.md"
