import gixy
from gixy.plugins.plugin import Plugin


class return_bypasses_allow_deny(Plugin):
    """
    Insecure example:
        location / {
            allow 127.0.0.1;
            deny all;
            return 200 "hi";
        }
    """

    summary = "Return directive bypasses allow/deny restrictions in the same context."
    severity = gixy.severity.HIGH
    description = "The return directive is executed before allow/deny take effect in the same context. Consider using a named location and try_files, or restructure access control."
    help_url = "https://gixy.io/plugins/return_bypasses_allow_deny/"
    directives = ["allow", "deny"]

    def audit(self, directive):
        parent = directive.parent
        return_directive = []

        if not parent:
            return

        for ctx in parent.find_recursive('return'):
            return_directive.append(ctx)

        if return_directive:
            self.add_issue(
                directive=[directive] + return_directive,
                reason = "`allow`/`deny` do not restrict responses produced by `return` in the same scope."
            )


