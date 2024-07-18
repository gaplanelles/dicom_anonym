#!/bin/bash

source ~/scripts/install/.functions.sh

log_message "Checking for existing MambaForge installation..."

if [ ! -x "$HOME/miniforge3/bin/conda" ]; then
    log_message "Downloading MambaForge..."

    curl -L -o Miniforge3-Linux-x86_64.sh https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh

    log_message "Configuring MambaForge..."

    chmod +x Miniforge3-Linux-x86_64.sh
    ./Miniforge3-Linux-x86_64.sh -b -p $HOME/miniforge3
    $HOME/miniforge3/bin/conda init bash

    log_message "Removing MambaForge installation artefacts..."
    rm Miniforge3-Linux-x86_64.sh

    log_message "MambaForge installation completed."
else
    log_message "MambaForge is already installed. Skipping installation."
fi