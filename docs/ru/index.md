GIXY
====
[![Mozilla Public License 2.0](https://img.shields.io/badge/license-MPLv2.0-brightgreen?style=flat-square)](https://github.com/dvershinin/gixy/blob/master/LICENSE)
[![Python tests](https://github.com/dvershinin/gixy/actions/workflows/pythonpackage.yml/badge.svg)](https://github.com/dvershinin/gixy/actions/workflows/pythonpackage.yml)
[![Your feedback is greatly appreciated](https://img.shields.io/maintenance/yes/2025.svg?style=flat-square)](https://github.com/dvershinin/gixy/issues/new)
[![GitHub issues](https://img.shields.io/github/issues/dvershinin/gixy.svg?style=flat-square)](https://github.com/dvershinin/gixy/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/dvershinin/gixy.svg?style=flat-square)](https://github.com/dvershinin/gixy/pulls)

# Обзор
<img style="float: right;" width="192" height="192" src="../gixy.png" alt="Логотип Gixy">

Gixy — это инструмент для анализа конфигурации Nginx.
Его цель — предотвращать ошибки конфигурации безопасности и автоматизировать выявление проблем.

В настоящее время поддерживаются Python 3.6–3.13.

Дисклеймер: Gixy хорошо протестирован на GNU/Linux; на других ОС возможны нюансы.

!!! tip "Укрепляйте NGINX с поддерживаемыми RPM"
    Используйте NGINX Extras от GetPageSpeed для постоянно обновляемого NGINX и модулей на RHEL/CentOS/Alma/Rocky.
    [Подробнее](https://nginx-extras.getpagespeed.com/).

# Что умеет
Сейчас Gixy выявляет:

*   [[ssrf] Подделка серверных запросов](plugins/ssrf.md)
*   [[http_splitting] HTTP‑разделение](plugins/httpsplitting.md)
*   [[origins] Проблемы проверки Referer/Origin](plugins/origins.md)
*   [[add_header_redefinition] Переопределение заголовков через "add_header"](plugins/addheaderredefinition.md)
*   [[host_spoofing] Подделка заголовка Host](plugins/hostspoofing.md)
*   [[valid_referrers] none в valid_referers](plugins/validreferers.md)
*   [[add_header_multiline] Многострочные заголовки ответа](plugins/addheadermultiline.md)
*   [[alias_traversal] Траверс путей из‑за неправильного alias](plugins/aliastraversal.md)
*   [[if_is_evil] if опасен в контексте location](plugins/if_is_evil.md)
*   [[allow_without_deny] allow без deny](plugins/allow_without_deny.md)
*   [[add_header_content_type] Установка Content‑Type через add_header](plugins/add_header_content_type.md)
*   [[resolver_external] Использование внешних DNS‑резолверов](plugins/resolver_external.md)
*   [[version_disclosure] Раскрытие версии](plugins/version_disclosure.md)
*   [[proxy_pass_normalized] Нормализация/декодирование пути при proxy_pass](plugins/proxy_pass_normalized.md)
*   [[regex_redos] Регэксп может вызвать ReDoS](plugins/regex_redos.md)

См. также задачи с меткой ["new plugin"](https://github.com/dvershinin/gixy/issues?q=is%3Aissue+is%3Aopen+label%3A%22new+plugin%22).

# Установка

## CentOS/RHEL и другие RPM‑системы

```bash
yum -y install https://extras.getpagespeed.com/release-latest.rpm
yum -y install gixy
```

### Другие системы

Gixy публикуется на [PyPI](https://pypi.python.org/pypi/gixy-ng). Рекомендуемый способ установки — через pip:

```bash
pip install gixy-ng
```

Запустите Gixy и посмотрите результат:
```bash
gixy
```

# Использование
По умолчанию Gixy анализирует конфигурацию Nginx по пути `/etc/nginx/nginx.conf`.

Можно указать нужный путь:
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

Или пропустить часть проверок:
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

Другие аргументы смотрите в справке: `gixy --help`

Можно передать конфигурацию через stdin, например:

```bash
echo "resolver 1.1.1.1;" | gixy -
```

## Использование Docker
Образ доступен на Docker Hub: [getpagespeed/gixy](https://hub.docker.com/r/getpagespeed/gixy/).
Смонтируйте конфиг как том и передайте путь к нему при запуске контейнера:
```
$ docker run --rm -v `pwd`/nginx.conf:/etc/nginx/conf/nginx.conf getpagespeed/gixy /etc/nginx/conf/nginx.conf
```

Если у вас уже есть образ с конфигурацией Nginx, можно примонтировать её во второй контейнер:
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

# Вклад
Мы всегда рады вашему участию! Вы можете:
  * Открыть issue с предложениями и описанием проблем;
  * Сделать форк и отправить pull request;
  * Улучшить документацию.

Требования к коду:
  * Соблюдайте [pep8](https://www.python.org/dev/peps/pep-0008/) по возможности;
  * Pull‑request с новыми плагинами должен содержать юнит‑тесты.
