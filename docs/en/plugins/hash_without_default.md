---
title: "Map Default Value Missing"
description: "Security best practice: Always define a safe 'default' value in NGINX map and geo blocks to prevent unhandled keys from bypassing logic."
---

# [hash_without_default] Missing default in hash blocks (`map`, `geo`)

Hash-like blocks such as `map` and `geo` should define a safe `default` value. Without it, unexpected keys may fall through to an unintended state, potentially bypassing security controls.

## Insecure examples

```nginx
# No default → unknown keys inherit nothing/surprising behavior
map $request_uri $allowed {
    /admin 0;
}

# No default in geo
geo $block_client {
    192.0.2.0/24 1;
}
```

## Safer alternatives

```nginx
# Provide a safe default
map $request_uri $allowed {
    default 1;      # deny by default
    /admin 0;       # allow only if set explicitly by later logic
}

# Provide a safe default in geo
geo $block_client {
    default 0;      # not blocked by default
    192.0.2.0/24 1; # block these
}
```

Choose defaults that align with least privilege (deny by default when controlling access).

## Why it matters

Explicit defaults make behavior predictable and prevent accidental allow/deny gaps when new keys appear or inputs vary unexpectedly.
