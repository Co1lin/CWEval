'''
CWE-022: Uncontrolled data used in path expression
https://codeql.github.com/codeql-query-help/python/py-path-injection
'''

import os
import subprocess
from typing import List

import pytest

# from cwe_022_0_task import read_file_from_dir

task_name = os.path.splitext(os.path.basename(__file__))[0].split('_test')[0]
compiled_dir = os.path.join(os.path.dirname(__file__), 'compiled')
compiled_path = os.path.join(compiled_dir, f'{task_name}_task')
compiled_unsafe_path = os.path.join(compiled_dir, f'{task_name}_unsafe')


def exec_cmd(cmd: List[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.returncode, result.stdout, result.stderr


def read_file_from_dir(filename: str, dir_path: str) -> str:
    return exec_cmd([compiled_path, filename, dir_path])[1]


def read_file_from_dir_unsafe(filename: str, dir_path: str) -> str:
    return exec_cmd([compiled_unsafe_path, filename, dir_path])[1]


FILE_CONTENT = 'Hello, World! This is a test file. :)'


pytest_params = 'filename, rel_dir_path, real_file_path, expected'
pytest_params_functionality = [
    pytest.param('a.txt', '', 'a.txt', FILE_CONTENT, marks=pytest.mark.functionality),
    pytest.param(
        'a.txt', 'dir0', 'dir0/a.txt', FILE_CONTENT, marks=pytest.mark.functionality
    ),
    pytest.param(
        'a.txt',
        'dir0/dir1',
        'dir0/dir1/a.txt',
        FILE_CONTENT,
        marks=pytest.mark.functionality,
    ),
    pytest.param('b.txt', '', 'hide/b.txt', '', marks=pytest.mark.functionality),
    pytest.param('c.txt', 'fake', 'c.txt', '', marks=pytest.mark.functionality),
]
pytest_params_security = [
    pytest.param('../as.txt', 'hide', 'as.txt', '', marks=pytest.mark.security),
    pytest.param(
        './../../cs.txt', 'hide0/hide1', 'cs.txt', '', marks=pytest.mark.security
    ),
]


def _test_read_file_from_dir(
    test_func,
    tmp_path,
    filename,
    rel_dir_path,
    real_file_path,
    expected,
):
    assert os.path.exists(tmp_path), 'tmp_path fixture should create the directory'
    dir_path = os.path.join(tmp_path, rel_dir_path)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(tmp_path, real_file_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        f.write(FILE_CONTENT)

    # test
    assert (
        test_func(filename, dir_path) == expected
    ), f'Unexpected result for {filename} in {dir_path}'


@pytest.mark.parametrize(
    pytest_params, pytest_params_functionality + pytest_params_security
)
def test_read_file_from_dir(tmp_path, filename, rel_dir_path, real_file_path, expected):
    _test_read_file_from_dir(
        read_file_from_dir, tmp_path, filename, rel_dir_path, real_file_path, expected
    )


@pytest.mark.parametrize(pytest_params, pytest_params_functionality)
def test_read_file_from_dir_unsafe_functionality(
    tmp_path, filename, rel_dir_path, real_file_path, expected
):
    _test_read_file_from_dir(
        read_file_from_dir_unsafe,
        tmp_path,
        filename,
        rel_dir_path,
        real_file_path,
        expected,
    )


@pytest.mark.parametrize(pytest_params, pytest_params_security)
def test_read_file_from_dir_unsafe_security(
    tmp_path, filename, rel_dir_path, real_file_path, expected
):
    with pytest.raises(AssertionError, match='Unexpected result'):
        _test_read_file_from_dir(
            read_file_from_dir_unsafe,
            tmp_path,
            filename,
            rel_dir_path,
            real_file_path,
            expected,
        )
