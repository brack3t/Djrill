# For python 3 compatibility, see http://python3porting.com/problems.html#nicer-solutions
import sys

if sys.version < '3':
    def b(x):
        return x
else:
    import codecs

    def b(x):
        return codecs.latin_1_encode(x)[0]