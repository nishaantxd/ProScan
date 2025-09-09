import google.generativeai as genai
import os
import json
import streamlit as st

# Get API key from Streamlit secrets or environment variables
try:
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
    except:
        # Fallback to environment variable
        api_key = os.environ.get("GOOGLE_API_KEY")
    
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in secrets or environment variables.")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"Error configuring Generative AI: {e}")
    model = None

#constants
# This is the master prompt that instructs the AI model.
# It's designed to be robust and to return a clean JSON output.
PROMPT_TEMPLATE = """
You are an expert HR analyst and career coach with years of experience in technical and non-technical recruitment.
Your task is to analyze a resume against a job description and provide a detailed, actionable comparison.

**Instructions:**
1.  **Analyze Thoroughly:** Read the entire resume and job description.
2.  **Extract Candidate Details:** Extract the candidate's full name, email address, phone number, LinkedIn profile URL, and GitHub profile URL. If a piece of information is not found, return `null` for that field.
3.  **Identify Key Skills:** Dynamically identify the most important skills, technologies, and qualifications required by the job description.
4.  **Compare:** Compare the skills and experience from the resume against the requirements from the job description.
5.  **Score:** Generate a "match_score" from 0 to 100, representing how well the resume aligns with the job description.
6.  **Summarize:** Write a concise "executive_summary" (2-3 sentences) explaining the score and the candidate's suitability.
7.  **Categorize Skills:**
    *   "technical_skills": Key technical skills (e.g., Python, React, AWS).
    *   "soft_skills": Important soft skills (e.g., Communication, Teamwork).
    *   "keywords": Other relevant keywords.
8.  **Experience Analysis:** Analyze the candidate's years of experience and compare it to the job description's requirements.
9.  **Project Analysis:** Identify key projects from the resume and summarize them, highlighting their relevance to the job.
10. **Question Generation:** Generate 3-5 interview questions based on the resume and job description.
11. **Overall Vibe:** Assess the overall tone and "vibe" of the resume (e.g., "Action-oriented," "Data-driven," "Creative").
12. **Recommend Courses:** For the top 3-5 most critical missing skills, recommend actual, popular Udemy courses. Format:
    * Use real course titles that exist on Udemy
    * URLs should be in the format: https://www.udemy.com/course/[course-slug]
    * Focus on courses with high ratings (4+ stars) and large enrollment numbers
    * Provide accurate, concise course descriptions
13. **Format Output:** You MUST return the analysis as a single, clean JSON object. Do not include any other text, just the JSON.

**JSON Output Structure:**
{{
  "candidate_name": "<string|null>",
  "email": "<string|null>",
  "phone": "<string|null>",
  "linkedin_url": "<string|null>",
  "github_url": "<string|null>",
  "match_score": <integer>,
  "executive_summary": "<string>",
  "skills_analysis": {{
    "technical_skills": {{"matching": ["<skill>"], "missing": ["<skill>"]}},
    "soft_skills": {{"matching": ["<skill>"], "missing": ["<skill>"]}},
    "keywords": {{"matching": ["<keyword>"], "missing": ["<keyword>"]}}
  }},
  "experience_analysis": "<string>",
  "project_analysis": [
    {{
      "title": "<Project Title>",
      "summary": "<Project Summary>"
    }}
  ],
  "interview_questions": ["<Question 1>", "<Question 2>"],
  "overall_vibe": "<string>",
  "recommended_courses": [
    {{
      "skill": "<missing_skill>",
      "course_title": "<Udemy Course Title>",
      "description": "<Brief course description>",
      "url": "<plausible_udemy_url>"
    }}
  ]
}}

**Input:**

**Job Description:**
---
{jd_text}
---

**Resume:**
---
{resume_text}
---

**Analysis (JSON Output Only):**
"""

def get_semantic_analysis(resume_text: str, jd_text: str) -> dict:
    """
    Performs a deep semantic analysis of a resume against a job description
    using a generative AI model.

    Args:
        resume_text: The full text of the resume.
        jd_text: The full text of the job description.

    Returns:
        A dictionary containing the analysis (score, summary, skills),
        or an error dictionary if the analysis fails.
    """
    if not model:
        return {
            "error": "Generative AI model not configured. Please check your API key."
        }

    if not resume_text or not jd_text:
        return {"error": "Resume or Job Description text is missing."}

    try:
        prompt = PROMPT_TEMPLATE.format(resume_text=resume_text, jd_text=jd_text)
        response = model.generate_content(prompt)

        # Clean the response to extract only the JSON part.
        # The model might sometimes include backticks or the word "json".
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "").strip()

        # Parse the JSON string into a Python dictionary
        analysis_result = json.loads(cleaned_response)
        return analysis_result

    except Exception as e:
        print(f"An error occurred during semantic analysis: {e}")
        # Fallback or error dictionary
        return {
            "error": "Failed to get analysis from the AI model.",
            "details": str(e)
        }
