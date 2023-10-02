source ./test/env.sh
docker-compose -f docker-compose.yaml down
docker kill rnwood/smtp4dev:v3
#rm -rf $ROOT_DIRECTORY"/DIMAP"
rm -rf ./outbox
