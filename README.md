Quick and dirty [JaCoCo](http://www.eclemma.org/jacoco/) test coverage reporter script for [Code Climate](https://codeclimate.com). "It may prove useful to some of you, someday, perhaps... in a somewhat bizarre circumstances."

Based heavily on [Code Climate's Python test reporter](https://github.com/codeclimate/python-test-reporter). In fact, the file about the CIs was blatantly ripped out from that.

# Requirements

Python 3 and the [Requests library](http://docs.python-requests.org/en/master/).

# Usage

`python report-jacoco.py FILENAME [SOURCE_ROOT_DIR] [PROJECT_ROOT_DIR]`

- `FILENAME` should point at JaCoCo's XML report.
- `SOURCE_ROOT_DIR` is the root directory of the tested sources. The Java package names will be prefixed with this.
- `PROJECT_ROOT_DIR` is the root directory of your project. Should be a prefix of `SOURCE_ROOT_DIR`. Useful if you run this from elsewhere.

The script expects you to provide your [authentication token]() in an environmental variable named `CODECLIMATE_REPO_TOKEN`.

# Limitations

JaCoCo does not really measure hits. We just report 1 for every line we deem tested. And a line is deemed to be "tested" is it has more instructions hit than missed.
