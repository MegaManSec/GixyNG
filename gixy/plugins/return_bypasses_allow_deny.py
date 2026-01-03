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

    def __init__(self, config):
        super(return_bypasses_allow_deny, self).__init__(config)
        self._reported_parents = set()

    def audit(self, directive):
        parent = directive.parent

        if not parent:
            return

        key = id(parent)
        if key in self._reported_parents:
            return
        self._reported_parents.add(key)

        return_directive = list(parent.find_recursive("return"))
        if return_directive:
            all_allow_directives = list(parent.find_recursive("allow"))
            all_deny_directives = list(parent.find_recursive("deny"))
            self.add_issue(
                directive=[directive] + return_directive + all_allow_directives + all_deny_directives,
                reason="`allow`/`deny` do not restrict responses produced by `return` in the same scope."
            )
