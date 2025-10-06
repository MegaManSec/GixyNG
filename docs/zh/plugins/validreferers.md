# [valid_referrers] 在 valid_referers 中使用 `none`

模块 [ngx_http_referer_module](https://nginx.org/en/docs/http/ngx_http_referer_module.html) 可用于基于 `Referer` 阻止访问。
它常被用于设置 `X-Frame-Options`（防点击劫持），也可用于其他场景。

当在 `valid_referers` 中使用 `none` 时，可能导致意外放行或规则变得难以预测。

建议谨慎使用 `none`，并明确列举允许来源或采用更严格的匹配方式。

--8<-- "zh/snippets/nginx-extras-cta.md"
