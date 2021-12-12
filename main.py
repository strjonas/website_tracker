from threading import Thread
from tracker import Tracker
import time
import send_email
import sys
from logging.handlers import RotatingFileHandler
from rich.console import Console
import logging
from dataclasses import dataclass
from prettytable import PrettyTable
import json

console = Console()

@dataclass
class Color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    W  = '\033[0m'  # white (normal)
    R  = '\033[31m' # red
    G  = '\033[32m' # green
    O  = '\033[33m' # orange
    B  = '\033[34m' # blue
    P  = '\033[35m' # purple

color = Color()

def get_logger():
    logger = logging.getLogger('app')
    handler = RotatingFileHandler("app.log", maxBytes=3*1024, backupCount=4)
    formater = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formater)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
class Main:
    def __init__(self):
        self.running = True
        self.active = False
        self.threads = []
        self.trackers = []
        self.defaultEmail = ""

    def check_working(self):
        global running

        while self.running:
            if len(self.trackers) == 0 and self.active:
                # email that no trackers are running anymore
                try:
                    send_email.send("No trackers are running anymore! Your trackers might have failed! Exiting tracker...", self.defaultEmail, "No trackers are running anymore!")
                except Exception as e:
                    print(e)

                self.running = False
                print("\nNo trackers are running anymore! Exiting tracker...")
                sys.exit()
            time.sleep(1)

    def add_tracker(self, url=None):
        if url is None:
            url = input("Enter the URL of the website you want to track: ")
        try:
            interval = int(input("Enter the interval in seconds between the checks: "))
        except:
            print("Invalid interval!")
            return
        email = input("Enter the email address you want to send the changemessages to(blank for default): ")
        message = input("Enter the message you want to send: ")

        if email == "":
            email = self.defaultEmail

        tracker = Tracker(url, interval, email, message, self.remove_cb)
        
        # run the tracker in a separate thread
        t = Thread(target=tracker.run)
        t.start()

        # add the thread to the list of threads
        self.threads.append(t)

        print(f"\nTracker for {url} started!")

        # add the tracker to the list of trackers and save in file
        self.trackers.append(tracker)

        js = []
        for tracker in self.trackers:
            js.append({"url": tracker.url, "interval": tracker.interval, "email": tracker.email, "message": tracker.message})

        with open("trackers.json", "w") as f:
            json.dump(js, f)
    
    def remove_tracker(self):

        print("")

        if len(self.trackers) == 0:
            print("No trackers are running!")
            return

        for i, tracker in enumerate(self.trackers):
            print(f"{i} - {tracker.url}")

        try:
            index = int(input("\nEnter the index of the website you want to remove: "))
        except:
            print("\nInvalid index!")
            return
        
        if index < 0 or index >= len(self.trackers):
            print("\nInvalid index!")
            return

        tracker = self.trackers[index]
        tracker.stop()
        self.trackers.remove(tracker)

        # writing the remaining trackers to the file
        js = []
        for tracker in self.trackers:
            js.append({"url": tracker.url, "interval": tracker.interval, "email": tracker.email, "message": tracker.message})

        with open("trackers.json", "w") as f:
            json.dump(js, f)

        print(f"\nTracker for {tracker.url} stopped!")
    
    def print_log(self):
        try:
            print("")
            log = ""
            try:
                with open("app.log.1", "r") as f:
                    log += f.read()
            except:
                pass
            with open("app.log", "r") as f:
                log += f.read()
            console.log(log)
        except FileNotFoundError:
            print("No log file found!")
    
    def print_welcome(self):
        print("")
        print("===========================")
        print("")
        print(f"Welcome to the {color.B}URL Tracker{color.W}!")
        print(f"This program will {color.B}track the changes{color.W} of a website and send you an email when the changes are detected.")
        print("")
        print("===========================\n")
    
    def print_help(self):
        print("")
        print(f"To {color.R}start{color.W} tracking a website, enter {color.G}'add'{color.W}.")
        print(f"To {color.R}stop{color.W} tracking a website, enter {color.G}'remove'{color.W}.")
        print(f"To {color.R}exit{color.W} the program, enter {color.G}'exit'{color.W}.")
        print(f"To see a list of all tracked websites, enter {color.G}'list'{color.W}.")
        print(f"To see the log, enter {color.G}'log'{color.W}.")
        print(f"To see this help again, enter {color.G}'help'{color.W}.")
    
    def remove_cb(self, url):
        global active

        active = True


        for tracker in self.trackers:
            if tracker.url == url:
                self.trackers.remove(tracker)

                # removing it from the file
                with open("trackers.txt", "w") as f:
                    for t in self.trackers:
                        f.write(f"{t.url};{t.interval};{t.email};{t.message}\n")
                break
   
    def import_trackers(self):
        try:
            urls = ""

            with open("trackers.json", "r") as f:
                js = json.load(f)
                for object in js:

                    urls += object["url"] + "\n"

                    tracker = Tracker(object["url"], object["interval"], object["email"], object["message"], self.remove_cb)
                    self.trackers.append(tracker)

                    t = Thread(target=tracker.run)
                    t.start()
                    self.threads.append(t)

            print(f"\nThe following websites have been importet are being tracked:\n\n{urls}")

        except FileNotFoundError:
            print(f"\n{color.WARNING}No trackers file found!{color.W}\nCreating one...")
            with open("trackers.json", "w") as f:
                json.dump([], f)

    
    def print_list(self):
        # printing list of all trackers with prettytable

        if len(self.trackers) == 0:
            print("\nNo trackers are running!")
            return

        print("")
        print("List of all trackers:")
        print("")
        table = PrettyTable(["URL", "Interval", "Email", "Message"])
        for tracker in self.trackers:
            table.add_row([tracker.url, tracker.interval, tracker.email, tracker.message])
        print(table)

    def run(self):
        self.print_welcome()
        self.defaultEmail = input("Enter the default email address you want to send the changemessages to: ")
        print("")

        # ask if they already tracked and want to import trackers from a file
        while True:
            choice = input("Do you want to import trackers from trackers.txt? (y/n): ")
            if choice == "y":
                self.import_trackers()
                break
            elif choice == "n":
                break
            else:
                print("Invalid input!")


        self.print_help()

        is_working_tracker = Thread(target=self.check_working, daemon=True)
        is_working_tracker.start()

        while self.running:
            print("\n-----------------------------------------------------")
            command = input("\nEnter a command: ")

            if command == "exit":
                for tracker in self.trackers:
                    tracker.stop()
                for thread in self.threads:
                    thread.join()
                sys.exit()

            elif "add" in command:
                command = command.split(" ")
                if len(command) == 1:
                    self.add_tracker()
                else:
                    self.add_tracker(command[1])

            elif command == "list":
                self.print_list()

            elif command == "help":
                self.print_help()

            elif "remove" in command:
                self.remove_tracker()

            elif "log" in command:
                self.print_log()
            
            else:
                print("\nInvalid command!")


if __name__ == '__main__':
    
    get_logger()

    tracker = None;

    try: 

        tracker = Main()
        tracker.run()

    except KeyboardInterrupt:

        tracker.running = False

        print("")
        print("Exiting...")
        sys.exit()