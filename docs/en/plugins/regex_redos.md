# Regular Expression Denial of Service (ReDoS)

ReDoS (Regular Expression Denial of Service) occurs when a regex pattern with certain structures causes catastrophic backtracking on specially crafted input, consuming excessive CPU time.

## Why this matters

nginx uses PCRE regular expressions in several directives where user-controlled input is matched:
- `location ~ pattern` - matches request URI
- `if ($var ~ pattern)` - matches variables like `$http_referer`, `$request_uri`
- `rewrite pattern replacement` - matches request URI
- `server_name ~pattern` - matches Host header

An attacker who can craft input matching a vulnerable regex can cause nginx workers to hang, leading to denial of service with minimal attack resources.

## Insecure example

```nginx
# Catastrophic backtracking for long "a" runs
location ~ ^/(a|aa|aaa|aaaa)+$ {
    return 200 "ok";
}
```

A path like `/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaab` can tie up CPU for a long time.

## Safer alternatives

- Anchor and simplify patterns; avoid nested alternations and ambiguous repetitions
- Prefer explicit, linear-time constructs where possible
- Constrain input length before applying expensive regexes

```nginx
# Safer: anchored and simplified
location ~ ^/a+$ {
    return 200 "ok";
}
```

## References

- [OWASP: Regular expression Denial of Service](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS)
- [Cloudflare: Details of the Cloudflare outage on July 2, 2019](https://blog.cloudflare.com/details-of-the-cloudflare-outage-on-july-2-2019/) - a famous ReDoS incident

--8<-- "en/snippets/nginx-extras-cta.md"
