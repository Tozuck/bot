#!/bin/bash

# Define the necessary variables
BOT_SCRIPT="~/bot/toz.py"
REQUIREMENTS_FILE="~/bot/requirements.txt"
LOG_DIR="logs"
VENV_DIR="venv"
CRON_JOB="@reboot ~/bot/bot.sh"

# Update package list and install system dependencies
echo "Updating package list and installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-dev libzbar0

# Install virtualenv if it's not installed
echo "Installing virtualenv..."
pip3 install virtualenv

# Create a virtual environment
echo "Creating a virtual environment..."
virtualenv $VENV_DIR

# Activate the virtual environment
echo "Activating the virtual environment..."
source $VENV_DIR/bin/activate

# Create requirements.txt
echo "Creating requirements.txt..."
cat > $REQUIREMENTS_FILE << EOL
pyTelegramBotAPI==4.9.1
requests==2.28.1
Pillow==9.1.1
pyzbar==0.1.9
EOL

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r $REQUIREMENTS_FILE

# Create a log directory if it doesn't exist
echo "Creating log directory..."
mkdir -p $LOG_DIR

# Run the bot in the background
echo "Running the bot in the background..."
nohup python3 $BOT_SCRIPT > $LOG_DIR/bot.log 2>&1 &

# Add crontab entry to ensure the bot starts on reboot
echo "Adding crontab entry..."
(crontab -l ; echo "$CRON_JOB") | crontab -

echo "Bot setup complete and running in the background."
