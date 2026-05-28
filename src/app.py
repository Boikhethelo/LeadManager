
from database.csv_repository import CsvLeadRepository, LeadFileHandler, LeadConfig
from models.cli_commands import Controller, CLIConfig
from models.commands import Commands


class App:
    def __init__(self):
        handler  = LeadFileHandler()
        config = LeadConfig()
        repository = CsvLeadRepository(handler , config)

        self.VALID_COMMANDS = {"search", "delete", "modify", "new", "exit", "quit"}

        self.controller = Controller(CLIConfig() , Commands(repository) , self.display)


    def main(self):

        print("Welcome to Lead Manager. \nThis is a fast CRM designed to manage high quilty B2B leads.")

        run = True

        while run:

            user_input = input("\nEnter command: ")

            if user_input.strip() == "help":
                self.print_help()
            elif user_input.strip() == "exit" or user_input == "quit":
                run = False
            elif self.validate_command(user_input):
                self.controller.run(user_input)
            else:
                print("Sorry , did not understand: " + user_input + "\nEnter 'help' for valid commands")



    def validate_command(self, input: str) -> bool:
        command = input.strip().split()[0] if input.strip() else ""
        return command in self.VALID_COMMANDS

    def print_help(self) -> None:

        print("""
        Commands:
          search <value> id                          - Find all records by ID
          search <value> contacts|company            - Search by field value
          new                                        - Create a blank lead
          modify <id> <category> <field> <value>     - Update a field
          delete <id>                                - Remove a lead by ID
          help                                       - Show this message
          exit / quit                                - Close the app
            """)

    def display(self, result: dict) -> None:
        if not result:
            print("No results found.")
            return
        for category, rows in result.items():
            if rows:
                print(f"\n── {category.upper()} ──")
                for row in rows:
                    for k, v in row.items():
                        print(f"  {k}: {v or '—'}")


if __name__ == "__main__":
    app = App()
    app.main()

