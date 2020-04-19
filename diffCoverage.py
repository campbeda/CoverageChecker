#!/usr/bin/env python

'''
The purpose of this script is to validate lines added in diff against coverage report.
Diff is provided as script input, either as a file or from stdin. Diff must be in
"unified diff format" for accurate parsing. Coverage report is provided as an input
file. Report must be in JSON format, and should follow the same output format generated
by `coverage.py` when `coverage json` is invoked.
'''

import argparse
import json
import re
import sys

# Color Codes
ESC='\033[0m'
GREEN='\033[32m'
RED='\033[31m'

def generateDiffAdditions(diff):
    '''Build dictionary mapping file name to line additions.'''
    additions = {}
    files = re.split(r'^diff --git.*$', diff, flags=re.MULTILINE)

    for f in files:
        if not f:
            continue
        lines = f.splitlines()

        # Manually iterate since format is well-defined
        lineIter = iter(lines)

        # Get file name
        line = next(lineIter)
        while not '+++' in line:
            line = next(lineIter)
        fileName = line.split('/')[-1]
        additions[fileName] = {}

        # Next line must be start of diff chunk
        line = next(lineIter)
        currentLineNum = 0
        while True:
            if '@@' in line:
                # Get starting line from first value in second tuple
                try:
                    currentLineNum = int(line.split('+')[-1].split(',')[0])
                except ValueError:
                    print("Invalid diff line format: {0}".format(line))
                    sys.exit(1)
            elif line.startswith('+'):
                additions[fileName][currentLineNum] = line[1:]
                currentLineNum += 1
            elif not line.startswith('-'):
                currentLineNum += 1
            try:
                line = next(lineIter)
            except StopIteration:
                break

    return additions

def validateCoverage(report, additions):
    '''Build dictionary of additions with missing coverage.'''
    missingCoverage = {}

    for fileName in report["files"]:
        for missingLine in report["files"][fileName]["missing_lines"]:
            if missingLine in report["files"][fileName]["excluded_lines"]:
                continue
            # Check if line was added by diff
            if fileName in additions and missingLine in additions[fileName]:
                if fileName not in missingCoverage:
                    missingCoverage[fileName] = []
                missingStr = "{0} {1}".format(missingLine, additions[fileName][missingLine])
                missingCoverage[fileName].append(missingStr)
    return missingCoverage

def printCoverage(missingCoverage):
    '''Print success if there is no missing coverage. If there is missing coverage,
       print failure and display missing coverage per file.'''

    isatty = sys.stdout.isatty()
    if not missingCoverage:
        if isatty:
            print(GREEN + "Success!" + ESC)
        else:
            print("Success!")
        sys.exit(0)
    else:
        if isatty:
            print(RED + "Failure" + ESC)
        else:
            print("Failure")
        print()
        print("Changes missing coverage:")
        for fileName in missingCoverage:
            print(fileName + ":")
            for line in missingCoverage[fileName]:
                print(line)
            print()
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Validate diff against coverage report.')
    parser.add_argument('-d', '--diff', action='store', dest='diff',
                        help='Path to diff file. Omit to use stdin.')
    parser.add_argument('-r', '--report', action="store", dest="report", required=True,
                        help='Path to coverage report.')
    results = parser.parse_args()

    # Read diff into string
    if results.diff is None:
        diff = sys.stdin.read()
    else:
        try:
            diff = open(results.diff, 'r').read()
        except FileNotFoundError:
            print("file {} does not exist".format(results.diff))
            sys.exit(1)

    # Read report into dictionary
    try:
        report = json.load(open(results.report, 'r'))
    except FileNotFoundError:
        print("file {} does not exist".format(results.report))
        sys.exit(1)
    except ValueError:
        print("{} must be in valid JSON format".format(results.report))
        sys.exit(1)

    # Determine which lines were added by diff
    additions = generateDiffAdditions(diff)

    # Compare missing coverage to diff
    missingCoverage = validateCoverage(report, additions)

    # Print missing coverage and return success or failure
    printCoverage(missingCoverage)
