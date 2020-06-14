import os
import pkg_resources
import pytest
import sys
from contextlib import redirect_stdout, redirect_stderr
import io
import re

from OLAP.OLAP import OLAP


@pytest.mark.parametrize(
    ("test_args", "expected_output"),
    [   
        ("param_noparams_countdefault", "param_noparams_countdefault"),
        ("param_count", "param_count"),
        ("param_max", "param_max"),
        ("param_min", "param_min"),
        ("param_mean", "param_mean"),
        ("param_sum", "param_sum"),
        ("param_groupby_simple", "param_groupby_simple"),
        ("param_groupby_all", "param_groupby_all"),
    ],indirect=['test_args', "expected_output"])

def test_stdout(test_args, expected_output):
    f = io.StringIO()
    with redirect_stdout(f):
        OLAP(test_args)

    output = re.sub("\r\n", "\n", f.getvalue())
    assert output == expected_output


@pytest.mark.parametrize(
    ("test_args", "expected_error"),
    [   
        ("error_missing_field", "error_missing_field"),
        ("error_groupby_arg_not_found", "error_groupby_arg_not_found"),
        ("error_capped_aggregate_distinct", "error_capped_aggregate_distinct"),
    ],indirect=['test_args', "expected_error"])

def test_stderr(test_args, expected_error):
    f = io.StringIO()
    with redirect_stderr(f):
        try:
            OLAP(test_args)
        except SystemExit:
            pass

    error = f.getvalue()
    assert error.split(":")[-1] == expected_error.split(":")[-1]
