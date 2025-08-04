# Open-Unroll ✉️

**Open-Unroll** is an intelligent Gmail management and productivity suite built with **Streamlit**, **LangChain**, and **ChatGroq**. It empowers users to efficiently manage their inbox through AI-powered prioritization, smart automation, and comprehensive email analysis tools.

---

## Demo Video - Open-Unroll 🎥



---

## ✨ Key Features

### � **Smart Email Prioritization**
- **AI-Powered Importance Scoring:** Uses advanced LLM models to score emails from 1-10 based on urgency and importance
- **Customizable Time Frames:** Filter emails by various time windows (1 hour to 2 weeks)
- **Non-Promotional Focus:** Automatically filters out promotional emails for better signal-to-noise ratio
- **Visual Priority Dashboard:** Clean, professional interface displaying top important emails

### 🤖 **Intelligent Email Management Tools**
- **Email Categorization:** Automatically sorts emails into categories (Work, Personal, Finance, Shopping, Social, Updates, Other)
- **Phishing & Scam Detection:** Proactively identifies suspicious emails using AI analysis
- **Reply Detection:** Identifies emails that require responses and highlights them
- **Draft Generation:** AI-powered draft responses for quick email replies

### 🗂️ **Advanced Attachment Processing**
- **Multi-Format Support:** Processes PDFs, DOCX, Excel sheets, and various Microsoft Office formats
- **Automatic Summarization:** Uses MarkItDown to extract and summarize attachment content
- **Smart Content Analysis:** AI-powered summaries of attachment contents for quick understanding

### 🧹 **Inbox Cleanup & Automation**
- **Smart Spam Removal:** Intelligent spam detection and removal with optional LLM verification
- **Promotional Email Management:** Bulk deletion of old promotional emails (configurable timeframe)
- **Social Media Cleanup:** Automated removal of old social media notifications
- **Intelligent Unsubscription:** AI-powered unsubscription from unwanted promotional emails while preserving important newsletters

### 💬 **Interactive Chat Interface**
- **Conversational Email Queries:** Ask natural language questions about your emails
- **Real-time Insights:** Get instant answers about email content, senders, and patterns
- **Context-Aware Responses:** AI understands your email context for more relevant answers

### ⚙️ **Professional Features**
- **GitHub Dark Theme UI:** Modern, professional interface optimized for productivity
- **Session Management:** Secure handling of multiple user sessions
- **Flexible Time Controls:** Multiple timeframe options for different use cases
- **Responsive Design:** Optimized for various screen sizes and devices

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Gmail account with API access enabled
- Groq API key for AI functionality

### Quick Start

**1. Clone the Repository:**
```bash
git clone https://github.com/yourusername/Open-Unroll.git
cd Open-Unroll
```

**2. Install Dependencies:**
```bash
pip install -r requirements.txt
```

**3. Environment Setup:**
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
```

**4. Run the Application:**
```bash
streamlit run src/app.py
```

## 📋 Dependencies

The application uses the following key libraries:

- **Streamlit 1.24.0** - Web application framework
- **LangChain 0.3.15** - LLM orchestration and prompt management
- **LangChain-Groq 0.2.4** - Groq integration for fast inference
- **SimpleGmail** - Gmail API wrapper for easy email access
- **MarkItDown** - Document processing and conversion
- **Pandas** - Data manipulation and analysis
- **BeautifulSoup4** - HTML parsing for email content
- **python-dotenv** - Environment variable management
- **python-dateutil** - Advanced date/time parsing

For a complete list, see `requirements.txt`.
## � API Configuration

### Get Your Groq API Key

Open-Unroll uses Groq for fast AI inference. To obtain your API key:

1. **Visit Groq Console**: [https://console.groq.com/playground](https://console.groq.com/playground)
2. **Sign up/Sign in** to your account
3. **Generate API Key** from the dashboard
4. **Add to Environment**: 
   ```env
   GROQ_API_KEY=your_api_key_here
   ```

### Gmail API Setup

To connect with your Gmail account:

1. **Google Cloud Console**: Visit [Google API Console](https://console.developers.google.com/)
2. **Create/Select Project**: Create a new project or select existing one
3. **Enable Gmail API**: Search for and enable the Gmail API
4. **Create Credentials**: 
   - Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
   - Choose "Desktop Application" as application type
   - Download the `client_secret.json` file
5. **Upload in App**: When you first run Open-Unroll, upload your `client_secret.json` file through the interface

The app will handle OAuth authentication and store your tokens securely for future use.

---

## 🏗️ Project Structure

```
Open-Unroll/
├── src/
│   ├── app.py                 # Main Streamlit application
│   └── utils/
│       ├── tool.py           # Core Gmail management tools
│       ├── attachment.py     # Attachment processing utilities
│       └── utils.py          # Helper functions and utilities
├── assets/
│   ├── logo.png             # Application logo
│   └── demo.mp4             # Demo video
├── requirements.txt          # Python dependencies
├── .env                     # Environment variables (create this)
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

---

## 🎯 How to Use

### 1. **Initial Setup**
- Launch the app: `streamlit run src/app.py`
- Upload your Gmail `client_secret.json` file
- Complete OAuth authentication in browser
- Set your Groq API key in the `.env` file

### 2. **Email Prioritization**
- Select your desired timeframe (1 hour to 2 weeks)
- Click "Fetch & Prioritize Emails"
- Review AI-scored important emails in the dashboard
- Identify emails that need replies

### 3. **Smart Tools**
- **Priority Inbox**: View top 5 most important emails
- **Categorization**: Organize emails by topic automatically
- **Security Scan**: Detect phishing and scam attempts
- **Cleanup Tools**: Remove spam, old promotions, and social notifications

### 4. **Chat Interface**
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

## 🤝 Contributing

We welcome contributions to Open-Unroll! Here's how you can help:

### Getting Started
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit with clear messages: `git commit -m "Add feature description"`
5. Push to your fork: `git push origin feature-name`
6. Submit a pull request

### Development Guidelines
- Follow PEP 8 style guidelines for Python code
- Add comments for complex logic
- Update documentation for new features
- Test your changes with different email scenarios
- Ensure all dependencies are properly listed

### Ideas for Contributions
- Additional email providers (Outlook, Yahoo, etc.)
- Enhanced AI models for better categorization
- Mobile-responsive UI improvements
- Integration with calendar apps
- Email templates and automation
- Advanced analytics and reporting

---

## 📝 License

This project is licensed under the **Apache License 2.0** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Streamlit** for the amazing web app framework
- **LangChain** for LLM orchestration capabilities  
- **Groq** for fast and efficient AI inference
- **Google** for Gmail API access
- **MarkItDown** for document processing capabilities

---

## 📞 Support & Contact

- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/yourusername/Open-Unroll/issues)
- **Discussions**: Join community discussions in [GitHub Discussions](https://github.com/yourusername/Open-Unroll/discussions)
- **Documentation**: Check our [Wiki](https://github.com/yourusername/Open-Unroll/wiki) for detailed guides

---

**⭐ If you find Open-Unroll helpful, please give it a star on GitHub!**
