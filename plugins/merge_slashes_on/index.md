# [merge_slashes_on] Enabling `merge_slashes`

## What this check looks for

This plugin looks for `merge_slashes` directives that are explicitly set to `on`.

## Why this is a problem

`merge_slashes on` collapses repeated slashes in the URI path. If NGINX and your upstream (or any auth middleware, cache, or WAF) do not normalize paths the same way, an attacker may be able to use repeated-slash variants to bypass routing rules or access controls that were written against a different interpretation of the path.

## Bad configuration

```
http {
    merge_slashes on;
}
```

## Better configuration

```
http {
    merge_slashes off;
}
```

With `merge_slashes off`, you avoid hidden path normalization that can differ from upstream behavior.

## Additional notes

If you intentionally want a canonical form for paths (for example to reduce duplicate routes) and you have verified your upstream and any intermediaries apply the same normalization rules, enabling it can be acceptable. Use with caution.
