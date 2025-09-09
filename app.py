import streamlit as st
from backend.document_extractor import extract_text
from backend.resume_analyzer import get_semantic_analysis
import random
import string
from captcha.image import ImageCaptcha

st.set_page_config(layout="wide")

# Session State
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "dark"
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = None
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "captcha_answer" not in st.session_state:
    st.session_state.captcha_answer = ""
if "captcha_question" not in st.session_state:
    st.session_state.captcha_question = ""
if "captcha_verified" not in st.session_state:
    st.session_state.captcha_verified = False
if "current_captcha" not in st.session_state:
    st.session_state.current_captcha = ""

# Captcha functions
def generate_new_captcha():
    """Generate a new CAPTCHA and store it in session state"""
    image = ImageCaptcha(width=280, height=90)
    # Generate a random string of 6 characters
    captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    # Save the correct answer in session state
    st.session_state.captcha_answer = captcha_text
    # Generate the image
    captcha_image = image.generate(captcha_text)
    return captcha_image, captcha_text

def verify_captcha():
    """Verify the CAPTCHA input and update verification status"""
    user_input = st.session_state.captcha_question.strip().upper()
    correct_answer = st.session_state.captcha_answer.strip().upper()
    st.session_state.captcha_verified = user_input == correct_answer
    if not st.session_state.captcha_verified:
        st.error("❌ Incorrect CAPTCHA. Please try again.")
    else:
        st.success("✅ CAPTCHA verified successfully!")

def reset_captcha_verification():
    """Reset CAPTCHA verification status and generate new CAPTCHA"""
    st.session_state.captcha_verified = False
    st.session_state.captcha_question = ""
    new_image, new_text = generate_new_captcha()
    st.session_state.current_captcha = new_image

# Theme Toggle Button
def toggle_theme():
    st.session_state.theme_mode = "light" if st.session_state.theme_mode == "dark" else "dark"

# Custom Styling
theme = st.session_state["theme_mode"]
bg_gradient = {
    "light": "linear-gradient(135deg, #b8d8f8, #e2c9f7)",
    "dark": "linear-gradient(135deg, #2e3a5e, #4a3d61)"
}[theme]

text_color = "#000" if theme == "light" else "#fff"
secondary_text_color = "#333" if theme == "light" else "#d3d3d3"

st.markdown(f"""
    <style>
    html, body, .stApp {{
        background: {bg_gradient};
        background-attachment: fixed;
        color: {text_color};
        font-family: 'Segoe UI', sans-serif;
        animation: fadeIn 0.6s ease-in-out;
    }}
    @keyframes fadeIn {{
        0% {{opacity: 0; transform: translateY(10px);}}
        100% {{opacity: 1; transform: translateY(0);}}
    }}

    .detailed-view {{
        animation: fadeIn 0.6s ease-in-out;
    }}

    .block-container {{
        max-width: 850px;
        margin: 5rem auto 2rem auto;
        padding: 2rem 2.5rem;
        padding: 2rem top;
        background: rgba(255,255,255,0.07);
        border-radius: 20px;
        backdrop-filter: blur(16px);
        box-shadow: 0 0 20px rgba(0,0,0,0.3);
    }}

    h1, h2, h3, h4, h5, .stTitle {{
        color: {text_color} !important;
        text-align: center;
    }}

    .stTextArea, .stFileUploader {{
        transition: all 0.3s ease-in-out;
        border-radius: 20px;
    }}

    .stFileUploader label {{
        color: {text_color} !important;
    }}

    .stFileUploader {{
        background: rgba(255, 255, 255, 0.15);
        padding: 1.2rem;
        border: 1px solid rgba(255,255,255,0.3);
        backdrop-filter: blur(14px);
        box-shadow: 0 0 12px rgba(130,180,255, 0.4);
    }}

    .stFileUploader:hover {{
        transform: scale(1.03);
        background: rgba(255, 255, 255, 0.3);
    }}

    .stButton > button {{
        background: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.25);
        color: {text_color};
        padding: 0.6em 1.3em;
        font-size: 1rem;
        font-weight: 600;
        border-radius: 14px;
        backdrop-filter: blur(10px);
        box-shadow: 0 0 10px rgba(150, 100, 255, 0.6);
        transition: all 0.25s ease-in-out;
    }}

    .stButton > button:hover {{
        transform: scale(1.08);
        background: rgba(255, 255, 255, 0.25);
        color: red;
    }}

    .stButton > button:active {{
        transform: scale(0.9);
    }}

    .get-started-button > button {{
        background-color: #4CAF50 !important;
        color: white !important;
        box-shadow: 0 0 15px #4CAF50;
    }}

    .get-started-button > button:hover {{
        background-color: #45a049 !important;
        color: #b2ffb2 !important;
        box-shadow: 0 0 25px #4CAF50;
    }}

    /* Top right floating theme toggle button */
    div[data-testid="stToolbar"] {{
        display: none !important;
    }}
    .stButton > button[title="🌞"], .stButton > button[title="🌙"] {{
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 1000;
    }}

    /* Pie chart size tweak */
    .element-container:has(canvas) {{
        display: flex;
        justify-content: center;
    }}

    .stExpander {{
        transition: all 0.5s ease-in-out !important;
    }}

    .course-card {{
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }}
    .course-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }}
    .course-title a {{
        color: {text_color} !important;
        font-weight: bold;
        text-decoration: none;
    }}
    .course-description {{
        font-style: italic;
        color: {secondary_text_color};
    }}
    </style>
""", unsafe_allow_html=True)

