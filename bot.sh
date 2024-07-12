#!/bin/bash

# Define the necessary variables
BOT_DIR="$HOME/bot"
BOT_SCRIPT="$BOT_DIR/toz.py"
REQUIREMENTS_FILE="$BOT_DIR/requirements.txt"
LOG_DIR="$BOT_DIR/logs"
VENV_DIR="$BOT_DIR/venv"
PYTHON="$VENV_DIR/bin/python"
PIP="$VENV_DIR/bin/pip"
CRON_JOB="@reboot $BOT_DIR/bot.sh"

# Update package list and install system dependencies
echo "Updating package list and installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-dev libzbar0 libjpeg-dev zlib1g-dev

# Create a virtual environment
echo "Creating a virtual environment..."
python3 -m venv $VENV_DIR

# Activate the virtual environment
echo "Activating the virtual environment..."
source $VENV_DIR/bin/activate

# Create requirements.txt
echo "Creating requirements.txt..."
cat > $REQUIREMENTS_FILE << EOL
pyTelegramBotAPI
requests==2.28.1
Pillow==9.1.1
pyzbar==0.1.9
EOL

# Install Python dependencies
echo "Installing Python dependencies..."
$PIP install -r $REQUIREMENTS_FILE

# Create a log directory if it doesn't exist
echo "Creating log directory..."
mkdir -p $LOG_DIR

# Run the bot in the background
echo "Running the bot in the background..."
nohup $PYTHON $BOT_SCRIPT > $LOG_DIR/bot.log 2>&1 &

# Add crontab entry to ensure the bot starts on reboot
echo "Adding crontab entry..."
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "Bot setup complete and running in the background."
