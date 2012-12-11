from setuptools import setup

setup(
    name="djrill",
    version="0.2.0",
    description='Django email backend for Mandrill.',
    keywords="django, mailchimp, mandrill, email, email backend",
    author="Kenneth Love <kenneth@brack3t.com>, Chris Jones <chris@brack3t.com>",
    author_email="kenneth@brack3t.com",
    url="https://github.com/brack3t/Djrill/",
    license="BSD",
    packages=["djrill"],
    zip_safe=False,
    install_requires=["requests", "django"],
    include_package_data=True,
    test_suite="runtests.runtests",
    tests_require=["mock"],
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Django",
        "Environment :: Web Environment",
    ],
    long_description="""\
Djrill is an email backend for Django users who want to take advantage of the
`Mandrill <http://mandrill.com>`_ transactional email service from MailChimp.

In general, Djrill "just works" with Django's built-in ``django.core.mail``
package. You can also take advantage of Mandrill-specific features like tags,
metadata, and tracking. An optional Django admin interface is included.

Full details are on the `project page <https://github.com/brack3t/Djrill>`_.
""",
)
