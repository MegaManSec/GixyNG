GIXY
====
[![Mozilla Public License 2.0](https://img.shields.io/badge/license-MPLv2.0-brightgreen?style=flat-square)](https://github.com/dvershinin/gixy/blob/master/LICENSE)
[![Python tests](https://github.com/dvershinin/gixy/actions/workflows/pythonpackage.yml/badge.svg)](https://github.com/dvershinin/gixy/actions/workflows/pythonpackage.yml)
[![Your feedback is greatly appreciated](https://img.shields.io/maintenance/yes/2025.svg?style=flat-square)](https://github.com/dvershinin/gixy/issues/new)
[![GitHub issues](https://img.shields.io/github/issues/dvershinin/gixy.svg?style=flat-square)](https://github.com/dvershinin/gixy/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/dvershinin/gixy.svg?style=flat-square)](https://github.com/dvershinin/gixy/pulls)

# 概览
<img style="float: right;" width="192" height="192" src="../gixy.png" alt="Gixy 标志">

Gixy 是一款用于分析 Nginx 配置的工具。
目标是预防安全性错误配置并自动化缺陷检测。

当前支持的 Python 版本为 3.6 至 3.13。

声明：Gixy 在 GNU/Linux 上经过充分测试；其他系统可能存在少量差异。

!!! tip "加固 NGINX，使用维护的 RPM"
    使用 GetPageSpeed 提供的 NGINX Extras 在 RHEL/CentOS/Alma/Rocky 上获取持续更新的 NGINX 与模块。
    [了解更多](https://nginx-extras.getpagespeed.com/).

# 功能
Gixy 目前可以发现：

*   [[ssrf] 服务器端请求伪造](plugins/ssrf.md)
*   [[http_splitting] HTTP 拆分](plugins/httpsplitting.md)
*   [[origins] 引用来源（Referer/Origin）校验问题](plugins/origins.md)
*   [[add_header_redefinition] 通过 "add_header" 重定义响应头](plugins/addheaderredefinition.md)
*   [[host_spoofing] 伪造请求的 Host 头](plugins/hostspoofing.md)
*   [[valid_referrers] 在 valid_referers 中使用 none](plugins/validreferers.md)
*   [[add_header_multiline] 多行响应头](plugins/addheadermultiline.md)
*   [[alias_traversal] 错误 alias 导致路径穿越](plugins/aliastraversal.md)
*   [[if_is_evil] 在 location 中使用 if 存在风险](plugins/if_is_evil.md)
*   [[allow_without_deny] 仅 allow 未配套 deny](plugins/allow_without_deny.md)
*   [[add_header_content_type] 使用 add_header 设置 Content‑Type](plugins/add_header_content_type.md)
*   [[resolver_external] 使用外部 DNS 解析器](plugins/resolver_external.md)
*   [[version_disclosure] 版本泄露](plugins/version_disclosure.md)
*   [[proxy_pass_normalized] proxy_pass 归一化/解码路径风险](plugins/proxy_pass_normalized.md)
*   [[regex_redos] 正则可能导致 ReDoS](plugins/regex_redos.md)

更多即将支持的检测项，见 Issues 中的 ["new plugin"](https://github.com/dvershinin/gixy/issues?q=is%3Aissue+is%3Aopen+label%3A%22new+plugin%22)。

# 安装

## CentOS/RHEL 及其他 RPM 系统

```bash
yum -y install https://extras.getpagespeed.com/release-latest.rpm
yum -y install gixy
```

### 其他系统

Gixy 在 [PyPI](https://pypi.python.org/pypi/gixy-ng) 发布，建议使用 pip 安装：

```bash
pip install gixy-ng
```

运行 Gixy 检查结果：
```bash
gixy
```

# 用法
默认分析 `/etc/nginx/nginx.conf`。

也可以指定路径：
```
$ gixy /etc/nginx/nginx.conf

==================== Results ===================

Problem: [http_splitting] Possible HTTP-Splitting vulnerability.
Description: Using variables that can contain "\n" may lead to http injection.
Additional info: https://github.com/dvershinin/gixy/blob/master/docs/ru/plugins/httpsplitting.md
Reason: At least variable "$action" can contain "\n"
Pseudo config:
include /etc/nginx/sites/default.conf;

	server {

		location ~ /v1/((?<action>[^.]*)\.json)?$ {
			add_header X-Action $action;
		}
	}


==================== Summary ===================
Total issues:
    Unspecified: 0
    Low: 0
    Medium: 0
    High: 1
```

跳过某些检查：
```
$ gixy --skips http_splitting /etc/nginx/nginx.conf

==================== Results ===================
No issues found.

==================== Summary ===================
Total issues:
    Unspecified: 0
    Low: 0
    Medium: 0
    High: 0
```

更多参数见帮助：`gixy --help`

也可通过 stdin 传入配置：

```bash
echo "resolver 1.1.1.1;" | gixy -
```

## Docker 用法
镜像托管在 Docker Hub：[getpagespeed/gixy](https://hub.docker.com/r/getpagespeed/gixy/)。
将需分析的配置以卷方式挂载并传入路径：
```
$ docker run --rm -v `pwd`/nginx.conf:/etc/nginx/conf/nginx.conf getpagespeed/gixy /etc/nginx/conf/nginx.conf
```

如果已有包含 Nginx 配置的镜像，也可将其作为卷挂载至 Gixy 容器：
```
$  docker run --rm --name nginx -d -v /etc/nginx
nginx:alpinef68f2833e986ae69c0a5375f9980dc7a70684a6c233a9535c2a837189f14e905

$  docker run --rm --volumes-from nginx dvershinin/gixy /etc/nginx/nginx.conf

==================== Results ===================
No issues found.

==================== Summary ===================
Total issues:
    Unspecified: 0
    Low: 0
    Medium: 0
    High: 0

```

# 参与贡献
欢迎贡献 Gixy！你可以：
  * 提交 Issue 提出改进与问题；
  * Fork 仓库并发起 Pull Request；
  * 改进文档。

代码规范：
  * 遵循 [pep8](https://www.python.org/dev/peps/pep-0008/)；
  * 新插件的 PR 必须包含单元测试。
