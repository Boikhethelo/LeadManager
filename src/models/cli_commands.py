import argparse
from models import commands

class Config:
    def __init__(self):

        self.parser = self.parser()
        self.subparsers = self.subparsers()
        self.searh_parser()
    
    def parser(self):
        return argparse.ArgumentParser(description="Lead Manager")
    
    def subparsers(self):
        return self.parser.add_subparsers(dest="command" , required=True)

    
    def searh_parser(self):
            search_parser = self.subparsers.add_parser("search")
            search_parser.add_argument("name_number" , help = "None")
            search_parser.add_argument("key" , choices=["company" , "contacts" , "interactions" , "id"])
            


class SearchHandler:
    def __init__(self):
        self.commands = commands.Commands()

    def handle(self, args: argparse.Namespace) -> None:
        self.commands.search(args.name_number, args.key)
        

class Controller:
    def __init__(self, config:Config):
        self.parser = config.parser
        self.handlers = {"search" : SearchHandler()}
        
    

    def run(self,input:str) -> None:
    
        # try:
            args = self.parser.parse_args(input.split())
            handler = self.handlers.get(args.command)
            if handler:
               
                handler.handle(args)
        # except Exception as e:
        #     print(f"Error:{e}")
        
    

