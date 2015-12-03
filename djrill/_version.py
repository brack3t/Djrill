VERSION = (2, 0, 'dev0')  # Remove the 'dev' component in release branches
__version__ = '.'.join([str(x) for x in VERSION])  # major.minor.patch or major.minor.devN
__minor_version__ = '.'.join([str(x) for x in VERSION[:2]])  # Sphinx's X.Y "version"
