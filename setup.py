from setuptools import setup
import re

# define __version__ and __minor_version__ from djrill/_version.py,
# but without importing from djrill (which would break setup)
with open("djrill/_version.py") as f:
    code = compile(f.read(), "djrill/_version.py", 'exec')
    exec(code)


def long_description_from_readme(rst):
    # Patch up some rest substitution variables (references only - not definitions):
    rst = re.sub(r'(?<!\.\. )\|release\|', __version__, rst)
    rst = re.sub(r'(?<!\.\. )\|version\|', __minor_version__, rst)
    rst = re.sub(r'(?<!\.\. )\|buildstatus\|', "", rst)  # hide latest-code Travis status indicator
    rst = re.sub(r'(djrill\.readthedocs\.org/\w+)/latest',
                 r'\1/' + __version__, rst)  # freeze docs link to this version
    return rst

with open('LICENSE') as f:
    license_text = f.read()
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
