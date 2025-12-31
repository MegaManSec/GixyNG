import gixy
from gixy.plugins.plugin import Plugin


class allow_without_deny(Plugin):
    """
    Warn when an 'allow' directive appears in a context without a corresponding
    'deny all;' (or equivalent restriction) in the same context.
    """

    summary = "Allow directives without a deny restriction."
    severity = gixy.severity.HIGH
    description = "Allow directives should typically be paired with a restrictive deny rule (for example, deny all;) in the same context."
    help_url = 'https://gixy.io/plugins/allow_without_deny/'
    directives = ['allow']

    def __init__(self, config):
        super(allow_without_deny, self).__init__(config)
        self._reported_parents = set()

    def audit(self, directive):
        parent = directive.parent
        if not parent:
            return
        if directive.args == ['all']:
            # for example, "allow all" in a nested location which allows access to otherwise forbidden parent location
            return

        key = id(parent)
        if key in self._reported_parents:
            return
        self._reported_parents.add(key)

        deny_found = False
        for child in parent.children:
            if child.name == 'deny':
                deny_found = True
                break

        if not deny_found:
            reason = "No deny rule was found in the same context; add `deny all;` after the `allow` directives."
            self.add_issue(
                directive=[directive] + list(parent.find_recursive('allow')),
                reason=reason
            )


