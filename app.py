import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from groq import Groq
import re
import time
from fpdf import FPDF
import validators
import base64
from datetime import datetime
import resend
import requests
import json
from bs4 import BeautifulSoup

# Load API keys from Streamlit secrets
groq_api_key = st.secrets["groq"]["api_key"]
resend.api_key = st.secrets["resend"]["api_key"]
sender_email = st.secrets["resend"]["sender_email"]
audience_id = st.secrets["resend"]["audience_id"]

# Initialize Groq client
groq_client = Groq(api_key=groq_api_key)

# Function to analyze text based on copywriting criteria
def analyze_text(text):
    """Analyze text based on copywriting criteria"""
    completion = groq_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": """You are a professional copywriting analyzer. Evaluate the text on a scale of 100 points based on these 10 criteria, where each is worth 10 points. Return a JSON response with exactly these keys:
                {
                    "scores": {
                        "Empathy": 0-10 score for understanding the audience,
                        "Clarity": 0-10 score for clear and concise message,
                        "Attention": 0-10 score for powerful headlines/hooks,
                        "Flow": 0-10 score for logical structure,
                        "Benefits": 0-10 score for focus on benefits,
                        "Action": 0-10 score for strong call to action,
                        "Trust": 0-10 score for credibility and authority,
                        "Emotion": 0-10 score for storytelling,
                        "Adaptation": 0-10 score for medium optimization,
                        "Influence": 0-10 score for persuasion
                    },
                    "suggestions": {
                        "Empathy": "Detailed explanation of score and suggestions for improving audience understanding",
                        "Clarity": "Detailed explanation of score and suggestions for improving message clarity",
                        "Attention": "Detailed explanation of score and suggestions for improving headlines/hooks",
                        "Flow": "Detailed explanation of score and suggestions for improving structure",
                        "Benefits": "Detailed explanation of score and suggestions for improving benefit focus",
                        "Action": "Detailed explanation of score and suggestions for improving call-to-action",
                        "Trust": "Detailed explanation of score and suggestions for improving credibility",
                        "Emotion": "Detailed explanation of score and suggestions for improving storytelling",
                        "Adaptation": "Detailed explanation of score and suggestions for improving medium optimization",
                        "Influence": "Detailed explanation of score and suggestions for improving persuasion"
                    }
                }
                
                Be extremely consistent with scoring. For the same text, always give exactly the same scores.
                Never deviate from your initial assessment.
                Be precise and methodical in your scoring approach.
                Use objective criteria whenever possible.
                Keep explanations and improvements concise but complete."""
            },
            {
                "role": "user",
                "content": text
            }
        ],
        model="mixtral-8x7b-32768",
        temperature=0.5,
        max_tokens=1000,
    )
    
    return completion.choices[0].message.content

# Function to get score color
def get_score_color(score):
    if score >= 8:
        return "#28a745"  # Green
    elif score >= 6:
        return "#ffc107"  # Yellow
    elif score >= 4:
        return "#fd7e14"  # Orange
    else:
        return "#dc3545"  # Red

# Function to display score bar
def display_score_bar(score, title, suggestions):
    color = get_score_color(score)
    
    # Create columns for layout
    col1, col2 = st.columns([1, 4])
    
    with col1:
        # Create circular progress indicator
        fig, ax = plt.subplots(figsize=(2, 2))
        ax.add_patch(plt.Circle((0.5, 0.5), 0.4, color='#f0f2f6'))
        ax.add_patch(plt.Circle((0.5, 0.5), 0.4, color=color, 
                              alpha=score/10))
        ax.text(0.5, 0.5, f'{score}', ha='center', va='center', 
               fontsize=20, fontweight='bold')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        st.pyplot(fig)
        plt.close()
    
    with col2:
        st.markdown(f"### {title}")
        st.progress(score/10)
        st.markdown(f"_{suggestions}_")

# Function to create PDF report
def create_pdf_report(text, scores, suggestions, final_comment):
    pdf = FPDF()
    pdf.add_page()
    
    # Add header with logo
    pdf.image("https://raw.githubusercontent.com/bobgraham77/Copyverificator/main/assets/copy_checker.svg", x=10, y=10, w=20)
    pdf.set_font("Arial", "B", 24)
    pdf.cell(0, 30, "Copycheck Analysis Report", ln=True, align="C")
    
    # Add date
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    
    # Add original text
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Analyzed Text:", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 10, text)
    
    # Add scores and suggestions
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Analysis Results:", ln=True)
    
    for criterion, score in scores.items():
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"{criterion}: {score}/10", ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 10, suggestions[criterion])
        pdf.ln(5)
    
    # Add final comment
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Overall Assessment:", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 10, final_comment)
    
    return pdf.output(dest='S')

# Function to add to audience
def add_to_audience(email):
    """Add email to Copycheck audience in Resend using direct API call"""
    try:
        # Resend API endpoint for adding contacts to an audience
        url = f"https://api.resend.com/audiences/{audience_id}/contacts"
        
        # Request headers
        headers = {
            "Authorization": f"Bearer {resend.api_key}",
            "Content-Type": "application/json"
        }
        
        # Request payload
        payload = {
            "contacts": [{
                "email": email,
                "first_name": "",
                "last_name": "",
                "data": {
                    "source": "copycheck_app",
                    "signup_date": datetime.now().isoformat()
                }
            }]
        }
        
        # Make the POST request
        response = requests.post(url, headers=headers, json=payload)
        
        # Log response for debugging
        print(f"Resend API Response Status: {response.status_code}")
        print(f"Resend API Response Body: {response.text}")
        
        # Check if request was successful
        if response.status_code in [200, 201]:
            print(f"Successfully added {email} to audience {audience_id}")
            return True
        else:
            print(f"Failed to add contact. Status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error adding to audience: {str(e)}")
        return False

# Function to send PDF email
def send_pdf_email(email, pdf_content, scores):
    """Send PDF report via email using Resend"""
    try:
        # First, add to audience
        add_to_audience(email)
        
        # Encode PDF in base64
        encoded_pdf = base64.b64encode(pdf_content).decode()
        
        # Calculate average score
        average_score = sum(scores.values()) / len(scores) if scores else 0
        
        # Create email with attachment
        params = {
            "from": sender_email,
            "to": email,
            "subject": "Your Copycheck Analysis Report",
            "html": f"""
                <h2>Your Copycheck Results</h2>
                <p>Thank you for using Copycheck!</p>
                <p>Your overall score is: {average_score:.1f}/10</p>
                <p>A detailed analysis report is attached to this email.</p>
                <p>Feel free to reach out if you have any questions.</p>
                <br>
                <p>Best regards,<br>
                Copycheck Team</p>
            """,
            "attachments": [{
                "filename": "copycheck_analysis.pdf",
                "content": encoded_pdf,
                "content_type": "application/pdf"
            }],
            "headers": {
                "X-Entity-Ref-ID": "copycheck"
            },
            "categories": ["Copycheck"]
        }
        
        try:
            # Send email
            response = resend.Emails.send(params)
            print(f"Email sent successfully: {response}")
            return True if response and response.get('id') else False
        except Exception as send_error:
            print(f"Error sending email via Resend: {send_error}")
            return False
            
    except Exception as e:
        print(f"Error preparing email: {e}")
        return False

# Function to parse analysis result
def parse_analysis_result(result):
    """Parse the analysis result and extract scores and suggestions"""
    try:
        # Ensure we have a valid result
        if not result or not isinstance(result, str):
            return {}, {}
            
        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if not json_match:
            return {}, {}
            
        data = eval(json_match.group())
        if not isinstance(data, dict):
            return {}, {}
            
        scores = data.get('scores', {})
        suggestions = data.get('suggestions', {})
        
        # Validate scores
        if not scores or not all(isinstance(v, (int, float)) for v in scores.values()):
            return {}, {}
            
        return scores, suggestions
    except Exception as e:
        print(f"Error parsing analysis result: {e}")
        return {}, {}

# Function to get final comment
def get_final_comment(average_score):
    """Get final assessment comment based on average score"""
    if not isinstance(average_score, (int, float)) or average_score < 0:
        return "Unable to calculate score. Please try again."
        
    if average_score >= 9:
        return "Excellent! Your copy is highly effective and persuasive."
    elif average_score >= 7:
        return "Very good! Your copy is effective with some room for improvement."
    elif average_score >= 5:
        return "Good start. Your copy needs some work to be more effective."
    else:
        return "Your copy needs significant improvement. Consider implementing the suggestions above."

# Function to extract article content from URL
def extract_article_content(url):
    """Extract article content from URL"""
    try:
        # Get the webpage content
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove unwanted elements
        for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        # Find the main content
        article = soup.find('article') or soup.find('main') or soup.find('div', class_='post-content')
        
        if article:
            # Extract text from paragraphs
            paragraphs = article.find_all('p')
            content = ' '.join([p.get_text().strip() for p in paragraphs])
            
            # Clean up the text
            content = re.sub(r'\s+', ' ', content)  # Remove extra whitespace
            content = content.strip()
            
            return content
        else:
            return None
            
    except Exception as e:
        print(f"Error extracting content: {str(e)}")
        return None

# Streamlit app layout
st.set_page_config(
    page_title="Copycheck",
    page_icon="✍️",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTextInput > div > div > input {
        padding: 1rem;
    }
    .stProgress > div > div > div {
        height: 20px;
        border-radius: 10px;
    }
    .overall-score {
        text-align: center;
        padding: 2rem;
        background-color: #f8f9fa;
        border-radius: 15px;
        margin-bottom: 2rem;
    }
    .score-circle {
        margin: auto;
        width: 150px;
        height: 150px;
    }
    </style>
    """, unsafe_allow_html=True)

