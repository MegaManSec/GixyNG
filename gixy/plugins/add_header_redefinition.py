import gixy
from gixy.plugins.plugin import Plugin


class add_header_redefinition(Plugin):
    """
    Insecure example (prior to nginx 1.29.3):
        server {
            add_header X-Content-Type-Options nosniff;
            location / {
                add_header X-Frame-Options DENY;
            }
        }

    Secure example (from nginx 1.29.3):
        server {
            add_header X-Content-Type-Options nosniff;
            location / {
                add_header_inherit merge;
                add_header X-Frame-Options DENY;
            }
        }
    """

    summary = 'Nested "add_header" drops parent headers.'
    severity = gixy.severity.LOW
    description = '"add_header" at a nested level replaces inherited headers unless `add_header_inherit merge` is in effect (nginx 1.29.3+).'
    help_url = 'https://gixy.io/plugins/add_header_redefinition/'
    directives = ['server', 'location', 'if']
    options = {'headers': set(), 'merge_reported_headers': True}
    options_help = {
        'headers': 'Only report dropped headers from this allowlist. Case-insensitive. Comma-separated list, e.g. "x-frame-options,content-security-policy".',
        'merge_reported_headers': 'Report headers declared in higher scopes that are not inherited (but were dropped at an intermediate level).'
    }

    def __init__(self, config):
        super(add_header_redefinition, self).__init__(config)
        raw_headers = self.config.get('headers')
        # Normalize configured headers to lowercase set for case-insensitive matching
        if isinstance(raw_headers, (list, tuple, set)):
            self.interesting_headers = set(h.lower().strip() for h in raw_headers if h and isinstance(h, str))
        else:
            self.interesting_headers = set()
        # Define secure headers that should escalate severity
        self.secure_headers = [
            'cache-control',
            'content-security-policy',
            'content-security-policy-report-only',
            'cross-origin-embedder-policy',
            'cross-origin-opener-policy',
            'cross-origin-resource-policy',
            'permissions-policy',
            'referrer-policy',
            'strict-transport-security',
            'x-content-type-options',
            'x-frame-options',
            'x-xss-protection',
            'x-permitted-cross-domain-policies',
            'expect-ct',
            'pragma',
            'expires',
            'content-disposition'
        ]
        self.merge_reported_headers = self.config.get('merge_reported_headers')

    def audit(self, directive):
        if not directive.is_block:
            # Skip all not block directives
            return

        current_headers = self.get_headers(directive)
        if not current_headers:
            return

        mode = self.effective_add_header_inherit_mode(directive)
        # 'merge', parent headers are appended.
        # 'off', inheritance is explicitly cancelled.
        if mode in ('merge', 'off'):
            return

        parent = getattr(directive, 'parent', None)
        if not parent:
            return

        parent_effective = self.effective_headers(parent)
        if not parent_effective:
            return

        if self.merge_reported_headers:
            # headers declared in ancestors (not including this directive)
            declared_above = self.get_headers(parent, inherited=True)
            # headers actually effective here
            current_effective = self.effective_headers(directive)
            diff = declared_above - current_effective
        else:
            diff = parent_effective - current_headers

        if self.interesting_headers:
            diff = diff & self.interesting_headers

        if diff:
            self._report_issue(directive, parent, diff)

    def _report_issue(self, current, parent, diff):
        directives = []
        # Use the parent's scope so we pick up server-level headers and includes.
        scope_add_headers = parent.find_imperative_directives_in_scope("add_header")
        directives.extend(
            d for d in scope_add_headers
            if getattr(d, "header", None) and d.header.lower() in diff
        )
        # and always include the headers at the current and parent level
        directives.extend(current.find("add_header"))
        directives.extend(parent.find("add_header"))

        directives.extend(parent.find("add_header_inherit"))
        directives.extend(current.find("add_header_inherit"))

        is_secure_header_dropped = any(h in self.secure_headers for h in diff)
        issue_severity = gixy.severity.MEDIUM if is_secure_header_dropped else self.severity

        if self.merge_reported_headers:
            reason = "Headers declared in higher scopes `{headers}` are not effective here.".format(
                headers="`, `".join(sorted(diff))
            )
        else:
            reason = "Parent headers `{headers}` were dropped at this level.".format(
                headers="`, `".join(sorted(diff))
            )

        self.add_issue(directive=directives, reason=reason, severity=issue_severity)

    def get_headers(self, directive, inherited=False):
        """
        Headers defined at this level.
        If inherited=True, also include headers declared in the current scope (ancestors + current)
        """
        headers = []
        if inherited:
            headers.extend(directive.find_imperative_directives_in_scope('add_header'))
        headers.extend(directive.find('add_header'))

        if not headers:
            return set()
        return {d.header.lower() for d in headers if getattr(d, "header", None)}

    def effective_add_header_inherit_mode(self, directive):
        """
        add_header_inherit itself is inherited "normally" (nearest definition wins).
        """
        node = directive
        while node is not None:
            inherit_directives = node.find('add_header_inherit')
            mode = None
            # If multiple are present at the same level, the last valid one wins.
            for d in inherit_directives:
                if getattr(d, 'args', None):
                    v = d.args[0].lower()
                    if v in ('on', 'off', 'merge'):
                        mode = v
            if mode is not None:
                return mode
            node = getattr(node, 'parent', None)
        return 'on'

    def effective_headers(self, directive):
        """
        Effective header names at this level, respecting add_header_inherit mode:
          - on    : standard behavior (if any headers here, they replace inherited; else inherit)
          - merge : inherit + append current
          - off   : cancel inheritance entirely (only current headers apply)
        """
        if directive is None:
            return set()

        mode = self.effective_add_header_inherit_mode(directive)
        own = self.get_headers(directive, inherited=False)
        parent = getattr(directive, 'parent', None)
        inherited = self.effective_headers(parent) if parent is not None else set()

        if mode == 'off':
            return set(own)
        if mode == 'merge':
            return set(inherited) | set(own)
        # mode == 'on'
        return set(own) if own else set(inherited)
