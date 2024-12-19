# Copywriting Impact Checker

A powerful tool that analyzes and scores your copywriting based on 10 essential criteria. Get instant feedback and suggestions to improve your writing's effectiveness.

## Features

- **Comprehensive Analysis**: Evaluates your text across 10 key copywriting criteria:
  - Empathy (Understanding the audience)
  - Clarity (Clear and concise message)
  - Attention (Powerful headlines/hooks)
  - Flow (Logical structure)
  - Benefits (Focus on benefits)
  - Action (Strong call to action)
  - Trust (Credibility and authority)
  - Emotion (Storytelling)
  - Adaptation (Optimized for the medium)
  - Influence (Persuasion)

- **Visual Feedback**:
  - Interactive circular progress chart
  - Color-coded score bars
  - Detailed improvement suggestions
  - Overall effectiveness rating

- **Multi-language Support**:
  - English
  - Spanish
  - French

## Installation

1. Clone the repository:
```bash
git clone [your-repository-url]
cd copyverificator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `secrets.toml` file in the project root with your Groq API key:
```toml
[groq]
api_key = "your-api-key-here"
```

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Enter your text in the input area
3. Select your language
4. Click "Analyze" to get your results

## Score Interpretation

- **Green** (8-10): Excellent performance
- **Yellow** (6-7.9): Good performance with room for improvement
- **Orange** (4-5.9): Needs significant improvement
- **Red** (0-3.9): Requires major revision

## Development

The project uses:
- Streamlit for the web interface
- Groq API for text analysis
- Matplotlib for data visualization
- Git hooks for automatic changelog updates

### Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes (changelog will update automatically)
4. Push to the branch
5. Create a Pull Request

## License

MIT

## Author

Bob Pressoir

## Acknowledgments

- Groq for their powerful LLM API
- Streamlit for the amazing web framework
- All contributors and users of this tool
