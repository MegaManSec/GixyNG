import gixy
from gixy.plugins.plugin import Plugin


class resolver_external(Plugin):
    """
    Syntax for the directive: resolver 127.0.0.1 [::1]:5353 valid=30s;
    """
    summary = 'Do not use external nameservers for "resolver".'
    severity = gixy.severity.HIGH
    description = 'Using external nameservers allows someone to send spoofed DNS replies to poison the resolver ' \
                  'cache, causing NGINX to proxy HTTP requests to an arbitrary upstream server.'
    help_url = 'https://gixy.io/plugins/resolver_external/'
    directives = ['resolver']

    def audit(self, directive):
        bad_nameservers = directive.get_external_nameservers()
        if bad_nameservers:
            self.add_issue(
                severity=gixy.severity.HIGH,
                directive=[directive, directive.parent],
                reason="Found use of external DNS servers {dns_servers}".format(
                    dns_servers=", ".join(bad_nameservers)
                )
            )


