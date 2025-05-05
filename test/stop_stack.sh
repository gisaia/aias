source ./test/env.sh
docker compose -f docker/compose/docker-compose.yaml -f docker/compose/docker-compose-tests.yaml down
