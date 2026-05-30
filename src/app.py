from posixpath import join

from database.csv_repository import CsvLeadRepository, LeadFileHandler, LeadConfig
from models.cli_commands import Controller, CLIConfig
from models.commands import Commands


class App:
    def __init__(self):
        handler  = LeadFileHandler()
        config = LeadConfig()
        repository = CsvLeadRepository(handler , config)

        self.VALID_COMMANDS = {"search", "delete", "modify", "new", "exit", "quit"}
        self.VALID_KEYS = {"company", "contacts", "interactions", "id"}

        self.controller = Controller(CLIConfig() , Commands(repository) , self.display)


    def main(self):

        print("Welcome to Lead Manager. \nThis is a fast CRM designed to manage high quilty B2B leads.")

        run = True

        while run:

            user_input = input("\nEnter command: ")

            if user_input.strip() == "help":
                self.print_help()
            elif user_input.strip() in ("exit" , "quit"):
                run = False
            else:
                command = self.validate_command(user_input)
                if command is not None:
                    self.controller.run(command)



    def validate_command(self, input: str) -> list[str] | None:

        parts = input.strip().split()

        if not parts:
            return None

        command = parts[0]

        if command not in self.VALID_COMMANDS:
            print(f"Unknown command: '{command}'. Enter 'help' for valid commands.")
            return None



        if command  == "search":
            return self.parse_search(parts)
        elif command == "modify":
            return self.parse_modify(parts)
        else:
            return parts


    def parse_search(self, parts: list[str]) -> list[str] | None :
        # Need a <command> <term> <key> structure
        if len(parts) < 3:
            print(f"'{command}' requires a search term and a category.")
            print(f"  Example: search Acme Corp company")
            return None


        key = parts[-1]

        if key not in self.VALID_KEYS:
            print(f"Unknown category: '{key}'. Valid: {', '.join(sorted(self.VALID_KEYS))}")
            return None

        # joins middle tokens, preserving spaces in names
        search_term = " ".join(parts[1:-1])


        return ["search" , search_term , key]

    def parse_modify(self, parts: list[str]) -> list[str] | None:
        #expects: modify <id> <category> <field> <value>
        if len(parts) < 5 :
            print("'modify' requires: modify <id> <category> <field> <value>")
            print("  Example: modify 1 leads Status Closed Won")
            return None

        lead_id = parts[1]
        category = parts[2]
        field = parts[3]
        change = " ".join(parts[4:])  # same multi-word fix as search
        return ["modify", lead_id, category, field, change]



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

    def display(self, results: list[dict]) -> None:
        if not results:
            print("No results found.")
            return
        for result in results:
            print("\n-RESULT-")

            for category, rows in result.items():
                if rows:
                    print(f"\n── {category.upper()} ──")
                    for row in rows:
                        for k, v in row.items():
                            print(f"  {k}: {v or '—'}")


if __name__ == "__main__":
    app = App()
    app.main()

