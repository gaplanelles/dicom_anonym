#!/bin/bash

source ~/scripts/install/.functions.sh

# Check if the conda name, service name, and script path are provided as arguments
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
    echo "Usage: $0 <conda-env-name> <service-name> <script-path>"
    exit 1
else
    USERNAME=$(whoami)
    LOG_DIR="/home/${USERNAME}/logs/service"
    CONDA_ENV_NAME="$1"
    SERVICE_NAME="$2"
    SCRIPT_PATH="/home/${USERNAME}/dicom_anonym/$3"
fi

SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
LOG_FILE="${LOG_DIR}/${SERVICE_NAME}.log"
ERROR_LOG_FILE="${LOG_DIR}/${SERVICE_NAME}_error.log"

if [ -f "$SERVICE_FILE" ]; then
    log_message "Service ${SERVICE_NAME} already exists. Skipping creation."
else
    log_message "Creating service for ${SERVICE_NAME}"

    echo "[Unit]
Description=${SERVICE_NAME} Service
After=network.target

[Service]
Type=simple
User=${USERNAME}
ExecStart=/bin/bash -c 'source $HOME/miniforge3/bin/activate ${CONDA_ENV_NAME} && cd $(dirname "${SCRIPT_PATH}") && python ${SCRIPT_PATH}'
StandardOutput=append:${LOG_FILE}
StandardError=append:${ERROR_LOG_FILE}
Restart=on-failure

[Install]
WantedBy=multi-user.target" | sudo tee $SERVICE_FILE
    sudo chown root:root $SERVICE_FILE
    sudo chmod 644 $SERVICE_FILE

    # Reloading systemd manager configuration
    log_message "Reloading systemd manager configuration"
    sudo systemctl daemon-reload

    # Enabling and starting the service
    log_message "Enabling and starting ${SERVICE_NAME} service"
    sudo systemctl enable ${SERVICE_NAME}.service
    sudo systemctl start ${SERVICE_NAME}.service

    log_message "Service creation completed."
fi