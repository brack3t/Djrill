from setuptools import setup

with open('LICENSE') as file:
    license_text = file.read()
with open('README.rst') as file:
    long_description = file.read()

setup(
    name="djrill",
    version="0.3.0",
    description='Django email backend for Mandrill.',
    keywords="django, mailchimp, mandrill, email, email backend",
    author="Kenneth Love <kenneth@brack3t.com>, Chris Jones <chris@brack3t.com>",
    author_email="kenneth@brack3t.com",
    url="https://github.com/brack3t/Djrill/",
    license=license_text,
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
    long_description=long_description,
)
