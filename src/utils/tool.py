import os
import re
import json
import time
from datetime import datetime, timedelta
from datetime import datetime, timedelta
from dateutil.parser import parse as parse_date
from dateutil.tz import tzlocal
from dotenv import load_dotenv

from simplegmail import Gmail
from langchain_groq import ChatGroq
from langchain.prompts.chat import ChatPromptTemplate
import requests
from bs4 import BeautifulSoup

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from email.utils import parseaddr
from email.message import EmailMessage
# Load environment variables (including GROQ_API_KEY) from repository secrets.
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


class GmailChat:
    def __init__(self, time_frame_hours: int = 24):
        """
        Initialize with a desired timeframe (in hours) for fetching emails.
        """
        self.time_frame_hours = time_frame_hours

    def fetch_emails(self):
        """
        Fetches emails from the inbox within the past time_frame_hours.
        Returns a list of email objects.
        """
        gmail = Gmail()
        time_threshold = datetime.now(tz=tzlocal()) - timedelta(hours=self.time_frame_hours)
        date_query = time_threshold.strftime("%Y/%m/%d")
        query = f"in:inbox -category:promotions after:{date_query}"
        emails = gmail.get_messages(query=query)
        filtered = []
        for email in emails:
            try:
                email_date = parse_date(email.date)
            except Exception:
                continue
            if email_date >= time_threshold:
                filtered.append(email)
        return filtered

    @staticmethod
    def summarize_email(email):
        """
        Returns a summary string for an email including subject, sender, date,
        a snippet from the body, and any attachment filenames if present.
        """
        summary = f"Subject: {email.subject}\nSender: {email.sender}\nDate: {email.date}\n"
        if hasattr(email, 'plain') and email.plain:
            body = email.plain
        else:
            body = email.snippet
        if len(body) > 200:
            body = body[:200] + "..."
        summary += f"Snippet: {body}\n"
        if hasattr(email, 'attachments') and email.attachments:
            att_names = [att.filename for att in email.attachments]
            summary += f"Attachments: {', '.join(att_names)}\n"
        return summary

    def build_emails_summary(self, emails):
        """
        Builds and returns a combined summary text for a list of emails.
        """
        summaries = [self.summarize_email(email) for email in emails]
        return "\n---------------------\n".join(summaries)

    def answer_query(self, query, emails_summary):
        """
        Uses ChatGroq to answer the query based on the provided emails summary.
        Returns the answer as a string.
        """
        llm = ChatGroq(
            model="llama3-8b-8192",
            temperature=0,
            max_tokens=150,
            timeout=60,
            max_retries=2,
            api_key=GROQ_API_KEY  # Using the repository secret
        )
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are a helpful assistant that answers queries based on a collection of email summaries. Provide a clear yes/no answer followed by a brief explanation."
            ),
            (
                "human",
                f"User query: {query}\n\nHere are the summaries of my emails from the past {self.time_frame_hours} hours:\n\n{emails_summary}\n\nBased on the above, answer the query."
            )
        ])
        messages_formatted = prompt.format_messages()
        response = llm.invoke(messages_formatted)
        return response.content.strip()

    def chat(self, query):
        """
        Fetches emails from the past timeframe, builds summaries, and then answers the query.
        Returns the final answer.
        """
        emails = self.fetch_emails()
        if not emails:
            return f"No emails found in the past {self.time_frame_hours} hours."
        emails_summary = self.build_emails_summary(emails)
        answer = self.answer_query(query, emails_summary)
        return answer

def delete_verified_spam_emails(verify_with_llm=False):
    """
    Deletes emails in the spam folder. Optionally verifies with LLM before deleting.
    """
    gmail = Gmail()
    spam_emails = gmail.get_messages(query="in:spam")
    deleted_count = 0
    if not spam_emails:
        return "No spam emails found."
    if verify_with_llm:
        llm = ChatGroq(
            model="llama3-8b-8192",
            temperature=0,
            max_tokens=50,
            timeout=30,
            max_retries=2,
            api_key=GROQ_API_KEY
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an email assistant. Answer only 'Yes' if the email is definitely spam, otherwise 'No'."),
            ("human", "Subject: {subject}\nSender: {sender}\nBody: {body}")
        ])
    for email in spam_emails:
        should_delete = True
        if verify_with_llm:
            body = getattr(email, 'plain', None) or getattr(email, 'snippet', "")
            prompt_inputs = {"subject": email.subject, "sender": email.sender, "body": body}
            try:
                messages_formatted = prompt.format_messages(**prompt_inputs)
                response = llm.invoke(messages_formatted)
                if response.content.strip().lower() != "yes":
                    should_delete = False
            except Exception:
                should_delete = False
        if should_delete:
            try:
                email.trash()  # Moves to trash
                deleted_count += 1
            except Exception:
                continue
    return f"Deleted {deleted_count} spam emails."  # Returns a summary

