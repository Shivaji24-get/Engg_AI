import os
import json
import logging
import asyncio
from typing import List, Dict, Any, Optional, Union
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
import openai
from dotenv import load_dotenv
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('assistant.log')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class OpenRouterAssistant:
    """
    The OpenRouterAssistant class manages:
    - Interaction with the OpenRouter API
    - Conversation history management
    - Tool execution
    """

    def __init__(self, model: str = "mistralai/mistral-7b-instruct"):
        """Initialize the OpenRouter assistant.
        
        Args:
            model: The model to use for completions. Defaults to "mistralai/mistral-7b-instruct"
        """
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        if not self.openrouter_api_key:
            logger.error("No OPENROUTER_API_KEY found in environment variables")
            raise ValueError("No OPENROUTER_API_KEY found in environment variables")
            
        # Initialize token tracking
        self.total_tokens_used = 0
        self.max_tokens_limit = 200000  # Default token limit

        try:
            # Initialize OpenAI client for OpenRouter with synchronous client
            self.client = openai.OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.openrouter_api_key,
                timeout=30.0
            )
            logger.info(f"Initialized OpenRouter client with model: {model}")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenRouter client: {str(e)}")
            raise

        self.conversation_history: List[Dict[str, Any]] = []
        self.console = Console()
        self.model = model

    def chat(self, message_content: Union[str, List[Dict[str, Any]]]) -> str:
        """
        Send a message to the assistant and get a response.
        
        Args:
            message_content: The message content (can be str or list of content blocks)
            
        Returns:
            str: The assistant's response
            
        Raises:
            Exception: If there's an error communicating with the API
        """
        logger.info(f"Processing message: {message_content[:100]}...")
        
        try:
            # Prepare messages for the API
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant."},
                *self.conversation_history,
                {"role": "user", "content": message_content}
            ]
            
            logger.debug(f"Sending messages to API: {json.dumps(messages, indent=2)}")

            # Make the API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False,
                max_tokens=1000,
                temperature=0.7
            )
            
            logger.debug(f"Received response: {response}")

            # Get the assistant's response and token usage
            if response.choices and response.choices[0].message:
                assistant_message = response.choices[0].message.content
                
                if not assistant_message or not assistant_message.strip():
                    logger.warning("Received empty response from the model")
                    return "I'm sorry, I couldn't generate a response. Please try again.", self.total_tokens_used, self.max_tokens_limit
                
                # Update token usage
                if hasattr(response, 'usage') and hasattr(response.usage, 'total_tokens'):
                    self.total_tokens_used += response.usage.total_tokens
                else:
                    # Estimate tokens if not provided by the API (roughly 4 chars per token)
                    estimated_tokens = len(assistant_message) // 4
                    self.total_tokens_used += estimated_tokens
                
                # Update conversation history
                self.conversation_history.append({"role": "user", "content": message_content})
                self.conversation_history.append({"role": "assistant", "content": assistant_message})
                
                logger.info(f"Successfully generated response. Tokens used: {self.total_tokens_used}")
                return assistant_message, self.total_tokens_used, self.max_tokens_limit
                
            logger.error(f"Unexpected response format: {response}")
            return "I'm sorry, I received an unexpected response format. Please try again.", self.total_tokens_used, self.max_tokens_limit
            
        except openai.APITimeoutError as e:
            error_msg = "The request to OpenRouter timed out. Please try again."
            logger.error(f"API Timeout: {str(e)}")
            return error_msg, self.total_tokens_used, self.max_tokens_limit
            
        except openai.APIError as e:
            error_msg = f"OpenRouter API error: {str(e)}"
            logger.error(f"API Error: {error_msg}")
            return error_msg, self.total_tokens_used, self.max_tokens_limit
            
        except Exception as e:
            error_msg = f"An unexpected error occurred: {str(e)}"
            logger.error(f"Unexpected error: {error_msg}", exc_info=True)
            return error_msg, self.total_tokens_used, self.max_tokens_limit

    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = []
        return "Conversation history has been reset."
