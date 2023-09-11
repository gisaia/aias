source ./test/env.sh
docker-compose -f docker-compose.yaml down
rm -rf $ROOT_DIRECTORY"/DIMAP"
