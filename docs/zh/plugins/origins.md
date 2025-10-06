# [origins] 引用来源（Referer/Origin）校验问题

在实践中，人们常用正则校验 `Referer` 或 `Origin` 请求头。
这通常用于设置 `X-Frame-Options`（防点击劫持）或处理跨域（CORS）。

常见错误包括：
- 正则表达式书写错误；
- 放行了第三方来源。

> 注意：默认情况下，Gixy 不会检查正则是否允许第三方来源。
> 你可以通过 `--origins-domains example.com,foo.bar` 传入可信域名列表。启用后，Gixy 会基于 Public Suffix List 以“可注册域”为单位识别来源，并标记那些放行域外值的正则。

## 如何发现？
"简单粗暴" 的办法：
- 找到所有对 `$http_origin` 或 `$http_referer` 进行校验的 `if` 指令；
- 确认这些正则没有问题。

错误示例：
```nginx
if ($http_origin ~* ((^https://www\.yandex\.ru)|(^https://ya\.ru)$)) {
	add_header 'Access-Control-Allow-Origin' "$http_origin";
	add_header 'Access-Control-Allow-Credentials' 'true';
}
```

TODO(buglloc): 覆盖正则编写中的典型问题
TODO(buglloc): Regex Ninja?

## 如何规避？
- 修正你的正则，或干脆放弃它 :)
- 如果你对 `Referer` 使用正则校验，那么也可以（不一定）考虑使用 [ngx_http_referer_module](https://nginx.org/en/docs/http/ngx_http_referer_module.htmll)；
- 对于 `Origin`，通常更好的做法是完全避免正则，而是使用 `map` 白名单：

```nginx
map $http_origin $allow_origin {
    ~^https://([A-Za-z0-9\-]+\.)?example\.com(?::[0-9]{1,5})?$ $http_origin;
    default "";
}
add_header Access-Control-Allow-Origin $allow_origin always;
```

Gixy 已能识别该模式，并会分析用于设置 `Access-Control-Allow-Origin` 的正则 `map` 键。

--8<-- "zh/snippets/nginx-extras-cta.md"
