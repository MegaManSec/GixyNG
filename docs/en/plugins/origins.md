# [origins] Problems with referrer/origin validation

It's not unusual to use regex for `Referer` or `Origin` headers validation.
It is often necessary for setting the `X-Frame-Options` header (ClickJacking protection) or Cross-Origin Resource Sharing.

The most common errors with this configuration are:
  - regex errors;
  - allow third-party origins.

> Notice: by default, Gixy doesn't check regexes for third-party origins matching.
> You can pass a list of trusted domains by using the option `--origins-domains example.com,foo.bar`.

### CLI and config options

- `--origins-domains domains` (Default: `*`): Comma-separated list of trusted registrable domains. Use `*` to disable third‑party checks. Example: `--origins-domains example.com,foo.bar`.
- `--origins-https-only true|false` (Default: `false`): When true, only the `https` scheme is considered valid for `Origin`/`Referer`.
- `--origins-lower-hostname true|false` (Default: `true`): Normalize hostnames to lowercase before validation.

Config file example:
```
[origins]
domains = example.com, example.org
https-only = true
```

## How can I find it?
"Eazy"-breezy:
  - you have to find all the `if` directives that are in charge of `$http_origin` or `$http_referer` check;
  - make sure your regexes are a-ok.

Misconfiguration example:
```nginx
if ($http_origin ~* ((^https://www\.yandex\.ru)|(^https://ya\.ru)$)) {
	add_header 'Access-Control-Allow-Origin' "$http_origin";
	add_header 'Access-Control-Allow-Credentials' 'true';
}
```

## What can I do?

  - fix your regex or toss it away :)
  - if you use regex validation for `Referer` request header, then, possibly (not 100%), you could use [ngx_http_referer_module](https://nginx.org/en/docs/http/ngx_http_referer_module.htmll);
  - often it's better to avoid regex entirely for `Origin` and use a `map` allowlist:

```nginx
map $http_origin $allow_origin {
    ~^https://([A-Za-z0-9\-]+\.)?example\.com(?::[0-9]{1,5})?$ $http_origin;
    default "";
}
add_header Access-Control-Allow-Origin $allow_origin always;
```

Gixy also understands this pattern, and will also analyze regex map keys feeding `Access-Control-Allow-Origin` in the above example.
