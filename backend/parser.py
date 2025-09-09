import re
import spacy
from spacy.matcher import PhraseMatcher, Matcher
from typing import Dict, List, Optional, Union

# Load the large English model. This is done once when the module is loaded.
# This might take a moment.
try:
    nlp = spacy.load("en_core_web_lg")
except OSError:
    print("Downloading language model for the first time. This may take a while...")
    from spacy.cli import download
    download("en_core_web_lg")
    nlp = spacy.load("en_core_web_lg")

# Skill categories with related keywords
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

def extract_contact_info(text: str) -> Dict[str, Union[str, List[str]]]:
    """Extract contact information from text."""
    # Email extraction
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    
    # Phone number extraction (supports various formats)
    phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phones = re.findall(phone_pattern, text)
    
    # LinkedIn profile extraction
    linkedin_pattern = r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/[a-zA-Z0-9-]+\/?'
    linkedin = re.findall(linkedin_pattern, text)
    
    return {
        'emails': emails[:1],  # Return only the first email if multiple found
        'phones': phones[:1],  # Return only the first phone if multiple found
        'linkedin': linkedin[0] if linkedin else None
    }

def extract_entities(resume_text: str) -> dict:
    """
    Extract entities like name, contact info, skills, and experience levels from the given resume text.
    
    Args:
        resume_text: The text content of the resume.
        
    Returns:
        A dictionary containing the extracted entities like name, contact info, skills, and experience levels.
    """
    doc = nlp(resume_text)
    
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
                    
                unit = next((t for t in token.head.subtree 
                          if t.text.lower() in ['year', 'month', 'yr', 'mo', 'yrs', 'mos']), None)
                
                if unit:
                    unit = unit.text.lower()
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
    
    return {
        "name": name,
        "contact": {
            "email": contact_info['emails'][0] if contact_info['emails'] else None,
            "phone": contact_info['phones'][0] if contact_info['phones'] else None,
            "linkedin": contact_info['linkedin']
        },
        "skills": all_skills,  
        "categorized_skills": categorized_skills
    }

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