def delete_old_promotions(days=7):
    """
    Deletes promotion emails older than the specified number of days.
    """
    gmail = Gmail()
    promo_emails = gmail.get_messages(query="category:promotions")
    deleted_count = 0
    if not promo_emails:
        return "No promotion emails found."
    threshold = datetime.now(tz=tzlocal()) - timedelta(days=days)
    for email in promo_emails:
        try:
            email_date = parse_date(email.date)
            if email_date < threshold:
                email.trash()
                deleted_count += 1
        except Exception:
            continue
    return f"Deleted {deleted_count} promotion emails older than {days} days."


def delete_old_social(days=7):
    """
    Deletes social emails older than the specified number of days.
    """
    gmail = Gmail()
    promo_emails = gmail.get_messages(query="category:social")
    deleted_count = 0
    if not promo_emails:
        return "No promotion emails found."
    threshold = datetime.now(tz=tzlocal()) - timedelta(days=days)
    for email in promo_emails:
        try:
            email_date = parse_date(email.date)
            if email_date < threshold:
                email.trash()
                deleted_count += 1
        except Exception:
            continue
    return f"Deleted {deleted_count} social emails older than {days} days."

def categorize_emails(time_frame_hours=24):
    """
    Categorizes recent emails using LLM. Returns a list of (email, category) tuples.
    """
    gmail = Gmail()
    time_threshold = datetime.now(tz=tzlocal()) - timedelta(hours=time_frame_hours)
    date_query = time_threshold.strftime("%Y/%m/%d")
    query = f"in:inbox after:{date_query}"
    emails = gmail.get_messages(query=query)
    if not emails:
        return []
    llm = ChatGroq(
        model="llama3-8b-8192",
        temperature=0,
        max_tokens=20,
        timeout=30,
        max_retries=2,
        api_key=GROQ_API_KEY
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an email assistant. Categorize the email as one of: Work, Personal, Finance, Shopping, Social, Updates, Other. Return only the category name."),
        ("human", "Subject: {subject}\nSender: {sender}\nBody: {body}")
    ])
    categorized = []
    for email in emails:
        body = getattr(email, 'plain', None) or getattr(email, 'snippet', "")
        prompt_inputs = {"subject": email.subject, "sender": email.sender, "body": body}
        try:
            messages_formatted = prompt.format_messages(**prompt_inputs)
            response = llm.invoke(messages_formatted)
            category = response.content.strip()
        except Exception:
            category = "Other"
        categorized.append((email, category))
    return categorized

def get_priority_emails(time_frame_hours=24, top_n=5):
    """
    Returns the top N important emails from the inbox using LLM scoring.
    """
    gmail = Gmail()
    time_threshold = datetime.now(tz=tzlocal()) - timedelta(hours=time_frame_hours)
    date_query = time_threshold.strftime("%Y/%m/%d")
    query = f"in:inbox -category:promotions after:{date_query}"
    emails = gmail.get_messages(query=query)
    if not emails:
        return []
    llm = ChatGroq(
        model="llama3-8b-8192",
        temperature=0,
        max_tokens=10,
        timeout=30,
        max_retries=2,
        api_key=GROQ_API_KEY
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an email assistant. Score the importance of the email from 1 (not important) to 10 (very important). Return only the number."),
        ("human", "Subject: {subject}\nSender: {sender}\nBody: {body}")
    ])
    scored = []
    for email in emails:
        body = getattr(email, 'plain', None) or getattr(email, 'snippet', "")
        prompt_inputs = {"subject": email.subject, "sender": email.sender, "body": body}
        try:
            messages_formatted = prompt.format_messages(**prompt_inputs)
            response = llm.invoke(messages_formatted)
            score = float(response.content.strip())
        except Exception:
            score = 0.0
        scored.append((email, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_n]

def detect_phishing_emails(time_frame_hours=24):
    """
    Detects phishing/scam emails using LLM. Returns a list of flagged emails.
    """
    gmail = Gmail()
    time_threshold = datetime.now(tz=tzlocal()) - timedelta(hours=time_frame_hours)
    date_query = time_threshold.strftime("%Y/%m/%d")
    query = f"in:inbox after:{date_query}"
    emails = gmail.get_messages(query=query)
    if not emails:
        return []
    llm = ChatGroq(
        model="llama3-8b-8192",
        temperature=0,
        max_tokens=10,
        timeout=30,
        max_retries=2,
        api_key=GROQ_API_KEY
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an email security assistant. Is this email a phishing or scam attempt? Answer only 'Yes' or 'No'."),
        ("human", "Subject: {subject}\nSender: {sender}\nBody: {body}")
    ])
    flagged = []
    for email in emails:
        body = getattr(email, 'plain', None) or getattr(email, 'snippet', "")
        prompt_inputs = {"subject": email.subject, "sender": email.sender, "body": body}
        try:
            messages_formatted = prompt.format_messages(**prompt_inputs)
            response = llm.invoke(messages_formatted)
            if response.content.strip().lower() == "yes":
                flagged.append(email)
        except Exception:
            continue
    return flagged

