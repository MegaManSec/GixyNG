# [if_is_evil] 在 location 中使用 if 存在风险

在 `location` 环境中使用 [`if`](https://nginx.org/en/docs/http/ngx_http_rewrite_module.html#if) 指令存在诸多问题，在某些情况下可能产生与预期不同的行为，甚至导致段错误。通常应尽量避免。

替代方案：
- [`return ...;`](https://nginx.org/en/docs/http/ngx_http_rewrite_module.html#return)
- [`rewrite ... last;`](https://nginx.org/en/docs/http/ngx_http_rewrite_module.html#rewrite)
- [`rewrite ... redirect;`](https://nginx.org/en/docs/http/ngx_http_rewrite_module.html#rewrite)
- [`rewrite ... permanent;`](https://nginx.org/en/docs/http/ngx_http_rewrite_module.html#rewrite)

在某些情况下，可以考虑使用内嵌脚本模块（如 [embedded perl](https://nginx.org/en/docs/http/ngx_http_perl_module.html) 或 [Lua](https://nginx-extras.getpagespeed.com/lua-scripting/)）来实现逻辑。

--8<-- "zh/snippets/nginx-extras-cta.md"
