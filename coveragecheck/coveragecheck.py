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
import os
import re
import sys

# Color Codes
ESC='\033[0m'
GREEN='\033[32m'
RED='\033[31m'

def generateDiffAdditions(diff, sources=None):
    '''Build dictionary mapping file name to line additions.'''
    additions = {}
    files = re.split(r'^diff --git.*$', diff, flags=re.MULTILINE)

    for f in files:
        if not f:
            continue
        lines = f.splitlines()

        # Manually iterate through file diff since format is well-defined
        lineIter = iter(lines)

        # Get file name
        skip = False
        line = next(lineIter)
        while not line.startswith('+++'):
            try:
                line = next(lineIter)
            except StopIteration:
                # Skip files that do not have diff chunks
                skip = True
                break
        if skip:
            continue

        filePath = line.split('b/')[-1]
        # If sources are passed, file must be in sources directory.
        if sources is not None:
            # Remove basename from filename
            fileName = filePath.split('/')[-1]
            basePath = filePath.replace('/' + fileName, '')
            if basePath not in sources:
                continue

        additions[filePath] = {}

        # Process diff chunks
        currentLineNum = 0
        line = next(lineIter)
        while True:
            if line.startswith('@@'):
                # Get current line number from first value in second tuple
                try:
                    currentLineNum = int(line.split('+', 1)[-1].split(',', 1)[0].rstrip(' @@'))
                except ValueError:
                    print("Invalid diff line format: {0}".format(line))
                    sys.exit(1)
            elif line.startswith('+'):
                # Skip empty lines and special Python keywords
                lineStrip = line[1:].strip()
                if lineStrip and not ( lineStrip.startswith('#') or
                                       lineStrip.startswith('class') or
                                       lineStrip.startswith('def') ):
                    additions[filePath][currentLineNum] = line[1:]
                currentLineNum += 1
            elif not line.startswith('-'):
                currentLineNum += 1
            try:
                line = next(lineIter)
            except StopIteration:
                break

    return additions

def validateCoverage(report, additions):
    '''For each line added in diff, verify line is covered or excluded.'''
    missingCoverage = {}

    for fileName in additions:
        if not fileName.endswith('.py'):
            continue
        # Find corresponding file in coverage report
        fileReport = report["files"].get(fileName, None)
        # Try prepending basename of cwd or stripping filename
        if fileReport is None:
            basename = os.path.basename( os.getcwd() )
            fileReport = report["files"].get(basename + fileName, None)
            if fileReport is None:
                fileReport = report["files"].get(fileName.split('/')[-1])
        for lineNum in additions[fileName]:
            # If python file is not present in coverage report, it must be totally uncovered.
            missing = fileReport is None or ( lineNum not in fileReport["executed_lines"] and
                                              lineNum not in fileReport["excluded_lines"] )
            if missing:
                if fileName not in missingCoverage:
                    missingCoverage[fileName] = []
                missingStr = "{0} {1}".format(lineNum, additions[fileName][lineNum])
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
        print("Files missing coverage:")
        print()
        for fileName in missingCoverage:
            print(fileName + ":")
            for line in missingCoverage[fileName]:
                print(line)
            print()
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
            description='Validate diff against coverage report. Script SHOULD be \
                        invoked from root of repository under test.')
    parser.add_argument('-d', '--diff', action='store', dest='diff',
                        help='Path to diff file. Omit to use stdin.')
    parser.add_argument('-r', '--report', action="store", dest="report", required=True,
                        help='Path to coverage report.')
    parser.add_argument('-s', '--source', action="store", dest="source",
                        help='List of directories within repo to consider for coverage. \
                              Paths are relative to root of repo. Omit for all.')
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

    # Generate list of directories to validate coverage against
    sources = None
    if results.source is not None:
        sources = results.source.split(',')

    # Determine which lines were added by diff
    additions = generateDiffAdditions(diff, sources)

    # Compare missing coverage to diff
    missingCoverage = validateCoverage(report, additions)

    # Print missing coverage and return success or failure
    printCoverage(missingCoverage)

if __name__ == "__main__":
    main()
