import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from groq import Groq
import re
import time
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import validators
import base64
from datetime import datetime
import requests
import json
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

# Load API keys from Streamlit secrets
try:
    groq_api_key = st.secrets["groq"]["api_key"]
    if not groq_api_key or groq_api_key.isspace():
        raise ValueError("Groq API key is empty")
    resend_api_key = st.secrets["resend"]["api_key"]
    sender_email = st.secrets["resend"]["sender_email"]
    audience_id = st.secrets["resend"]["audience_id"]
except Exception as e:
    st.error("Erreur de configuration : Vérifiez que le fichier secrets.toml contient toutes les clés API nécessaires.")
    logging.error(f"Configuration error: {str(e)}")
    st.stop()

# Initialize Groq client
try:
    groq_client = Groq(api_key=groq_api_key)
except Exception as e:
    st.error("Erreur d'initialisation de l'API Groq. Veuillez vérifier votre clé API.")
    logging.error(f"Groq client initialization error: {str(e)}")
    st.stop()

# Function to analyze text based on copywriting criteria
def analyze_text(text):
    """Analyze text based on copywriting criteria"""
    try:
        logging.debug("Starting analysis...")
        logging.debug(f"Text length: {len(text)} characters")
        
        # Truncate text if it's too long
        max_text_length = 12000
        if len(text) > max_text_length:
            text = text[:max_text_length] + "..."
            logging.warning(f"Text truncated to {max_text_length} characters")
        
        logging.debug("Preparing API call to Groq...")
        logging.debug(f"Using API key: {groq_api_key[:4]}{'*' * (len(groq_api_key)-8)}{groq_api_key[-4:]}")
        
        # Use non-streaming API call
        try:
            completion = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "Evaluate the article on 10 copywriting criteria (10 points each):\n1. Empathy (audience understanding)\n2. Clarity (clear message)\n3. Attention (headlines/hooks)\n4. Flow (structure)\n5. Benefits (value focus)\n6. Action (call-to-action)\n7. Trust (credibility)\n8. Emotion (storytelling)\n9. Adaptation (medium fit)\n10. Influence (persuasion)\n\nFor each criterion provide:\nScore: X/10\nReasoning: Brief explanation\nImprovement: One key suggestion"
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                temperature=0.1,
                max_tokens=2048,
                top_p=1,
                stream=False,
                stop=None,
                seed=42
            )
            logging.debug("API call successful")
        except Exception as api_error:
            logging.error(f"API call failed: {str(api_error)}")
            raise Exception(f"Erreur lors de l'appel à l'API Groq: {str(api_error)}")
        
        response = completion.choices[0].message.content
        logging.debug("Analysis complete")
        logging.debug(f"Response length: {len(response)} characters")
        
        if not response or not response.strip():
            raise Exception("Réponse vide reçue de l'API")
            
        return response
            
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        error_msg = str(e) if "Erreur lors de l'appel à l'API Groq" in str(e) else "Une erreur s'est produite lors de l'analyse. Veuillez réessayer ou contacter le support si le problème persiste."
        st.error(error_msg)
        return None

# Function to get score color
def get_score_color(score):
    """Get color based on score value"""
    if score >= 8:
        return "#28a745"  # Green
    elif score >= 6:
        return "#ffc107"  # Yellow
    elif score >= 4:
        return "#fd7e14"  # Orange
    else:
        return "#dc3545"  # Red

# Function to get improvement summary
def get_improvement_summary(scores):
    """Get a summary of the main areas for improvement"""
    # Sort scores by value to find lowest scores
    sorted_scores = sorted(scores.items(), key=lambda x: x[1])
    lowest_scores = sorted_scores[:3]  # Get 3 lowest scores
    
    if lowest_scores[0][1] < 5:
        urgency = "urgent"
    else:
        urgency = "important"
    
    areas = ", ".join([f"{area}" for area, score in lowest_scores])
    return f"The {urgency} areas for improvement are: {areas}. Focus on these aspects to significantly enhance your copy's effectiveness."

