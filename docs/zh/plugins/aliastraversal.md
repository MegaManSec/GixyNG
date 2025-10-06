# [alias_traversal] 因错误的 alias 配置导致路径穿越

[`alias`](https://nginx.ru/en/docs/http/ngx_http_core_module.html#alias) 指令用于替换指定位置的路径。
例如，以下配置：
```nginx
location /i/ {
    alias /data/w3/images/;
}
```
当请求 `/i/top.gif` 时，将返回文件 `/data/w3/images/top.gif`。

但如果 `location` 未以目录分隔符（即 `/`）结尾：

```nginx
location /i {
    alias /data/w3/images/;
}
```
当请求 `/i../app/config.py` 时，将返回文件 `/data/w3/app/config.py`。

换言之，错误的 `alias` 配置可能允许攻击者读取目标目录之外的文件。

## 如何规避？
很简单：
- 找到所有 `alias` 指令；
- 确保其上级前缀位置以目录分隔符结尾；
- 如果只想映射单个文件，确保位置以 `=` 开头，例如使用 `=/i.gif` 而不是 `/i.gif`。

--8<-- "zh/snippets/nginx-extras-cta.md"
