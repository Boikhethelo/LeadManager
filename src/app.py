from models import cli_commands

class App:
    def __init__(self): 

        self.controller = cli_commands.Controller(cli_commands.Config())

    def main(self):

        test = "search L1 id"

        self.controller.run(test)

if __name__ == "__main__":
    app = App()
    app.main()

