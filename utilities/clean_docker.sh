#!/bin/bash

# Stop all running containers
docker stop $(docker ps -aq)

# Remove all containers
docker rm $(docker ps -aq)

# Remove all images
docker rmi $(docker images -q)

# Remove volumes
docker volume prune -f

# Remove networks
docker network prune -f

# Remove Docker Compose stacks/configs
docker stack rm $(docker stack ls -q)
docker config rm $(docker config ls -q)

# Remove Docker Compose files
sudo rm -rf /var/lib/docker/stacks/*

# Stop Docker service
sudo service docker stop

# Remove Docker CE
sudo apt-get purge docker-ce
sudo rm -rf /var/lib/docker

# Remove Docker Compose
sudo rm /usr/local/bin/docker-compose

# Clean up any leftover Docker files
sudo apt autoremove -y

# Delete all images, containers, and volumes
docker system prune -af --volumes