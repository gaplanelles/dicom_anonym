#!/bin/bash

source ~/scripts/install/.functions.sh

# Check if the correct number of parameters are passed
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <compartment_id> <namespace> <bucket_name>"
    exit 1
else
    USERNAME=$(whoami)
    COMPARTMENT_ID=$1
    NAMESPACE=$2
    BUCKET_NAME=$3
    DICOM_CONFIG_FILE_PATH="/home/${USERNAME}/dicom_anonym/backend_ikard/config.json"
    TXT_CONFIG_FILE_PATH="/home/${USERNAME}/dicom_anonym/text_anonymizer/config.json"
fi

log_message "Updating configuration..."

sed -i "s|<compartment_id/>|$COMPARTMENT_ID|g" "$DICOM_CONFIG_FILE_PATH"
sed -i "s|<namespace/>|$NAMESPACE|g" "$DICOM_CONFIG_FILE_PATH"
sed -i "s|<bucket_name/>|$BUCKET_NAME|g" "$DICOM_CONFIG_FILE_PATH"

sed -i "s|<compartment_id/>|$COMPARTMENT_ID|g" "$TXT_CONFIG_FILE_PATH"
sed -i "s|<namespace/>|$NAMESPACE|g" "$TXT_CONFIG_FILE_PATH"
sed -i "s|<bucket_name/>|$BUCKET_NAME|g" "$TXT_CONFIG_FILE_PATH"

log_message "Configuration update complete."