import streamlit as st
import pdfplumber
import docx
import firebase_admin
from firebase_admin import credentials, firestore

def load_css():
    with open("styles/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Firebase setup
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Skills list
skills = [
    "Python",
    "Java",
    "Machine Learning",
    "Cloud",
    "SQL",
    "AI",
    "HTML",
    "CSS"
]

st.title("AI Resume Screening App")

uploaded_file = st.file_uploader(
    "Upload Resume",
    type=["pdf", "docx"]
)

# Function to extract text
def extract_text(file):
    text = ""

    if file.name.endswith(".pdf"):
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                if page.extract_text():
                    text += page.extract_text()

    elif file.name.endswith(".docx"):
        doc = docx.Document(file)
        for para in doc.paragraphs:
            text += para.text

    return text


if uploaded_file:

    text = extract_text(uploaded_file)

    st.subheader("Resume Text")
    st.write(text[:1000])

    # Skill Detection
    found_skills = []

    for skill in skills:
        if skill.lower() in text.lower():
            found_skills.append(skill)

    st.subheader("Detected Skills")
    st.write(found_skills)

    # Candidate Ranking
    score = len(found_skills)

    if score >= 5:
        rank = "Excellent Candidate"
    elif score >= 3:
        rank = "Good Candidate"
    elif score >= 1:
        rank = "Average Candidate"
    else:
        rank = "Needs Improvement"

    st.subheader("Candidate Score")
    st.write(score)

    st.subheader("Candidate Ranking")
    st.write(rank)

    # Store in Firebase
    data = {
        "filename": uploaded_file.name,
        "skills": found_skills,
        "score": score,
        "ranking": rank
    }

    db.collection("resumes").add(data)

    st.success("Resume uploaded and stored successfully!")
    
