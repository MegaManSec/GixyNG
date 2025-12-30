---
title: "Outdated/stale cached DNS records used in proxy_pass"
description: "Detects proxy_pass targets that may keep using cached, stale/outdated IP addresses because hostnames are only resolved at startup. Use a resolver-based proxy_pass (variables) or upstream server ... resolve with a shared zone so DNS TTLs are respected/honored."
---

# [stale_dns_cache] Outdated/stale cached DNS records used in proxy_pass

## What this check looks for

This plugin detects risky `proxy_pass` and `upstream` configurations where NGINX can keep using stale/outdated DNS cache entries, causing requests to be routed to the wrong upstream IP addresses.

GixyNG's `stale_dns_cache` mainly catches two patterns:

- `proxy_pass` points at a literal hostname, for example `proxy_pass https://api.example.com;`,
- `proxy_pass` points to an `upstream`, and one or more `server` entries inside that `upstream` are hostnames without the `resolve` option.

## Why this is a problem

By default, NGINX does not automatically honor DNS TTL values for upstream hostnames. Unless otherwise configured, it resolves upstream hostnames once at startup, then continues using the same resolved IP addresses until NGINX is reloaded or restarted; even if the DNS records change in the meantime. That behavior can lead to traffic being sent to an unintended host and data being exchanged with the wrong upstream.

If you want NGINX to re-resolve names at runtime, you have to opt into it using either:

- variables in `proxy_pass` plus a configured `resolver`, or
- `upstream` servers with the `resolve` parameter plus a configured `resolver` and a shared `zone` (available in NGINX Open Source starting 1.27.3; previously NGINX Plus only).

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
    resolver 127.0.0.1 valid=30s;

    server {
        location / {
            set $backend api.example.com;
            proxy_pass https://$backend;
        }
    }
}
```

One way to force NGINX to resolve addresses of hostnames with `proxy_pass` is to use variables. If there is a variable (any variable at all) in the `proxy_pass` directive, DNS resolution will occur. Note however, that a `resolver` MUST be set for it to work. When using `resolver`, if you do not set the `valid=` option, the DNS record's TTL will be respected; otherwise the record's TTL will not be honored and the `valid=` option will take preference.

### upstream server ... resolve (open source NGINX 1.27.3+)

```nginx
http {
    resolver 127.0.0.1 valid=30s;

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
