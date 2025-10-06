# [ssrf] 服务器端请求伪造（SSRF）

服务器端请求伪造是一类攻击，诱使服务器（在本项目中为 Nginx）代表攻击者发起任意请求。
当攻击者可以控制被代理服务器的地址（`proxy_pass` 指令的第二个参数）时，即有可能发生。

## 如何发现？
使服务器暴露于 SSRF 的常见两类错误：
- 缺少 [`internal`](https://nginx.org/en/docs/http/ngx_http_core_module.html#internal) 指令。该指令用于标记某个 `location` 仅允许内部请求访问；
- 不安全的内部重定向。

### 缺少 internal 指令
以下为典型的错误配置，因缺少 `internal` 指令而导致 SSRF：
```nginx
location ~ /proxy/(.*)/(.*)/(.*)$ {
    proxy_pass $1://$2/$3;
}
```
攻击者对被代理地址拥有完全控制权，从而可以让 Nginx 代表其向任意目标发起请求。

### 不安全的内部重定向
假设你的配置中有一个仅用于内部访问的 `location`，并且该位置使用了请求中的数据作为被代理服务器的地址。

例如：
```nginx
location ~* ^/internal-proxy/(?<proxy_proto>https?)/(?<proxy_host>.*?)/(?<proxy_path>.*)$ {
    internal;

    proxy_pass $proxy_proto://$proxy_host/$proxy_path ;
    proxy_set_header Host $proxy_host;
}
```
根据 Nginx 文档，内部请求包括：
>  - 由 **error_page**、index、random_index 和 **try_files** 指令触发的重定向；
>  - 上游服务器通过 “X-Accel-Redirect” 响应头触发的重定向；
>  - 由 `ngx_http_ssi_module` 模块的 “include virtual” 命令以及 `ngx_http_addition_module` 模块的指令形成的子请求；
>  - 由 **rewrite** 指令改变的请求。

因此，任何不安全的 `rewrite` 都可能允许攻击者构造内部请求并控制被代理服务器的地址。

错误示例：
```nginx
rewrite ^/(.*)/some$ /$1/ last;

location ~* ^/internal-proxy/(?<proxy_proto>https?)/(?<proxy_host>.*?)/(?<proxy_path>.*)$ {
    internal;

    proxy_pass $proxy_proto://$proxy_host/$proxy_path ;
    proxy_set_header Host $proxy_host;
}
```

## 如何规避？
编写此类配置时建议遵循以下规则：
- 仅通过“内部位置（internal location）”进行代理；
- 尽可能避免传递用户可控的数据；
- 保护被代理服务器地址：
  * 若可代理的主机集合有限（例如仅 S3 等），应将其硬编码并通过 `map` 等方式选择；
  * 若无法枚举所有可能主机，应对地址进行签名校验。

--8<-- "zh/snippets/nginx-extras-cta.md"