# Function to display score bar
def display_score_bar(score, title, suggestions):
    """Display a criterion score with a circular progress indicator"""
    color = get_score_color(score)
    
    # Create columns for layout
    col1, col2 = st.columns([1, 4])
    
    with col1:
        # Create circular progress indicator
        fig, ax = plt.subplots(figsize=(2, 2))
        # Outer circle (background)
        ax.add_patch(plt.Circle((0.5, 0.5), 0.4, color='#f0f2f6', zorder=1))
        # Progress arc
        theta = np.linspace(0, 2*np.pi*(score/10), 50)
        x = 0.5 + 0.4*np.cos(theta)
        y = 0.5 + 0.4*np.sin(theta)
        ax.plot(x, y, color=color, linewidth=8, zorder=2)
        # Score text
        ax.text(0.5, 0.5, f'{score:.1f}', ha='center', va='center', 
               fontsize=20, fontweight='bold', zorder=3)
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
    """Create a PDF report with the analysis results"""
    try:
        # Initialize PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Set default font
        pdf.set_font('helvetica', size=12)
        
        # Add title
        pdf.set_font('helvetica', 'B', 24)
        pdf.cell(0, 20, 'Copycheck Analysis Report', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(10)
        
        # Add date
        pdf.set_font('helvetica', 'I', 12)
        pdf.cell(0, 10, f'Generated on {datetime.now().strftime("%Y-%m-%d %H:%M")}', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(20)
        
        # Add analyzed text
        pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 10, 'Analyzed Text:', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(5)
        pdf.set_font('helvetica', size=12)
        pdf.multi_cell(0, 10, text[:500] + '...' if len(text) > 500 else text)
        pdf.ln(10)
        
        # Add scores and suggestions
        pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 10, 'Analysis Results:', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(10)
        
        # Calculate average score
        average_score = sum(scores.values()) / len(scores) if scores else 0
        
        pdf.set_font('helvetica', 'B', 12)
        pdf.cell(0, 10, f'Overall Score: {int(average_score*10)}%', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(10)
        
        for criterion, score in scores.items():
            pdf.set_font('helvetica', 'B', 12)
            pdf.cell(0, 10, f'{criterion}: {score:.1f}/10', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font('helvetica', 'I', 12)
            if criterion in suggestions:
                pdf.multi_cell(0, 10, f'Suggestion: {suggestions[criterion]}')
            pdf.ln(5)
        
        # Add areas for improvement
        pdf.ln(10)
        pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 10, 'Areas for Improvement:', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(5)
        pdf.set_font('helvetica', size=12)
        pdf.multi_cell(0, 10, get_improvement_summary(scores))
        
        return pdf.output()
    except Exception as e:
        logging.error(f"Error creating PDF: {e}")
        return None

# Function to add to audience
def add_to_audience(email):
    """Add email to Copycheck audience in Resend using direct API call"""
    try:
        # Resend API endpoint for adding contacts to an audience
        url = f"https://api.resend.com/audiences/{audience_id}/contacts"
        
        # Request headers
        headers = {
            "Authorization": f"Bearer {resend_api_key}",
            "Content-Type": "application/json"
        }
        
        # Request payload
        payload = {
            "email": email,
            "first_name": "",
            "last_name": "",
            "data": {
                "source": "copycheck_app",
                "signup_date": datetime.now().isoformat()
            }
        }
        
        # Make the POST request
        response = requests.post(url, headers=headers, json=payload)
        
        # Log response for debugging
        logging.debug(f"Resend API Response Status: {response.status_code}")
        logging.debug(f"Resend API Response Body: {response.text}")
        
        # Check if request was successful
        if response.status_code in [200, 201]:
            logging.info(f"Successfully added {email} to audience {audience_id}")
            return True
        else:
            logging.error(f"Failed to add contact. Status code: {response.status_code}")
            return False
            
    except Exception as e:
        logging.error(f"Error adding to audience: {str(e)}")
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
            "to": [email],
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
                "content": encoded_pdf
            }]
        }
        
        try:
            # Send email
            response = requests.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {resend_api_key}",
                    "Content-Type": "application/json"
                },
                json=params
            )
            
            if response.status_code in [200, 201]:
                logging.info("Email sent successfully")
                return True
            else:
                logging.error(f"Failed to send email. Status: {response.status_code}, Response: {response.text}")
                raise Exception(f"Failed to send email: {response.text}")
                
        except Exception as send_error:
            logging.error(f"Error sending email via Resend: {send_error}")
            raise Exception(f"Error sending email: {str(send_error)}")
            
    except Exception as e:
        logging.error(f"Error preparing email: {e}")
        st.error(f"There was an issue sending the email. Please try again: {str(e)}")
        return False

