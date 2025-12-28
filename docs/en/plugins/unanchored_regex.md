---
title: "Unanchored Regex Pattern"
description: "Detects regex locations or matches that are not anchored with ^ and/or $. Unanchored patterns can match unintended URLs and slow request processing."
---

# [unanchored_regex] Regular expression without anchors

## What this check looks for

This plugin flags regular expressions (commonly in `location ~` blocks) that are not anchored to the start and/or end of the string.

## Why this is a problem

Without anchors, the regex engine can match anywhere inside the input. That has two downsides:

- you may match URLs you did not intend to match,
- the engine has to work harder because it can try many starting positions.

## Bad configuration

```nginx
# Matches any URL that contains /v1/ anywhere
location ~ /v1/ {
    # ...
}
```

Another common example:

```nginx
# Matches /foo.php and also /foo.phpanything
location ~ \.php {
    # ...
}
```

## Better configuration

Anchor patterns to reflect what you really mean:

```nginx
location ~ ^/v1/ {
    # ...
}

location ~ \.php$ {
    # ...
}
```

## Additional notes

It's also worth considering whether your regular expressions are vulnerable to ReDoS. See the [regex_redos](https://gixy.io/plugins/regex_redos/) plugin for more information.
