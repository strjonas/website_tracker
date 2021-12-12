from threading import Thread
from tracker import Tracker
import time
import send_email
import sys

running = True
active = False

threads = []
trackers = []
defaultEmail = ""



W  = '\033[0m'  # white (normal)
R  = '\033[31m' # red
G  = '\033[32m' # green
O  = '\033[33m' # orange
B  = '\033[34m' # blue
P  = '\033[35m' # purple


def check_working():
    global running

    while running:
        if len(trackers) == 0 and active:
            # email that no trackers are running anymore
            try:
                send_email.send("No trackers are running anymore! Your trackers might have failed! Exiting tracker...", defaultEmail, "No trackers are running anymore!")
            except Exception as e:
                print(e)

            running = False
            print("\nNo trackers are running anymore! Exiting tracker...")
            sys.exit()
        time.sleep(1)



def add_tracker():

    url = input("Enter the URL of the website you want to track: ")
    try:
        interval = int(input("Enter the interval in seconds between the checks: "))
    except:
        print("Invalid interval!")
        return
    email = input("Enter the email address you want to send the changemessages to(blank for default): ")
    message = input("Enter the message you want to send: ")

    if email == "":
        email = defaultEmail

    # takes parameters: url, interval, email, message
    tracker = Tracker(url, interval, email, message, remove_cb)
    
    # run the tracker in a separate thread
    t = Thread(target=tracker.run)
    t.start()

    # add the tracker to the list of trackers
    trackers.append(tracker)

    # add the thread to the list of threads
    threads.append(t)

    print(f"\nTracker for {url} started!")

def remove_tracker():
    url = input("Enter the URL of the website you want to stop tracking: ")
    for tracker in trackers:
        if tracker.url == url:
            tracker.stop()
            trackers.remove(tracker)
            print(f"Tracker for {url} stopped!")
            break
    else:
        print("\nThe website you entered is not being tracked.\n")

def print_log():
    try:
        with open("app.log", "r") as f:
            print(f.read())
    except FileNotFoundError:
        print("No log file found!")

def print_welcome():
    print("")
    print("===========================")
    print("")
    print(f"Welcome to the {B}URL Tracker{W}!")
    print(f"This program will {B}track the changes{W} of a website and send you an email when the changes are detected.")
    print("")
    print("===========================")

def print_help():
    print("")
    print(f"To {R}start{W} tracking a website, enter {G}'add'{W}.")
    print(f"To {R}stop{W} tracking a website, enter {G}'remove'{W}.")
    print(f"To {R}exit{W} the program, enter {G}'exit'{W}.")
    print(f"To see a list of all tracked websites, enter {G}'list'{W}.")
    print(f"To see the log, enter {G}'log'{W}.")
    print(f"To see this help again, enter {G}'help'{W}.")

def remove_cb(url):
    global active

    active = True


    for tracker in trackers:
        if tracker.url == url:
            trackers.remove(tracker)



def main():
    global defaultEmail

    print_welcome()
    defaultEmail = input("Enter the default email address you want to send the changemessages to: ")
    print("")
    print_help()

    is_working_tracker = Thread(target=check_working, daemon=True)
    is_working_tracker.start()

    while running:
        command = input("\nEnter a command: ")

        if command == "exit":
            for tracker in trackers:
                tracker.stop()
            for thread in threads:
                thread.join()
            break

        elif "add" in command:
            add_tracker()

        elif command == "list":
            print("Currently tracking:\n")
            for tracker in trackers:
                print(tracker.url)

        elif command == "help":
            print_help()

        elif "remove" in command:
            remove_tracker()

        elif "log" in command:
            print_log()
            
        else:
            print("Invalid command!")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("")
        print("Exiting...")