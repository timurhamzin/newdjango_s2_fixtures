cd /app/tests

# move files if exist
[ -f ./pytest.ini ] && mv -f ./pytest.ini /app/pytest.ini
[ -f ./author.json ] && mv -f ./author.json /app/author.json
[ -f ./test.py ] && mv -f ./test.py /app/test.py

# подавляем сообщение о необходимости обновить pip
export PIP_DISABLE_PIP_VERSION_CHECK=1

python3 -m pip install -r /app/tests/requirements.txt

cd /app

LF=$'\n'
echo $LF 1>&2
echo $LF 1>&2

echo \`\`\` 1>&2

if pytest 1>&2; then
  exit 0
else
  status=$?
  echo \`\`\` 1>&2
  exit $status
fi