# Header with logo
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://raw.githubusercontent.com/bobgraham77/Copyverificator/main/assets/copy_checker.svg", width=100)
with col2:
    st.title("Copycheck")
    st.markdown("Analyze and improve your copywriting with AI-powered insights")

# User inputs
user_input = st.text_area('Enter your text or URL to analyze:', height=200)
email = st.text_input('Enter your email to receive the analysis:')

# Analyze button
if st.button('Analyze', type='primary'):
    if user_input:
        if not email or not validators.email(email):
            st.error('Please enter a valid email address to receive your analysis.')
        else:
            # Check if input is URL
            if validators.url(user_input):
                with st.spinner('Extracting article content...'):
                    content = extract_article_content(user_input)
                    if content:
                        user_input = content
                    else:
                        st.error('Could not extract article content. Please try copying and pasting the text directly.')
                        st.stop()
            
            with st.spinner('Analyzing your text...'):
                analysis_result = analyze_text(user_input)
                scores, suggestions = parse_analysis_result(analysis_result)
                
                # Check if we got valid scores
                if not scores:
                    st.error("Sorry, there was an error analyzing your text. Please try again.")
                else:
                    # Calculate average score for overall progress
                    average_score = sum(scores.values()) / len(scores) if scores else 0
                    
                    # Display overall score with improved styling
                    st.markdown('<div class="overall-score">', unsafe_allow_html=True)
                    st.markdown("### Overall Score")
                    
                    # Create circular progress indicator
                    fig, ax = plt.subplots(figsize=(4, 4))
                    circle = plt.Circle((0.5, 0.5), 0.4, color='#f0f2f6')
                    score_circle = plt.Circle((0.5, 0.5), 0.4, 
                                           color=get_score_color(average_score),
                                           alpha=0.8)
                    
                    ax.add_patch(circle)
                    ax.add_patch(score_circle)
                    ax.text(0.5, 0.5, f'{average_score:.1f}', 
                           ha='center', va='center',
                           fontsize=40, fontweight='bold',
                           color='#1f1f1f')
                    ax.text(0.5, 0.3, '/10', 
                           ha='center', va='center',
                           fontsize=20, color='#666666')
                    
                    ax.set_xlim(0, 1)
                    ax.set_ylim(0, 1)
                    ax.axis('off')
                    
                    # Display the overall score circle
                    st.pyplot(fig, clear_figure=True)
                    plt.close()
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Display individual scores
                    st.markdown("### Detailed Analysis")
                    for title, score in scores.items():
                        display_score_bar(score, title, suggestions[title])
                    
                    # Get and display final comment
                    final_comment = get_final_comment(average_score)
                    st.markdown(f"### Overall Assessment\n{final_comment}")
                    
                    # Generate PDF report
                    pdf_content = create_pdf_report(user_input, scores, suggestions, final_comment)
                    
                    # Send PDF via email
                    if send_pdf_email(email, pdf_content, scores):
                        st.success('Analysis complete! Check your email for the detailed report.')
                    else:
                        st.error('There was an issue sending the email. Please try again.')
    else:
        st.warning('Please enter some text to analyze.')
