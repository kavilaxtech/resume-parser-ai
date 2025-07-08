from flask import Flask, request, render_template
import spacy
import fitz  # PyMuPDF
import re

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_info(text):
    doc = nlp(text)
    name = ""
    email = ""
    phone = ""
    skills = []

    # 1. Extract NAME: avoid including city (like Chennai) in name
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text.strip()

            # Remove common locations if attached
            common_locations = ["chennai", "bangalore", "mumbai", "delhi", "hyderabad"]
            for city in common_locations:
                name = name.replace(city, "").replace(city.capitalize(), "").strip()
            break

    # 2. Extract Email
    email_match = re.search(r"[\w\.-]+@[\w\.-]+", text)
    if email_match:
        email = email_match.group(0)

    # 3. Extract Phone Number
    phone_match = re.search(r"\+?\d[\d\s-]{8,}\d", text)
    if phone_match:
        phone = phone_match.group(0)

    # 4. Extract Skills
    skills_keywords = [
        "python", "java", "c++", "machine learning", "deep learning",
        "html", "css", "javascript", "sql", "flask", "pandas", "numpy", "react", "angular"
    ]
    skills_found = [skill for skill in skills_keywords if skill.lower() in text.lower()]

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": skills_found
    }

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["resume"]
        if file:
            text = extract_text_from_pdf(file)
            info = extract_info(text)
            return render_template("result.html", info=info)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
