import gixy
from gixy.plugins.plugin import Plugin


class valid_referers(Plugin):
    """
    Insecure example:
        valid_referers none server_names *.webvisor.com;
    """
    summary = 'Used "none" as valid referer.'
    severity = gixy.severity.HIGH
    description = (
        'Using "none" in valid_referers treats requests with no Referer as trusted, '
        'effectively disabling referer-based access control and clickjacking protection.'
    )
    help_url = 'https://gixy.io/plugins/valid_referers/'
    directives = ['valid_referers']

    def audit(self, directive):
        if 'none' in directive.args:
            self.add_issue(directive=directive)
