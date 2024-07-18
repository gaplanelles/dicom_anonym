#!/bin/bash

source ~/scripts/install/.functions.sh

log_message "OS upgrade started."

log_message "Disabling interactive frontend..."
export DEBIAN_FRONTEND=noninteractive
sudo apt-get -y remove needrestart

log_message "Upgrading... "
sudo apt-get -y upgrade

log_message "Configuring firewall... "
sudo apt-get -y install firewalld
sudo firewall-cmd --zone=public --add-port=2053/tcp --permanent
sudo firewall-cmd --zone=public --add-port=3000/tcp --permanent
sudo firewall-cmd --zone=public --add-port=2055/tcp --permanent
sudo firewall-cmd --reload

log_message "Installing OpenGL support... "
sudo apt-get -y install libgl1-mesa-glx libglib2.0-0

log_message "OS upgrade completed."
