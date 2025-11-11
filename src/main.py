import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_engg.app import app, assistant

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
