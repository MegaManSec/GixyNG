# [add_header_multiline] Multiline response headers

You should avoid using multiline response headers, because:
  * they are deprecated (see [RFC 7230](https://tools.ietf.org/html/rfc7230#section-3.2.4));
  * some HTTP-clients and web browser never supported them (e.g. IE/Edge/Nginx).

## How can I find it?
Misconfiguration example:
```nginx
# https://nginx.org/en/docs/http/ngx_http_headers_module.html#add_header
add_header Content-Security-Policy "
    default-src: 'none';
    script-src data: https://yastatic.net;
    style-src data: https://yastatic.net;
    img-src data: https://yastatic.net;
    font-src data: https://yastatic.net;";

# https://nginx-extras.getpagespeed.com/modules/headers-more/
more_set_headers -t 'text/html text/plain'
    'X-Foo: Bar
        multiline';
```

## What can I do?

Use variable nesting to split long headers across multiple lines in your config file while keeping the actual header value on a single line:

```nginx
# Split a long CSP header across multiple lines using variables
set $csp_default "default-src 'self'";
set $csp_script "script-src 'self' https://cdn.example.com";
set $csp_style "style-src 'self' https://cdn.example.com";
set $csp_img "img-src 'self' data: https://cdn.example.com";
set $csp_font "font-src 'self' https://cdn.example.com";

set $csp "${csp_default}; ${csp_script}; ${csp_style}; ${csp_img}; ${csp_font}";
add_header Content-Security-Policy $csp;
```

Or use progressive concatenation:

```nginx
set $csp "default-src 'self'; ";
set $csp "${csp}script-src 'self' https://cdn.example.com; ";
set $csp "${csp}style-src 'self' https://cdn.example.com; ";
set $csp "${csp}img-src 'self' data:; ";
set $csp "${csp}font-src 'self'";

add_header Content-Security-Policy $csp;
```

This keeps your config readable while producing a valid single-line header.

See also: [ServerFault: How to split nginx config across multiple lines](https://serverfault.com/questions/780075/how-to-split-the-nginx-config-across-multiple-lines)
 
--8<-- "en/snippets/nginx-extras-cta.md"