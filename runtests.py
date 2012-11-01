# python setup.py test
#   or
# python runtests.py

import sys
from django.conf import settings

APP='djrill'

settings.configure(
    DEBUG=True,
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
        }
    },
    ROOT_URLCONF=APP+'.urls',
    INSTALLED_APPS=(
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.admin',
        APP,
    )
)

from django.test.simple import DjangoTestSuiteRunner

def runtests():
    test_runner = DjangoTestSuiteRunner(verbosity=1)
    failures = test_runner.run_tests([APP, ])
    sys.exit(failures)

if __name__ == '__main__':
    runtests()
