#!/bin/bash

sudo apt-get update --allow-releaseinfo-change
sudo apt install etherwake curl netcat-openbsd python3-venv

# Automatically get the current script directory
SCRIPT_DIR=$(dirname "$(realpath "$0")")
# Calculate the parent directory
PARENT_DIR=$(dirname "$SCRIPT_DIR")

# Step 0: Change to parent directory and create venv if it doesn't exist
echo "Changing to parent directory $PARENT_DIR and creating venv 'pienv' if needed..."
cd "$PARENT_DIR"
if [ ! -d "pienv" ]; then
    python3 -m venv pienv
    echo "Created venv 'pienv'."
else
    echo "Venv 'pienv' already exists."
fi

SERVICE_FILE="/etc/systemd/system/WakeOnLan.service"

# Step 1: Create the systemd service file with dynamic paths
echo "Creating $SERVICE_FILE..."

sudo bash -c "cat > $SERVICE_FILE" << EOL
[Unit]
Description=Smart WakeOnLan Service
After=network.target

[Service]
WorkingDirectory=$PARENT_DIR
ExecStart=/bin/bash -c "source ./pienv/bin/activate && python3 ./WakOnLan/app.py"
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOL

# Step 2: Reload systemd, enable, and start the service
echo "Reloading systemd, enabling and starting the WakeOnLan service..."

sudo systemctl daemon-reload
sudo systemctl enable WakeOnLan.service
sudo systemctl start WakeOnLan.service

# Step 3: Display the service status
echo "Displaying the status of the WakeOnLan service..."
sudo systemctl status WakeOnLan.service
