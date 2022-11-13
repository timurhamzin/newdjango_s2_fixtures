# -*- coding: utf-8 -*-
import pytest
import pytest_dependency
import pytest_order

# -*- coding: utf-8 -*-
import pytest
import pytest_dependency
import pytest_order
import json
import os
import re
import subprocess
import sys
from io import StringIO
from pathlib import Path
from typing import Union, Optional

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

def run_pytest_runner(__file__of_test, setup_django: Optional[bool] = None):
    """
    Run tests from a test file.
    To be called from a test file like so:

    if __name__ == '__main__':
        run_pytest_runner(__file__, setup_django=<True, False or None>)

    This is how tests must be run in production.
    """
    def _setup_django():
        import django
        from django.conf import settings
        if not settings.configured:
            settings.configure()
            django.setup()

    if setup_django is None:
        try:
            _setup_django()
        except Exception:
            pass
    elif setup_django:
        _setup_django()

    pytest_runner = PytestRunner(__file__of_test)
    pytest_runner.run_capturing_traceback()

def get_short_path(path: Union[Path, str], base_dir) -> Path:
    return Path(path).relative_to(base_dir)

@pytest.fixture
def base_dir() -> Path:
    return Path(__file__).parent

@pytest.fixture
def author_json_str(base_dir) -> str:
    return """[
{
  "model": "ice_cream.topping",
  "pk": 1,
  "fields": {
    "is_published": true,
    "name": "Шоколадный Sgroppino (шоколад и лимонный шербет)",
    "slug": "chilli_pandilla"
  }
},
{
  "model": "ice_cream.topping",
  "pk": 2,
  "fields": {
    "is_published": true,
    "name": "Chilli pandilla (перец и мёд)",
    "slug": "chilli_pandilla"
  }
},
{
  "model": "ice_cream.topping",
  "pk": 3,
  "fields": {
    "is_published": true,
    "name": "Vari marmellata (ассорти из варенья)",
    "slug": "vari_marmellata"
  }
},
{
  "model": "ice_cream.topping",
  "pk": 4,
  "fields": {
    "is_published": true,
    "name": "Кисельные берега (клюквенный кисель)",
    "slug": "kissel"
  }
},
{
  "model": "ice_cream.topping",
  "pk": 5,
  "fields": {
    "is_published": true,
    "name": "Вилли Вонка (шоколадный соус)",
    "slug": "villi_vonka"
  }
},
{
  "model": "ice_cream.topping",
  "pk": 6,
  "fields": {
    "is_published": true,
    "name": "Honey pot (ассорти из мёда)",
    "slug": "honey_pot"
  }
},
{
  "model": "ice_cream.topping",
  "pk": 7,
  "fields": {
    "is_published": true,
    "name": "Сладкий топ (коктейль из сгущёнки, мёда и сахарного сиропа)",
    "slug": "sweet_top"
  }
},
{
  "model": "ice_cream.topping",
  "pk": 8,
  "fields": {
    "is_published": false,
    "name": "Экстремально острый с перцем Каролинcкий жнец",
    "slug": "carolina_reaper"
  }
}
]
"""

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
        cleaned = msg
        err_prefixes = re.findall(r'^E\s+', cleaned, flags=re.MULTILINE)
        if err_prefixes:
            cleaned = re.sub(
                fr'^{err_prefixes[0]}', '', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'^E\s+', '', cleaned, flags=re.MULTILINE)
        cleaned = cleaned.replace('assert False', '')
        cleaned = cleaned.rstrip('\n')
        return cleaned

    def run_capturing_traceback(self, with_args_for_webpack=False) -> None:
        if with_args_for_webpack:
            self.set_run_args_for_webpack()

        traceback = []
        system_cmd = [f'pytest "{str(Path(self.path).as_posix())}"']
        with subprocess.Popen(
                system_cmd, stdout=subprocess.PIPE, bufsize=1,
                universal_newlines=True, shell=True, text=True,
                env=os.environ) as p:
            for line in p.stdout:
                traceback.append(line)

        code = p.returncode

        if int(code) != 0:
            cleaned_msg = ''
            traceback_str = ''.join(traceback)
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
