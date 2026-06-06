# AI-Powered Lead Manager CRM

A fast, text-based Customer Relationship Management (CRM) system designed for managing high-quality B2B leads. Built with Python, this application features a decoupled MVC-style architecture, local CSV storage, and integrates Google's Gemini 2.0 AI for automated lead scoring.

## Features
* **Interactive CLI:** Validated, robust command-line interface for rapid data entry and retrieval.
* **AI Lead Scoring:** Evaluates leads as Hot, Warm, or Cold based on dynamic data via the Gemini API.
* **Automated Reminders:** Tracks due and overdue follow-ups to maintain engagement.
* **Data Portability:** Export your entire CRM database to standardized Excel (`.xlsx`) or CSV formats.
* **Local Storage:** No external database required; data is seamlessly managed in local CSV files.

## Architecture

This project is built using strict object-oriented principles, utilizing Dependency Injection and a clean separation of concerns.

## How To Run

Step 1 install dependencies: 
pip3 install -r requirements.txt

Step 2: Configure API Keys:
Create a .env file in the root directory and add your Gemini API key for the AI scoring feature:

Code snippet
GEMINI_API_KEY=your_api_key_here

Step 3:
Run the application 

## Usage Examples

Create a new lead: new

Update lead status: modify A1B2 leads Status Warm

Search by company: search TechCorp company

Run AI scoring: score A1B2

Check follow-ups: due today or due late

Export data: export q1_report excel

### Class Diagram

```mermaid
classDiagram
    class App {
        +main()
    }
    class Controller {
        +run(user_input)
    }
    class Validator {
        +validate_command(raw_input)
    }
    class Presenter {
        +display(results)
    }
    class Commands {
        +search()
        +add_new_lead()
        +modify()
        +delete()
        +score_lead()
    }
    class LeadRepository {
        <<interface>>
        +get_by_id()
        +save()
    }
    class CsvLeadRepository {
        -data: dict
        +ensure_loaded()
    }
    class LeadScoringService {
        +score_lead()
    }
    
    App --> Controller
    App --> Validator
    App --> Presenter
    Controller --> Commands
    Commands --> LeadRepository
    Commands --> LeadScoringService
    LeadRepository <|-- CsvLeadRepository