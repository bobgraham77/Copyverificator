# Copycheck 

An AI-powered copywriting analysis tool that helps you improve your marketing content.

## Features

- Instant AI analysis of your copy
- Detailed scoring across multiple criteria
- Specific improvement suggestions
- PDF report generation
- Automatic email delivery of reports

## How it Works

1. Enter your marketing copy
2. Provide your email
3. Get instant analysis and a detailed PDF report

## Technology Stack

- Streamlit for the web interface
- Groq AI for text analysis
- Resend for email delivery
- FPDF for PDF generation

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/copycheck.git
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables in `.streamlit/secrets.toml`:
```toml
[groq]
api_key = "your-groq-api-key"

[resend]
api_key = "your-resend-api-key"
sender_email = "your-verified-email@domain.com"
```

4. Run the app:
```bash
streamlit run app.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
