import argparse
from models import commands

class CLIConfig:
    def __init__(self):

        self.parser = argparse.ArgumentParser(description="Lead Manager")
        self.subparsers = self.parser.add_subparsers(dest="command" , required=True)
        self.search_parser()

    
    def search_parser(self):
            search_parser = self.subparsers.add_parser("search")
            search_parser.add_argument("name_number" , help = "None")
            search_parser.add_argument("key" , choices=["company" , "contacts" , "interactions" , "id"])
            


class SearchHandler:
    def __init__(self, commands: commands.Commands):
        self.commands = commands

    def handle(self, args: argparse.Namespace) -> None:
        self.commands.search(args.name_number, args.key)
        

class Controller:
    def __init__(self, config:CLIConfig, commands: commands.Commands):
        self.parser = config.parser
        self.handlers = {"search" : SearchHandler(commands)}
        
    

    def run(self,input:str) -> None:
    
        # try:
            args = self.parser.parse_args(input.split())
            handler = self.handlers.get(args.command)

            if handler:
                handler.handle(args)
        # except Exception as e:
        #     print(f"Error:{e}")
        
    

