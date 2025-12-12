# Variables & Drop-ins

## Custom variables drop-ins

Some third-party NGINX modules define additional variables (e.g. `$brotli_ratio`). By default, Gixy warns when it cannot resolve a variable. You can teach Gixy about extra variables via simple drop-in files.

## Enabling drop-ins

Provide one or more directories containing variable definitions using either CLI or config:

- CLI: `--vars-dirs /etc/gixy/vars,~/.config/gixy/vars`
- gixy.cfg: `vars-dirs = [/etc/gixy/vars, ~/.config/gixy/vars]`

All files with `.cfg` or `.conf` extensions inside those directories are read.

## File format

Each non-empty, non-comment line defines one variable as `name value`. Supported value forms:

- Quoted literal: `'...'` or `"..."` → treated as a literal value (non user-controlled)
- Regex: `r'...'` or `r"..."` → a regular expression describing allowed content
- `none`/`null` (case-insensitive) → mark as non user-controlled
- Trailing comma after the value is tolerated

Examples:

```cfg
# /etc/gixy/vars/nginx-module-brotli.cfg
brotli_ratio none

# /etc/gixy/vars/nginx-module-foo.cfg
foo_host "example.com"
foo_uri  r'/[^\s]*',
```

Prefix variables are supported using names ending with `_` (like built-ins), e.g. `http_` will match `$http_foo`.

## Notes

- Drop-in variables override built-ins when names collide.
- Only variables referenced during analysis are instantiated.
- This mechanism affects variable resolution only; it does not change NGINX behavior.


