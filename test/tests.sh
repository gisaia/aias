./test/start_stack.sh
# Set env variable
source ./test/env.sh
docker build -f Dockerfile-tests -t pythontests .                                                                                         

docker run  --rm -v `pwd`:/app/  --network aias_aias pythontests python3 -m test.airs_tests
