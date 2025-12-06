import re

import gixy
from gixy.plugins.plugin import Plugin
from gixy.core.variable import compile_script


class alias_traversal(Plugin):
    r"""
    Insecure examples:
        location /files {
            alias /home/;
        }
        location ~ /site/(l\.)(.*) {
            alias /lol$1/$2;
        }
    """
    summary = 'Path traversal via misconfigured alias.'
    severity = gixy.severity.HIGH
    description = (
        "Using alias in a prefixed location that doesn't end with directory separator "
        "could lead to path traversal vulnerability."
    )
    help_url = 'https://github.com/dvershinin/gixy/blob/master/docs/en/plugins/aliastraversal.md'
    directives = ['alias']

    def audit(self, directive):
        for location in directive.parents:
            if location.name != 'location':
                continue

            if location.modifier in ('~', '~*'):
                self._check_regex_location(directive, location)
            elif not location.modifier or location.modifier == '^~':
                self._check_prefix_location(directive, location)
            return

    def _check_prefix_location(self, directive, location):
        """Check prefix-based locations (no modifier or ^~)."""
        if not location.path.endswith('/'):
            severity = gixy.severity.HIGH if directive.path.endswith('/') else gixy.severity.MEDIUM
            self._report_issue(directive, location, severity)

    def _check_regex_location(self, directive, location):
        """Check regex-based locations (~ or ~*)."""
        # Parse alias path into literal strings and regex variables
        alias_parts = compile_script(directive.path)

        # Unescape the location regex for matching (e.g., \. -> .)
        location_pattern = re.sub(r"\\(.)", r"\1", location.path)

        search_pos = 0
        prev_part = None

        for part in alias_parts:
            if not part.regexp:
                # Literal string part - just track it
                prev_part = part
                continue

            # This is a regex variable (e.g., $1) - find its capture group in location
            capture_group = '(' + str(part.value) + ')'
            group_pos = location_pattern.find(capture_group, search_pos)

            if group_pos < 0:
                # Capture group not found in location pattern
                prev_part = part
                continue

            search_pos = group_pos

            # Check if location has slash before capture group
            location_has_slash_before = (
                (group_pos == 0 and part.must_startswith('/')) or
                (group_pos > 0 and (location_pattern[group_pos - 1] == '/' or part.must_startswith('/')))
            )

            # Determine vulnerability based on alias structure
            if prev_part is None:
                # Alias starts with regex variable - always dangerous
                self._report_issue(directive, location, gixy.severity.HIGH)
            elif not location_has_slash_before:
                # No slash boundary in location before capture
                alias_has_slash_before = str(prev_part.value).endswith('/')
                if alias_has_slash_before:
                    # alias /foo/$1 with location /bar(.*)
                    if part.can_startswith('.'):
                        if part.can_contain('/'):
                            self._report_issue(directive, location, gixy.severity.HIGH)
                        else:
                            self._report_issue(directive, location, gixy.severity.MEDIUM)
                else:
                    # alias /foo$1 with location /bar(.*)
                    self._report_issue(directive, location, gixy.severity.MEDIUM)
            else:
                # Location has slash before capture - check alias
                alias_has_slash_before = str(prev_part.value).endswith('/')
                if not alias_has_slash_before and not part.must_startswith('/'):
                    # location /site/(.*) with alias /lol$1 (missing slash)
                    self._report_issue(directive, location, gixy.severity.MEDIUM)

            prev_part = part

    def _report_issue(self, directive, location, severity):
        self.add_issue(
            severity=severity,
            directive=[directive, location]
        )
