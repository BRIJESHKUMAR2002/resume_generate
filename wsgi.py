import sys
import os
from flask import Flask

# Add the application directory to the sys.path
sys.path.insert(0, '/var/www/html/Resume-domnic')

# Create the Flask application
from main import app as application  # assuming your Flask app is named 'app' and defined in app.py

if __name__ == "__main__":
    application.run(debug=True)
