# gmail_attachment_summarizer.py

import os
import tempfile
import warnings
from datetime import datetime, timedelta
from dateutil.parser import parse as parse_date
from dateutil.tz import tzlocal
from dotenv import load_dotenv

from simplegmail import Gmail
from markitdown import MarkItDown
from langchain_groq import ChatGroq
from langchain.prompts.chat import ChatPromptTemplate

# Suppress resource and deprecation warnings.
warnings.filterwarnings("ignore", category=ResourceWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Load environment variables (e.g., GROQ_API_KEY) from GitHub repository secrets.
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class GmailAttachmentSummarizer:
    """
    A class to fetch Gmail emails with attachments and generate concise summaries
    of both the email content and each attachment using MarkItDown and ChatGroq.
    """

    def __init__(self, time_frame_hours: int = 4):
        """
        Initialize the summarizer with a specified time frame (in hours) and instantiate the clients.
        :param time_frame_hours: The number of past hours to search for emails.
        """
        self.time_frame_hours = time_frame_hours
        self.gmail = Gmail()  # Uses your preconfigured Gmail secret file.
        self.markdown_converter = MarkItDown()
        self.llm = ChatGroq(
            model="llama3-8b-8192",
            temperature=0,
            max_tokens=300,
            timeout=60,
            max_retries=2,
            api_key=GROQ_API_KEY  # Now using the repository secret.
        )

    def fetch_emails_with_attachments(self):
        """
        Fetch emails from the inbox within the past time frame that contain attachments.
        :return: List of email objects with attachments.
        """
        time_threshold = datetime.now(tz=tzlocal()) - timedelta(hours=self.time_frame_hours)
        date_query = time_threshold.strftime("%Y/%m/%d")
        query = f"in:inbox -category:promotions after:{date_query}"
        emails = self.gmail.get_messages(query=query)
        filtered = []
        for email in emails:
            try:
                email_date = parse_date(email.date)
            except Exception:
                continue
            if email_date >= time_threshold and hasattr(email, 'attachments') and email.attachments:
                filtered.append(email)
        return filtered

  

    def summarize_emails(self) -> str:
        """
        Fetches emails with attachments in the past time frame and builds a combined summary.
        :return: A combined summary string of all relevant emails.
        """
        emails = self.fetch_emails_with_attachments()
        if not emails:
            return f"No emails with attachments found in the past {self.time_frame_hours} hours."
        
        summaries = [self.summarize_email(email) for email in emails]
        return "\n\n---------------------\n\n".join(summaries)


def main():
    # Example usage when running this module directly.
    print("=== Email Attachment Summarizer ===")
    summarizer = GmailAttachmentSummarizer(time_frame_hours=48)
    print("Fetching emails with attachments from the past 48 hours...\n")
    final_summary = summarizer.summarize_emails()
    print("Final Summary:\n")
    print(final_summary)


if __name__ == "__main__":
    main()
