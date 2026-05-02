from database.csv_repository import CsvLeadRepository, LeadFileHandler, LeadConfig
from models.cli_commands import Controller, CLIConfig
from models.commands import Commands


class App:
    def __init__(self):
        handler  = LeadFileHandler()
        config = LeadConfig()
        repository = CsvLeadRepository(handler , config)

        self.controller = Controller(CLIConfig() , Commands(repository))

    def main(self):

        test = "search 1 id"

        self.controller.run(test)

if __name__ == "__main__":
    app = App()
    app.main()

