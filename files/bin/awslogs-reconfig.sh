#!/bin/bash
export PYTHONPATH="/var/awslogs/nlm/lib"

exec /var/awslogs/bin/python $* <<EOF
import nlminit
import sys

nlminit.main(sys.argv)
EOF
