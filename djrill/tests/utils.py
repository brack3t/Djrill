import re
import six

__all__ = (
    'BackportedAssertions',
    'override_settings',
)

try:
    from django.test.utils import override_settings

except ImportError:
    # Back-port override_settings from Django 1.4
    # https://github.com/django/django/blob/stable/1.4.x/django/test/utils.py
    from django.conf import settings, UserSettingsHolder
    from django.utils.functional import wraps

    class override_settings(object):
        """
        Acts as either a decorator, or a context manager. If it's a decorator it
        takes a function and returns a wrapped function. If it's a contextmanager
        it's used with the ``with`` statement. In either event entering/exiting
        are called before and after, respectively, the function/block is executed.
        """
        def __init__(self, **kwargs):
            self.options = kwargs
            self.wrapped = settings._wrapped

        def __enter__(self):
            self.enable()

        def __exit__(self, exc_type, exc_value, traceback):
            self.disable()

        def __call__(self, test_func):
            from django.test import TransactionTestCase
            if isinstance(test_func, type) and issubclass(test_func, TransactionTestCase):
                original_pre_setup = test_func._pre_setup
                original_post_teardown = test_func._post_teardown
                def _pre_setup(innerself):
                    self.enable()
                    original_pre_setup(innerself)
                def _post_teardown(innerself):
                    original_post_teardown(innerself)
                    self.disable()
                test_func._pre_setup = _pre_setup
                test_func._post_teardown = _post_teardown
                return test_func
            else:
                @wraps(test_func)
                def inner(*args, **kwargs):
                    with self:
                        return test_func(*args, **kwargs)
            return inner

        def enable(self):
            override = UserSettingsHolder(settings._wrapped)
            for key, new_value in self.options.items():
                setattr(override, key, new_value)
            settings._wrapped = override
            # No setting_changed signal in Django 1.3
            # for key, new_value in self.options.items():
            #     setting_changed.send(sender=settings._wrapped.__class__,
            #                          setting=key, value=new_value)

        def disable(self):
            settings._wrapped = self.wrapped
            # No setting_changed signal in Django 1.3
            # for key in self.options:
            #     new_value = getattr(settings, key, None)
            #     setting_changed.send(sender=settings._wrapped.__class__,
            #                          setting=key, value=new_value)


class BackportedAssertions(object):
    """Handful of useful TestCase assertions backported to Python 2.6/Django 1.3"""

    # Backport from Python 2.7/3.1
    def assertIn(self, member, container, msg=None):
        """Just like self.assertTrue(a in b), but with a nicer default message."""
        if member not in container:
            self.fail(msg or '%r not found in %r' % (member, container))

    # Backport from Django 1.4
    def assertRaisesMessage(self, expected_exception, expected_message,
                            callable_obj=None, *args, **kwargs):
        return six.assertRaisesRegex(self, expected_exception, re.escape(expected_message),
                                     callable_obj, *args, **kwargs)