# Function to parse analysis result
def parse_analysis_result(result):
    """Parse the analysis result and extract scores and suggestions"""
    try:
        # Ensure we have a valid result
        if not result or not isinstance(result, str):
            logging.error("Invalid result format")
            return {}, {}
            
        scores = {}
        suggestions = {}
        
        # Parse the text response
        sections = result.split('\n\n')
        current_criterion = None
        
        for section in sections:
            # Look for criterion headers
            if ':' in section:
                lines = section.strip().split('\n')
                for line in lines:
                    if 'Score:' in line:
                        # Extract score
                        try:
                            score_str = line.split('Score:')[1].strip()
                            score = int(score_str.split('/')[0])
                            if current_criterion:
                                scores[current_criterion] = score
                        except:
                            continue
                    elif 'Improvement:' in line:
                        # Extract improvement suggestion
                        suggestion = line.split('Improvement:')[1].strip()
                        if current_criterion:
                            suggestions[current_criterion] = suggestion
                    else:
                        # Try to identify criterion
                        for criterion in ['Empathy', 'Clarity', 'Attention', 'Flow', 'Benefits', 
                                       'Action', 'Trust', 'Emotion', 'Adaptation', 'Influence']:
                            if criterion in line:
                                current_criterion = criterion
                                break
        
        # Validate scores
        if not scores or len(scores) == 0:
            logging.error("No scores found in response")
            return {}, {}
            
        logging.debug(f"Parsed scores: {scores}")
        logging.debug(f"Parsed suggestions: {suggestions}")
        
        return scores, suggestions
    except Exception as e:
        logging.error(f"Error parsing analysis result: {e}")
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
        padding: 1rem;
    }
    .stProgress > div > div > div {
        height: 20px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Header
st.title("Copycheck")
st.write("✍️")
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
                if analysis_result is None:
                    st.stop()
                scores, suggestions = parse_analysis_result(analysis_result)
                
                # Check if we got valid scores
                if not scores:
                    st.error("Sorry, there was an error analyzing your text. Please try again.")
                    st.stop()
                
                # Calculate average score
                average_score = sum(scores.values()) / len(scores)
                
                # Display results
                st.markdown("## Analysis Results")
                
                # Create two columns for layout
                col1, col2 = st.columns(2)
                
                with col1:
                    # Display overall score
                    st.markdown("### Overall Score")
                    fig, ax = plt.subplots(figsize=(3, 3))
                    # Outer circle (background)
                    ax.add_patch(plt.Circle((0.5, 0.5), 0.4, color='#f0f2f6', zorder=1))
                    # Progress arc
                    theta = np.linspace(0, 2*np.pi*(average_score/10), 50)
                    x = 0.5 + 0.4*np.cos(theta)
                    y = 0.5 + 0.4*np.sin(theta)
                    ax.plot(x, y, color=get_score_color(average_score), linewidth=8, zorder=2)
                    # Score text
                    ax.text(0.5, 0.5, f'{int(average_score*10)}%', ha='center', va='center', 
                           fontsize=24, fontweight='bold', zorder=3)
                    ax.set_xlim(0, 1)
                    ax.set_ylim(0, 1)
                    ax.axis('off')
                    st.pyplot(fig)
                    plt.close()
                
                with col2:
                    # Areas for improvement
                    st.markdown("### Areas for Improvement")
                    st.write(get_improvement_summary(scores))
                
                # Display individual scores
                st.markdown("## Detailed Analysis")
                for criterion, score in scores.items():
                    display_score_bar(score, criterion, suggestions.get(criterion, ""))
                
                # Create and send PDF report
                with st.spinner('Generating PDF report...'):
                    pdf_content = create_pdf_report(user_input, scores, suggestions, get_improvement_summary(scores))
                    if pdf_content:
                        if send_pdf_email(email, pdf_content, scores):
                            st.success('Analysis complete! Check your email for the detailed report.')
                        else:
                            st.error('There was an issue sending the email. Please try again.')
                            st.stop()
                    else:
                        st.error('There was an issue generating the PDF report. Please try again.')
                        st.stop()
    else:
        st.error('Please enter some text to analyze.')
