#!/bin/bash

# This script executes merge validation checks for Jenkins pipeline.

set -e

BRANCH="" # Feature branch to merge into master
COVER="" # coverage.py args

# 0. Assume master branch is checked out and env variables are set.

# 1. Generate diff between feature branch and master.
git diff $BRANCH > branch.diff

# 2. Merge feature branch into master. Merge conflicts should terminate script.
git merge $BRANCH

# 3. Run coverage report (optionally pass --sources).
coverage run $COVER

# 4. Generate JSON from coverage report.
coverage json

# 5. Compare diff against coverage report.
./diffCoverage.py -d branch.diff -r coverage.json

# 6. Return status to Github?
