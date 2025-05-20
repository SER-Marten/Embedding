from fastapi import FastAPI, UploadFile, File
import pandas as pd
from serpapi.google_search_results import GoogleSearch

app = FastAPI()

API_KEY = "YOUR_SERPAPI_KEY"  # <- Vervang dit!

def get_related_questions(query):
    params = {
        "api_key": API_KEY,
        "engine": "google",
        "google_domain": "google.nl",
        "q": query,
        "gl": "nl",
        "hl": "nl"
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    related_questions = results.get("related_questions", [])
    questions_data = []
    for question in related_questions:
        current_answer = question.get("snippet", "") or \
                         " ".join(question.get("list", [])) if "list" in question else \
                         question.get("title", "")
        q_data = {
            "Question": question.get("question"),
            "Current Answer": current_answer,
            "Source Page Title": question.get("title"),
            "Source URL": question.get("link")
        }
        questions_data.append(q_data)
    return questions_data

@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)
    output_data = []

    for _, row in df.iterrows():
        keyword = row['Keyword']
        search_volume = row['Search Volume']
        keyword_difficulty = row['Keyword Difficulty']
        position = row['Position']
        url = row['URL']

        related_questions = get_related_questions(keyword)

        for question_data in related_questions:
            question_data.update({
                "From Keyword": keyword,
                "Search Volume": search_volume,
                "Pos. keyword": position,
                "Keyword Difficulty": keyword_difficulty,
                "URL": url
            })
            output_data.append(question_data)

    return output_data
