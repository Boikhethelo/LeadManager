import argparse
from models import commands

class CLIConfig:
    def __init__(self):

        self.parser = argparse.ArgumentParser(description="Lead Manager")
        self.subparsers = self.parser.add_subparsers(dest="command" , required=True)
        self.search_parser()
        self.delete_parser()
        self.modify_parser()
        self.add_lead_parser()

    
    def search_parser(self):
            search_parser = self.subparsers.add_parser("search")
            search_parser.add_argument("name_number" , help = "None")
            search_parser.add_argument("key" , choices=["company" , "contacts" , "interactions" , "id"])
            
    def delete_parser(self):
        delete_parser = self.subparsers.add_parser("delete")
        delete_parser.add_argument("id" , help = "The id of the lead")

    def modify_parser(self):
        modify_parser = self.subparsers.add_parser("modify")
        modify_parser.add_argument("id" , help=None)
        modify_parser.add_argument("category", help=None)
        modify_parser.add_argument("key" , help=None)
        modify_parser.add_argument("change" , help=None)

    def add_lead_parser(self):
        add_lead_parser = self.subparsers.add_parser("new")



class SearchHandler:
    def __init__(self, commands: commands.Commands , display):
        self.commands = commands
        self.display = display

    def handle(self, args: argparse.Namespace) -> None:
        result = self.commands.search(args.name_number, args.key)
        self.display(result)


class DeleteHandler:
    def __init__(self,commands: commands.Commands):
        self.commands = commands

    def handle(self, args: argparse.Namespace) -> None:
        self.commands.delete(args.id)

class ModifyHandler:
    def __init__(self,commands:commands.Commands):
        self.commands = commands

    def handle(self, args: argparse.Namespace):
        self.commands.modify(args.id , args.category, args.key , args.change)


class AddLeadHandler:
    def __init__(self,commands:commands.Commands , display):
        self.commands = commands
        self.display = display

    def handle(self , args):
       result =  self.commands.add_new_lead()
       self.display(result)


class Controller:
    def __init__(self, config:CLIConfig, commands: commands.Commands , display):
        self.parser = config.parser
        self.display = display
        self.handlers = {"search" : SearchHandler(commands , display),
                         "delete" : DeleteHandler(commands),
                         "modify" : ModifyHandler(commands),
                         "new" : AddLeadHandler(commands , display)}
        
    

    def run(self,input:list[str]) -> None:
    
         try:
            args = self.parser.parse_args(input)
            handler = self.handlers.get(args.command)

            if handler:
                handler.handle(args)
         except SystemExit:
             print("Invalid arguments. Type 'help' for usage. ")
        
    

