import streamlit as st

# ==============================================================================
# STUDENT GRADE MANAGER (PURE PYTHON + STREAMLIT)
# Purpose: Store student marks, calculate letter grades, handle bad user input
#          safely, and display a clean summary report in a web browser.
# ==============================================================================


# ------------------------------------------------------------------------------
# 1. GRADE CALCULATION LOGIC
# Takes a numeric mark (0-100) and returns the matching letter grade.
# We check from highest to lowest so boundary numbers like 90 or 80 work cleanly.
# ------------------------------------------------------------------------------
def calculate_grade(mark: float) -> str:
    if mark >= 90:
        return "A"
    elif mark >= 80:
        return "B"
    elif mark >= 70:
        return "C"
    elif mark >= 60:
        return "D"
    else:
        return "E"


# ------------------------------------------------------------------------------
# 2. INPUT VALIDATION: STUDENT NAME & MARK
# Checks both inputs once when the user clicks "Add Student".
# Rejects empty names, numbers/symbols in names, and invalid marks.
# Returns 3 values: (is_valid: bool, name_or_error_msg: str, valid_mark: float)
# ------------------------------------------------------------------------------
def validate_inputs(raw_name: str, raw_mark: str) -> tuple[bool, str, float | None]:
    # .strip() removes extra spaces from the start and end of what they typed
    name = raw_name.strip()

    # Stop and return an error message if the name is blank
    if not name:
        return False, "Error: Name cannot be empty. Please try again.", None

    # Check that every character in the name is either a letter (A-Z, a-z) or a space.
    # This blocks integers like "123", mixed text like "Priya123", or symbols like "@#$".
    if not all(char.isalpha() or char.isspace() for char in name):
        return False, "Error: Name must contain only letters and spaces (no numbers or symbols).", None

    # Clean up extra spaces around the mark input
    raw_mark_clean = raw_mark.strip()

    # Try converting the text into a decimal number (float).
    # If the user typed letters like "abc", Python jumps to 'except ValueError'.
    try:
        mark = float(raw_mark_clean)
    except ValueError:
        return False, f"Error: '{raw_mark_clean}' is not a valid number. Please enter digits.", None

    # Check if the number falls inside the allowed 0 to 100 range
    if not (0 <= mark <= 100):
        return False, "Error: Mark must be between 0 and 100 inclusive.", None

    # Everything passed! Return True along with the cleaned name and numeric mark
    return True, name, mark


# ------------------------------------------------------------------------------
# 3. MAIN APPLICATION & WEB INTERFACE
# Sets up the browser page, stores student records across button clicks, and
# renders both the input form and the results dashboard.
# ------------------------------------------------------------------------------
def main() -> None:
    # Configure the browser tab title, icon, and page width
    st.set_page_config(page_title="Student Grade Manager", page_icon="🎓", layout="centered")

    # Display the main heading at the top of the web page
    st.title("🎓 Student Grade Manager")

    # st.session_state acts like browser memory so our 'students' list is not
    # wiped out every time Streamlit reruns the script on a button click.
    if "students" not in st.session_state:
        st.session_state.students = []

    # --------------------------------------------------------------------------
    # SECTION A: ADDING A STUDENT RECORD (Replaces Terminal Menu Option 1)
    # --------------------------------------------------------------------------
    st.subheader("Add a Student")

    # st.form groups inputs together so the page only updates when the submit
    # button is clicked. 'clear_on_submit=True' empties the boxes afterward.
    with st.form("add_student_form", clear_on_submit=True):
        # Create 2 side-by-side columns so Name and Mark sit next to each other
        col1, col2 = st.columns(2)

        with col1:
            raw_name = st.text_input("Student Name", placeholder="e.g., Priya")
        with col2:
            # Using text_input lets our custom validation catch letters like "abc"
            # or out-of-range numbers like 105 just like the original terminal app
            raw_mark = st.text_input("Mark (0 - 100)", placeholder="e.g., 85.5")

        # Create the submit button inside the form
        submitted = st.form_submit_button("Add Student", use_container_width=True)

        # This block runs only when the user clicks "Add Student"
        if submitted:
            # Run our validation function on both inputs
            is_valid, result_or_error, mark = validate_inputs(raw_name, raw_mark)

            if not is_valid:
                # Show a red error banner if validation failed
                st.error(result_or_error)
            else:
                # Unpack the valid name and calculate the letter grade
                name = result_or_error
                grade = calculate_grade(mark)

                # Store each student as a dictionary inside our session_state list.
                # Using a list of dictionaries ensures two students named "Priya"
                # won't overwrite each other's data.
                st.session_state.students.append({
                    "name": name,
                    "mark": mark,
                    "grade": grade,
                })

                # Show a green confirmation banner
                st.success(f"Added: **{name}** | Mark: **{mark:g}** | Grade: **{grade}**")

    # Draw a horizontal divider line between the form and the results table
    st.divider()

    # --------------------------------------------------------------------------
    # SECTION B: DISPLAYING RESULTS & CLASS STATISTICS (No Pandas Required!)
    # --------------------------------------------------------------------------
    st.subheader("Results & Class Statistics")

    # Grab the current list of students from memory
    students = st.session_state.students

    # Stop early if no students have been added yet (avoids dividing by zero later)
    if not students:
        st.info("No student records found yet. Add some students first!")
    else:
        # Build a clean list of dictionaries for display using pure Python.
        # Dictionary keys automatically become the table's column headers!
        table_rows = []
        for index, student in enumerate(students, start=1):
            table_rows.append({
                "No.": index,
                "Student Name": student["name"],
                "Mark": f"{student['mark']:.1f}",  # Format to 1 decimal place
                "Grade": student["grade"],
            })

        # Render the list of dictionaries directly as a clean static table
        st.table(table_rows)

        # Extract all marks into a simple list to calculate class stats easily
        marks = [s["mark"] for s in students]
        average = sum(marks) / len(marks)
        highest = max(marks)
        lowest = min(marks)

        # Create 4 equal columns to display summary stat cards side-by-side
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Students", len(students))
        m2.metric("Class Average", f"{average:.2f}")
        m3.metric("Highest Mark", f"{highest:.1f}")
        m4.metric("Lowest Mark", f"{lowest:.1f}")

        # Add a button to wipe the list and start fresh
        if st.button("Clear All Records"):
            st.session_state.students = []
            # Immediately refresh the page so the cleared state shows right away
            st.rerun()


# ------------------------------------------------------------------------------
# 4. PROGRAM ENTRY POINT
# Ensures main() runs only when this file is executed directly.
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
