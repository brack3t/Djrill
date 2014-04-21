from setuptools import setup
import re

# define __version__ and __minor_version__ from djrill/_version.py,
# but without importing from djrill (which would break setup)
with open("djrill/_version.py") as f:
    code = compile(f.read(), "djrill/_version.py", 'exec')
    exec(code)


def long_description_from_readme(rst):
    # In release branches, freeze some external links to refer to this X.Y version:
    if not "dev" in __version__:
        rst = re.sub(r'branch=master', 'branch=v' + __minor_version__, rst)  # Travis build status
        rst = re.sub(r'/latest', '/v' + __minor_version__, rst)  # ReadTheDocs
    return rst

with open('README.rst') as f:
    long_description = long_description_from_readme(f.read())

setup(
    name="djrill",
    version=__version__,
    description='Mandrill transactional email for Django',
    keywords="django, mailchimp, mandrill, email, email backend",
    author="Kenneth Love <kenneth@brack3t.com>, Chris Jones <chris@brack3t.com>",
    author_email="kenneth@brack3t.com",
    url="https://github.com/brack3t/Djrill/",
    license="BSD License",
    packages=["djrill"],
    zip_safe=False,
    install_requires=["requests>=1.0.0", "django>=1.3"],
    include_package_data=True,
    test_suite="runtests.runtests",
    tests_require=["mock"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Django",
        "Environment :: Web Environment",
    ],
    long_description=long_description,
)
