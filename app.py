from flask import Flask, request, render_template, send_file
import logging
import pandas as pd
import random
import os

app = Flask(__name__)

# File paths
EMPLOYEES_FILE = "employees.csv"
LAST_YEAR_FILE = "previous_assignment_history.csv"  # Stores all previous years' assignments
OUTPUT_FILE = "new_secret_santa.csv"

# Configure logging
logging.basicConfig(level=logging.INFO)


class EmployeeManager:
    """Handles employee data loading and validation."""

    @staticmethod
    def load_employees(file_path):
        """Loads employees from a CSV file."""
        try:
            df = pd.read_csv(file_path)
            return df.to_dict(orient="records")
        except FileNotFoundError:
            logging.error(f"Error: {file_path} not found.")
            return None


class FileManager:
    """Handles file operations for reading/writing assignments."""

    @staticmethod
    def load_previous_assignments(file_path):
        """Loads all previous years' assignments from CSV file."""
        previous_assignments = {}

        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                for _, row in df.iterrows():
                    giver_email = row["Employee_EmailID"]
                    receiver_email = row["Secret_Child_EmailID"]

                    if giver_email not in previous_assignments:
                        previous_assignments[giver_email] = set()

                    previous_assignments[giver_email].add(receiver_email)

            except Exception as e:
                logging.error(f"Error loading previous assignments: {e}")

        return previous_assignments

    @staticmethod
    def save_assignments(file_path, assignments, append=True):
        """Saves assignments to a CSV file. If append=True, it appends instead of overwriting."""

        df_new = pd.DataFrame(assignments)

        # If file exists and append is True, merge it with existing data
        if append and os.path.exists(file_path):
            df_existing = pd.read_csv(file_path)
            df_combined = pd.concat([df_existing, df_new]).drop_duplicates()
        else:
            df_combined = df_new

        df_combined.to_csv(file_path, index=False)


class AssignmentManager:
    """Handles Secret Santa assignment logic."""

    def __init__(self, employees, previous_assignments):
        self.employees = employees
        self.previous_assignments = previous_assignments
        self.assignments = {}

    def assign_secret_santa(self):
        """Assign secret children ensuring constraints are met."""
        if not self.employees:
            logging.error("Error: No employees loaded.")
            return False

        employees_list = self.employees[:]
        random.shuffle(employees_list)
        valid_assignment = False
        attempts = 0

        while not valid_assignment and attempts < 100:
            attempts += 1
            random.shuffle(employees_list)
            assignments = {}

            for giver in employees_list:
                giver_email = giver["Employee_EmailID"]

                possible_recipients = [
                    e for e in employees_list
                    if e["Employee_EmailID"] != giver_email  # Cannot be their own Secret Santa
                       and e["Employee_EmailID"] not in self.previous_assignments.get(giver_email,
                                                                                      set())  # Avoid all past matches
                       and e["Employee_EmailID"] not in assignments.values()  # Ensure uniqueness
                ]

                if not possible_recipients:
                    break  # Restart if no valid recipient found

                recipient = random.choice(possible_recipients)
                assignments[giver_email] = recipient["Employee_EmailID"]

            if len(assignments) == len(self.employees):
                valid_assignment = True

        if not valid_assignment:
            logging.error("Error: Could not generate a valid Secret Santa assignment.")
            return False

        self.assignments = assignments
        return True

    def format_assignments(self):
        """Formats assignments into a structured list."""
        formatted_data = []
        for giver_email, recipient_email in self.assignments.items():
            giver = next(emp for emp in self.employees if emp["Employee_EmailID"] == giver_email)
            recipient = next(emp for emp in self.employees if emp["Employee_EmailID"] == recipient_email)

            row = {
                "Employee_Name": giver["Employee_Name"],
                "Employee_EmailID": giver["Employee_EmailID"],
                "Secret_Child_Name": recipient["Employee_Name"],
                "Secret_Child_EmailID": recipient["Employee_EmailID"]
            }

            formatted_data.append(row)
        return formatted_data


@app.route("/", methods=["GET", "POST"])
def index():
    """Render the upload page and process file submission."""
    assignments = None

    if request.method == "POST":
        if "file" not in request.files:
            return render_template("index.html", error="No file uploaded!")

        file = request.files["file"]
        if file.filename == "":
            return render_template("index.html", error="No selected file!")

        file.save(EMPLOYEES_FILE)

        employees = EmployeeManager.load_employees(EMPLOYEES_FILE)
        if not employees:
            return render_template("index.html", error="Failed to load employee data!")

        previous_assignments = FileManager.load_previous_assignments(LAST_YEAR_FILE)

        game = AssignmentManager(employees, previous_assignments)

        if game.assign_secret_santa():
            formatted_assignments = game.format_assignments()

            # Save the current year's assignments to a new file
            FileManager.save_assignments(OUTPUT_FILE, formatted_assignments, append=False)

            # Append to the history file instead of overwriting it
            FileManager.save_assignments(LAST_YEAR_FILE, formatted_assignments, append=True)

            return render_template("index.html", success=True, assignments=formatted_assignments, file_available=True)
        else:
            return render_template("index.html", error="Failed to assign Secret Santa!")

    return render_template("index.html")


@app.route("/download")
def download():
    """Download the generated CSV file."""
    return send_file(OUTPUT_FILE, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
