#!/bin/bash
export path_to_bb=/Users/timurhamzin/Work/2022/bb/backend-developer/for_test/newdjango_s2_fixtures
export branch=newdjango_s2_fixtures
cp -R ./tests/* $path_to_bb
cd $path_to_bb
git checkout $branch
echo "Merge branch $branch from $path_to_bb into master to update tests on the server."
