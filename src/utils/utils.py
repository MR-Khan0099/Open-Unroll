import os
import time
import logging
import base64
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from dateutil.parser import parse as parse_date

from simplegmail import Gmail
from simplegmail.query import construct_query
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts.chat import ChatPromptTemplate


import os
print(os.listdir())  # Check if 'client_secret.json' is listed


# Configure logging for better debugging and traceability.
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
load_dotenv()  # Load environment variables from a .env file if present.
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class EmailDraftUtil:
    def __init__(self, gmail=None):
        """
        Initialize the utility. If no Gmail object is provided,
        authenticate using the default client_secret.json.
        """
        if gmail is None:
            self.gmail = self.authenticate_gmail()
        else:
            self.gmail = gmail

    def authenticate_gmail(self):
        """
        Authenticates the Gmail API using the client_secret.json file.
        On the first run, a browser window will open for you to grant permissions.
        
        Returns:
            An authenticated Gmail object.
        """
        # Debugging: Print working directory and file existence
        import os
        print("[DEBUG] Current working directory:", os.getcwd())
        print("[DEBUG] Files in directory:", os.listdir())
        print("[DEBUG] client_secret.json exists:", os.path.exists("client_secret.json"))
        try:
            gmail = Gmail()  # Uses client_secret.json by default.
            logging.info("Successfully authenticated with Gmail.")
            return gmail
        except Exception as e:
            logging.error("Failed to authenticate with Gmail: %s", e)
            raise

def authenticate_gmail():
    """
    Module-level helper to authenticate and return a Gmail object.
    """
    ed_util = EmailDraftUtil()
    return ed_util.gmail

