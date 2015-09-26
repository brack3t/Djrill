from django.conf import settings

from djrill.exceptions import MandrillAPIError, NotSupportedByMandrillError
from ._version import __version__, VERSION


# This backend was developed against this API endpoint.
# You can override in settings.py, if desired.
MANDRILL_API_URL = getattr(settings, "MANDRILL_API_URL",
    "https://mandrillapp.com/api/1.0")
