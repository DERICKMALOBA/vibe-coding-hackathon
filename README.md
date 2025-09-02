# AI Study Buddy

## Project Description

AI Study Buddy is a full-stack web application designed to help students create and manage flashcards from their notes using artificial intelligence. Students can paste their notes into an input box, and the application will generate quiz-style flashcards using a Hugging Face Question-Answering model. These flashcards can then be saved to a Supabase database and managed from a personal dashboard.

## Features

-   **Notes Input:** A `textarea` where students can paste their study notes.
-   **Flashcard Generation:** AI-powered generation of 5-10 quiz-style flashcards from pasted notes using the Hugging Face Question-Answering API and spaCy for enhanced question diversity.
-   **Interactive Flashcards:** Flashcard UI that allows users to flip cards to reveal answers.
-   **Dashboard:** A dedicated page to display and manage all saved flashcards.
-   **Flashcard Saving:** Ability to save generated flashcards to a personal collection in Supabase.
-   **Modular Code:** Clean separation of frontend and backend components.

## Technologies Used

### Frontend
-   HTML5
-   CSS3 (Vanilla CSS)
-   Vanilla JavaScript

### Backend
-   **Flask:** A lightweight Python web framework.
-   **Hugging Face Transformers:** For the Question-Answering AI model (`distilbert-base-cased-distilled-squad`).
-   **spaCy:** For advanced Natural Language Processing (Named Entity Recognition, noun chunk extraction) to improve question generation.
-   **Supabase Client (Python):** For interacting with the Supabase database.
-   **Gunicorn:** A WSGI HTTP server for deploying Flask applications.
-   **Flask-CORS:** For handling Cross-Origin Resource Sharing.
-   **python-dotenv:** For loading environment variables from a `.env` file during local development.

### AI Layer
-   Hugging Face Question-Answering API: Utilizes a pre-trained model to extract answers based on generated questions from the notes.
-   spaCy: Used to identify key entities (persons, locations, dates, etc.) and noun phrases to formulate diverse "who," "what," "where," and "when" questions.

### Database
-   **Supabase:** A Postgres-based open-source Firebase alternative for storing flashcards.

## Project Structure

```
ai-study-buddy/
├── frontend/
│   ├── index.html        # Main HTML file for the application
│   ├── style.css         # Stylesheets for the frontend
│   └── script.js         # Frontend JavaScript logic
└── backend/
    ├── app.py            # Flask application entry point
    ├── requirements.txt  # Python dependencies
    ├── Procfile          # For deployment to platforms like Bolt.new (e.g., Gunicorn setup)
    ├── .env.example      # Example file for environment variables
    ├── .env              # (Sensitive) Environment variables for local development (ignored by Git)
    └── .gitignore        # Specifies files/directories to ignore in Git (e.g., .env, venv/)
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/DERICKMALOBA/vibe-coding-hackathon.git
cd vibe-coding-hackathon
```

### 2. Backend Setup

Navigate to the `backend` directory:
```bash
cd backend
```

#### Create and Activate a Python Virtual Environment (Recommended)

```bash
python -m venv venv
# On Windows (Command Prompt)
.\venv\Scripts\activate
# On Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# On macOS/Linux
source venv/bin/activate
```

#### Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### Download spaCy Model

```bash
python -m spacy download en_core_web_sm
```

### 3. Supabase Setup

1.  **Create a Supabase Project:** If you don't have one, sign up at [Supabase](https://supabase.com/) and create a new project.
2.  **Get Credentials:** From your Supabase project settings, find your Project URL and `anon` (public) `Service Role Key`.
3.  **Create `flashcards` Table:** In your Supabase SQL Editor, run the following SQL to create the `flashcards` table:

    ```sql
    CREATE TABLE flashcards (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      question TEXT NOT NULL,
      answer TEXT NOT NULL,
      userId TEXT NOT NULL,
      created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    ```

### 4. Environment Variables

Create a file named `.env` in your `backend/` directory (it's already in `.gitignore`):

```
# backend/.env
SUPABASE_URL="your_supabase_project_url"
SUPABASE_KEY="your_supabase_anon_key"
```
Replace `"your_supabase_project_url"` and `"your_supabase_anon_key"` with your actual Supabase credentials. A `.env.example` file is provided for reference.

### 5. Running the Application Locally

#### Start the Backend Server

Ensure you are in the `backend/` directory and your virtual environment is activated.

```bash
python app.py
```
The Flask server will start, typically on `http://127.0.0.1:5000/`.

#### Open the Frontend

Open your web browser and navigate to the `index.html` file located in the `frontend/` directory of your project.

Example path: `file:///C:/Users/dukeg/OneDrive/Desktop/Vibe%20coding/frontend/index.html`

### 6. Deployment to Bolt.new (or similar PaaS)

1.  **Push to Git:** Ensure your code is pushed to your Git repository (e.g., GitHub, GitLab). The `Procfile` in the `backend/` directory tells platforms like Bolt.new how to start your Flask application using Gunicorn.
    ```bash
    git add .
    git commit -m "Initial commit of AI Study Buddy project"
    git push origin main # Or 'master', depending on your default branch
    ```
2.  **Environment Variables:** Configure `SUPABASE_URL` and `SUPABASE_KEY` as environment variables directly in your Bolt.new deployment settings. Do **NOT** commit your `.env` file.
3.  **Static Files:** The Flask application is configured to serve static files from the `frontend/` directory.

## Usage

1.  Paste your notes into the textarea on the main page.
2.  Click "Generate Flashcards" to create quiz-style flashcards.
3.  Flip the generated flashcards to reveal their answers.
4.  Click "Save Generated Flashcards" to store them in your Supabase database.
5.  View your saved flashcards on the dashboard section.
