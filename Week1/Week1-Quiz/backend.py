from fastapi import FastAPI  # Imports the main FastAPI class to create the web API server
from pydantic import BaseModel  # Imports BaseModel to define and validate structured data shapes
from typing import List, Dict  # Imports type hints so Python/Pydantic/FastAPI know exact container types

# ==============================================================================
# 1. INITIALIZE FASTAPI APPLICATION
# ==============================================================================
# Creates the core 'app' instance. Uvicorn will look for this 'app' variable to serve requests.
app = FastAPI(title="Future of AI Quiz API")


# ==============================================================================
# 2. QUIZ DATA STORE (LIST OF DICTIONARIES)
# ==============================================================================
# WHY A 'list' (`[...]`) FOR QUIZ_DATA?
# - A list preserves ORDER (Question 1, 2, 3... up to 10) and allows indexing/iteration in sequence.
# - A 'set' (`{...}`) would be wrong here because sets are unordered and cannot hold unhashable dicts.
#
# WHY A 'dict' (`{...}`) FOR EACH QUESTION?
# - Each question has named fields/keys ("id", "question", "options", "answer") with different types.
#   Accessing values by key name (e.g., q["answer"]) is much clearer than remembering tuple positions.
#
# WHY A 'list' (`[...]`) FOR "options" INSTEAD OF A 'set'?
# - A 'set' does NOT guarantee display order, so choices would jump around unpredictably.
#   A 'list' keeps the exact 4 choices in a predictable order for the UI.
QUIZ_DATA = [
    {
        "id": 1,  # 'int' (integer): unique numeric identifier for Question 1
        "question": "What does AGI stand for in the context of future AI development?",  # 'str' (string)
        "options": [  # 'list' of 4 'str' items
            "Automated Graphical Interface",
            "Artificial General Intelligence",
            "Advanced Generative Integration",
            "Algorithmic Governance Initiative"
        ],
        "answer": "Artificial General Intelligence"  # 'str': kept on server so users cannot view it in browser
    },
    {
        "id": 2,
        "question": "Which concept refers to AI systems that can autonomously plan, use tools, and execute multi-step tasks?",
        "options": [
            "Agentic AI",
            "Static Machine Learning",
            "Rule-Based Expert Systems",
            "Optical Character Recognition"
        ],
        "answer": "Agentic AI"
    },
    {
        "id": 3,
        "question": "What is the primary goal of 'AI Alignment' research?",
        "options": [
            "Making GPUs run faster",
            "Ensuring AI systems act in accordance with human values and intentions",
            "Aligning text in UI layouts automatically",
            "Connecting multiple databases together"
        ],
        "answer": "Ensuring AI systems act in accordance with human values and intentions"
    },
    {
        "id": 4,
        "question": "What are 'Small Language Models' (SLMs) primarily valued for in future edge computing?",
        "options": [
            "Requiring massive data centers",
            "Running efficiently on local devices with lower power and latency",
            "Replacing all forms of human communication",
            "Generating only single-word answers"
        ],
        "answer": "Running efficiently on local devices with lower power and latency"
    },
    {
        "id": 5,
        "question": "Which technology combines quantum mechanics with machine learning to solve complex optimization problems?",
        "options": [
            "Quantum AI",
            "Blockchain AI",
            "Analog Computing",
            "Virtual Reality"
        ],
        "answer": "Quantum AI"
    },
    {
        "id": 6,
        "question": "What is 'Synthetic Data' used for in training next-generation AI models?",
        "options": [
            "Artificially generated data used when real-world data is scarce or privacy-sensitive",
            "Data stored on physical magnetic tapes",
            "Deleting corrupted datasets",
            "Slowing down model convergence"
        ],
        "answer": "Artificially generated data used when real-world data is scarce or privacy-sensitive"
    },
    {
        "id": 7,
        "question": "What does 'Multimodal AI' mean?",
        "options": [
            "AI that only understands SQL queries",
            "AI capable of processing and generating text, images, audio, and video together",
            "AI that requires multiple passwords to log in",
            "AI restricted to a single programming language"
        ],
        "answer": "AI capable of processing and generating text, images, audio, and video together"
    },
    {
        "id": 8,
        "question": "Which field focuses on making AI decision-making processes transparent and understandable to humans?",
        "options": [
            "Black-Box Computing",
            "Explainable AI (XAI)",
            "Dark Data Analytics",
            "Obfuscated Neural Networks"
        ],
        "answer": "Explainable AI (XAI)"
    },
    {
        "id": 9,
        "question": "What is 'Neuromorphic Computing' inspired by?",
        "options": [
            "Traditional vacuum tubes",
            "The structure and function of the human brain",
            "Solar panel efficiency",
            "Classical mechanical clocks"
        ],
        "answer": "The structure and function of the human brain"
    },
    {
        "id": 10,
        "question": "What is a major environmental concern regarding the future scaling of massive AI models?",
        "options": [
            "High electricity and water consumption in data centers",
            "Depletion of global helium reserves",
            "Increased radio wave interference with satellites",
            "Excessive paper usage"
        ],
        "answer": "High electricity and water consumption in data centers"
    }
]


