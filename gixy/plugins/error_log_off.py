import gixy
from gixy.plugins.plugin import Plugin


class error_log_off(Plugin):
    """
    Insecure example:
        error_log off;
    """

    summary = "error_log set to off."
    severity = gixy.severity.MEDIUM
    description = "The error_log directive should not be set to off. It should be set to a valid file path."
    help_url = "https://gixy.io/plugins/error_log_off/"
    directives = ["error_log"]

    def audit(self, directive):
        if directive.args and directive.args[0].lower() == "off":
            self.add_issue(
                directive=[directive],
                reason = "Configured `error_log off;` which treats 'off' as a filename."
            )
