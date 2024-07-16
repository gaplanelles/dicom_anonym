wget https://repo.anaconda.com/archive/Anaconda3-2024.02-1-Linux-x86_64.sh
chmod +x Anaconda3-2024.02-1-Linux-x86_64.sh
./Anaconda3-2024.02-1-Linux-x86_64.sh
sudo apt-get update 
sudo apt -y install firewalld
sudo firewall-cmd --zone=public --add-port=2053/tcp --permanent
sudo firewall-cmd --zone=public --add-port=3000/tcp --permanent
sudo firewall-cmd --zone=public --add-port=2055/tcp --permanent
sudo firewall-cmd --reload