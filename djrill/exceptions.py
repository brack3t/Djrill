import json
from requests import HTTPError


def format_response(response):
    """Return a string-formatted version of response

    Format json if available, else just return text.
    Returns "" if neither json nor text available.
    """
    try:
        json_response = response.json()
        return "\n" + json.dumps(json_response, indent=2)
    except (AttributeError, KeyError, ValueError):  # not JSON = ValueError
        try:
            return response.text
        except AttributeError:
            pass
    return ""


class MandrillAPIError(HTTPError):
    """Exception for unsuccessful response from Mandrill API."""
    def __init__(self, status_code, response=None, log_message=None, *args, **kwargs):
        super(MandrillAPIError, self).__init__(*args, **kwargs)
        self.status_code = status_code
        self.response = response  # often contains helpful Mandrill info
        self.log_message = log_message

    def __str__(self):
        message = "Mandrill API response %d" % self.status_code
        if self.log_message:
            message += "\n" + self.log_message
        # Include the Mandrill response, nicely formatted, if possible
        if self.response is not None:
            message += "\nMandrill response: " + format_response(self.response)
        return message


class MandrillRecipientsRefused(IOError):
    """Exception for send where all recipients are invalid or rejected."""
    def __init__(self, message, response=None, *args, **kwargs):
        super(MandrillRecipientsRefused, self).__init__(message, *args, **kwargs)
        self.response = response

    def __str__(self):
        message = self.args[0]
        if self.response is not None:
            message += "\nMandrill response: " + format_response(self.response)
        return message


class NotSupportedByMandrillError(ValueError):
    """Exception for email features that Mandrill doesn't support.

    This is typically raised when attempting to send a Django EmailMessage that
    uses options or values you might expect to work, but that are silently
    ignored by or can't be communicated to Mandrill's API. (E.g., non-HTML
    alternative parts.)

    It's generally *not* raised for Mandrill-specific features, like limitations
    on Mandrill tag names or restrictions on from emails. (Djrill expects
    Mandrill to return an API error for these where appropriate, and tries to
    avoid duplicating Mandrill's validation logic locally.)

    """
