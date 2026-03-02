🚀 Python Lead Manager (CRM)
A lightweight, local Relationship Management tool designed for sales professionals to track prospects from initial contact to closing. This project demonstrates CRUD operations, relational database management, and automated lead scoring.

📌 Key Features
Lead Categorization: Categorize prospects as Cold, Warm, or Hot based on custom interaction triggers.

Relational Data: Tracks Companies, Key Contacts, and Products in a linked SQLite database.

Activity Logs: Keep a historical record of every call, email, and meeting.

Automated Reminders: Built-in logic to flag "Hot" leads that haven't been contacted in 3+ days.

Export to CSV: Generate sales reports ready for Excel or Google Sheets.

🛠️ Tech Stack
Language: Python 3.10+

Database: SQLite / SQLAlchemy (ORM)

UI/Framework: Flask (Web) / Click (CLI) (Choose one)

Data Analysis: Pandas

📂 Project Structure
Plaintext

lead-manager/
├── src/
│   ├── database/        # SQLite schema and initialization
│   ├── models/          # Data models (Lead, Company, Contact)
│   ├── services/        # Business logic (Scoring, Emailing)
│   └── app.py           # Application entry point
├── tests/               # Unit tests for core logic
├── requirements.txt     # Dependency list
└── README.md            # You are here!
⚙️ Installation & Setup
Clone the repository:

Bash

git clone https://github.com/yourusername/lead-manager.git
cd lead-manager
Set up a virtual environment:

Bash

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies:

Bash

pip install -r requirements.txt
Initialize the database:

Bash

python src/init_db.py
📈 Future Enhancements
[ ] Integration with LinkedIn API for contact enrichment.

[ ] Dashboard visualization using Matplotlib or Plotly.

[ ] Multi-user authentication for sales teams.

📄 License
Distributed under the MIT License. See LICENSE for more information.