def unsubscribe_promotions():
    """
    Intelligently unsubscribes from promotional emails using LLM classification.
    1. Uses LLM to classify emails as important/unimportant
    2. Processes in batches of 50
    3. Only unsubscribes from unimportant promotional emails
    4. Preserves important newsletters (jobs, educational, etc.)
    """
    gmail = Gmail()
    # Fetch all promotional emails
    promo_emails = gmail.get_messages(query="category:promotions")
    
    if not promo_emails:
        return "No promotion emails found."
    
    # Initialize LLM for classification
    llm = ChatGroq(
        model="llama3-8b-8192",  # Updated to currently supported model
        temperature=0,
        max_tokens=50,
        timeout=30,
        max_retries=2,
        api_key=GROQ_API_KEY
    )
    
    # Classification prompt
    classification_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an email assistant that classifies promotional emails as IMPORTANT or UNIMPORTANT.
        
        IMPORTANT emails include:
        - Educational content
        - Professional development
        - Job opportunities and career-related
        - Research and academic content
        
        UNIMPORTANT emails include:
        - courses, learning
        - Generic promotional content
        - Newsletters from unknown sources
        - Health and wellness content
        - Technology updates and tutorials
        - Generic marketing promotions
        - Sales and discounts
        - Entertainment newsletters
        - Spam-like content
        - Generic promotional content
        - Unsolicited offers
        - Event Invitations
        - Survey Requests
        - Social Media Notifications
        - Unsolicited newsletters
        - Unrelated content
        - Industry news and insights
        - Financial/Investment newsletters
        
        Classify the email based on the subject, sender, and snippet.
        Return only the classification as either IMPORTANT or UNIMPORTANT.
        
        Respond with only: IMPORTANT or UNIMPORTANT"""),
        ("human", "Subject: {subject}\nSender: {sender}\nSnippet: {snippet}")
    ])
    
    # Headers to avoid 403 errors
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    unsubscribed_count = 0
    failed_count = 0
    preserved_count = 0
    details = []
    unsubscribed_list = []
    preserved_list = []
    
    # Process in batches of 50
    batch_size = 50
    total_emails = len(promo_emails)
    
    print(f" Found {total_emails} promotional emails. Processing in batches of {batch_size}...")
    
    for i in range(0, total_emails, batch_size):
        batch = promo_emails[i:i + batch_size]
        batch_num = i//batch_size + 1
        total_batches = (total_emails + batch_size - 1)//batch_size
        
        print(f"\n BATCH {batch_num}/{total_batches} - Processing {len(batch)} emails...")
        print("=" * 60)
        
        # Classify all emails in this batch
        batch_classifications = []
        print(" CLASSIFYING EMAILS IN THIS BATCH:")
        print("-" * 40)
        
        for email in batch:
            try:
                snippet = getattr(email, 'snippet', '') or getattr(email, 'plain', '')[:200]
                classification_inputs = {
                    "subject": email.subject,
                    "sender": email.sender,
                    "snippet": snippet
                }
                
                messages_formatted = classification_prompt.format_messages(**classification_inputs)
                response = llm.invoke(messages_formatted)
                classification = response.content.strip().upper()
                
                batch_classifications.append((email, classification))
                print(f"  {email.sender}: {classification}")
                
            except Exception as e:
                print(f"  Error classifying email from {email.sender}: {e}")
                # If classification fails, preserve the email to be safe
                batch_classifications.append((email, "IMPORTANT"))
        
        # Show batch classification summary
        important_count = sum(1 for _, classification in batch_classifications if classification == "IMPORTANT")
        unimportant_count = sum(1 for _, classification in batch_classifications if classification == "UNIMPORTANT")
        
        print(f"\ BATCH {batch_num} CLASSIFICATION SUMMARY:")
        print(f"   Important emails: {important_count}")
        print(f"    Unimportant emails: {unimportant_count}")
        
        # Process unsubscribe for unimportant emails in this batch
        print(f"\ UNSUBSCRIBING FROM UNIMPORTANT EMAILS IN BATCH {batch_num}:")
        print("-" * 50)
        
        for email, classification in batch_classifications:
            if classification == "UNIMPORTANT":
                print(f"\n Processing: {email.sender} (UNIMPORTANT)")
                
                unsubscribe_url = None
                
                # Check List-Unsubscribe header for a web link
                header_val = email.headers.get("List-Unsubscribe") if hasattr(email, 'headers') else None
                if header_val:
                    for part in header_val.split(','):
                        part = part.strip().strip('<>')
                        if part.lower().startswith('http'):
                            unsubscribe_url = part
                            break

                #  If not found, parse HTML for <a> tags with unsubscribe-like text
                if not unsubscribe_url and hasattr(email, 'html') and email.html:
                    soup = BeautifulSoup(email.html, 'html.parser')
                    # Expanded keywords for better detection
                    keywords = ['unsubscribe', 'manage subscription', 'opt out', 'opt-out', 'unsub', 'cancel subscription', 'stop emails', 'remove from list']
                    for a in soup.find_all('a', href=True):
                        link_text = a.get_text().strip().lower()
                        href = a['href']
                        
                        # Check if any keyword is in the link text
                        if any(keyword in link_text for keyword in keywords):
                            # If relative, join with sender's domain
                            if not href.lower().startswith('http'):
                                # Extract sender domain
                                sender_email = email.sender if hasattr(email, 'sender') else ""
                                domain = ""
                                match = re.search(r'@([A-Za-z0-9.-]+)', sender_email)
                                if match:
                                    domain = match.group(1)
                                if domain:
                                    base_url = f"https://{domain}"
                                    unsubscribe_url = urljoin(base_url, href)
                                else:
                                    unsubscribe_url = href  # fallback
                            else:
                                unsubscribe_url = href
                            break
                        
                        # Also check if 'unsubscribe' is in the href itself
                        elif 'unsubscribe' in href.lower():
                            if not href.lower().startswith('http'):
                                # Extract sender domain
                                sender_email = email.sender if hasattr(email, 'sender') else ""
                                domain = ""
                                match = re.search(r'@([A-Za-z0-9.-]+)', sender_email)
                                if match:
                                    domain = match.group(1)
                                if domain:
                                    base_url = f"https://{domain}"
                                    unsubscribe_url = urljoin(base_url, href)
                                else:
                                    unsubscribe_url = href  # fallback
                            else:
                                unsubscribe_url = href
                            break

                # Try GET, then POST to the unsubscribe URL with headers
                if unsubscribe_url:
                    try:
                        resp = requests.get(unsubscribe_url, headers=headers, timeout=10)
                        if 200 <= resp.status_code < 300:
                            unsubscribed_count += 1
                            success_msg = f" SUCCESSFULLY UNSUBSCRIBED from: {email.sender}"
                            print(success_msg)
                            details.append(f"Unsubscribed from: {email.sender} ({unsubscribe_url}) [GET {resp.status_code}]")
                            unsubscribed_list.append(email.sender)
                            
                            # Delete the email after successful unsubscribe
                            try:
                                email.trash()
                                print(f"  Deleted email from: {email.sender}")
                                details.append(f"  -> Email moved to trash")
                            except Exception as e:
                                print(f"  Failed to delete email from: {email.sender}: {e}")
                                details.append(f"  -> Failed to delete email: {e}")
                                
                        else:
                            details.append(f"GET request failed for: {email.sender} ({unsubscribe_url}) [Status: {resp.status_code}]. Trying POST...")
                            try:
                                resp_post = requests.post(unsubscribe_url, headers=headers, timeout=10)
                                if 200 <= resp_post.status_code < 300:
                                    unsubscribed_count += 1
                                    success_msg = f" SUCCESSFULLY UNSUBSCRIBED from: {email.sender}"
                                    print(success_msg)
                                    details.append(f"Unsubscribed from: {email.sender} ({unsubscribe_url}) [POST {resp_post.status_code}]")
                                    unsubscribed_list.append(email.sender)
                                    
                                    # Delete the email after successful unsubscribe
                                    try:
                                        email.trash()
                                        print(f"  Deleted email from: {email.sender}")
                                        details.append(f"  -> Email moved to trash")
                                    except Exception as e:
                                        print(f"  Failed to delete email from: {email.sender}: {e}")
                                        details.append(f"  -> Failed to delete email: {e}")
                                        
                                else:
                                    failed_count += 1
                                    details.append(f"POST request also failed for: {email.sender} ({unsubscribe_url}) [Status: {resp_post.status_code}]")
                            except Exception as e_post:
                                failed_count += 1
                                details.append(f"POST request error for: {email.sender} ({unsubscribe_url}): {e_post}")
                    except Exception as e_get:
                        details.append(f"GET request error for: {email.sender} ({unsubscribe_url}): {e_get}. Trying POST...")
                        try:
                            resp_post = requests.post(unsubscribe_url, headers=headers, timeout=10)
                            if 200 <= resp_post.status_code < 300:
                                unsubscribed_count += 1
                                success_msg = f" SUCCESSFULLY UNSUBSCRIBED from: {email.sender}"
                                print(success_msg)
                                details.append(f"Unsubscribed from: {email.sender} ({unsubscribe_url}) [POST {resp_post.status_code}]")
                                unsubscribed_list.append(email.sender)
                                
                                # Delete the email after successful unsubscribe
                                try:
                                    email.trash()
                                    print(f"  Deleted email from: {email.sender}")
                                    details.append(f"  -> Email moved to trash")
                                except Exception as e:
                                    print(f"  Failed to delete email from: {email.sender}: {e}")
                                    details.append(f"  -> Failed to delete email: {e}")
                                    
                            else:
                                failed_count += 1
                                details.append(f"POST request also failed for: {email.sender} ({unsubscribe_url}) [Status: {resp_post.status_code}]")
                        except Exception as e_post:
                            failed_count += 1
                            details.append(f"POST request error for: {email.sender} ({unsubscribe_url}): {e_post}")
                else:
                    failed_count += 1
                    details.append(f"No unsubscribe link found for: {email.sender}")
                    print(f" No unsubscribe link found for: {email.sender}")
            else:
                # IMPORTANT email - preserve it
                preserved_count += 1
                preserved_list.append(email.sender)
                print(f" PRESERVED important email from: {email.sender}")

        # Step 4: Show batch completion summary
        print(f"\n BATCH {batch_num} COMPLETED!")
        print(f"   Processed: {len(batch)} emails")
        print(f"  Preserved: {important_count} important emails")
        print(f"    Unsubscribed: {unimportant_count} unimportant emails")
        print("=" * 60)

        # Be polite to servers between batches
        import time
        time.sleep(2)

    # Print comprehensive summary
    print(f"\n INTELLIGENT UNSUBSCRIBE SUMMARY:")
    print(f" Total promotional emails processed: {total_emails}")
    print(f" Successfully unsubscribed from: {unsubscribed_count} emails")
    print(f" Preserved important emails: {preserved_count} emails")
    print(f" Failed to unsubscribe from: {failed_count} emails")
    
    if unsubscribed_list:
        print(f"\n SUCCESSFULLY UNSUBSCRIBED EMAILS:")
        for i, sender in enumerate(unsubscribed_list, 1):
            print(f"  {i}. {sender}")
    
    if preserved_list:
        print(f"\n PRESERVED IMPORTANT EMAILS:")
        for i, sender in enumerate(preserved_list, 1):
            print(f"  {i}. {sender}")
    
    summary = f"Intelligent unsubscribe completed: {unsubscribed_count} unsubscribed, {preserved_count} preserved, {failed_count} failed."
    return summary + "\n" + "\n".join(details)



def main():
    print("=== Email Chat Mode ===")
    query = input("Enter your query: ")
    chat_instance = GmailChat(time_frame_hours=24)
    print("Fetching and processing your emails...")
    answer = chat_instance.chat(query)
    result = unsubscribe_promotions()
    print("\nAnswer:")
    print(answer)

if __name__ == "__main__":
    main()
