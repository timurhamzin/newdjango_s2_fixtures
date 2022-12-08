# Script to run tests locally in a docker container

# Before running this file manually place student's solution to `../toppings.json`

# cd to parent dir so that all of its files are available for docker's COPY
cd ..

# execute `./create_container.sh` to create the `newdjango_s2_fixtures` container
export cont=newdjango_s2_fixtures
source ./docker/create_container.sh

# run tests in the created container
docker run -d --rm --name $cont $cont tail -f /dev/null || true
docker exec -it $cont bash  # docker exec -i newdjango_s2_fixtures bash
# run following line in docker container's bash:
# cd /app/tests && ./run.sh