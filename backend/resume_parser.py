import re
import spacy
from spacy.matcher import PhraseMatcher, Matcher
from typing import Dict, List, Optional, Union
import json
from extractor import extract_section

# Load the large English model. This is done once when the module is loaded.
# This might take a moment.
try:
    nlp = spacy.load("en_core_web_lg")
except OSError:
    print("Downloading language model for the first time. This may take a while...")
    from spacy.cli import download
    download("en_core_web_lg")
    nlp = spacy.load("en_core_web_lg")

# Load skill categories from JSON file
try:
    with open("backend/skills_config.json", "r") as f:
        SKILL_CATEGORIES = json.load(f)
except FileNotFoundError:
    SKILL_CATEGORIES = {
        "Programming Languages": ["python", "java", "c++", "javascript", "ruby", "typescript", "go", "rust"],
        "Web Development": ["react", "angular", "vue", "node.js", "django", "flask", "fastapi", "express", "spring"],
        "Databases": ["sql", "mysql", "postgresql", "mongodb", "nosql", "redis", "oracle", "dynamodb"],
        "Cloud & DevOps": ["aws", "azure", "google cloud", "gcp", "docker", "kubernetes", "terraform", "ansible", "jenkins"],
        "Machine Learning": ["machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn", "keras", "opencv"],
        "Data Science": ["data analysis", "pandas", "numpy", "matplotlib", "seaborn", "plotly", "pyspark"],
        "AI & NLP": ["natural language processing", "nlp", "spacy", "nltk", "huggingface", "transformers", "gpt", "llm"],
        "Tools & Practices": ["git", "jira", "agile", "scrum", "ci/cd", "tdd", "rest", "graphql"]
    }

# Flatten the categories for matching
SKILL_KEYWORDS = [skill for skills in SKILL_CATEGORIES.values() for skill in skills]
EDUCATION_KEYWORDS = ["education", "academic background", "qualifications"]
PROJECTS_KEYWORDS = ["projects", "personal projects", "academic projects"]


