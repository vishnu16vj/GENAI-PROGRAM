# ==============================================================================
# STUDENT GRADE MANAGER
# Purpose: Store student marks, calculate letter grades, handle bad user input
#          safely, and print a clean summary report in the terminal.
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
# 2. INPUT VALIDATION: STUDENT NAME
# Keeps asking until the user enters a real name (not just empty spaces).
# ------------------------------------------------------------------------------
def get_valid_name() -> str:
    while True:
        # .strip() removes extra spaces from the start and end of what they typed
        name = input("Enter student name: ").strip()

        # If the string is not empty, return it and exit the loop
        if name:
            return name

        print("Error: Name cannot be empty. Please try again.")


# ------------------------------------------------------------------------------
# 3. INPUT VALIDATION: STUDENT MARK
# Keeps asking until the user enters a valid number between 0 and 100.
# Prevents crashes when someone types text like "abc" or invalid numbers like 105.
# ------------------------------------------------------------------------------
def get_valid_mark() -> float:
    while True:
        raw_input = input("Enter mark (0 - 100): ").strip()

        # Try converting the text into a decimal number (float).
        # If the user typed letters like "abc", Python jumps to 'except ValueError'.
        try:
            mark = float(raw_input)
        except ValueError:
            print(f"Error: '{raw_input}' is not a valid number. Please enter digits.")
            continue  # Restart the loop and ask again

        # Check if the number falls inside the allowed 0 to 100 range
        if 0 <= mark <= 100:
            return mark
        else:
            print("Error: Mark must be between 0 and 100 inclusive.")


# ------------------------------------------------------------------------------
# 4. ADDING A STUDENT RECORD
# Collects validated name and mark, calculates the grade, and stores everything
# as a dictionary inside our main list.
# ------------------------------------------------------------------------------
def add_student(students: list[dict]) -> None:
    name = get_valid_name()
    mark = get_valid_mark()
    grade = calculate_grade(mark)

    # Append a new dictionary for this student.
    # Using a list of dictionaries ensures two students named "Priya" won't
    # overwrite each other's data.
    students.append({
        "name": name,
        "mark": mark,
        "grade": grade,
    })

    print(f"Added: {name} | Mark: {mark:g} | Grade: {grade}")


# ------------------------------------------------------------------------------
# 5. DISPLAYING RESULTS AND CLASS STATISTICS
# Prints all stored students in a neatly aligned table, followed by the
# class average, highest mark, and lowest mark.
# ------------------------------------------------------------------------------
def show_results(students: list[dict]) -> None:
    # Stop early if no students have been added yet (avoids dividing by zero later)
    if not students:
        print("\nNo student records found yet. Add some students first!")
        return

    # Print the table header using column width formatting (< = left-align, > = right-align)
    print("\n" + "=" * 42)
    print(f"{'No.':<5}{'Student Name':<20}{'Mark':>8}{'Grade':>8}")
    print("-" * 42)

    # Loop through each student in the list, numbering them starting from 1
    for index, student in enumerate(students, start=1):
        print(
            f"{index:<5}"
            f"{student['name']:<20}"
            f"{student['mark']:>8.1f}"
            f"{student['grade']:>8}"
        )

    print("=" * 42)

    # Extract all marks into a simple list to calculate class stats easily
    marks = [s["mark"] for s in students]
    average = sum(marks) / len(marks)
    highest = max(marks)
    lowest = min(marks)

    # Print the summary statistics below the table
    print(f"Total Students : {len(students)}")
    print(f"Class Average  : {average:.2f}")
    print(f"Highest Mark   : {highest:.1f}")
    print(f"Lowest Mark    : {lowest:.1f}")
    print("=" * 42)


# ------------------------------------------------------------------------------
# 6. MAIN MENU LOOP
# Creates the storage list and keeps showing the menu until the user quits.
# ------------------------------------------------------------------------------
def main() -> None:
    # Our main data structure: a list that will hold one dictionary per student
    students: list[dict] = []

    while True:
        print("\n--- Student Grade Manager ---")
        print("1. Add student")
        print("2. Show results")
        print("3. Quit")

        # Read user choice, remove spaces, and convert to lowercase for easy matching
        choice = input("Choose an option (1-3): ").strip().lower()

        if choice in ("1", "add", "a"):
            add_student(students)
        elif choice in ("2", "show", "s"):
            show_results(students)
        elif choice in ("3", "quit", "q", "exit"):
            print("Goodbye!")
            break  # Exit the while loop and end the program
        else:
            print("Invalid option. Please enter 1, 2, or 3.")


# ------------------------------------------------------------------------------
# 7. PROGRAM ENTRY POINT
# Ensures main() runs only when this file is executed directly.
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
