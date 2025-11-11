import os
import logging
import traceback
from flask import Flask, render_template, request, jsonify, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
import base64
import asyncio
from .core.assistant_openrouter import OpenRouterAssistant

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__, static_folder='static')
    # Enable CORS for all routes
    CORS(app, resources={"*": {"origins": "*"}})
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['JSON_AS_ASCII'] = False  # Ensure proper UTF-8 encoding

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize the assistant
    try:
        assistant = OpenRouterAssistant()
        logger.info("Successfully initialized OpenRouter assistant")
    except Exception as e:
        logger.error(f"Failed to initialize OpenRouter assistant: {str(e)}")
        raise

    return app, assistant

# Create the Flask application and assistant
app, assistant = create_app()

@app.route('/')
def home():
    """Render the main chat interface."""
    logger.info("Rendering home page")
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages from the client."""
    logger.info("Received chat request")
    
    try:
        # Parse JSON data
        data = request.get_json()
        if not data:
            logger.warning("No JSON data received")
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400
            
        message = data.get('message', '').strip()
        if not message:
            logger.warning("Empty message received")
            return jsonify({
                'status': 'error',
                'message': 'Message cannot be empty'
            }), 400
            
        logger.info(f"Processing message: {message[:100]}")
        
        # Get response from the assistant
        try:
            response, tokens_used, max_tokens = assistant.chat(message)
            logger.info(f"Successfully generated response. Tokens used: {tokens_used}/{max_tokens}")
            
            return jsonify({
                'status': 'success',
                'response': response,
                'token_usage': {
                    'total_tokens': tokens_used,
                    'max_tokens': max_tokens
                }
            })
            
        except Exception as e:
            logger.error(f"Error in assistant.chat: {str(e)}\n{traceback.format_exc()}")
            return jsonify({
                'status': 'error',
                'message': f'Error processing your message: {str(e)}'
            }), 500
            
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'status': 'error',
            'message': 'An unexpected error occurred. Please try again.'
        }), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file uploads."""
    logger.info("Received file upload request")
    
    try:
        if 'file' not in request.files:
            logger.warning("No file part in request")
            return jsonify({'error': 'No file part'}), 400
            
        file = request.files['file']
        if file.filename == '':
            logger.warning("No file selected")
            return jsonify({'error': 'No selected file'}), 400
            
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            try:
                file.save(filepath)
                logger.info(f"Successfully saved file: {filename}")
                
                return jsonify({
                    'status': 'success',
                    'filename': filename,
                    'url': url_for('static', filename=f'uploads/{filename}')
                })
                
            except Exception as e:
                logger.error(f"Error saving file: {str(e)}\n{traceback.format_exc()}")
                return jsonify({
                    'status': 'error',
                    'message': f'Error saving file: {str(e)}'
                }), 500
        
        return jsonify({
            'status': 'error',
            'message': 'File upload failed'
        }), 400
        
    except Exception as e:
        logger.error(f"Unexpected error in upload: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'status': 'error',
            'message': 'An unexpected error occurred during file upload.'
        }), 500

@app.route('/reset', methods=['POST'])
def reset():
    """Reset the conversation history."""
    try:
        logger.info("Resetting conversation history")
        assistant.reset_conversation()
        return jsonify({
            'status': 'success',
            'message': 'Conversation history has been reset.'
        })
    except Exception as e:
        logger.error(f"Error resetting conversation: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to reset conversation.'
        }), 500

if __name__ == '__main__':
    try:
        logger.info("Starting Flask application")
        app.run(host='0.0.0.0', port=5001, debug=True)
    except Exception as e:
        logger.critical(f"Failed to start application: {str(e)}\n{traceback.format_exc()}")
        raise 