cd /app/tests

rm -f /app/pytest.ini || true
rm -f /app/author.json || true
rm -f /app/test.py || true

mv ./pytest.ini /app/pytest.ini
mv ./author.json /app/author.json
mv ./test.py /app/test.py
cp /app/precode.json ./precode.json

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
