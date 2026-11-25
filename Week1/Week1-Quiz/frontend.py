import streamlit as st  # Imports Streamlit to build the interactive web UI
import requests      # Imports Requests to make HTTP GET and POST calls to FastAPI

# Base URL where the local FastAPI (Uvicorn) server is listening
API_URL = "http://127.0.0.1:8000"


# ==============================================================================
# 1. PAGE CONFIGURATION & HEADER
# ==============================================================================
# Configures browser tab title, icon, and centered layout width
st.set_page_config(page_title="Future of AI Quiz", page_icon="🤖", layout="centered")
st.title("🤖 Future of AI — Knowledge Quiz")
st.write("Test your understanding of where Artificial Intelligence is headed. Maximum 10 questions.")


# ==============================================================================
# 2. SESSION STATE INITIALIZATION (DICT-LIKE PERSISTENT STORE)
# ==============================================================================
# WHY USE 'st.session_state'?
# - Streamlit reruns this Python script from top to bottom on user interactions.
# - Normal local variables get reset on every rerun, whereas 'st.session_state'
#   behaves like a persistent 'dict' across reruns for a user's browser session.
if "questions" not in st.session_state:
    # Initialized as an empty 'list' (`[]`); will hold a list of question 'dict's from the API
    st.session_state.questions = []

if "submitted" not in st.session_state:
    # Initialized as a 'bool' (`False`); switches to `True` once the user submits answers
    st.session_state.submitted = False

if "result_data" not in st.session_state:
    # Initialized as `None` (NoneType); will hold the grading response 'dict' from POST /submit
    st.session_state.result_data = None


# ==============================================================================
# 3. FETCH QUESTIONS FUNCTION
# ==============================================================================
def load_questions():
    try:
        # Sends an HTTP GET request to http://127.0.0.1:8000/questions
        response = requests.get(f"{API_URL}/questions")
        # Raises an HTTPError exception if the server returned 4xx or 5xx status codes
        response.raise_for_status()
        # Parses JSON array into a Python 'list' of 'dict's and stores it in session state
        st.session_state.questions = response.json()
    except requests.exceptions.RequestException as e:
        # Catches network/connection errors (e.g., if FastAPI server isn't started yet)
        st.error(f"Could not connect to FastAPI backend. Make sure it is running! Error: {e}")


# On first load (when 'questions' list is empty), fetch questions from the backend
if not st.session_state.questions:
    load_questions()


# ==============================================================================
# 4. RESTART QUIZ HELPER
# ==============================================================================
def restart_quiz():
    # Reset state flags back to their initial values so the quiz form appears again
    st.session_state.submitted = False
    st.session_state.result_data = None
    load_questions()


# ==============================================================================
# 5. QUIZ FORM VIEW (SHOWN BEFORE SUBMISSION)
# ==============================================================================
if st.session_state.questions and not st.session_state.submitted:
    # WHY USE 'st.form'?
    # - Without a form, clicking a radio button triggers an immediate script rerun.
    # - Inside 'st.form', selections are gathered and only submitted when the form submit
    #   button is clicked, keeping the UI smooth and intentional.
    with st.form("quiz_form"):
        # 'dict' mapping question_id ('int') -> selected_option ('str' or None)
        user_answers = {}

        # enumerate(..., start=1) gives both a 1-based display number ('idx') and the question 'dict' ('q')
        for idx, q in enumerate(st.session_state.questions, start=1):
            st.subheader(f"Q{idx}. {q['question']}")

            # st.radio renders a group of mutually exclusive choice buttons from q['options'] ('list').
            # - key: unique string per question so Streamlit tracks each radio widget separately.
            # - index=None: starts with NO option pre-selected (returns None until clicked).
            choice = st.radio(
                label="Choose your answer:",
                options=q["options"],
                key=f"question_{q['id']}",
                index=None,
                label_visibility="collapsed"
            )

            # Save this question's chosen value ('str' or None) into the 'user_answers' dict
            user_answers[q["id"]] = choice
            st.divider()

        # Submit button belonging to 'quiz_form'
        submit_button = st.form_submit_button("Submit Quiz", type="primary")

        if submit_button:
            # Check if ANY value in the 'user_answers' dict is None (meaning a question was skipped)
            if None in user_answers.values():
                st.warning("⚠️ Please answer all 10 questions before submitting!")
            else:
                try:
                    # Send JSON body matching backend's SubmissionIn schema: {"answers": {1: "...", ...}}
                    response = requests.post(
                        f"{API_URL}/submit",
                        json={"answers": user_answers}
                    )
                    response.raise_for_status()

                    # Store the returned grading 'dict' in session state and flip 'submitted' to True
                    st.session_state.result_data = response.json()
                    st.session_state.submitted = True

                    # Rerun immediately so the script enters the 'elif st.session_state.submitted' block
                    st.rerun()
                except requests.exceptions.RequestException as e:
                    st.error(f"Error submitting quiz: {e}")


# ==============================================================================
# 6. RESULTS VIEW (SHOWN AFTER SUBMISSION)
# ==============================================================================
elif st.session_state.submitted and st.session_state.result_data:
    # 'res' is a 'dict' with keys: "score", "total", "percentage", and "details"
    res = st.session_state.result_data

    st.success(f"### 🎉 Final Score: {res['score']} / {res['total']} ({res['percentage']}%)")

    # Trigger Streamlit's balloon animation for scores of 80% or higher
    if res["percentage"] >= 80:
        st.balloons()

    st.subheader("Detailed Breakdown")

    # 'res["details"]' is a 'list' of 'dict's—one dictionary per question
    for item in res["details"]:
        # 'item["is_correct"]' is a 'bool' returned by the backend grading loop
        if item["is_correct"]:
            st.markdown(f"✅ **Q{item['id']}: {item['question']}**")
            st.write(f"Your answer: `{item['your_answer']}`")
        else:
            st.markdown(f"❌ **Q{item['id']}: {item['question']}**")
            st.write(f"Your answer: `{item['your_answer']}` | Correct answer: `{item['correct_answer']}`")
        st.divider()

    # Clicking 'Retake Quiz' resets session state and reruns the script back to the form
    if st.button("Retake Quiz"):
        restart_quiz()
        st.rerun()