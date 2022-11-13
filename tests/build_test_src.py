import sys

from pathlib import Path

from yap_testing.manage import TestSrcBuilder

sys.path.insert(0, Path('..').absolute().as_posix())

if __name__ == '__main__':
    builder = TestSrcBuilder(
        build_for_django=False,
        find_test_src_above_build_dirs=False
    )
    builder.build_test_src_files(
        build_in_paths=['..'],
        dry_run=False,
        move_test_src_webpacked_to='test.py',
    )
