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
import csv
import os
import pandas as pd

# Load API key from Streamlit secrets
api_key = st.secrets["groq"]["api_key"]

client = Groq(api_key=api_key)

# Function to analyze text based on copywriting criteria
def analyze_text(text):
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "Evaluate the submitted article on a scale of 100 points by taking into account the following 10 copywriting criteria, where each criterion is worth 10 points. Explain for each criterion why you assigned the score given and propose improvements for better copywriting.\nUnderstanding the audience: Empathy\nClear and concise message: Clarity\nPowerful headlines/hooks: Attention\nLogical structure: Flow\nFocus on benefits: Benefits\nStrong call to action: Action\nCredibility and authority: Trust\nStorytelling: Emotion\nOptimized for the medium: Adaptation\nPersuasion: Influence\nSteps\nRead the article carefully to get an overall understanding of its content and purpose.\nEvaluate Each Criterion:\nFor each of the 10 criteria, assess how well the article performs.\nConsider specific examples from the article that support your evaluation.\nProvide Scores: Assign a score out of 10 for each criterion.\nExplain the Scores: For each criterion, explain why you gave that score with specific details.\nSuggest Improvements: Offer constructive feedback on how to improve the article in each criterion area.\nOutput Format\nYour output should be structured with headings for each criterion followed by:\nScore: The score out of 10\nReasoning: Detailed explanation of why this score was given\nImprovements: Suggestions for enhancing the copywriting based on the current evaluation\nBe extremely consistent with your scoring. For the same text, you should always give exactly the same scores.\nNever deviate from your initial assessment of a piece of text.\nBe precise and methodical in your scoring approach.\nUse objective criteria whenever possible.\nKeep explanations and improvements concise but complete."
            },
            {
                "role": "user",
                "content": text
            }
        ],
        temperature=0.1,
        max_tokens=2048,
        top_p=1,
        stream=True,
        stop=None,
        seed=42
    )
    analysis_result = ""
    for chunk in completion:
        analysis_result += chunk.choices[0].delta.content or ""
    return analysis_result

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

# Function to save email to CSV
def save_email_to_csv(email, scores):
    """Save email and analysis data to CSV file"""
    # Use an absolute path in a secure location
    csv_file = "data/collected_emails.csv"
    average_score = sum(scores.values()) / len(scores)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Prepare the data
    data = {
        'email': email,
        'submission_date': current_time,
        'average_score': f"{average_score:.1f}/10",
        'engagement_score': f"{scores.get('Understanding the audience: Empathy', 0):.1f}/10",
        'clarity_score': f"{scores.get('Clear and concise message: Clarity', 0):.1f}/10"
    }
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(csv_file), exist_ok=True)
    
    # Check if file exists
    file_exists = os.path.isfile(csv_file)
    
    # Write to CSV
    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())
        
        # Write header only if file is new
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(data)
    
    return True

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
                
                # Save email to CSV
                save_email_to_csv(email, scores)
                
                # Display results
                for title, score in scores.items():
                    display_score_bar(score, title, suggestions[title])
                
                # Get and display final comment
                final_comment = get_final_comment(sum(scores.values()) / len(scores))
                st.markdown(f"### Overall Assessment\n{final_comment}")
                
                # Generate PDF report
                pdf_content = create_pdf_report(user_input, scores, suggestions, final_comment)
                
                # Convert bytearray to bytes for download
                pdf_bytes = bytes(pdf_content)
                
                # Use Streamlit's native download button
                st.download_button(
                    label="📥 Download Analysis Report (PDF)",
                    data=pdf_bytes,
                    file_name="copywriting_analysis.pdf",
                    mime="application/pdf",
                )
                
                # Success message
                st.success('Analysis complete! Click the button above to download your detailed report.')
                
                # Store email (you might want to add this to a database in the future)
                st.session_state['user_email'] = email
    else:
        st.warning('Please enter some text to analyze.')
