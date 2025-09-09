from sentence_transformers import SentenceTransformer, util
import numpy as np

# Load a pre-trained sentence transformer model. This is done once when the module is loaded.
# The model is optimized for semantic similarity tasks.
model = SentenceTransformer('all-MiniLM-L6-v2')

def calculate_similarity(resume_skills: list, jd_skills: list) -> float:
    """
    Calculates a similarity score between resume skills and job description skills
    using sentence embeddings and cosine similarity.

    Args:
        resume_skills: A list of skills extracted from the resume.
        jd_skills: A list of skills extracted from the job description.

    Returns:
        A float representing the similarity score, from 0 to 100.
    """
    if not jd_skills or not resume_skills:
        return 0.0

    # Convert skill lists to embeddings (vectors)
    resume_embeddings = model.encode(resume_skills, convert_to_tensor=True)
    jd_embeddings = model.encode(jd_skills, convert_to_tensor=True)

    # Calculate cosine similarity between each resume skill and all JD skills
    cosine_scores = util.cos_sim(resume_embeddings, jd_embeddings)

    # For each resume skill, find the highest similarity score against any JD skill.
    # This means if a resume has 'react', it will be matched with 'react.js' in the JD.
    max_scores = np.max(cosine_scores.cpu().numpy(), axis=1)
    
    # Calculate the average similarity for resume skills
    avg_resume_similarity = np.mean(max_scores) if len(max_scores) > 0 else 0
    
    # Calculate how many of the JD skills were matched (similarity > 0.7)
    matched_jd_skills = np.sum(np.max(cosine_scores.cpu().numpy(), axis=0) > 0.7)
    jd_coverage = matched_jd_skills / len(jd_skills) if jd_skills else 0
    
    # Combine both metrics (50% weight each)
    final_score = (avg_resume_similarity * 0.5 + jd_coverage * 0.5) * 100
    
    # Apply a non-linear scaling to make the scores more meaningful
    # This makes it harder to get very high scores without good matches
    final_score = 100 * (1 - np.exp(-final_score / 30))
    
    # Ensure the score is between 0 and 100
    return min(max(round(final_score, 1), 0), 100)
