---
title: "proxy_path Normalization"
description: "Prevent path traversal and double-decoding issues in proxy_pass. Understand how NGINX normalizes URIs when a path is specified."
---

# [proxy_pass_normalized] `proxy_pass` may decode and normalize paths

When `proxy_pass` includes a path (anything after the host), NGINX will decode percent-encodings and normalize the URL path before proxying. This can lead to:

- Decoding of encoded slashes like `%2F..%2F` into `/../`
- Path normalization side effects
- Double-encoding pitfalls when combined with certain `rewrite` usages

These behaviors may cause upstreams to see different paths than intended, potentially enabling path traversal or bypassing security controls.

## Insecure examples

```nginx
location /api/ {
    # Includes a path component after the host
    proxy_pass http://backend/api/;  # Normalization/decoding may occur
}
```

Combining with a rewrite that copies the full request URI without using captured groups also risks double-encoding:

```nginx
location / {
    rewrite ^ $request_uri;  # copies entire URI
    proxy_pass http://backend/service;  # path present and no $1 or $uri
}
```

## Safer alternatives

- Prefer omitting the path in `proxy_pass`, and let the request path pass through unchanged:

```nginx
location /api/ {
    proxy_pass http://backend;  # No path → upstream receives original path
}
```

- If you must include a path, use a captured group or `$uri` to avoid double-encoding and keep control over the path:

```nginx
location ~ ^/api/(.*)$ {
    proxy_pass http://backend/api/$1;  # Uses captured group
}
```

- Avoid `rewrite ^ $request_uri;` paired with a `proxy_pass` path unless you also include `$1` or `$uri` appropriately.

## Why it matters

Normalizing and decoding can alter how the upstream interprets requests, especially for security-sensitive routing. By removing the path from `proxy_pass` or carefully controlling it with variables, you reduce unexpected behavior.
