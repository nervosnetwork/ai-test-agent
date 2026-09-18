#!/usr/bin/env python3
"""Native unittest runner with exact test IDs; called by pr_workflow run."""
import json
import os
import sys
import unittest
from pathlib import Path


class Result(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []

    def record(self, test, status):
        self.records.append({"selector": test.id(), "status": status, "unstable": False})

    def addSuccess(self, test):
        super().addSuccess(test)
        self.record(test, "passed")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.record(test, "failed")

    def addError(self, test, err):
        super().addError(test, err)
        self.record(test, "failed")

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.record(test, "skipped")

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self.record(test, "skipped")

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self.record(test, "failed")

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        self.record(subtest, "passed" if err is None else "failed")
        if err:
            self.record(test, "failed")


def main():
    program = unittest.main(module=None, testRunner=unittest.TextTestRunner(resultclass=Result, verbosity=2), exit=False)
    result = program.result
    output = os.environ.get("AI_TEST_AGENT_RESULT")
    if output:
        Path(output).write_text(json.dumps({"schema_version": "2.0", "collected": result.testsRun, "results": result.records}), encoding="utf-8")
    return int(not result.wasSuccessful())


if __name__ == "__main__":
    sys.exit(main())
