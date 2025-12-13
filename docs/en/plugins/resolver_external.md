---
title: "External DNS Resolvers"
description: "Avoid DNS spoofing risks by using local resolvers. Why pointing NGINX directly to public DNS (8.8.8.8) is a security risk for internal proxies."
---

# [resolver_external] Using external DNS nameservers

Using public DNS servers directly in the `resolver` directive can make nginx vulnerable to DNS cache poisoning and off-path response injection. Spoofed DNS replies may poison nginx's cache and cause it to proxy requests to attacker-controlled hosts.

## Insecure example

```nginx
# Public, external resolvers (unsafe)
resolver 1.1.1.1 8.8.8.8;

# Variable-based upstream resolution depends on resolver
set $backend upstream.internal.example;
location / {
    proxy_pass http://$backend;
}
```

## Safer alternatives

- Run a local, caching resolver and point nginx to loopback only:

```nginx
# Use only local resolvers
resolver 127.0.0.1 [::1] valid=10s;
resolver_timeout 5s;
```

- Prefer static upstreams (avoid variable-based `proxy_pass`) when feasible
- Keep `valid` low to reduce cache lifetime; ensure your local resolver is trusted and hardened

## Why it matters

- External resolvers increase the attack surface for response spoofing
- Poisoned cache entries can silently redirect traffic to arbitrary upstreams
- A local resolver (e.g., `unbound`, `dnsmasq`) on loopback significantly mitigates this risk
