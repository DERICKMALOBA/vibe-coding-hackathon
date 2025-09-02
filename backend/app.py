from flask import Flask, request, jsonify
import os
from transformers import pipeline
from supabase import create_client, Client
from flask_cors import CORS # Import CORS
import spacy # Import spacy
from dotenv import load_dotenv # Import load_dotenv

load_dotenv() # Load environment variables from .env file

app = Flask(__name__, static_folder='../frontend', static_url_path='') # Configure Flask to serve static files
CORS(app) # Enable CORS for all routes

# Load spaCy English model
# Run 'python -m spacy download en_core_web_sm' in your terminal if the model is not found.
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spacy model 'en_core_web_sm'...")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Supabase Configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Load the Hugging Face Question-Answering pipeline
# You can choose a different model if needed, e.g., "distilbert-base-cased-distilled-squad"
qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

@app.route('/generate', methods=['POST'])
def generate_flashcards():
    data = request.get_json()
    notes = data.get('notes', '')

    if not notes:
        return jsonify({"error": "No notes provided"}), 400

    doc = nlp(notes)
    flashcards = []

    # Strategy 1: Question generation from Named Entities
    for ent in doc.ents:
        if len(flashcards) >= 10:
            break

        question = ""
        if ent.label_ in ["PERSON", "ORG", "NORP"]:
            question = f"Who is {ent.text}?"
        elif ent.label_ in ["GPE", "LOC"]:
            question = f"Where is {ent.text}?"
        elif ent.label_ in ["DATE", "EVENT", "TIME"]:
            question = f"When did {ent.text} happen?"
        elif ent.label_ == "CARDINAL": # For numbers/quantities
            question = f"What is the significance of {ent.text}?"
        elif ent.label_ == "PRODUCT": # For products
            question = f"What is {ent.text}?"
        elif ent.label_ == "WORK_OF_ART": # For works of art
            question = f"What is {ent.text}?"
        elif ent.label_ == "LAW": # For laws
            question = f"What is {ent.text}?"
        elif ent.label_ == "LANGUAGE": # For languages
            question = f"What is {ent.text}?"
        elif ent.label_ == "MONEY": # For money
            question = f"How much is {ent.text}?"
        elif ent.label_ == "PERCENT": # For percentages
            question = f"What is {ent.text} percentage?"
        elif ent.label_ == "QUANTITY": # For quantities
            question = f"What is {ent.text} quantity?"
        elif ent.label_ == "ORDINAL": # For ordinals
            question = f"What is the ordinal {ent.text}?"
        elif ent.label_ == "FAC": # For facilities
            question = f"What is {ent.text}?"
        elif ent.label_ == "ORG": # For organizations
            question = f"What is {ent.text}?"
        elif ent.label_ == "EVENT": # For events
            question = f"What is {ent.text}?"

        if question:
            try:
                qa_result = qa_pipeline(question=question, context=notes)
                if qa_result['score'] > 0.7: # High confidence score
                    flashcards.append({"question": question, "answer": qa_result['answer']})
            except Exception as e:
                print(f"Error with QA pipeline for entity '{ent.text}': {e}")

    # Strategy 2: Question generation from Noun Chunks (for "What is..." questions)
    for chunk in doc.noun_chunks:
        if len(flashcards) >= 10:
            break
        # Avoid generating questions for very short chunks or chunks already covered by entities
        if len(chunk.text.split()) > 1 and chunk.root.pos_ != "PRON" and chunk.text.lower() not in [f.get("question", "").lower() for f in flashcards]:
            question = f"What is {chunk.text}?"
            try:
                qa_result = qa_pipeline(question=question, context=notes)
                if qa_result['score'] > 0.6: # Slightly lower confidence for more general questions
                    flashcards.append({"question": question, "answer": qa_result['answer']})
            except Exception as e:
                print(f"Error with QA pipeline for noun chunk '{chunk.text}': {e}")

    # Fallback: If not enough flashcards, use simple sentence-based questions
    if len(flashcards) < 5:
        sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        for sentence in sentences:
            if len(flashcards) >= 10:
                break
            if " is " in sentence and len(flashcards) < 10:
                parts = sentence.split(" is ", 1)
                question = f"What is {parts[0].strip()}?"
                answer_candidate = parts[1].strip()
                qa_result = qa_pipeline(question=question, context=sentence)
                answer = qa_result['answer'] if qa_result['score'] > 0.5 else answer_candidate
                if question and answer and len(answer) > 2:
                    flashcards.append({"question": question, "answer": answer})
            elif " are " in sentence and len(flashcards) < 10:
                parts = sentence.split(" are ", 1)
                question = f"What are {parts[0].strip()}?"
                answer_candidate = parts[1].strip()
                qa_result = qa_pipeline(question=question, context=sentence)
                answer = qa_result['answer'] if qa_result['score'] > 0.5 else answer_candidate
                if question and answer and len(answer) > 2:
                    flashcards.append({"question": question, "answer": answer})

    # Ensure 5-10 flashcards, prioritizing quality
    final_flashcards = []
    unique_questions = set()
    for card in flashcards:
        if card["question"] not in unique_questions:
            final_flashcards.append(card)
            unique_questions.add(card["question"])

    if len(final_flashcards) > 10:
        final_flashcards = final_flashcards[:10]
    elif len(final_flashcards) < 5:
        # As a last resort, if we still don't have enough, create very generic questions
        # This part could be further refined with more advanced summarization techniques.
        if len(notes) > 50:
            generic_questions = [
                {"question": "What is the main topic of these notes?", "answer": notes.split('.')[0] + "..."},
                {"question": "Can you provide a summary?", "answer": notes[:150] + "..."},
            ]
            for q in generic_questions:
                if q["question"] not in unique_questions and len(final_flashcards) < 5:
                    final_flashcards.append(q)
                    unique_questions.add(q["question"])
    
    return jsonify({"flashcards": final_flashcards})

@app.route('/save', methods=['POST'])
def save_flashcards():
    data = request.get_json()
    flashcards = data.get('flashcards', [])
    user_id = data.get('userId', 'anonymous') # Default to anonymous if no user ID provided

    if not flashcards:
        return jsonify({"error": "No flashcards to save"}), 400

    try:
        for card in flashcards:
            supabase.table("flashcards").insert({"question": card["question"], "answer": card["answer"], "userid": user_id}).execute()
        return jsonify({"message": "Flashcards saved successfully"}), 201
    except Exception as e:
        print(f"Error saving flashcards to Supabase: {e}")
        return jsonify({"error": "Failed to save flashcards"}), 500

@app.route('/flashcards', methods=['GET'])
def get_flashcards():
    user_id = request.args.get('userId', 'anonymous') # Get userId from query parameter, default to anonymous

    try:
        response = supabase.table("flashcards").select("id, question, answer, userid, created_at").eq("userid", user_id).execute()
        flashcards = response.data
        return jsonify({"flashcards": flashcards}), 200
    except Exception as e:
        print(f"Error fetching flashcards from Supabase: {e}")
        return jsonify({"error": "Failed to fetch flashcards"}), 500

if __name__ == '__main__':
    app.run(debug=True)
