from database.csv_repository import CsvLeadRepository, LeadFileHandler, LeadConfig
from models.cli_commands import Controller, CLIConfig
from models.commands import Commands
from models.validator import Validator
from models.presenter import Presenter


class App:
    def __init__(self):
        handler  = LeadFileHandler()
        config = LeadConfig()
        repository = CsvLeadRepository(handler , config)

        self.validator = Validator()
        self.presenter = Presenter()
        self.controller = Controller(CLIConfig() , Commands(repository) , self.presenter.display)


    def main(self):

        print("Welcome to Lead Manager. \nThis is a fast CRM designed to manage high quilty B2B leads.")

        run = True

        while run:

            user_input = input("\nEnter command: ")

            if user_input.strip() == "help":
                self.presenter.print_help()
            elif user_input.strip() in ("exit" , "quit"):
                run = False
            else:
                command = self.validator.validate_command(user_input)
                if command is not None:
                    self.controller.run(command)





if __name__ == "__main__":
    app = App()
    app.main()

