from selenium import webdriver
from selenium.webdriver.edge.options import Options
import argparse
import os
import sys
from getpass import getpass

from search import search
from quest import quest


def display_welcome():
    print("\n" + "=" * 50)
    print("EDGE AUTOMATOR TOOL".center(50))
    print("=" * 50)
    print("\nChoose your mode:\n")
    print("1. Search Mode - Perform automated searches")
    print("2. Quest Mode - Complete quests and activities")
    print("3. Exit\n")


def get_user_choice():
    while True:
        try:
            choice = int(input("Enter your choice (1-3): "))
            if 1 <= choice <= 3:
                return choice
            print("Please enter a number between 1 and 3")
        except ValueError:
            print("Invalid input. Please enter a number.")


def get_device_preference():
    print("\nDevice Options:")
    print("1. Desktop Mode (default)")
    print("2. Phone Mode (iPhone 10)")
    choice = input("Choose device (1-2, default 1): ").strip()
    return choice == '2'


def main():
    # Parse command line arguments for non-interactive use
    parser = argparse.ArgumentParser(
        description='Edge Automator Tool - Perform automated browser tasks',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('--mode', choices=['search', 'quest'],
                        help='Run in specific mode:\n'
                             'search - Perform automated searches\n'
                             'quest - Complete quests and activities')
    parser.add_argument('--phone', action='store_true',
                        help='Run in phone mode (iPhone 10)')
    parser.add_argument('--interactive', action='store_true',
                        help='Launch in interactive mode to choose options')
    args = parser.parse_args()

    # Interactive mode if specified or no arguments provided
    if args.interactive or (not args.mode and not args.phone):
        display_welcome()
        choice = get_user_choice()

        if choice == 3:
            print("Exiting...")
            sys.exit(0)

        is_phone = get_device_preference()
        mode = 'search' if choice == 1 else 'quest'
    else:
        # Non-interactive mode using command line args
        mode = args.mode or 'quest'  # default to quest if not specified
        is_phone = args.phone or os.environ.get('EDGE_AUTOMATOR_PHONE', '').lower() in ('true', '1', 'yes')

    # Display configuration
    print("\n" + "-" * 50)
    print(f"Starting in {'Phone' if is_phone else 'Desktop'} mode")
    print(f"Running: {mode.capitalize()} Mode")
    print("-" * 50 + "\n")

    # Run the selected mode
    if mode == 'quest':
        quest(isPhone=is_phone)
    else:
        search(isPhone=is_phone)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        sys.exit(1)