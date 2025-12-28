import re
from urllib.parse import urlparse

import gixy
from gixy.plugins.plugin import Plugin


class proxy_pass_normalized(Plugin):
    r"""
    This plugin detects if there is any path component (slash or more)
    after the host in a proxy_pass directive.
    Example flagged directives:
        proxy_pass http://backend/;
        proxy_pass http://backend/foo/bar;
    """

    summary = "proxy_pass path normalization issues."
    severity = gixy.severity.MEDIUM
    description = "A path (beginning with a slash) after the host in proxy_pass leads to unexpected encoding."
    help_url = "https://gixy.io/plugins/proxy_pass_normalized/"
    directives = ["proxy_pass"]

    def __init__(self, config):
        super(proxy_pass_normalized, self).__init__(config)
        self.num_pattern = re.compile(r"\$\d+")

    def audit(self, directive):
        rewrite_fail = False
        parent = directive.parent

        if not parent:
            return

        # Only analyze HTTP context: inside location, or inside if/limit_except within location.
        # This avoids false positives for the stream module, where proxy_pass has different semantics.
        effective_location = None
        if parent.name == 'location':
            effective_location = parent
        elif parent.name in ['limit_except', 'if']:
            grandparent = parent.parent
            if grandparent and grandparent.name == 'location':
                effective_location = grandparent

        if not effective_location:
            # Not in HTTP location context -> skip
            return

        # Skip exact-match locations where normalization concerns do not apply
        if effective_location.modifier == '=':
            return

        proxy_pass_args = directive.args

        if proxy_pass_args[0].startswith("$") and '/' not in proxy_pass_args[0]:
            # If proxy pass destination is defined by only a variable, it is not possible to check for path normalization issues
            return

        parsed = urlparse(proxy_pass_args[0])

        host = parsed.netloc
        path = parsed.path
        if host == "unix:":
            path_parts = path.split(":", 1)
            host = path_parts[0]
            path = path_parts[1] if len(path_parts) > 1 else ""

        for rewrite in directive.find_directives_in_scope("rewrite"):
            if (
                rewrite.pattern == "^"
                and rewrite.replace == "$request_uri"
            ):
                if path:
                    # Check for $uri or any numbered variable in the path.
                    if "$uri" in path or self.num_pattern.search(path):
                        return
                    rewrite_fail = True
                    break
                else:
                    if "$uri" in host or self.num_pattern.search(host):
                        return
                    rewrite_fail = True
                    break

        if not path and not rewrite_fail:
            return

        self.add_issue(
            directive=[directive, directive.parent],
            reason = (
                "A path is present after the host in `proxy_pass` without using `$request_uri` and a variable (for example, `$1` or `$uri`). "
                "This can lead to path decoding or double-encoding issues."
            )
        )
