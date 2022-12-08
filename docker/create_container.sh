# run from parent directory
export cont=newdjango_s2_fixtures
source ./copy_tests.sh
docker container stop $cont || true
docker container rm $cont || true
docker image rm $cont || true
docker build -f ./docker/Dockerfile -t $cont .
docker run -d --rm --name $cont $cont tail -f /dev/null
docker commit $cont $cont
docker container stop $cont
