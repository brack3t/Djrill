from setuptools import setup

setup(
    name="djrill",
    version="0.1.0",
    description='Django email backend for Mandrill.',
    long_description='Email backend and new message class to send emails through the Mandrill email service.',
    keywords="django, mailchimp, mandrill, email, email backend",
    author="Kenneth Love <kenneth@brack3t.com>, Chris Jones <chris@brack3t.com>",
    author_email="kenneth@brack3t.com",
    url="https://github.com/brack3t/Djrill/",
    license="BSD",
    packages=["djrill"],
    zip_safe=False,
    install_requires=["requests", "django"],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Django",
        "Environment :: Web Environment",
    ],
)
