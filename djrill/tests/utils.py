import sys


# Backport from Django 1.8 (django.test.utils)
# with fix suggested by https://code.djangoproject.com/ticket/21049
def reset_warning_registry():
    """
    Clear warning registry for all modules. This is required in some tests
    because of a bug in Python that prevents warnings.simplefilter("always")
    from always making warnings appear: http://bugs.python.org/issue4180

    The bug was fixed in Python 3.4.2.
    """
    key = "__warningregistry__"
    for mod in list(sys.modules.values()):
        if hasattr(mod, key):
            getattr(mod, key).clear()
