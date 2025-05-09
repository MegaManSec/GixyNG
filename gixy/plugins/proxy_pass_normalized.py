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

    summary = "Detect path after host in proxy_pass (potential URL decoding issue)"
    severity = gixy.severity.MEDIUM
    description = "A path (beginning with a slash) after the host in proxy_pass leads to the path being decoded and normalized before proxying downstream, leading to unexpected behavior related to encoded slashes like %2F..%2F. Likewise, the usage of 'rewrite ^ $request_uri;' without using '$1' or '$uri' (or another captured group) in the path of proxy_pass leads to double-encoding of paths."
    help_url = "https://joshua.hu/proxy-pass-nginx-decoding-normalizing-url-path-dangerous#nginx-proxy_pass"
    directives = ["proxy_pass"]

    def __init__(self, config):
        super(proxy_pass_normalized, self).__init__(config)
        self.num_pattern = re.compile(r"\$\d+")

    def audit(self, directive):
        proxy_pass_args = directive.args
        rewrite_fail = False
        parent = directive.parent

        if not proxy_pass_args:
            return

        if not parent or parent.name != 'location' or parent.modifier == '=':
            return

        if proxy_pass_args[0].startswith("$") and '/' not in proxy_pass_args[0]:
            # If proxy pass destination is defined by only a variable, it is not possible to check for path normalization issues
            return

        parsed = urlparse(proxy_pass_args[0])

        if not parsed:
            return

        host = parsed.netloc
        path = parsed.path
        if host == "unix:":
            path_parts = path.split(":", 1)
            host = path_parts[0]
            path = path_parts[1] if len(path_parts) > 1 else ""

        for rewrite in directive.find_directives_in_scope("rewrite"):
            if (
                getattr(rewrite, "pattern", None) == "^"
                and getattr(rewrite, "replace", None) == "$request_uri"
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
            severity=self.severity,
            directive=[directive, directive.parent],
            reason=(
                "Found a path after the host in proxy_pass, without using $request_uri and a variable (such as $1 or $uri). "
                "This can lead to path decoding issues or double-encoding issues."
            ),
        )
