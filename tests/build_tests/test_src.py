import json
import os
import re
import subprocess
import sys
from io import StringIO
from pathlib import Path
from typing import Union, Optional

import pytest

from yap_testing.output import CapturingStdout
from yap_testing.run_pytest import PytestRunner, run_pytest_runner
from yap_testing.webpack.pytest_webpack import PytestFileWebpacker

dependencies = [
    f'{str(PytestRunner)}',
    f'{str(Union)}',
    f'{str(Optional)}',
    f'{str(CapturingStdout)}',
    f'{str(StringIO)}',
    f'{str(re)}',
    f'{str(sys)}',
    f'{str(subprocess)}',
]

ignore_dependencies = [
    'dependencies',
    f'{str(PytestFileWebpacker)}',
]


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


def get_short_path(path: Union[Path, str], base_dir) -> Path:
    return Path(path).relative_to(base_dir)


@pytest.fixture
def user_json(base_dir):
    fname = 'toppings.json'
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
    if 'DEVELOPMENT' in os.environ:
        run_pytest_runner(__file__)
    else:  # webpack for production
        webpacked_fpath = PytestFileWebpacker(
            __file__,
            remove_target_file=True,
            include_runner_code=True
        ).webpack_py_file()
        run_pytest_runner(webpacked_fpath)
