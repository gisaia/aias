source ./test/env.sh
docker compose -f docker-compose-tests.yaml down
docker compose -f docker-compose.yaml down
rm -rf ./outbox
docker rm airs-server rabbitmq redis fam-service elasticsearch smtp4dev minio agate aproc-service aproc-processes
