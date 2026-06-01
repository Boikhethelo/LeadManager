
class Validator:
    def __init__(self):
        self.VALID_COMMANDS = {"search", "delete", "modify", "new", "exit", "quit"}
        self.VALID_KEYS = {"company", "contacts", "interactions", "id"}


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
            print(f"'{parts[0]}' requires a search term and a category.")
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
