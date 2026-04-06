import argparse
import commands

class Config:
    def __init__(self , commands:commands):

        self.parser = argparse.ArgumentParser(description="Lead Manager")
        self.subparsers = self.parser.add_subparsers(dest="command" , required=True)
        self.searh_parser()

    
    def searh_parser(self):
            search_parser = self.subparsers.add_parser("search")
            search_parser.add_argument("name_number" , help = "None")
            search_parser.add_argument("key" , choices=["company" , "contacts" , "interactions" , "leads"])
            


class SearchHandler:
    def handle(self, args: argparse.Namespace) -> None:
        commands.Commands.search(args.name_number, args.keys)
        




class Controller:
    def __init__(self, config:Config):
        self.parser =config.parser
        self.handlers = {"search" : SearchHandler()}
        
    

    def run(self,input:str) -> None:
        try:
            args = self.parser.parse_args(input.split())
            handler = self.handlers.get(args.command)
            if handler:
                handler.handle(args)
        except Exception as e:
            print("Error running command")
        
    

