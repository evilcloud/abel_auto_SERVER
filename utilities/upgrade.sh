#!/bin/bash

echo "Stopping docker-compose service..."
sudo systemctl stop docker-compose

echo "Cleaning up Docker..."
./clean_docker.sh

echo "Backing up data..."
mv /root/abel_auto_SERVER/data/data.db /root/
mv /root/abel_auto_SERVER/data/config.json /root/

echo "Removing old code..."
rm -rf /root/abel_auto_SERVER

echo "Cloning latest code..."
git clone https://github.com/evilcloud/abel_auto_SERVER /root/abel_auto_SERVER

echo "Restoring data..."
mv /root/data.db /root/abel_auto_SERVER/data/
mv /root/config.json /root/abel_auto_SERVER/data/

echo "Reloading and restarting docker-compose..."
sudo systemctl daemon-reload
sudo systemctl enable docker-compose
sudo systemctl start docker-compose

echo "Upgrade complete!"