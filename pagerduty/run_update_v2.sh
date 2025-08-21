#!/bin/bash
# Wrapper script to run update command with proper timeout handling

echo "🚀 Starting PagerDuty incident update..."
echo "📝 Output will be logged to update_log.txt"
echo "⏱️ This process may take 30+ minutes..."

# Set unlimited timeout and run in background with logging
nohup timeout 1800 python3 main_v2.py --update-incidents ${1:-7} > update_log.txt 2>&1 &

# Get the process ID
PID=$!

echo "🔄 Process started with PID: $PID"
echo "📋 Monitor progress with: tail -f update_log.txt"
echo "🛑 Stop process with: kill $PID"

# Function to show progress
show_progress() {
    while kill -0 $PID 2>/dev/null; do
        if [ -f update_log.txt ]; then
            # Show last few lines of log
            echo "------- Latest Progress ($(date)) -------"
            tail -n 3 update_log.txt | grep -E "(Progress:|Still processing|Processed|✅|🚨)"
        fi
        sleep 30
    done
}

# Ask user if they want to monitor
echo ""
read -p "🔍 Monitor progress in real-time? (y/n): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📊 Monitoring progress (Ctrl+C to stop monitoring, process continues)..."
    show_progress
else
    echo "✅ Process running in background. Check update_log.txt for progress."
fi

# Wait for completion
wait $PID
EXIT_CODE=$?

echo ""
echo "🏁 Process completed with exit code: $EXIT_CODE"

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Update completed successfully!"
    echo "📊 Run: python3 main_v2.py --show-summary to see results"
elif [ $EXIT_CODE -eq 124 ]; then
    echo "⏰ Process timed out after 30 minutes"
    echo "💾 Partial results may have been saved"
else
    echo "❌ Process failed with error"
    echo "📝 Check update_log.txt for details"
fi

echo "📄 Full log available in: update_log.txt"