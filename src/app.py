import os
import time
import re
import json
import html  # For escaping HTML special characters
import uuid
from datetime import datetime, timedelta
from dateutil.parser import parse as parse_date
from dateutil.tz import tzlocal, gettz
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from simplegmail import Gmail
from langchain_groq import ChatGroq
from langchain.prompts.chat import ChatPromptTemplate
from utils.tool import GmailChat, delete_verified_spam_emails, delete_old_promotions, unsubscribe_promotions, delete_old_social, get_priority_emails, categorize_emails, detect_phishing_emails
from utils.attachment import GmailAttachmentSummarizer
from dotenv import load_dotenv

load_dotenv()
# Load any existing environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --------------------------------------------------
# Create a session-specific ID (if not already set)
# --------------------------------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = uuid.uuid4().hex
# Session-specific filename for client secret
client_file = f"client_secret_{st.session_state.session_id}.json"

# --------------------------------------------------
# Credentials Upload & Validation (Gmail client secret only)
# --------------------------------------------------
# Initialize show_upload_form if it's not set
if "show_upload_form" not in st.session_state:
    st.session_state.show_upload_form = False

if "client_secret" not in st.session_state:
    # First, show the welcome screen with features
    st.markdown(
        """
        <style>
        .welcome-container {
            background-color: #0d1117; /* GitHub Dark Theme Background */
            color: #c9d1d9; /* GitHub Dark Theme Text */
            padding: 40px;
            border-radius: 16px;
            text-align: center;
            margin: 20px auto;
            width: 90%;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.5);
            border: 1px solid #30363d;
        }
        .welcome-container h1 {
            color: #58a6ff; /* GitHub Blue */
            font-size: 3.5em;
            font-weight: 800;
            margin-bottom: 10px;
        }
        .welcome-container h3 {
            color: #c9d1d9;
            font-size: 1.8em;
            font-weight: 400;
            margin-bottom: 30px;
        }
        .feature-list {
            list-style-type: none;
            padding: 0;
            text-align: left;
            margin: 0 auto 30px auto;
            max-width: 600px;
        }
        .feature-list li {
            background-color: #161b22;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 4px solid #58a6ff;
            border-radius: 8px;
            font-size: 1.1em;
            display: flex;
            align-items: center;
        }
        .feature-list li strong {
            color: #58a6ff;
            min-width: 150px;
        }
        .feature-list li span {
            color: #c9d1d9;
        }
        .start-button {
            background-color: #58a6ff !important;
            color: #0d1117 !important;
            border: none;
            border-radius: 8px;
            padding: 15px 30px;
            font-size: 1.2em;
            font-weight: bold;
            cursor: pointer;
            transition: background-color 0.3s, transform 0.2s;
        }
        .start-button:hover {
            background-color: #4493e8 !important;
            transform: translateY(-2px);
        }
        .upload-form-container {
            background-color: #161b22;
            padding: 30px;
            border-radius: 12px;
            margin-top: 30px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            border: 1px solid #30363d;
        }
        .stFileUploader > div > button {
            color: #000000;
            background-color: #58a6ff;
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-size: 1.1em;
            font-weight: bold;
            transition: background-color 0.3s;
        }
        .stFileUploader > div > button:hover {
            background-color: #4493e8;
        }
        </style>
        <div class="welcome-container">
            <h1>Welcome to Open-Unroll ✉️</h1>
            <h3>Reclaim your inbox with the power of AI.</h3>
            <ul class="feature-list">
                <li>
                    <strong>Effortless Unsubscribe:</strong>
                    <span>Instantly get rid of annoying promotional emails and newsletters with a single click.</span>
                </li>
                <li>
                    <strong>AI-Powered Priority Inbox:</strong>
                    <span>Our intelligent AI identifies and surfaces your most critical messages, so you never miss what's important.</span>
                </li>
                <li>
                    <strong>Concise Summaries:</strong>
                    <span>Get the gist of any long email or attachment in a quick, easy-to-read summary.</span>
                </li>
                <li>
                    <strong>One-Click Cleanup:</strong>
                    <span>Automatically delete old spam, social notifications, and bulk mail with powerful, customizable cleanup tools.</span>
                </li>
            </ul>
            <p><strong>Reclaim Your Inbox, Reclaim Your Time.</strong> Stop drowning in email and start focusing on what truly matters.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    if not st.session_state.show_upload_form:
        if st.button("Connect to Gmail and Get Started", key="start_button"):
            st.session_state.show_upload_form = True
            st.experimental_rerun()
    
    if st.session_state.show_upload_form:
        with st.form(key="credentials_form", clear_on_submit=True):
            st.markdown(
                """
                <div class="upload-form-container">
                    <p style="color: white;">Please upload your Gmail client secret JSON file to securely connect. If you don't have one, please refer to this <a href="https://stackoverflow.com/questions/52200589/where-to-download-your-client-secret-file-json-file#:~:text=Go%20to%20your%20Google%20API%20Console%20where%20you%27ll,arrow%20on%20the%20farthest%20right%20of%20the%20page%3A" target="_blank" style="color:#58a6ff;">guide here</a>.</p>
                """,
                unsafe_allow_html=True,
            )
            uploaded_file = st.file_uploader("Upload Gmail Client Secret JSON", type=["json"])
            submitted = st.form_submit_button("Submit Credentials")
            st.markdown("</div>", unsafe_allow_html=True)
            
            if submitted:
                if not uploaded_file:
                    st.error("Please upload your Gmail client secret JSON file.")
                else:
                    try:
                        client_secret_data = json.load(uploaded_file)
                        # Validate structure: check for "installed" or "web" keys
                        if "installed" in client_secret_data or "web" in client_secret_data:
                            st.session_state.client_secret = client_secret_data
                            # Write the uploaded client secret to a session-specific file
                            with open(client_file, "w") as f:
                                json.dump(client_secret_data, f)
                            st.success("Client secret file uploaded and validated successfully.")
                            st.experimental_rerun()
                        else:
                            st.error("Invalid client secret file format. Please upload a valid Gmail client secret JSON file.")
                    except Exception as e:
                        st.error(f"Error processing credentials: {e}")
    st.stop()  # Halt further execution until valid credentials are provided

# -------------------------------
# Session State Initialization
# -------------------------------
if "result" not in st.session_state:
    st.session_state.result = None
if "email_summaries" not in st.session_state:
    st.session_state.email_summaries = {}
if "mode" not in st.session_state:
    st.session_state.mode = "home"  # "home" or "chat"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # List of dicts: {"role": "user"/"assistant", "text": ...}

# ------------------------------------
# Helper: Format date to CET with AM/PM (no seconds)
# ------------------------------------
def format_date(date_str):
    try:
        dt = parse_date(date_str)
        cet_tz = gettz("Europe/Berlin")
        dt_cet = dt.astimezone(cet_tz)
        return dt_cet.strftime("%Y-%m-%d %I:%M%p")
    except Exception as e:
        st.error(f"Error formatting date: {e}")
        return date_str

# ------------------------------------
# Helper: Summarize Email Content + Attachments
# ------------------------------------
def summarize_email(email):
    """
    Summarizes the email body using ChatGroq. If the email has attachments,
    it calls the GmailAttachmentSummarizer to generate attachment summaries.
    The final summary is a combination of the text summary and the attachment summary.
    """
    email_body = getattr(email, 'plain', None) or getattr(email, 'snippet', "")
    if email_body:
        if len(email_body) > 2000:
            email_body = email_body[:2000] + "..."
        llm = ChatGroq(
            model="llama3-8b-8192",
            temperature=0.7,
            max_tokens=75,
            timeout=30,
            max_retries=2,
        )
        summary_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                (
                    "You are Mohammed Rizwan’s professional email assistant. Summarize the following email content concisely in 2-3 lines in English only. "
                    "Do not use any German language. Return only the summary."
                )
            ),
            (
                "human",
                "Email Content:\n{body}"
            )
        ])
        prompt_inputs = {"body": email_body}
        try:
            messages_formatted = summary_prompt.format_messages(**prompt_inputs)
            response_obj = llm.invoke(messages_formatted)
            text_summary = response_obj.content.strip()
        except Exception as e:
            text_summary = f"Error summarizing text: {e}"
    else:
        text_summary = ""

    if hasattr(email, 'attachments') and email.attachments:
        att_summarizer = GmailAttachmentSummarizer(time_frame_hours=4)
        att_summaries = []
        for att in email.attachments:
            try:
                att_summary = att_summarizer.summarize_attachment(att)
                att_summaries.append(att_summary)
            except Exception as e:
                att_summaries.append(f"Error summarizing attachment: {e}")
        attachments_summary = " ".join(att_summaries)
        combined_summary = f"{text_summary} \n\n Attachments Summary: {attachments_summary}"
        full_summary = f"This email contains attachments. {combined_summary}"
    else:
        full_summary = text_summary

    return full_summary

# ------------------------------------
# Email Prioritizer Function
# ------------------------------------
def email_prioritizer(time_frame_hours: int = 24):
    try:
        gmail = Gmail(client_secret_file=client_file)
    except Exception as e:
        st.error(f"Error initializing Gmail: {e}")
        return json.dumps({"top_important_emails": [], "reply_needed_emails": []}, indent=4), []
    
    time_threshold = datetime.now(tz=tzlocal()) - timedelta(hours=time_frame_hours)
    date_query = time_threshold.strftime("%Y/%m/%d")
    query = f"in:inbox -category:promotions after:{date_query}"
    
    try:
        messages = gmail.get_messages(query=query)
    except Exception as e:
        st.error(f"Error fetching messages: {e}")
        return json.dumps({"top_important_emails": [], "reply_needed_emails": []}, indent=4), []
    
    if not messages:
        result = {"top_important_emails": [], "reply_needed_emails": []}
        return json.dumps(result, indent=4), []
    
    recent_messages = []
    for msg in messages:
        try:
            msg_dt = parse_date(msg.date)
        except Exception as e:
            st.error(f"Could not parse date for message with subject '{msg.subject}': {e}")
            continue
        if msg_dt >= time_threshold:
            recent_messages.append(msg)
    st.write(f"**Found {len(recent_messages)} messages** from the past {time_frame_hours} hours.")
    
    if not recent_messages:
        result = {"top_important_emails": [], "reply_needed_emails": []}
        return json.dumps(result, indent=4), []
    
    filtered_messages = []
    marketing_keywords = ["marketing", "discount", "sale", "offer", "deal"]
    for msg in recent_messages:
        lower_subject = msg.subject.lower() if hasattr(msg, 'subject') else ""
        lower_sender = msg.sender.lower() if hasattr(msg, 'sender') else ""
        if any(keyword in lower_subject for keyword in marketing_keywords) or any(keyword in lower_sender for keyword in marketing_keywords):
            continue
        filtered_messages.append(msg)
    
    if not filtered_messages:
        result = {"top_important_emails": [], "reply_needed_emails": []}
        return json.dumps(result, indent=4), []
    
    llm = ChatGroq(
        model="llama3-8b-8192",
        temperature=0,
        max_tokens=50,
        timeout=60,
        max_retries=2,
    )
    ranking_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            (
                "You are an intelligent email assistant specialized in evaluating email urgency and importance. "
                "Score the following email on a scale from 1 to 10, where 10 means extremely important and urgent, and 1 means not important at all. "
                "Return only a single numerical score with no additional text."
            )
        ),
        (
            "human",
            "Email subject: {subject}\nEmail received on: {date}\nEmail body: {body}"
        )
    ])
    
    top_emails_list = []
    max_body_length = 500
    for email in filtered_messages:
        if hasattr(email, 'plain') and email.plain:
            email_body = email.plain
        else:
            email_body = email.snippet if hasattr(email, 'snippet') else ""
        if len(email_body) > max_body_length:
            email_body = email_body[:max_body_length] + "..."
    
        rank_inputs = {"subject": email.subject, "date": email.date, "body": email_body}
        try:
            messages_formatted = ranking_prompt.format_messages(**rank_inputs)
            response_obj = llm.invoke(messages_formatted)
            response_text = response_obj.content.strip()
            score_match = re.search(r'\d+(\.\d+)?', response_text)
            score = float(score_match.group()) if score_match else 0.0
        except Exception as e:
            st.error(f"Error processing email with subject '{email.subject}' for ranking: {e}")
            score = 0.0
        top_emails_list.append((email, score))
    
    time.sleep(1)
    
    sorted_emails = sorted(top_emails_list, key=lambda x: x[1], reverse=True)
    top_emails = sorted_emails[:5]
    
    top_emails_output = []
    for email, score in top_emails:
        email_summary = summarize_email(email)
        clean_summary = html.escape(email_summary.replace("\n", " ").strip())
        email_info = {
            "Sender": email.sender,
            "Summary": clean_summary,
            "Date": format_date(email.date),
            "Importance Score": score
        }
        top_emails_output.append(email_info)
    
    result = {"top_important_emails": top_emails_output}
    return json.dumps(result, indent=4), top_emails_output

# ------------------------------------
# Helper: Render HTML table with custom styling for Top Emails
# ------------------------------------
def render_table(df: pd.DataFrame) -> str:
    html_table = df.to_html(index=False, classes="custom-table", border=0)
    style = """
    <style>
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        font-family: sans-serif;
        background-color: #161b22; /* GitHub's slightly lighter dark background */
        color: #c9d1d9;
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #30363d;
    }
    .custom-table th, .custom-table td {
        border: 1px solid #30363d;
        padding: 15px;
        text-align: left;
    }
    .custom-table th {
        background-color: #0d1117; /* GitHub's main dark background */
        color: #58a6ff;
        font-weight: bold;
        font-size: 1.1em;
    }
    .custom-table tr:hover {
        background-color: #1f2732;
    }
    .custom-table td {
        color: #c9d1d9;
    }
    </style>
    """
    return style + html_table

# ------------------------------------
# Main App Interface: Open-Unroll
# ------------------------------------
st.set_page_config(
    page_title="Open-Unroll",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* Global Styles */
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
    }

    /* Main content area */
    .main .block-container {
        background-color: #0d1117; /* GitHub Dark Theme Background */
        color: #c9d1d9; /* GitHub Dark Theme Text */
        border-radius: 16px;
        padding: 3rem 2rem;
    }
    /* Sidebar: Revert to dark theme for consistency and readability */
    [data-testid="stSidebar"] {
        background-color: #161b22; /* Slightly lighter than main for distinction */
        color: #c9d1d9;
        border-right: 1px solid #30363d;
    }
    /* Ensure all text within the sidebar is light */
    [data-testid="stSidebar"] * {
        color: #c9d1d9 !important;
    }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #58a6ff !important;
    }
    /* Ensure number input text is visible */
    [data-testid="stSidebar"] .stNumberInput input {
        background-color: #0d1117; /* Darker background for input */
        color: #c9d1d9 !important; /* Light text for contrast */
        border: 1px solid #30363d;
    }
    /* Ensure checkbox text is visible */
    [data-testid="stSidebar"] .stCheckbox span {
        color: #c9d1d9 !important;
    }

    /* Button styling */
    div.stButton button {
        background-color: #58a6ff; /* GitHub Blue */
        color: #0d1117;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: bold;
        border: none;
        transition: background-color 0.3s, transform 0.2s;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    div.stButton button:hover {
        background-color: #4493e8;
        transform: translateY(-2px);
    }
    /* Text Input and Selectbox styling */
    .stTextInput input, .stSelectbox > div {
        color: #c9d1d9 !important;
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }
    /* Headers */
    h1, h2, h3, h4 {
        color: #58a6ff;
    }
    p, .stMarkdown, label {
        color: #c9d1d9;
    }
    hr {
        border-top: 1px solid #30363d;
    }

    /* Card-like container for sections */
    .card-container {
        background-color: #161b22;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        margin-bottom: 2rem;
    }
    
    /* Hero section */
    .hero-section {
        text-align: center;
        padding: 50px 0;
        background: linear-gradient(135deg, #0d1117, #161b22);
        border-radius: 16px;
        margin-bottom: 30px;
    }
    .hero-section h1 {
        font-size: 3.5rem;
        font-weight: 800;
        color: #58a6ff;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.4);
    }
    .hero-section h3 {
        font-size: 1.8rem;
        font-weight: 400;
        color: #c9d1d9;
        margin-bottom: 20px;
    }
    .hero-section p {
        max-width: 800px;
        margin: 0 auto;
        font-size: 1.2rem;
        line-height: 1.8;
        color: #8b949e;
    }
    
    .stAlert {
        border-radius: 8px;
    }
    
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar Mode Toggle: Chat Inbox vs Home.
if "mode" not in st.session_state:
    st.session_state.mode = "home"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

with st.sidebar:
    st.markdown("---")
    st.markdown("<h2>Navigation</h2>", unsafe_allow_html=True)
    if st.session_state.mode == "home":
        if st.button("💬 Go to Inbox Chat"):
            st.session_state.mode = "chat"
    else:
        if st.button("🏠 Back to Home"):
            st.session_state.mode = "home"
    st.markdown("---")
    st.markdown("<h2>Email Cleanup</h2>", unsafe_allow_html=True)

    # Spam Cleanup
    st.markdown("<h3>Spam Cleanup</h3>", unsafe_allow_html=True)
    verify_spam = st.checkbox("Verify with AI before deleting spam?", value=False)
    if st.button("🗑️ Delete Verified Spam Emails"):
        with st.spinner("Deleting spam emails..."):
            result = delete_verified_spam_emails(verify_with_llm=verify_spam)
        st.success(result)
    
    # Promotion Cleanup
    st.markdown("---")
    st.markdown("<h3>Promotion Cleanup</h3>", unsafe_allow_html=True)
    promo_days = st.number_input("Delete promotions older than (days):", min_value=1, max_value=365, value=7)
    if st.button("🧹 Delete Old Promotion Emails"):
        with st.spinner("Deleting all old promotion emails..."):
            result = delete_old_promotions(days=promo_days)
        st.success(result)
        
    st.markdown("---")
    if st.button("🚫 Unsubscribe from Promotions"):
        with st.spinner("Unsubscribing from promotion emails..."):
            result = unsubscribe_promotions()
        st.success(result)

    # Social Emails Cleanup
    st.markdown("---")
    st.markdown("<h3>Social Emails Cleanup</h3>", unsafe_allow_html=True)
    social_days = st.number_input("Delete social emails older than (days):", min_value=1, max_value=365, value=7)
    if st.button("📦 Delete Old Social Emails"):
        with st.spinner(f"Deleting social emails older than {social_days} days..."):
            result = delete_old_social(days=social_days)
        st.success(result)


# Main UI: Chat Mode or Home Mode.
if st.session_state.mode == "chat":
    st.markdown("<h1 style='color: #58a6ff;'>Open-Unroll Chat 💬</h1>", unsafe_allow_html=True)
    st.markdown("<h4>Ask me to summarize, find, or manage your emails. For example, 'Summarize the most recent email from John Doe.'</h4>", unsafe_allow_html=True)
    
    chat_container = st.container()
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            chat_container.markdown(f"<p style='background-color:#161b22; padding:15px; border-radius:12px;'><strong>You:</strong> {msg['text']}</p>", unsafe_allow_html=True)
        else:
            chat_container.markdown(f"<p style='background-color:#1f2732; padding:15px; border-radius:12px;'><strong>Open-Unroll:</strong> {msg['text']}</p>", unsafe_allow_html=True)
            
    chat_query = st.text_input("Enter your query:", key="chat_query", placeholder="Type your query here...")
    
    if st.button("Send Query"):
        if chat_query:
            with st.spinner("Processing your request..."):
                chat_instance = GmailChat(time_frame_hours=24)
                answer = chat_instance.chat(chat_query)
                st.session_state.chat_history.append({"role": "user", "text": chat_query})
                st.session_state.chat_history.append({"role": "assistant", "text": answer})
                st.experimental_rerun()
else:
    # Improved Hero Section for the home page
    st.markdown(
        """
        <div class="hero-section">
            <h1>Open-Unroll ✉️</h1>
            <h3>Reclaim your inbox with the power of AI.</h3>
            <p><strong>Open-Unroll</strong> is your smart email assistant designed to take control of your inbox. Intelligently prioritize and summarize important emails, get rid of annoying promotions with a single click, and automate the cleanup of your spam and social notifications. Optimize your Gmail and focus on what truly matters.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("<h2>✨ Inbox Prioritization</h2>", unsafe_allow_html=True)
    with st.container():
        st.markdown(
            """
            <div class="card-container">
                <p>Let AI sort through the noise. We'll identify the most important emails in your inbox, based on a customizable timeframe, so you can address them first.</p>
                <div style="margin-top: 20px;">
            """,
            unsafe_allow_html=True
        )
        col1, col2 = st.columns([1, 3])
        with col1:
            time_option = st.selectbox(
                "Select Timeframe:",
                options=["1 Hour", "6 Hours", "12 Hours", "24 Hours", "3 Days", "1 Week", "2 Weeks"],
                index=3,
                help="Choose how old emails should be considered."
            )
            time_mapping = {
                "1 Hour": 1,
                "6 Hours": 6,
                "12 Hours": 12,
                "24 Hours": 24,
                "3 Days": 72,
                "1 Week": 168,
                "2 Weeks": 336
            }
            time_frame_hours = time_mapping[time_option]
            
            if st.button("Fetch & Prioritize Emails"):
                with st.spinner("Fetching and prioritizing emails... Please wait..."):
                    result_json, reply_email_objects = email_prioritizer(time_frame_hours=time_frame_hours)
                    st.session_state.result = json.loads(result_json)
                    st.session_state.reply_email_objects = reply_email_objects
        
        with col2:
            if st.session_state.result:
                result = st.session_state.result
                st.markdown("<h3 style='color: #58a6ff;'>Top Important Emails</h3>", unsafe_allow_html=True)
                if result["top_important_emails"]:
                    df_top = pd.DataFrame(result["top_important_emails"])
                    components.html(render_table(df_top), height=300, scrolling=True)
                else:
                    st.markdown("<p style='color: #8b949e;'>No top important emails found in the selected timeframe.</p>", unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h2>💡 Smart AI Tools</h2>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        tool_col1, tool_col2, tool_col3 = st.columns(3)
        
        with tool_col1:
            st.markdown("<h3>Priority Inbox</h3>", unsafe_allow_html=True)
            st.markdown("<p>Find your most critical messages instantly.</p>", unsafe_allow_html=True)
            if st.button("Show Top Priority Emails"):
                with st.spinner("Scoring emails for importance..."):
                    top_priority = get_priority_emails(time_frame_hours=24, top_n=5)
                if top_priority:
                    for email, score in top_priority:
                        st.markdown(f"<b>Subject:</b> {email.subject} <br> <b>Sender:</b> {email.sender} <br> <b>Date:</b> {email.date} <br> <b>Importance Score:</b> {score}", unsafe_allow_html=True)
                        st.markdown("<hr>", unsafe_allow_html=True)
                else:
                    st.info("No important emails found.")
                    
        with tool_col2:
            st.markdown("<h3>Categorization</h3>", unsafe_allow_html=True)
            st.markdown("<p>Automatically organize emails by topic.</p>", unsafe_allow_html=True)
            if st.button("Categorize Recent Emails"):
                with st.spinner("Categorizing emails with AI..."):
                    categorized = categorize_emails(time_frame_hours=24)
                if categorized:
                    import collections
                    grouped = collections.defaultdict(list)
                    for email, category in categorized:
                        grouped[category].append(email)
                    for category, emails in grouped.items():
                        st.markdown(f"<h4 style='color:#58a6ff;'>{category} ({len(emails)})</h4>", unsafe_allow_html=True)
                        for email in emails:
                            st.markdown(f"<b>Subject:</b> {email.subject} <br> <b>Sender:</b> {email.sender} <br> <b>Date:</b> {email.date}", unsafe_allow_html=True)
                            st.markdown("<hr>", unsafe_allow_html=True)
                else:
                    st.info("No recent emails found to categorize.")
                    
        with tool_col3:
            st.markdown("<h3>Phishing/Scam Detection</h3>", unsafe_allow_html=True)
            st.markdown("<p>Proactively scan for suspicious messages.</p>", unsafe_allow_html=True)
            if st.button("Scan for Phishing/Scam"):
                with st.spinner("Scanning emails for phishing/scam attempts..."):
                    flagged = detect_phishing_emails(time_frame_hours=24)
                if flagged:
                    st.warning(f"{len(flagged)} suspicious emails detected:")
                    for email in flagged:
                        st.markdown(f"<b>Subject:</b> {email.subject} <br> <b>Sender:</b> {email.sender} <br> <b>Date:</b> {email.date}", unsafe_allow_html=True)
                        st.markdown("<hr>", unsafe_allow_html=True)
                else:
                    st.success("No phishing or scam emails detected.")
        st.markdown("</div>", unsafe_allow_html=True)