# Open-Unroll ✉️

**Open-Unroll** is an AI-powered Gmail assistant that helps you reclaim control of your inbox. Built with **Streamlit**, **LangChain**, and **ChatGroq**, it intelligently prioritizes important emails, automates cleanup, and offers smart tools for inbox optimization—all within a simple, user-friendly interface.

---

## 🎥 Demo Video

Watch the app in action: [demo.mp4](assets/demo.mp4) <!-- Replace with actual link -->

---

## 🚀 Key Features

### 🔍 Intelligent Inbox Management
- **AI-Powered Prioritization:** Assigns importance scores (1–10) to help you focus on your most relevant emails.
- **Summarization:** Uses LangChain and ChatGroq to generate concise summaries of emails and attachments.
- **Time-Based Filtering:** Analyze emails by hour, day, week, or a custom time range.

### 🧹 Automated Email Cleanup
- **Smart Unsubscribe:** Automatically identifies and unsubscribes from promotional emails while preserving valuable newsletters (e.g., job alerts, educational content).
- **Phishing & Spam Detection:** Flags suspicious or malicious emails.
- **One-Click Cleanup:** Deletes old promotional and social emails based on a configurable age.
- **Batch Processing:** Handles email operations efficiently to ensure stability.

### 💬 Conversational Email Assistant
- **Interactive Chat:** Ask questions about your inbox and get real-time insights.
- **Natural Language Queries:** Get summaries, stats, or specific answers about senders, topics, and timeframes.

### 🗂️ Smart Categorization & Attachment Support
- **Auto-Categorization:** Groups emails into categories like Work, Personal, Finance, Social, etc.
- **Attachment Intelligence:** Extracts and summarizes content from PDFs, Word docs, Excel sheets, and images using **MarkItDown**.

---

## 🔧 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/MR-Khan0099/Open-Unroll.git
cd Open-Unroll
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Get Your LangChain Groq API Key
To use LangChain with Groq, you need an API key. Follow these steps:
- Go to the Groq Console: [Click here to get your API key](https://console.groq.com/playground)
- Sign in or Sign up if you haven't already.
- Generate an API key and copy it.
- Set up the key in your environment:
  - If running locally, add it to your `.env` file:
    ```env
    GROQ_API_KEY=your_api_key_here
    ```
  - If deploying to a cloud service, add it to your environment variables or repository secrets.

✅ Now, you're all set to use Groq with LangChain! 🚀

### 4. Get Your Gmail Client Secret JSON File
To connect to your Gmail account, you need a Client Secret JSON file. Follow these steps:
- Go to Google API Console: [Follow this guide to download your client secret file](https://stackoverflow.com/questions/52200589/where-to-download-your-client-secret-file-json-file)
- Enable the Gmail API for your Google Cloud project.
- Download the `client_secret.json` file from the Credentials section.
- The application will prompt you to upload this file when you first run the Streamlit app.

✅ Now, you're ready to authenticate and interact with Gmail in your app! ✉️

---

## ▶️ Running the Application
```bash
streamlit run app.py
```

----

## 🎯 How to Use

- Launch the app: `streamlit run src/app.py`
- Authenticate: Upload your Gmail `client_secret.json` and complete the OAuth flow.
- Set Timeframe: Choose the time range you want to process (e.g., last 24 hours).
- Prioritize Emails: Click "Fetch & Prioritize Emails" to get AI-ranked messages.
- Explore Tools:
   - View your top 5 important emails.
   - Categorize inbox contents.
   - Detect spam and phishing.
   - Clean up old or unwanted emails.
- Use Chat Assistant: Ask natural language questions to explore and summarize inbox data.



---


## 🛡️ Security & Privacy

Open-Unroll takes your email security seriously:

- **Local Processing**: All email analysis happens locally on your machine
- **OAuth 2.0**: Secure authentication using Google's OAuth 2.0 standard
- **No Data Storage**: Email content is not permanently stored
- **API Key Security**: Environment variables keep your API keys safe
- **Session Management**: Secure session handling for multi-user environments

---

---

## 🤝 Contributing
Contributions are welcome! If you’d like to improve Open-Unroll or add new features, please fork the repository and submit a pull request.

---

## 📄 License
This project is licensed under the Apache 2.0 License.