def landing_page():
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            <div style="display: flex; justify-content: center; align-items: center; margin-top: -20px; margin-bottom: -10px; margin-right: 22px">
                <img src="https://i.ibb.co/5XKqNLMf/notion-face.png" alt="Logo" style="height: 100px;">
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(f"<h1 style='margin-top:0; color:{text_color};'>ProScan</h1>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<h3 style='text-align: left; color:{text_color};'>Your AI-Powered Resume Screener</h3>", unsafe_allow_html=True)
        st.markdown("Effortlessly analyze resumes against job descriptions, get instant match scores, and identify top candidates in seconds.")
        
        st.session_state.user_name = st.text_input("Enter Your Name")
        st.session_state.user_email = st.text_input("Enter Your Email")

        st.markdown("<div class='get-started-button'>", unsafe_allow_html=True)
        if st.button("Get Started", key="get_started"):
            st.session_state.page = "main_app"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

def display_analysis(analysis_result, extracted_text):
    if not analysis_result or "error" in analysis_result:
        error_message = analysis_result.get("details", "An unknown error occurred.") if analysis_result else "Analysis result is empty."
        st.error(f"Failed to perform analysis. Please try again. Error: {error_message}")
        return

    # Calculate scores and colors
    similarity_score = analysis_result.get("match_score", 0)
    color = "red" if similarity_score < 20 else "yellow" if similarity_score < 50 else "lightgreen" if similarity_score < 70 else "green"

    # Skills Analysis
    skills_analysis = analysis_result.get("skills_analysis", {})
    all_matching_skills = []
    all_missing_skills = []
    
    for skill_type in ["technical_skills", "soft_skills", "keywords"]:
        if skill_type in skills_analysis:
            all_matching_skills.extend(skills_analysis[skill_type].get("matching", []))
            all_missing_skills.extend(skills_analysis[skill_type].get("missing", []))

    # Main Analysis Container
    st.markdown("""
        <style>
        .analysis-section {
            background: rgba(255, 255, 255, 0.03);
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 15px;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        .section-heading {
            font-family: 'Segoe UI', sans-serif;
            font-weight: 700;
            font-size: 1.5rem;
            margin-bottom: 1rem;
            text-shadow: var(--heading-glow);
        }
        .light-mode .section-heading {
            --heading-glow: 0 0 10px rgba(0, 0, 0, 0.2);
        }
        .dark-mode .section-heading {
            --heading-glow: 0 0 10px rgba(255, 255, 255, 0.2);
        }
        </style>
    """, unsafe_allow_html=True)

    # Score and Summary Section
    st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"""
            <div style="display: flex; justify-content: center;">
                <div style="position: relative; width: 200px; height: 200px;">
                    <svg width="200" height="200" viewBox="0 0 200 200">
                        <circle cx="100" cy="100" r="90" fill="none" stroke="#e6e6e6" stroke-width="10"></circle>
                        <circle cx="100" cy="100" r="90" fill="none" stroke="{color}" stroke-width="10" stroke-dasharray="{2 * 3.14159 * 90}" stroke-dashoffset="{2 * 3.14159 * 90 * (1 - similarity_score / 100)}" transform="rotate(-90 100 100)"></circle>
                    </svg>
                    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 2rem; font-weight: bold;">{similarity_score}%</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("<h3 class='section-heading'>📝 Executive Summary</h3>", unsafe_allow_html=True)
        st.write(analysis_result.get("executive_summary", "No summary available."))
    st.markdown('</div>', unsafe_allow_html=True)

    # Skills Analysis
    st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
    st.markdown("<h3 class='section-heading'>🎯 Skills Analysis</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<h4 class='section-heading'>💫 Matching Skills</h4>", unsafe_allow_html=True)
        if all_matching_skills:
            st.success(f"✨ Found {len(all_matching_skills)} matching skills:")
            st.markdown(f"""
                <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                    {''.join([f'<span style="background-color: #2E8B57; color: white; padding: 5px 10px; border-radius: 15px;">{skill} ✓</span>' for skill in all_matching_skills])}
                </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No direct skill matches found 🔍")
    
    with col2:
        st.markdown("<h4 class='section-heading'>🎯 Missing Skills</h4>", unsafe_allow_html=True)
        if all_missing_skills:
            st.warning(f"⚠️ Identified {len(all_missing_skills)} potential gaps:")
            st.markdown(f"""
                <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                    {''.join([f'<span style="background-color: #FF4500; color: white; padding: 5px 10px; border-radius: 15px;">{skill} ⚡</span>' for skill in all_missing_skills])}
                </div>
            """, unsafe_allow_html=True)
        else:
            st.success("✅ No significant skill gaps identified!")
    st.markdown('</div>', unsafe_allow_html=True)

    # Candidate Details Section
    st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
    st.markdown("<h3 class='section-heading'>👤 Candidate Details</h3>", unsafe_allow_html=True)
    details_md = ""
    if analysis_result.get("candidate_name"):
        details_md += f"**Name:** {analysis_result['candidate_name']}\n\n"
    if analysis_result.get("email"):
        details_md += f"**Email:** {analysis_result['email']}\n\n"
    if analysis_result.get("phone"):
        details_md += f"**Phone:** {analysis_result['phone']}\n\n"
    if analysis_result.get("linkedin_url"):
        details_md += f"**LinkedIn:** [{analysis_result['linkedin_url']}]({analysis_result['linkedin_url']})\n\n"
    if analysis_result.get("github_url"):
        details_md += f"**GitHub:** [{analysis_result['github_url']}]({analysis_result['github_url']})\n\n"
    
    if details_md:
        st.markdown(details_md)
    else:
        st.info("No contact details found in the resume.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Learning Recommendations Section
    st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
    st.markdown('<h3 class="section-heading">📚 Recommended Learning</h3>', unsafe_allow_html=True)
    recommended_courses = analysis_result.get("recommended_courses", [])
    if recommended_courses:
        for course in recommended_courses:
            # Udemy search URL with filters for top-rated courses
            search_url = (
                'https://www.udemy.com/courses/search/'
                f'?q={course["skill"].replace(" ", "%20")}'
                '&sort=rating'  # Sort by rating
                '&ratings=4.5'  # Minimum 4.5 stars
                '&instructional_level=all'
            )
            
            st.markdown(f"""
            <div class="course-card">
                <div class="course-title">
                    <a href="{search_url}" target="_blank">Find top-rated courses for: {course['skill']}</a>
                </div>
                <div class="course-description">
                    {course['description']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No specific course recommendations at this time.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Original Resume Section (Collapsible)
    with st.expander("View Original Resume"):
        if extracted_text:
            st.code(extracted_text)

def main_app():
    # Theme Toggle Button
    st.button("🌞" if st.session_state.theme_mode == "dark" else "🌙", on_click=toggle_theme, key="theme_toggle")

    # Logo + Title
    st.markdown(f'''
        <div style="display: flex; justify-content: center; align-items: center; margin-top: -20px; margin-bottom: -10px;">
            <img src="https://i.ibb.co/5XKqNLMf/notion-face.png" alt="Logo" style="height: 100px;">
        </div>
        <h1 style="margin-top:0; margin-left: 20px; color:{text_color}; text-align: center;">ProScan</h1>
        ''',
        unsafe_allow_html=True
    )
    st.markdown(f"<p style='text-align: center; color: {text_color};'>Welcome, {st.session_state.user_name}!</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-size: 0.8rem; color: #808080;'>{st.session_state.user_email}</p>", unsafe_allow_html=True)


    # Inputs
    uploaded_file = st.file_uploader("Upload your resume (PDF/DOCX)", type=["pdf", "docx"])
    jd_input = st.text_area("Job Description Input", height=200, placeholder="Paste Job Description here", label_visibility="hidden")

    # CAPTCHA Section
    st.markdown("### Security Verification")
    
    # Generate new CAPTCHA if needed
    if not st.session_state.current_captcha:
        new_image, _ = generate_new_captcha()
        st.session_state.current_captcha = new_image

    # Display CAPTCHA
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.image(st.session_state.current_captcha, width=200)
        captcha_input = st.text_input(
            "Enter CAPTCHA text",
            key="captcha_question",
            label_visibility="collapsed",
            placeholder="Enter the text shown above"
        )
    
    with col2:
        if st.button("Verify CAPTCHA"):
            verify_captcha()
    
    with col3:
        if st.button("New CAPTCHA"):
            reset_captcha_verification()
            st.rerun()

    # Analysis Section
    analyze_col1, analyze_col2 = st.columns([3, 1])
    with analyze_col1:
        analyze = st.button(
            "Analyze Resume",
            use_container_width=True,
            disabled=not st.session_state.captcha_verified
        )
    
    with analyze_col2:
        if st.session_state.captcha_verified:
            st.success("✅ Verified")
        else:
            st.error("⚠️ Verify CAPTCHA first")

    # If analyze button is clicked and CAPTCHA is verified
    if analyze and st.session_state.captcha_verified:
        # Reset CAPTCHA for next analysis
        reset_captcha_verification()
        st.rerun()

    # Resume Logic
    if analyze:
        if captcha_answer.lower() != st.session_state.captcha_answer.lower():
            st.error("Incorrect captcha answer.")
            return

        if uploaded_file and jd_input:
            with st.spinner("Performing AI analysis... This may take a moment."):
                resume_bytes = uploaded_file.read()
                resume_text = extract_text(resume_bytes, uploaded_file.name)
                st.session_state.extracted_text = resume_text
                
                if not resume_text:
                    st.error("Could not extract text from resume.")
                else:
                    analysis = get_semantic_analysis(resume_text, jd_input)
                    st.session_state.analysis_result = analysis
                    st.session_state.analysis_done = True
                    st.session_state.captcha_question = "" # Reset captcha
                    st.session_state.captcha_image_data = None
        elif not uploaded_file:
            st.warning("Please upload a resume to continue.")
        elif not jd_input:
            st.warning("Paste a job description to analyze your resume.")

    if st.session_state.analysis_done:
        display_analysis(st.session_state.analysis_result, st.session_state.extracted_text)

if st.session_state.page == "landing":
    landing_page()
else:
    main_app()
