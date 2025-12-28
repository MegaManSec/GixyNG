---
title: "Header Inheritance Issues"
description: "Detects add_header usage that unintentionally drops headers due to inheritance rules. Adding a header in a nested block replaces all add_header values from the parent level."
---

# [add_header_redefinition] Redefining response headers with add_header

## What this check looks for

This plugin looks for nested contexts where `add_header` is used in both places.

## Why this is a problem

`add_header` follows an all-or-nothing inheritance rule: headers from the previous level are inherited only if there are no `add_header` directives at the current level. As soon as you add any header in a nested block, you stop inheriting every header defined above it.

That is how teams end up with security headers on most pages, but missing on "just one location".

## Bad configuration

```nginx
server {
    add_header X-Frame-Options "DENY";
    add_header X-Content-Type-Options "nosniff";

    location /static/ {
        # Looks harmless, but it drops the two headers above for /static/
        add_header Cache-Control "public, max-age=86400";
    }
}
```

Requests under `/static/` will only get `Cache-Control`, and the security headers vanish.

## Better configuration

Option 1: keep all headers at one level (often `server`), and avoid redefining them in child blocks.

```nginx
server {
    add_header X-Frame-Options "DENY";
    add_header X-Content-Type-Options "nosniff";
    add_header Cache-Control "public, max-age=86400";
}
```

Option 2: if you really need headers that vary by location, repeat the important ones in the nested block:

```nginx
server {
    add_header X-Frame-Options "DENY";
    add_header X-Content-Type-Options "nosniff";

    location /static/ {
        add_header X-Frame-Options "DENY";
        add_header X-Content-Type-Options "nosniff";
        add_header Cache-Control "public, max-age=86400";
    }
}
```

## Configuration

You can tune this plugin to only report on specific headers. This is useful if you only care about specific headers and want to ignore noise like caching tweaks.

### headers

You can use the `headers` option to only report dropped headers that match the specified list. By default, this value is empty (reports all dropped headers).

The value should be a comma-separated list of header names.

#### CLI

```bash
# The add_header_redefinition plugin will only report about dropped x-frame-options and content-security-policy headers
gixy --add-header-redefinition-headers "x-frame-options,content-security-policy"
```

#### Config

```ini
[add_header_redefinition]
; only report about dropped x-frame-options and content-security-policy headers
headers = x-frame-options,content-security-policy
```

## Additional information

Recent NGINX versions added `add_header_inherit` to adjust how `add_header` inherits across levels. If you have it available (nginx 1.29.3+), enabling inheritance with `add_header_inherit on;` prevents nested `add_header` blocks from wiping out headers defined at higher levels. See the [documentation](https://nginx.org/en/docs/http/ngx_http_headers_module.html#add_header_inherit).

### How severity is determined

This plugin treats some headers as "secure headers" and escalates severity when they are dropped. Concretely:

- If a nested block drops only non-security headers, the issue is reported as LOW.
- If a nested block drops any header from the secure list below, the issue is reported as MEDIUM.

The following headers are considered security-sensitive:

- `strict-transport-security`
- `content-security-policy`
- `content-security-policy-report-only`
- `x-frame-options`
- `x-content-type-options`
- `permissions-policy`
- `referrer-policy`
- `cross-origin-embedder-policy`
- `cross-origin-opener-policy`
- `cross-origin-resource-policy`
- `x-xss-protection`
- `x-permitted-cross-domain-policies`
- `expect-ct`
- `cache-control`
- `pragma`
- `expires`
- `content-disposition`
