
from os import path

# Load __version__ from disk.
here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'VERSION')) as fp:
    __version__ = fp.read().strip()
