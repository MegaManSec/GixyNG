---
title: "Stale DNS records used in proxy_pass"
description: "Detects proxy_pass targets that may keep using outdated IP addresses because hostnames are only resolved at startup. Use a resolver-based proxy_pass (variables) or upstream server ... resolve with a shared zone so DNS TTLs are respected."
---

# [stale_dns] Stale DNS records used in proxy_pass

## What this check looks for

This plugin flags `proxy_pass` configurations where NGINX will resolve a hostname once (on startup or reload) and then keep using that IP address even if DNS changes later.

It mainly catches two patterns:

- `proxy_pass` points at a literal hostname (not an IP, not a unix socket), for example `proxy_pass https://api.example.com;`
- `proxy_pass` points to an `upstream`, and one or more `server` entries inside that upstream are hostnames without `resolve`

It intentionally ignores:

- unix sockets (`unix:`)
- literal IPv4/IPv6 addresses
- localhost-style names (`localhost`, `ip6-localhost`, and `*.localhost`)

## Why this is a problem

By default, a hostname in `proxy_pass` or an upstream `server` is resolved during config load, and NGINX will keep using those IP addresses until the next reload. If the backend IP address of that host ever changes, NGINX will keep sending traffic to the stale address.

If you want NGINX to re-resolve names at runtime, you have to opt into it using either:

- variables in `proxy_pass` plus a configured `resolver`, or
- `upstream` servers with the `resolve` parameter plus a configured `resolver` and a shared `zone`.

## Bad configuration

### static hostname in proxy_pass

```nginx
location / {
    proxy_pass https://api.example.com;
}
```

In this example, NGINX resolves the domain's DNS records on startup, and continues to use them until reload/restart.

### upstream uses hostnames without resolve

```nginx
upstream backend {
    server api-1.example.com;
    server api-2.example.com;
}

server {
    location / {
        proxy_pass http://backend;
    }
}
```

In this example, NGINX will also resolve the domains' DNS records on startup, and continue to use them until reload/restart.

### variables, but without resolver

```nginx
location / {
    set $backend api.example.com;
    proxy_pass https://$backend;
}
```

In this case, the proxy will not work at all, because there is no `resolver` configured.

### upstream with resolve, but no resolver

```nginx
upstream backend {
    zone backend 64k;
    server api.example.com resolve;
}

server {
    location / {
        proxy_pass http://backend;
    }
}
```

Like above, the proxy will not work at all, because there is no `resolver` configured.

## Better configuration

### variables in proxy_pass with a resolver

```nginx
http {
    resolver 10.0.0.1 valid=30s;

    server {
        location / {
            set $backend api.example.com;
            proxy_pass https://$backend;
        }
    }
}
```

One way to force NGINX to resolve addresses of hostnames with `proxy_pass` is to use variables. If there is a variable (any variable at all) in the `proxy_pass` directive, DNS resolution will occur. Note however, that a `resolver` MUST be set for it to work. When using `resolver`, if you do not set the `valid=` option, the DNS record's TTL will be respected.

### upstream server ... resolve (open source NGINX 1.27.3+)

```nginx
http {
    resolver 10.0.0.1 valid=30s;

    upstream backend {
        zone backend 64k;
        server api.example.com resolve;
    }

    server {
        location / {
            proxy_pass http://backend;
        }
    }
}
```

Since NGINX 1.27.3, it has also been possible to specify an upstream server to use the resolver, like above. As with the other example, a `resolver` MUST be set for it to work.

## Additional notes

For more information about this issue, read [this post](https://joshua.hu/nginx-dns-caching).
