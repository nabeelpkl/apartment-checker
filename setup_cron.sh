#!/bin/bash

# Setup script for daily apartment availability email notifications
# This script will create a cron job that runs daily at 5:30 PM

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/email_notification.py"

# Check if the Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "❌ Error: email_notification.py not found in $SCRIPT_DIR"
    exit 1
fi

# Create the cron job entry
CRON_JOB="30 17 * * * cd $SCRIPT_DIR && source venv/bin/activate && python email_notification.py >> apartment_check.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "email_notification.py"; then
    echo "⚠️  Cron job already exists. Removing old entry..."
    crontab -l 2>/dev/null | grep -v "email_notification.py" | crontab -
fi

# Add the new cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✅ Cron job created successfully!"
echo "📅 The script will run daily at 5:30 PM"
echo "📝 Logs will be saved to apartment_check.log"
echo ""
echo "To view current cron jobs: crontab -l"
echo "To remove the cron job: crontab -e"
echo ""
echo "⚠️  IMPORTANT: Make sure to update the email configuration in email_notification.py:"
echo "   - SENDER_EMAIL: Your Gmail address"
echo "   - SENDER_PASSWORD: Your Gmail app password"
echo "   - RECIPIENT_EMAIL: Where to send notifications" 