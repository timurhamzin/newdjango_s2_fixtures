# -*- coding: utf-8 -*-
import json
import os
import pprint
import re
import sys
from io import StringIO
from pathlib import Path
from typing import Union, Optional

import pytest


@pytest.fixture
def user_json(base_dir):
    fname = 'precode.json'
    user_fpath = base_dir / fname
    user_rfpath = get_short_path(user_fpath, base_dir)
    assert os.path.isfile(user_fpath), (
        f'Не обнаружен файл `{user_rfpath}`.'
    )
    with open(user_fpath, 'r', encoding='utf-8') as f:
        try:
            user_json = json.loads(f.read())
        except Exception as e:
            assert False, (
                f'Ошибка при чтении файла `{fname}`: {str(e)}.'
            )
        return user_json


def run_pytest_runner(__file__of_test):
    """
    Run tests from a test file.
    To be called from a test file like so:

    if __name__ == '__main__':
        run_pytest_runner()

    This is how tests must be run in production
    """
    pytest_runner = PytestRunner(__file__of_test)
    pytest_runner.run_capturing_traceback()


def get_short_path(path: Union[Path, str], base_dir) -> Path:
    return Path(path).relative_to(base_dir)


@pytest.fixture
def base_dir() -> Path:
    return Path(__file__).parent


@pytest.fixture
def author_json_str(base_dir) -> str:
    fpath = base_dir / 'author.json'
    with open(fpath, 'r', encoding='utf-8') as f:
        return f.read()


@pytest.fixture
def author_json(author_json_str):
    return json.loads(author_json_str)


class PytestRunner:
    """
    Run pytest and optionally raise AssertionError with the 1st error
    message from the traceback
    """

    def __init__(self, path: Union[str, Path],
                 args='--exitfirst --disable-warnings',
                 strip_traceback_to_err=True,
                 test_name_contains_expr: Optional[str] = None):
        """
        :param path: path to run pytest on
        :param args: args-string to pass on to pytest
        :param strip_traceback_to_err: search captured traceback for the 1st
            error message and assert False with this message
        :param test_name_contains_expr: e.g. 'test_method',
            'test_method or test_other', 'not test_method and not test_other'
        """
        self.path = path
        self.args = args
        self.strip_traceback_to_err = strip_traceback_to_err
        self.test_name_contains_expr = test_name_contains_expr

    def set_run_args_for_webpack(self):
        self.args = ''
        self.strip_traceback_to_err = False

    @staticmethod
    def clean_msg(msg):
        cleaned = re.sub(r'^E\s+', '', msg, flags=re.MULTILINE)
        cleaned = cleaned.replace('assert False', '')
        cleaned = cleaned.rstrip('\n')
        return cleaned

    def run_capturing_traceback(self, with_args_for_webpack=False) -> None:
        if with_args_for_webpack:
            self.set_run_args_for_webpack()
        with CapturingStdout() as traceback:
            self.args = self.args.split()
            if self.test_name_contains_expr:
                self.args.append(f'-k {self.test_name_contains_expr}')
            self.args.append(str(Path(self.path).as_posix()))
            code = pytest.main(args=self.args)
        if code == 1:
            cleaned_msg = ''
            traceback_str = '\n'.join(traceback)
            if self.strip_traceback_to_err:
                first_err_msg_re = (
                    r'^E\s+.*?(\w+Error|\w+Exception):([\w\W]+?)(?:^.+\1)')
                found = re.findall(
                    first_err_msg_re, traceback_str, re.MULTILINE)
                if found:
                    # last error in traceback is AssertionError or uncaught
                    # exception
                    cleaned_msg = self.clean_msg(found[-1][1])
            if cleaned_msg:
                assert False, cleaned_msg


class CapturingStdout(list):
    """
    Context manager for capturing stdout.
    Usage:
        with Capturing() as func_output:
            func()
    check func() output in func_output variable
    """

    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        sys.stdout = self._stdout
        self.append(self._stringio.getvalue())
        self._stringio.close()
        del self._stringio


def test_json_structure(user_json, author_json):
    all_field_vals = []
    assert isinstance(user_json, list), (
        'Убедитесь, что содержимое json-файла - список.')
    for toppings_rec in user_json:
        for k in ['model', 'pk', 'fields']:
            assert k in toppings_rec, (
                'Убедитесь, что содержимое json-файла - список словарей, '
                f'в которых есть ключ `{k}`.'
            )
        fields = toppings_rec['fields']
        assert isinstance(fields, dict), (
            'Убедитесь, что содержимое json-файла - список словарей, '
            'в которых по ключу `fields` лежат словари.'
        )
        field_vals = []
        for k in ['is_published', 'name', 'slug']:
            assert k in fields, (
                'Убедитесь, что содержимое json-файла - список словарей, '
                'в которых по ключу `fields` лежат словари, в которых '
                f'есть ключ `{k}`.'
            )
            field_vals.append((k, fields[k]))
        all_field_vals.append(tuple(field_vals))
    for expected_record in author_json:
        expected_fields = expected_record['fields']
        items = tuple(expected_fields.items())
        if items not in all_field_vals:
            assert False, (
                'Убедитесь, что в json-файле содержится запись со '
                f'следующим словарём в ключе `fields`: ```{expected_fields}```'
            )
        else:
            del all_field_vals[all_field_vals.index(items)]
    if all_field_vals:
        assert False, (
            'В json-файле обнаружена лишняя или дублирующаяся запись, '
            'содержащая '
            f'следующий словарь по ключу `fields`:  ```{all_field_vals[0]}```'
        )


if __name__ == '__main__':
    run_pytest_runner(__file__)
