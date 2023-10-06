source ./test/env.sh
docker-compose -f docker-compose-tests.yaml down
docker-compose -f docker-compose.yaml down
rm -rf ./outbox
