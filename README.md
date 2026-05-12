# Interview Coach

A multi-turn AI-powered chatbot that helps users prepare for technical job interviews by posing questions, evaluating answers, and providing structured feedback.

## How to run the project

1. Clone the project
2. Navigate to the project root:
    cd interview_preparation
3. Activate virtual environment (Windows):
    venv\Scripts\activate
4. Install dependencies:
    pip install -r requirements.txt
5. Create `.env` file — see Environment Variables section below
6. Navigate to the app folder:
    cd interview_coach
7. Run the app:
    streamlit run app.py
8. To deactivate virtual environment:
    deactivate


## Environment Variables

Create a `.env` file in the `interview_coach` folder with the following keys:

MISTRAL_API_KEY=your_mistral_key_here
GEMINI_API_KEY=your_gemini_key_here

- Get Mistral API key at: https://console.mistral.ai
- Get Gemini API key at: https://aistudio.google.com


## Application Components

- **config.py** — Loads initial configuration, API keys, and initializes LLM clients
- **llm.py** — Contains all LLM-related methods including retry logic and fallback chain
- **interview.py** — Contains business logic for interview flow, feedback, and summary generation
- **app.py** — Connects all components and renders the Streamlit UI

## How to Use the Application

1. Run the application and open it in your browser
2. Pick a role (e.g. Frontend Developer) and difficulty level (Junior, Mid, Senior)
3. Click **Start an interview**
4. Answer each question as you would in a real interview
5. After each answer you will receive feedback covering what was good, what was missing, and one specific improvement
6. After 5 questions the session ends automatically with a summary of your performance
7. Download the summary as a `.txt` file for future reference

## Live Demo

The application is deployed and accessible at:
https://practical-interview-preparation.streamlit.app/