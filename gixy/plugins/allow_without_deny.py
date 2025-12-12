import gixy
from gixy.plugins.plugin import Plugin


class allow_without_deny(Plugin):
    """
    Warn when an 'allow' directive appears in a context without a corresponding
    'deny all;' (or equivalent restriction) in the same context.
    """
    summary = 'Found allow directive(s) without deny in the same context.'
    severity = gixy.severity.HIGH
    description = 'The "allow" directives should be typically accompanied by "deny all;" directive.'
    help_url = 'https://gixy.io/plugins/allow_without_deny/'
    directives = ['allow']

    def audit(self, directive):
        parent = directive.parent
        if not parent:
            return
        if directive.args == ['all']:
            # for example, "allow all" in a nested location which allows access to otherwise forbidden parent location
            return

        deny_found = False
        for child in parent.children:
            if child.name == 'deny':
                deny_found = True
        if not deny_found:
            reason = 'You probably want "deny all;" after all the "allow" directives'
            self.add_issue(
                directive=directive,
                reason=reason
            )


