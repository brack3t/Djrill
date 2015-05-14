VERSION = (1, 4, 0)
__version__ = '.'.join([str(x) for x in VERSION[:3]])  # major.minor.patch
if len(VERSION) > 3:  # x.y.z-pre.release (note the hyphen)
    __version__ += '-' + '.'.join([str(x) for x in VERSION[3:]])
__minor_version__ = '.'.join([str(x) for x in VERSION[:2]])  # Sphinx's X.Y "version"
