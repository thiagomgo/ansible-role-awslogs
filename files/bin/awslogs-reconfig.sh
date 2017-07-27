#!/var/awslogs/bin/python
from os.path import dirname, join
import sys

# Modify python load path so we can find our stuff
BASE_DIR = dirname(__file__)
LIB_DIR = join(BASE_DIR, 'lib')
sys.path.insert(1, LIB_DIR)

# Import our module
import nlminit

# Run the command
nlminit.main(sys.argv[1:])
