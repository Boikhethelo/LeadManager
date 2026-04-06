from database import creator , manager
from models import cli_commands

class App:
    def __init__(self):
        self.config = creator.LeadConfig()
        self.handler = creator.LeadFileHandler()
        self.lead_manager = manager.LeadManager(self.handler, self.config)


    

    def main(self):

        self.lead_manager.initialize_system()


        test = "search L1 id"
        controller = cli_commands.Controller(cli_commands.Config())

        controller.run(test)



if __name__ == "__main__":
    app = App()
    app.main()

