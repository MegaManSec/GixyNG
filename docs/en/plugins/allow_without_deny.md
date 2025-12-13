---
title: "Allow Without Deny"
description: "Fix ineffective access controls. Allowing an IP range without a 'deny all' directive leaves your NGINX resources open to the public."
---

# [allow_without_deny] `allow` without `deny`

When a configuration block contains `allow` directive with some IP address or subnet, it most likely should also contain `deny all;` directive (or it should be enforced somewhere else).
**Otherwise, there's basically no access limitation.**

## Bad Example

```nginx
location / {
      root /var/www/;
      allow 10.0.0.0/8;
      . . .
}
```

## Good Example

```nginx
location / {
      root /var/www/;
      allow 10.0.0.0/8;
      deny all;
      . . .
}
```
