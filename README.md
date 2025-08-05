# Open-Unroll ✉️

**Open-Unroll** is an AI-powered Gmail assistant designed to help you reclaim control of your inbox. Built with **Streamlit**, **Langchain**, and **ChatGroq**, it intelligently prioritizes important emails, automates the cleanup of unwanted mail, and provides powerful tools for managing your mail box and optimizing it—all in one clean, intuitive interface.

---

## Demo Video 🎥
A link to a demo video would go here, showcasing the app in action. For example: [demo.mp4](assets/demo.mp4)

---

## 🚀 Features

### Intelligent Inbox Management
- **AI-Powered Prioritization:** Uses a custom ranking model to score emails from 1 (least important) to 10 (extremely important), helping you focus on what matters most.
- **Concise Summaries:** Get a quick overview of any email or attachment. The application uses Langchain and ChatGroq to generate a clear summary of the content.
- **Customizable Time Frame:** Filter and process emails from the past hour, day, week, or any time window you choose.

### Automated Cleanup & Optimization
- **Effortless Unsubscribe:** Intelligently identifies and unsubscribes from unwanted promotional emails and newsletters. It even checks for "unsubscribe" links in headers and HTML, then preserves important newsletters (like career or educational content) by classifying them with AI.
- **Spam & Phishing Detection:** Proactively scans your inbox for suspicious emails and phishing attempts, flagging them for your review.
- **One-Click Cleanup:** Quickly and automatically deletes old emails from categories like promotions and social, based on a configurable age (e.g., older than 7 days).
- **Batch Processing:** Processes promotional emails in batches to ensure polite interaction with servers and stable performance.

### Seamless Integration & Tools
- **Interactive Chat Mode:** Engage with your inbox through a conversational chat interface to ask queries about your emails and get real-time insights.
- **Categorization:** Automatically categorizes recent emails into groups like Work, Personal, Finance, Shopping, Social, and Other for better organization.
- **Attachment Support:** Summarizes a variety of attachments using MarkItDown to provide a clear, readable overview of their content.

---

## 🔧 Installation & Setup

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

### 1. Initial Setup
- Launch the app: `streamlit run src/app.py`
- Upload your Gmail `client_secret.json` file
- Complete OAuth authentication in the browser
- Set your Groq API key in the `.env` file

### 2. Email Prioritization
- Select your desired timeframe (1 hour to 2 weeks)
- Click "Fetch & Prioritize Emails"
- Review AI-scored important emails in the dashboard
- Identify emails that need replies

### 3. Smart Tools
- **Priority Inbox**: View top 5 most important emails
- **Categorization**: Organize emails by topic automatically
- **Security Scan**: Detect phishing and scam attempts
- **Cleanup Tools**: Remove spam, old promotions, and social notifications

### 4. Chat Interface
- Ask natural language questions about your emails
- Get insights about specific senders, topics, or timeframes
- Receive AI-powered summaries and recommendations

---

## 🔧 Advanced Features

### Intelligent Unsubscription
The app can intelligently unsubscribe from unwanted promotional emails while preserving important content:

- **Smart Classification**: Distinguishes between spam and valuable newsletters
- **Preserves Important Content**: Keeps job alerts, educational content, financial updates
- **Batch Processing**: Handles large volumes efficiently
- **Safety First**: Optional verification before unsubscribing

### Attachment Intelligence
Process and understand email attachments automatically:

- **Multi-Format Support**: PDFs, Word docs, Excel sheets, images
- **Content Extraction**: Uses MarkItDown for accurate text extraction
- **AI Summarization**: Generates concise summaries of attachment content
- **Visual Formatting**: Clean, readable presentation of results

### Time-Based Analytics
Flexible timeframe analysis for different use cases:

- **Recent Activity**: 1-6 hours for immediate action items
- **Daily Review**: 24 hours for end-of-day processing
- **Weekly Cleanup**: 1-2 weeks for bulk management
- **Custom Ranges**: Adaptable to your workflow needs

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