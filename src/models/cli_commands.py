import argparse
import commands

class Config:
    def __init__(self , commands:commands):

        self.parser = argparse.ArgumentParser(description="Lead Manager")
        self.subparsers = self.parser.add_subparsers(dest="command" , required=True)

        search_parser = self.subparsers.add_parser("search")
        search_parser.add_argument("key" , help = "None")
        search_parser.set_defaults(func=commands.search)

class Controller:
    def __init__(self, config:Config):
        self.parser =config.parser
        
    

    def run(self,input:str) -> argparse:
        try:
            args = self.parser.parse_args(input.split())
            return args.func(args)
        except Exception as e:
            print("Error running command")
            return None

