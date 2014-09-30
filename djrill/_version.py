VERSION = (1, 3, 0, 'dev1')  # Remove the 'dev1' component in release branches
__version__ = '.'.join([str(x) for x in VERSION])
__minor_version__ = '.'.join([str(x) for x in VERSION[:2]])  # Sphinx's X.Y "version"
