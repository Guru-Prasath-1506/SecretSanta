🎅 Secret Santa Generator
📌 Overview
This is a Secret Santa assignment generator built using Flask and Python. It ensures fair assignments while preventing participants from being assigned to themselves or previous matches. The application supports file uploads, generates a downloadable CSV, and maintains assignment history.

🛠 Features
✅ Upload employee list via CSV
✅ Generate randomized Secret Santa pairs
✅ Prevent past assignments from repeating
✅ View assignments in a web-based Flask UI
✅ Download assignments as a CSV file
✅ Logs errors and maintains data consistency
✅ Fully tested with pytest

🚀 Installation
1) Clone the Repository
git clone https://github.com/Guru-Prasath-1506/SecretSanta.git

2) Install Dependencies
pip install -r requirements.txt

3) Run the Application
python app.py

The app will start on http://127.0.0.1:5000/

🧪 Running Tests
This project includes unit tests using pytest. To run tests:
pytest

📁 Project Structure
SecretSanta/
│── app.py                   # Main Flask application
│── templates/
│   └── index.html            # Frontend UI
│── tests/                    # Unit tests
│── data/
│   ├── employees.csv         # Employee data
│   ├── previous_assignment_history.csv  # Past Secret Santa records
│   ├── new_secret_santa.csv  # Current year's assignments
│── requirements.txt          # Python dependencies
│── README.md                 # Documentation
│── .gitignore                # Ignore unnecessary files

🔥 Future Enhancements
✅ Add email notifications to send assignments
✅ Support multiple years' history tracking
✅ Allow manual corrections before finalizing assignments
✅ UI enhancements for better user experience

