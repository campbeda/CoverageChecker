# coveragecheck
coveragecheck is a tool that reports lines of code from diff that are not covered (or excluded) in project coverage report. 
The intent is for this tool to be invoked in a continuous integration pipeline to enforce that merging code has full statement 
coverage.

The tool is compatible with any diff in unified diff format, and a coverage report formatted as a JSON dictionary similar to the
output of [coverage.py](https://coverage.readthedocs.io). Example usage is shown below.

## Installing
The simplest way to install is to use pip:
```
pip install coveragecheck
```

The tool can also be installed by cloning this repository and putting coveragecheck.py on your path:
```
git clone https://github.com/jdn5126/CoverageChecker.git
```

## Continuous Integration Pipeline
For an example script for a continuous integration pipeline, check out the GitHub Actions configured for this repository in
`.github/workflows/coverage_check.yml`. These steps should translate to any continuous integration application/automation server.

## Example
The example directory, which contains a simple Python library and test file, allows us to test `coveragecheck`:

Add a new class to `example/lib.py` without any test coverage:
```
class Bar(object):
    def __init__(self, name):
        self.name = name

    def getName(self):
        return self.name
```

Generate the coverage report using [coverage.py](https://coverage.readthedocs.io):
```
$ cd example
$ coverage run -m unittest discover
$ coverage json
```

Invoke `coveragecheck` to show missing coverage:
```
$ git diff | coveragecheck -r coverage.json
Failure
Files missing coverage:

example/lib.py:
16       self.name = name
19       return self.name
```

Add coverage to `test.py`:
```
from lib import Foo, Bar
...

class TestBarCoverage(unittest.TestCase):
    def test_bar(self):
        print( 'TestBarCoverage: test_bar')
        bar = Bar("bar")
        assert bar.getName() == "bar"
```

Regenerate coverage report as shown above, then invoke `coveragecheck`:
```
$ git diff | coveragecheck.py -r coverage.json
Success!
```

## Contributing
Contributions and issues are welcome!

To get started, simply install the required Python dependencies using:
`pip install -r requirements.txt`
