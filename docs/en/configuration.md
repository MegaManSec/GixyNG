---
title: "Configuration & Usage Guide"
description: "Learn how to configure GixyNG, manage plugins, use CLI options, and set up custom variable drop-ins for your NGINX security scans."
---

# Configuration & Usage Guide

## Configuration (gixy.cfg)

Gixy reads configuration from the following locations (first found wins):

- `/etc/gixy/gixy.cfg`
- `~/.config/gixy/gixy.conf`

You can also pass a custom config path via `-c/--config` and write out a populated template with `--write-config`.

Configuration files use simple `key = value` pairs, optional sections, and support lists with `[a, b, c]` syntax. Keys mirror long CLI flags, with dashes, for example `--disable-includes` becomes `disable-includes`.

Note: the severity filter is CLI-only via `-l` repeats (e.g. `-l`, `-ll`, `-lll`). It is not read from the config file.

## Managing plugins

- **Run only selected plugins**: set `tests` to a comma-separated list of plugin class names.
- **Skip specific plugins**: set `skips` to a comma-separated list of plugin class names.

Examples:

```ini
# Only these plugins will run
tests = if_is_evil, http_splitting

# These plugins will be excluded from the run
skips = origins, version_disclosure
```

## Plugin-specific options

Plugin options can be provided as sectioned keys where the section name is the plugin class name written with hyphens (underscores replaced by hyphens). Keys inside sections also use hyphens. Examples:

```ini
[origins]
domains = example.com, example.org
https-only = true

[regex-redos]
url = ^/api/.*
```

The same effect can be achieved without sections by combining the plugin name and option with a dash, e.g. `origins-domains = ...`, but sections are easier to organize.

## Other useful options

- **Output format**: `format = console|text|json` (same as `-f/--format`)
- **Write report to file**: `output = /path/to/report.txt` (same as `-o/--output`)
- **Disable include processing**: `disable-includes = true` (same as `--disable-includes`)
- **Custom variables directories**: `vars-dirs = [/etc/gixy/vars, ~/.config/gixy/vars]` (see "Custom variables drop-ins")

## Full example

```ini
# gixy.cfg

format = console
output = /tmp/gixy-report.txt
disable-includes = false

# Limit analysis to a subset of plugins
tests = if_is_evil, http_splitting

# Skip some plugins
skips = version_disclosure

# Load custom variable definitions (see variables-dropins)
vars-dirs = [/etc/gixy/vars, ~/.config/gixy/vars]

[origins]
domains = example.com, example.org
https-only = true

[regex-redos]
url = ^/api/.*
```


