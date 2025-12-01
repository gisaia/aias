#!/bin/bash

# Loop through all provided container arguments
for container in "$@"; do
    # Print a clear header for each container
    echo "=================================================="
    echo "DOCKER LOGS FOR CONTAINER: $container"
    echo "=================================================="

    # Get and display logs for the current container
    docker logs "$container"

    # Add a separator between containers
    echo ""
    echo "--------------------------------------------------"
    echo ""
done
