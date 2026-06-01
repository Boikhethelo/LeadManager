
class Presenter:
    def __init__(self):

        self.help = """
            Commands:
                search <value> id                          - Find all records by ID
                search <value> contacts|company            - Search by field value
                new                                        - Create a blank lead
                modify <id> <category> <field> <value>     - Update a field
                delete <id>                                - Remove a lead by ID
                help                                       - Show this message
                exit / quit                                - Close the app
                   """

    def print_help(self):
        print(self.help)


    def display(self, results: list[dict] | str) -> None:

        if not results:
            print("No results found.")
            return



        if isinstance(results, str):
            print(results)
            return

        print("\n-RESULT-")

        for result in results:


            for category, rows in result.items():
                if rows:
                    print(f"\n── {category.upper()} ──")
                    for row in rows:
                        for k, v in row.items():
                            print(f"  {k}: {v or '—'}")












