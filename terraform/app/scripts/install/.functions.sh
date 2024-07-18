#!/bin/bash

function log_message {
    local message="$1"
    local length=${#message}
    local border_length=$((length + 4))

    # Create the border line
    local border=""
    for (( i=0; i<border_length; i++ )); do
        border+="*"
    done

    # Print the message surrounded by borders
    echo "$border"
    echo "* $message *"
    echo "$border"
}

# Export the function to make it available in the environment
export -f log_message