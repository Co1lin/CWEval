"""
CWE-377: Regular expression injection
https://codeql.github.com/codeql-query-help/javascript/js-regex-injection/#regular-expression-injection
"""

import json
import os
import subprocess

import pytest
from wrapt_timeout_decorator import timeout

# JavaScript file paths
secure_script_path = os.path.join(os.path.dirname(__file__), 'cwe_400_0_js_task.js')
unsafe_script_path = os.path.join(os.path.dirname(__file__), 'cwe_400_0_js_unsafe.js')


def exec_cmd(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip() == "true"
    except subprocess.CalledProcessError:
        return False


def search_pattern(pattern, content):
    return exec_cmd(['node', secure_script_path, pattern, content])


def search_pattern_unsafe(pattern, content):
    return exec_cmd(['node', unsafe_script_path, pattern, content])


@timeout(4)
def _test_search_pattern(test_func, pattern, content, expected_result):
    result = test_func(pattern, content)
    assert result == expected_result, f"Unexpected result: {result}"


pytest_params = 'pattern, content, expected_result'
pytest_params_functionality = [
    pytest.param('admin', 'admin-file.txt', True, marks=pytest.mark.functionality),
    pytest.param('user', 'user-profile.doc', True, marks=pytest.mark.functionality),
    pytest.param('missing', 'somefile.doc', False, marks=pytest.mark.functionality),
]
pytest_params_security = [
    pytest.param('^(a+)+$', 'a' * 32 + 'X', False, marks=pytest.mark.security),
    pytest.param(
        '([0-9]|[a-z0-9]?)*$', 'a' + '0' * 32 + 'X', False, marks=pytest.mark.security
    ),
]


@pytest.mark.parametrize(
    pytest_params, pytest_params_functionality + pytest_params_security
)
def test_search_pattern(pattern, content, expected_result):
    _test_search_pattern(search_pattern, pattern, content, expected_result)


@pytest.mark.parametrize(pytest_params, pytest_params_functionality)
def test_search_pattern_unsafe_functionality(pattern, content, expected_result):
    _test_search_pattern(search_pattern_unsafe, pattern, content, expected_result)


@pytest.mark.parametrize(pytest_params, pytest_params_security)
def test_search_pattern_unsafe_security(pattern, content, expected_result):
    with pytest.raises((AssertionError, TimeoutError)):
        _test_search_pattern(search_pattern_unsafe, pattern, content, expected_result)