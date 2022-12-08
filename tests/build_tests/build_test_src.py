import os
import shutil
import sys

from pathlib import Path

root_dir = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, root_dir.as_posix())

from yap_testing.manage import TestSrcBuilder


class PrepareForTesting:

    def __init__(self):
        self._user_src_fpath = root_dir / 'toppings.json'
        tests_dpath = root_dir / 'tests'
        self._user_trg_fpath = tests_dpath / 'toppings.json'
        self._files_to_remove_on_exit = [
            tests_dpath / 'conftest_joined.py',
            tests_dpath / 'conftest_joined_webpacked.py',
            tests_dpath / 'test_src.py',
            tests_dpath / 'test_src_webpacked.py',
            self._user_trg_fpath
        ]

    def __enter__(self):
        # replace student code in build directory
        shutil.copyfile(self._user_src_fpath, self._user_trg_fpath)
        return self._user_trg_fpath

    def __exit__(self, exc_type, exc_val, exc_tb):
        for file_to_remove in self._files_to_remove_on_exit:
            if os.path.isfile(file_to_remove):
                os.remove(file_to_remove)


if __name__ == '__main__':
    with PrepareForTesting():
        builder = TestSrcBuilder(
            build_for_django=False,
            find_test_src_above_build_dirs=False
        )
        builder.build_test_src_files(
            build_in_paths=['..'],
            dry_run=False,
            move_test_src_webpacked_to='test.py',
        )