def extract_contact_info(text: str) -> Dict[str, Optional[str]]:
    """Extract contact information from text, returning single entries for each."""
    info = {
        'email': None,
        'phone': None,
        'linkedin': None,
        'github': None
    }

    # Email
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    if email_match:
        info['email'] = email_match.group(0)

    # Phone: More robust pattern for various formats (e.g., +1 (123) 456-7890, 123-456-7890, 123.456.7890)
    phone_match = re.search(r'(?:\+\d{1,4}[-.\s]?)?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}(?:\s*(?:ext|x|\#)\s*\d{2,6})?', text)
    if phone_match:
        info['phone'] = phone_match.group(0)

    # LinkedIn
    linkedin_match = re.search(r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/[a-zA-Z0-9-]+\/?', text)
    if linkedin_match:
        info['linkedin'] = linkedin_match.group(0)

    # GitHub
    github_match = re.search(r'(?:https?:\/\/)?(?:www\.)?github\.com\/[a-zA-Z0-9-]+\/?', text)
    if github_match:
        info['github'] = github_match.group(0)
        
    return info

def extract_experience(text: str) -> list:
    """Extract work experience from resume text."""
    # This is a simple regex-based approach and may need to be improved
    # for better accuracy.
    experience_pattern = re.compile(r'''
        (^[A-Z][a-z]+(?:\s[A-Z][a-z]+)*)            # Job Title
        (?:\s+at\s+|\s*\n)                           # Separator
        ([A-Z][a-zA-Z0-9\s,]+)                      # Company
        (?:\s*\n|\s*\()                             # Separator
        ((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s\d{4})  # Start Date
        (?:\s*-\s*)                                  # Separator
        ((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s\d{4}|Present) # End Date
    ''', re.VERBOSE | re.MULTILINE)
    
    experiences = []
    for match in experience_pattern.finditer(text):
        experiences.append({
            'title': match.group(1).strip(),
            'company': match.group(2).strip(),
            'start_date': match.group(3).strip(),
            'end_date': match.group(4).strip()
        })
    return experiences

def extract_education(text: str) -> list:
    """Extract education from resume text."""
    sections = extract_section(text, EDUCATION_KEYWORDS)
    education_text = "\n".join(sections.values())
    # A simple parser, splitting by lines. Can be improved.
    return [line.strip() for line in education_text.split('\n') if line.strip()]

def extract_projects(text: str) -> list:
    """Extract projects from resume text."""
    sections = extract_section(text, PROJECTS_KEYWORDS)
    projects_text = "\n".join(sections.values())
    # A simple parser, splitting by lines. Can be improved.
    return [line.strip() for line in projects_text.split('\n') if line.strip()]


def extract_entities(resume_text: str, jd_text: str = "") -> dict:
    """
    Extract entities like name, contact info, skills, and experience levels from the given resume text.
    
    Args:
        resume_text: The text content of the resume.
        
    Returns:
        A dictionary containing the extracted entities like name, contact info, skills, and experience levels.
    """
    doc = nlp(resume_text)
    jd_doc = nlp(jd_text)
    
    # Extract contact information
    contact_info = extract_contact_info(resume_text)
    
    # Extract person names using NER (try to get the first name if multiple found)
    person_names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    primary_name = person_names[0] if person_names else "Unknown"
    
    # Create a matcher for skills
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    skill_patterns = [nlp(skill) for skill in SKILL_KEYWORDS]
    matcher.add("SKILL", skill_patterns)
    matches = matcher(doc)
    
    def parse_experience_value(token_text):
        """Safely parse experience value from text, handling both numeric and word numbers."""
        try:
            # Try direct numeric conversion first
            return float(token_text) if '.' in token_text else int(token_text)
        except (ValueError, TypeError):
            # Handle word numbers (e.g., 'one', 'two', 'three')
            word_to_num = {
                'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
                'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
                'first': 1, 'second': 2, 'third': 3, 'fourth': 4, 'fifth': 5,
                '1st': 1, '2nd': 2, '3rd': 3, '4th': 4, '5th': 5
            }
            return word_to_num.get(token_text.lower().strip(), 0)  # Default to 0 if can't parse
    
    # Extract experience indicators (years, months, etc.)
    experience_indicators = []
    for sent in doc.sents:
        for token in sent:
            # Look for number-like tokens or specific number words
            if (token.like_num or token.text.lower() in ['one', 'two', 'three', 'first', 'second', 'third']) \
               and any(t.text.lower() in ['year', 'month', 'yr', 'mo', 'yrs', 'mos'] 
                     for t in token.head.subtree):
                
                # Get the number and time unit
                num = parse_experience_value(token.text)
                if num <= 0:  # Skip invalid or zero values
                    continue
                    
                unit = next((t.text for t in token.head.subtree 
                          if t.text.lower() in ['year', 'month', 'yr', 'mo', 'yrs', 'mos']), None)
                
                if unit:
                    unit = unit.lower()
                    # Normalize units
                    if unit in ['year', 'yr', 'yrs']:
                        multiplier = 12  # Convert years to months
                    else:
                        multiplier = 1  # Already in months
                        
                    experience_indicators.append({
                        'skill': None,  # Will be linked to skills later
                        'value': num * multiplier,
                        'unit': 'months'
                    })
    
    # Extract the matched spans and their categories with experience
    matched_skills = {} 
    skill_experience = {}
    
    # First pass: Find all skills and their context
    for match_id, start, end in matches:
        skill = doc[start:end].text.lower()
        skill_span = doc[start:end]
        
        # Find experience for this skill in surrounding sentences
        exp_months = 0
        for sent in doc.sents:
            # Only check sentences that are close to the skill mention
            if skill_span.sent == sent or skill_span.sent in sent.sent:
                for token in sent:
                    # Look for number-like tokens or specific number words
                    if (token.like_num or token.text.lower() in ['one', 'two', 'three', 'first', 'second', 'third']) \
                       and any(t.text.lower() in ['year', 'month', 'yr', 'mo', 'yrs', 'mos'] 
                             for t in token.head.subtree):
                        
                        num = parse_experience_value(token.text)
                        if num <= 0:  # Skip invalid or zero values
                            continue
                            
                        unit = next((t.text.lower() for t in token.head.subtree 
                                  if t.text.lower() in ['year', 'month', 'yr', 'mo', 'yrs', 'mos']), None)
                        
                        if unit:
                            # Convert all to months for consistency
                            multiplier = 12 if unit in ['year', 'yr', 'yrs'] else 1
                            exp_months = max(exp_months, num * multiplier)
        
        # Store experience for this skill
        skill_experience[skill] = exp_months
        
        # Categorize the skill
        for category, skills in SKILL_CATEGORIES.items():
            if skill in skills:
                if category not in matched_skills:
                    matched_skills[category] = {}
                matched_skills[category][skill] = exp_months
                break
    
    # Convert to frontend-friendly format
    categorized_skills = {}
    for category, skills in matched_skills.items():
        categorized_skills[category] = [
            {
                "name": skill,
                "experience": exp_months,
                "experience_text": format_experience(exp_months)
            }
            for skill, exp_months in skills.items()
        ]
    
    # Flatten all skills for backward compatibility
    all_skills = [skill for skills in matched_skills.values() for skill in skills]

    # Prioritize the longest name found, often the full name.
    name = primary_name
    
    extracted_data = {
        "name": name,
        "skills": all_skills,  
        "categorized_skills": categorized_skills,
        "experience": extract_experience(resume_text),
        "education": extract_education(resume_text),
        "projects": extract_projects(resume_text)
    }
    extracted_data.update(contact_info)

    return extracted_data

def format_experience(months: float) -> str:
    """Format experience in months to a human-readable string."""
    if not months:
        return "No experience specified"
    
    years = months // 12
    remaining_months = months % 12
    
    parts = []
    if years >= 1:
        parts.append(f"{int(years)} {'year' if years == 1 else 'years'}")
    if remaining_months >= 1:
        parts.append(f"{int(remaining_months)} {'month' if remaining_months == 1 else 'months'}")
    
    return "Experience: " + " and ".join(parts) if parts else "Experience: Less than a month"