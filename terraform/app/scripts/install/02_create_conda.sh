#!/bin/bash

source ~/miniforge3/etc/profile.d/conda.sh
source ~/scripts/install/.functions.sh

# Check if the conda name is provided as an argument
if [ -z "$1" ]; then
  echo "Usage: $0 <conda-env-name>"
  exit 1
else
  CONDA_ENV_NAME="$1"
fi

# Check if the conda environment already exists
if conda info --envs | grep -q "^$CONDA_ENV_NAME\s"; then
  log_message "Conda environment '$CONDA_ENV_NAME' already exists."
else
  log_message "Conda creation started."
  conda create --name $CONDA_ENV_NAME python=3.10 -y
fi

log_message "Installing Python dependencies..."
conda activate $CONDA_ENV_NAME
pip install -r ~/dicom_anonym/backend_ikard/requirements_ikard.txt

log_message "Conda creation completed."