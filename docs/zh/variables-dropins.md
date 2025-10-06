### 自定义变量扩展（drop-ins）

一些第三方 NGINX 模块会定义额外的变量（例如 `$brotli_ratio`）。默认情况下，若 Gixy 无法解析某变量，会给出告警。你可以通过简单的扩展文件教会 Gixy 识别这些变量。

#### 启用扩展

使用 CLI 或配置文件提供一个或多个包含变量定义的目录：

- CLI：`--vars-dirs /etc/gixy/vars,~/.config/gixy/vars`
- gixy.cfg：`vars-dirs = [/etc/gixy/vars, ~/.config/gixy/vars]`

上述目录中所有以 `.cfg` 或 `.conf` 结尾的文件都会被读取。

#### 文件格式

每一行（非空、非注释）定义一个变量：`name value`。支持的值形式：

- 引号字面量：`'...'` 或 `"..."` → 作为常量（非用户可控）
- 正则：`r'...'` 或 `r"..."` → 描述允许内容的正则表达式
- `none`/`null`（不区分大小写）→ 标记为非用户可控
- 值后允许保留一个逗号

示例：

```cfg
# /etc/gixy/vars/nginx-module-brotli.cfg
brotli_ratio none

# /etc/gixy/vars/nginx-module-foo.cfg
foo_host "example.com"
foo_uri  r'/[^\s]*',
```

支持前缀变量：变量名以 `_` 结尾（类似内置变量），例如 `http_` 将匹配 `$http_foo`。

#### 说明

- 当变量名冲突时，扩展中的变量会覆盖内置变量；
- 仅在分析期间被引用的变量才会被实例化；
- 该机制只影响变量解析，不会改变 NGINX 的实际行为。
