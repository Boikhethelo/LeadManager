"""
main.py

The main entry point for the Lead Manager application.
Assembles all components (repository, controller, validator, presenter)
and runs the interactive command-line interface loop.
"""

from database.csv_repository import CsvLeadRepository, LeadFileHandler, LeadConfig
from models.cli_commands import Controller, CLIConfig
from models.commands import Commands
from models.validator import Validator
from models.presenter import Presenter
from services.lead_scoring import LeadScoringService

class App:
    """Initializes and runs the Lead Manager application.

    This class acts as the central composition root, wiring together the
    data access layer, business logic, validation, and presentation layers
    before starting the main terminal application loop.
    """

    def __init__(self):
        # 1. Initialize the Data Access Layer (Repository)
        handler = LeadFileHandler()
        config = LeadConfig()
        repository = CsvLeadRepository(handler, config)

        # 2. Initialize the Presentation and Validation Layers
        self.validator = Validator()
        self.presenter = Presenter()

        display = self.presenter.display

        scoring_services = LeadScoringService("API KEY")
        app_commands = Commands(repository, scoring_services )

        # 3. Initialize the Controller with injected dependencies
        self.controller = Controller(CLIConfig(), app_commands , display)

    def main(self) -> None:
        """Starts the main interactive application loop.

        Continuously prompts the user for terminal input, handles top-level
        commands like 'help' and 'exit', and routes all valid operational
        commands through the application controller.
        """
        print("Welcome to Lead Manager. \nThis is a fast CRM designed to manage high quality B2B leads.")

        run = True

        while run:
            user_input = input("\nEnter command: ")

            # Handle top-level app commands directly
            if user_input.strip() == "help":
                self.presenter.print_help()
            elif user_input.strip() in ("exit", "quit"):
                run = False
            else:
                # Pass operational commands to the validator and controller
                command = self.validator.validate_command(user_input)
                if command is not None:
                    self.controller.run(command)


if __name__ == "__main__":
    app = App()
    app.main()