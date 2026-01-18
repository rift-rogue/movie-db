#!/data/data/com.termux/files/usr/bin/bash

# Movie Database Installer for Termux
# One-run installation script

echo "Movie Database Installer"
echo "======================="
echo ""

# Update packages
echo "Updating Termux packages..."
pkg update -y && pkg upgrade -y

# Install Python
echo "Installing Python..."
pkg install python -y

# Install required Python packages
echo "Installing Flask and dependencies..."
pip install --upgrade pip
pip install flask requests

# Create startup script
echo "Creating startup script..."
cat > start.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd "$(dirname "$0")"
echo "Starting Movie Database..."
echo "Open: http://127.0.0.1:8000"
echo "Press Ctrl+C to stop"
python app.py
EOF

chmod +x start.sh

# Create background service script
echo "Creating background service..."
cat > service.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd "$(dirname "$0")"
nohup python app.py > /dev/null 2>&1 &
echo "Movie Database started in background"
echo "Open: http://127.0.0.1:8000"
echo "To stop: pkill -f 'python app.py'"
EOF

chmod +x service.sh

echo ""
echo "Installation complete!"
echo ""
echo "Usage:"
echo "  Start normally:    ./start.sh"
echo "  Start background:  ./service.sh"
echo "  Stop background:   pkill -f 'python app.py'"
echo ""
echo "Access at: http://127.0.0.1:8000"
echo ""

# Ask to start now
read -p "Start the app now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ./start.sh
fi