# ==============================================================================
# 3. PYDANTIC SCHEMAS (DATA CONTRACTS BETWEEN BACKEND & FRONTEND)
# ==============================================================================
# QuestionOut defines the exact fields sent to the frontend when fetching questions.
# Notice there is NO 'answer' field here—Pydantic strips 'answer' automatically
# even though each item in QUIZ_DATA contains 'answer'.
class QuestionOut(BaseModel):
    id: int              # Must be an integer
    question: str        # Must be a string
    options: List[str]   # Must be a list of strings


# SubmissionIn defines the JSON body expected by the POST /submit endpoint.
class SubmissionIn(BaseModel):
    # WHY A 'dict' (`Dict[int, str]`) FOR "answers"?
    # - Maps each question's 'id' ('int' key) directly to the user's chosen option ('str' value).
    # - Fast O(1) lookup by question ID without scanning a list of pairs.
    # - Note: In JSON, object keys arrive as strings like "1", and Pydantic automatically
    #   converts/coerces them to 'int' keys (1) when type is Dict[int, str].
    answers: Dict[int, str]


# ==============================================================================
# 4. ENDPOINT: GET /questions
# ==============================================================================
@app.get("/questions", response_model=List[QuestionOut])
def get_questions():
    # Returns the 'list' of question 'dict's.
    # Because response_model=List[QuestionOut] is set, FastAPI filters every dictionary
    # so only 'id', 'question', and 'options' are serialized into the JSON response.
    return QUIZ_DATA


# ==============================================================================
# 5. ENDPOINT: POST /submit
# ==============================================================================
@app.post("/submit")
def submit_quiz(submission: SubmissionIn):
    # 'int' counter tracking how many answers matched the expected answer
    score = 0

    # 'list' of 'dict's: stores detailed grading feedback for each question in order
    results = []

    # Iterate through every question dictionary 'q' in the QUIZ_DATA list
    for q in QUIZ_DATA:
        q_id = q["id"]                  # Extract question ID ('int')
        correct_answer = q["answer"]    # Extract ground-truth answer ('str')

        # Use .get(q_id) on the 'answers' dict instead of submission.answers[q_id]:
        # .get() safely returns None instead of crashing with a KeyError if a key is missing.
        user_answer = submission.answers.get(q_id)

        # 'bool' (True or False): checks exact string equality between user choice and answer
        is_correct = (user_answer == correct_answer)

        # Increment score only when is_correct evaluates to True
        if is_correct:
            score += 1

        # Append a new 'dict' summarizing this single question's result to the 'results' list
        results.append({
            "id": q_id,
            "question": q["question"],
            "your_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct
        })

    # Return a summary 'dict' containing overall stats ('int' / 'float') and 'details' ('list')
    return {
        "score": score,                                              # 'int'
        "total": len(QUIZ_DATA),                                     # 'int': total number of questions (10)
        "percentage": round((score / len(QUIZ_DATA)) * 100, 2),      # 'float' rounded to 2 decimal places
        "details": results                                           # 'list' of result 'dict's
    }