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

# Load API keys from Streamlit secrets
groq_api_key = st.secrets["groq"]["api_key"]
resend.api_key = st.secrets["resend"]["api_key"]
sender_email = st.secrets["resend"]["sender_email"]

# Initialize Groq client
groq_client = Groq(api_key=groq_api_key)

# Function to analyze text based on copywriting criteria
def analyze_text(text):
    """Analyze text based on copywriting criteria"""
    completion = groq_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": """You are a professional copywriting analyzer. Evaluate the given text based on these criteria:
                1. Understanding the audience: Empathy
                2. Clear and concise message: Clarity
                3. Power words and persuasion
                4. Logical flow
                5. Focus on benefits
                6. Strong call-to-action
                7. Credibility elements

                For each criterion:
                1. Give a score out of 10
                2. Provide specific suggestions for improvement
                Format your response as JSON with 'scores' and 'suggestions' objects."""
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
    if score > 8:
        return '#00CC96'  # Green
    elif score >= 6:
        return '#FFD700'  # Yellow
    elif score >= 4:
        return '#FFA500'  # Orange
    return '#FF4B4B'  # Red

# Function to display score bars and descriptions
def display_score_bar(score, title, suggestions):
    color = get_score_color(score)
    # Calculate width of the bar based on score
    bar_width = score * 10  # Scale to 100 for display
    st.markdown(f'## **{title}**')  # Title as H2 and bold
    bar = st.progress(0)
    for i in range(bar_width):
        bar.progress(i + 1)
        time.sleep(0.01)
    st.markdown(f'<div style="width: {bar_width}px; height: 20px; background-color: {color};"></div>', unsafe_allow_html=True)
    st.markdown(f'<p style="font-size: 1.2em; font-weight: bold;">Score: {score}/10</p>', unsafe_allow_html=True)  # Score in bold and larger
    st.markdown('### Suggestion')
    st.markdown(suggestions)

# Function to parse analysis result
def parse_analysis_result(analysis_result):
    criteria_scores = {}
    criteria_suggestions = {}
    
    # Split the analysis into sections
    sections = analysis_result.split('###')
    
    for section in sections:
        if not section.strip():
            continue
            
        # Extract criterion name
        criterion = section.split('\n')[0].strip()
        
        # Extract score (now looking for just the number after "Score: ")
        score_match = re.search(r'Score: (\d+)', section)
        if score_match:
            score = int(score_match.group(1))
            criteria_scores[criterion] = score
            
        # Extract improvements
        improvements_match = re.search(r'Improvements?: (.*?)(?=(?:\n###|\Z))', section, re.DOTALL)
        if improvements_match:
            criteria_suggestions[criterion] = improvements_match.group(1).strip()
    
    return criteria_scores, criteria_suggestions

# Function to get final comment
def get_final_comment(score):
    if score > 80:
        return "Excellent! Your copy is highly effective"
    elif score > 60:
        return "Good work! Some room for improvement"
    elif score > 40:
        return "Needs improvement to be more effective"
    else:
        return "Significant revision recommended"

# Function to create PDF report
def create_pdf_report(text, scores, suggestions, final_comment):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Add header with logo
    pdf.image("https://raw.githubusercontent.com/bobgraham77/Copyverificator/main/assets/copy_checker.svg", x=10, y=10, w=20)
    pdf.set_font("Arial", "B", 24)
    pdf.cell(0, 30, "Copywriting Analysis Report", ln=True, align="C")
    
    # Add date
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    
    # Add analyzed text
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Analyzed Text:", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 7, text)
    
    # Add some spacing
    pdf.ln(10)
    
    # Add scores and suggestions
    for title, score in scores.items():
        # Score header with colored background
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", "B", 12)
        score_text = f"{title}: {score}/10"
        pdf.cell(0, 10, score_text, ln=True, fill=True)
        
        # Add suggestions with proper spacing and formatting
        pdf.set_font("Arial", "", 11)
        pdf.ln(2)
        pdf.multi_cell(0, 7, suggestions[title])
        pdf.ln(5)
    
    # Add final comment
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Overall Assessment:", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 7, final_comment)
    
    return pdf.output(dest='S')

# Function to send PDF email
def send_pdf_email(email, pdf_content, scores):
    """Send PDF report via email using Resend"""
    try:
        # Encode PDF in base64
        encoded_pdf = base64.b64encode(pdf_content).decode()
        
        # Calculate average score
        average_score = sum(scores.values()) / len(scores)
        
        # Create email with attachment
        params = {
            "from": sender_email,
            "to": email,
            "subject": "Your Copywriting Analysis Report",
            "html": f"""
                <h2>Your Copywriting Analysis Results</h2>
                <p>Thank you for using our Copywriting Impact Checker!</p>
                <p>Your overall score is: {average_score:.1f}/10</p>
                <p>A detailed analysis report is attached to this email.</p>
                <p>Feel free to reach out if you have any questions.</p>
                <br>
                <p>Best regards,<br>
                Copywriting Impact Checker Team</p>
            """,
            "attachments": [
                {
                    "filename": "copywriting_analysis.pdf",
                    "content": encoded_pdf,
                }
            ]
        }
        
        # Send email
        response = resend.Emails.send(params)
        return True if response and response.get('id') else False
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# Streamlit app layout
col1, col2 = st.columns([1, 4])

with col1:
    st.image("https://raw.githubusercontent.com/bobgraham77/Copyverificator/main/assets/copy_checker.svg", width=100)
with col2:
    st.title('Copywriting Impact Checker')

# Custom CSS for the button
st.markdown("""
<style>
    .stButton>button {
        background-color: #0066cc;
        color: white;
    }
    .stButton>button:hover {
        background-color: #0052a3;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# User input
user_input = st.text_area('Enter your text or URL here:')

# Language selection
language = st.selectbox('Select the language of the text to analyze:', ['English', 'Spanish', 'French'])

# Email input
email = st.text_input('Enter your email to receive a detailed PDF report:', key='email')

# Analyze button with simple check mark
if st.button('Analyze'):
    if user_input:
        if not email or not validators.email(email):
            st.error('Please enter a valid email address to receive your analysis.')
        else:
            with st.spinner('Analyzing your text...'):
                analysis_result = analyze_text(user_input)
                scores, suggestions = parse_analysis_result(analysis_result)
                
                # Display results
                for title, score in scores.items():
                    display_score_bar(score, title, suggestions[title])
                
                # Get and display final comment
                final_comment = get_final_comment(sum(scores.values()) / len(scores))
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
