import gixy
from gixy.plugins.plugin import Plugin


class merge_slashes_on(Plugin):
    """
    Insecure example:
        merge_slashes on;
    """

    summary = "Avoid `merge_slashes on`."
    severity = gixy.severity.MEDIUM
    description = "Enabling `merge_slashes` can cause URI normalization mismatches that may bypass routing or access controls."
    help_url = "https://gixy.io/plugins/merge_slashes_on/"
    directives = ["merge_slashes"]

    def audit(self, directive):
        if not directive.args:
            return

        try:
            value = str(directive.args[0]).strip().lower()
        except (TypeError, IndexError):
            return

        if value == "on":
            self.add_issue(
                directive=directive,
                reason="`merge_slashes` is set to `on`.",
            )
