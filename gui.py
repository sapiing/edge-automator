import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import queue
import sys
import io
import os
import time
from search import search
from quest import quest

# Dark blue theme colors
DARK_BLUE = "#1e2a38"
MEDIUM_BLUE = "#2c3e50"
LIGHT_BLUE = "#3498db"
TEXT_COLOR = "#ecf0f1"
ACCENT_COLOR = "#2ecc71"
BUTTON_COLOR = "#34495e"
HOVER_COLOR = "#4e6d8c"

class RedirectText:
    """Redirect stdout to the console widget"""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.queue = queue.Queue()
        self.update_timer = None

    def write(self, string):
        self.queue.put(string)
        if self.update_timer is None:
            self.update_timer = self.text_widget.after(100, self.update_text)

    def update_text(self):
        try:
            while True:
                text = self.queue.get_nowait()
                self.text_widget.configure(state="normal")
                self.text_widget.insert(tk.END, text)
                self.text_widget.see(tk.END)
                self.text_widget.configure(state="disabled")
                self.queue.task_done()
        except queue.Empty:
            pass
        self.update_timer = None

    def flush(self):
        pass

class EdgeAutomatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Edge Automator")
        self.root.geometry("900x600")
        self.root.configure(bg=DARK_BLUE)

        # Configure style for ttk widgets
        self.style = ttk.Style()
        self.style.theme_use('default')

        # Configure colors for various widget states
        self.style.configure('TFrame', background=DARK_BLUE)
        self.style.configure('TLabel', background=DARK_BLUE, foreground=TEXT_COLOR)
        self.style.configure('TButton', background=BUTTON_COLOR, foreground=TEXT_COLOR)
        self.style.map('TButton', 
                       background=[('active', HOVER_COLOR)],
                       foreground=[('active', TEXT_COLOR)])
        self.style.configure('TRadiobutton', background=DARK_BLUE, foreground=TEXT_COLOR)
        self.style.configure('TCheckbutton', background=DARK_BLUE, foreground=TEXT_COLOR)
        self.style.configure('TProgressbar', background=ACCENT_COLOR)
        self.style.configure('TNotebook', background=DARK_BLUE, foreground=TEXT_COLOR)
        self.style.configure('TNotebook.Tab', background=MEDIUM_BLUE, foreground=TEXT_COLOR, padding=[10, 5])
        self.style.map('TNotebook.Tab',
                       background=[('selected', LIGHT_BLUE)],
                       foreground=[('selected', TEXT_COLOR)])

        # Variables
        self.is_phone = tk.BooleanVar(value=False)
        self.num_searches = tk.IntVar(value=10)
        self.headless_mode = tk.BooleanVar(value=False)
        self.search_running = False
        self.quest_running = False

        # Edge profiles
        self.edge_profiles = self.get_edge_profiles()
        self.profile_vars = {}  # Will store BooleanVars for profile checkboxes

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create tabs
        self.search_tab = ttk.Frame(self.notebook)
        self.quest_tab = ttk.Frame(self.notebook)
        self.console_tab = ttk.Frame(self.notebook)
        self.misc_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.search_tab, text="Search")
        self.notebook.add(self.quest_tab, text="Quest")
        self.notebook.add(self.console_tab, text="Console")
        self.notebook.add(self.misc_tab, text="Misc")

        # Setup tabs
        self.setup_search_tab()
        self.setup_quest_tab()
        self.setup_console_tab()
        self.setup_misc_tab()

        # Redirect stdout to console
        self.redirect = RedirectText(self.console_text)
        sys.stdout = self.redirect

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_search_tab(self):
        # Device selection frame
        device_frame = ttk.LabelFrame(self.search_tab, text="Device Selection")
        device_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Radiobutton(device_frame, text="Desktop", variable=self.is_phone, value=False).pack(side=tk.LEFT, padx=20, pady=10)
        ttk.Radiobutton(device_frame, text="Phone (iPhone 10)", variable=self.is_phone, value=True).pack(side=tk.LEFT, padx=20, pady=10)

        # Search count frame
        search_count_frame = ttk.LabelFrame(self.search_tab, text="Number of Searches")
        search_count_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(search_count_frame, text="How many searches:").pack(side=tk.LEFT, padx=10, pady=10)
        search_count_entry = ttk.Entry(search_count_frame, textvariable=self.num_searches, width=5)
        search_count_entry.pack(side=tk.LEFT, padx=10, pady=10)

        # Profile selection frame
        profile_frame = ttk.LabelFrame(self.search_tab, text="Edge Profiles")
        profile_frame.pack(fill=tk.X, padx=10, pady=10)

        if not self.edge_profiles:
            ttk.Label(profile_frame, text="No Edge profiles found").pack(padx=10, pady=10)
        else:
            # Create a scrollable frame for profiles if there are many
            profile_canvas = tk.Canvas(profile_frame, bg=DARK_BLUE, highlightthickness=0)
            profile_scrollbar = ttk.Scrollbar(profile_frame, orient="vertical", command=profile_canvas.yview)
            profile_scrollable_frame = ttk.Frame(profile_canvas)

            profile_scrollable_frame.bind(
                "<Configure>",
                lambda e: profile_canvas.configure(scrollregion=profile_canvas.bbox("all"))
            )

            profile_canvas.create_window((0, 0), window=profile_scrollable_frame, anchor="nw")
            profile_canvas.configure(yscrollcommand=profile_scrollbar.set)

            profile_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            profile_scrollbar.pack(side="right", fill="y", pady=10)

            # Add checkboxes for each profile
            for profile_name, profile_path in self.edge_profiles.items():
                var = tk.BooleanVar(value=profile_name == "Default")  # Default profile selected by default
                self.profile_vars[profile_name] = var
                ttk.Checkbutton(profile_scrollable_frame, text=profile_name, variable=var).pack(anchor="w", padx=5, pady=2)

        # Progress frame
        progress_frame = ttk.LabelFrame(self.search_tab, text="Progress")
        progress_frame.pack(fill=tk.X, padx=10, pady=10)

        self.search_progress = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.search_progress.pack(fill=tk.X, padx=10, pady=10)

        self.search_status = ttk.Label(progress_frame, text="Ready")
        self.search_status.pack(padx=10, pady=5)

        # Button frame
        button_frame = ttk.Frame(self.search_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        self.start_search_button = ttk.Button(button_frame, text="Start Search", command=self.start_search)
        self.start_search_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.stop_search_button = ttk.Button(button_frame, text="Stop Search", command=self.stop_search, state=tk.DISABLED)
        self.stop_search_button.pack(side=tk.LEFT, padx=10, pady=10)

    def setup_quest_tab(self):
        # Device info
        info_frame = ttk.Frame(self.quest_tab)
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(info_frame, text="Note: Quest mode only works properly on desktop.").pack(padx=10, pady=10)

        # Profile selection frame
        profile_frame = ttk.LabelFrame(self.quest_tab, text="Edge Profiles")
        profile_frame.pack(fill=tk.X, padx=10, pady=10)

        if not self.edge_profiles:
            ttk.Label(profile_frame, text="No Edge profiles found").pack(padx=10, pady=10)
        else:
            # Create a scrollable frame for profiles if there are many
            profile_canvas = tk.Canvas(profile_frame, bg=DARK_BLUE, highlightthickness=0)
            profile_scrollbar = ttk.Scrollbar(profile_frame, orient="vertical", command=profile_canvas.yview)
            profile_scrollable_frame = ttk.Frame(profile_canvas)

            profile_scrollable_frame.bind(
                "<Configure>",
                lambda e: profile_canvas.configure(scrollregion=profile_canvas.bbox("all"))
            )

            profile_canvas.create_window((0, 0), window=profile_scrollable_frame, anchor="nw")
            profile_canvas.configure(yscrollcommand=profile_scrollbar.set)

            profile_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            profile_scrollbar.pack(side="right", fill="y", pady=10)

            # Add checkboxes for each profile (reusing the same BooleanVars from search tab)
            for profile_name, profile_path in self.edge_profiles.items():
                if profile_name not in self.profile_vars:
                    self.profile_vars[profile_name] = tk.BooleanVar(value=profile_name == "Default")
                ttk.Checkbutton(profile_scrollable_frame, text=profile_name, variable=self.profile_vars[profile_name]).pack(anchor="w", padx=5, pady=2)

        # Progress frame
        progress_frame = ttk.LabelFrame(self.quest_tab, text="Progress")
        progress_frame.pack(fill=tk.X, padx=10, pady=10)

        self.quest_progress = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=100, mode='indeterminate')
        self.quest_progress.pack(fill=tk.X, padx=10, pady=10)

        self.quest_status = ttk.Label(progress_frame, text="Ready")
        self.quest_status.pack(padx=10, pady=5)

        # Button frame
        button_frame = ttk.Frame(self.quest_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        self.start_quest_button = ttk.Button(button_frame, text="Start Quest", command=self.start_quest)
        self.start_quest_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.stop_quest_button = ttk.Button(button_frame, text="Stop Quest", command=self.stop_quest, state=tk.DISABLED)
        self.stop_quest_button.pack(side=tk.LEFT, padx=10, pady=10)

    def setup_console_tab(self):
        console_frame = ttk.Frame(self.console_tab)
        console_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create scrolled text widget for console output
        self.console_text = scrolledtext.ScrolledText(console_frame, bg=MEDIUM_BLUE, fg=TEXT_COLOR, wrap=tk.WORD)
        self.console_text.pack(fill=tk.BOTH, expand=True)
        self.console_text.configure(state="disabled")

        # Button to clear console
        clear_button = ttk.Button(console_frame, text="Clear Console", command=self.clear_console)
        clear_button.pack(pady=10)

    def setup_misc_tab(self):
        misc_frame = ttk.LabelFrame(self.misc_tab, text="Options")
        misc_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Checkbutton(misc_frame, text="Headless Mode (No Browser UI)", variable=self.headless_mode).pack(padx=10, pady=10, anchor=tk.W)

        # Add explanation
        explanation = ttk.Label(self.misc_tab, text="Headless mode runs the browser without showing the UI.\n"
                                                   "This can be useful for running in the background.")
        explanation.pack(padx=10, pady=10)

    def start_search(self):
        if self.search_running:
            return

        self.search_running = True
        self.start_search_button.configure(state=tk.DISABLED)
        self.stop_search_button.configure(state=tk.NORMAL)
        self.search_status.configure(text="Running...")
        self.search_progress['value'] = 0

        # Create and start search thread
        self.search_thread = threading.Thread(target=self.run_search)
        self.search_thread.daemon = True
        self.search_thread.start()

    def stop_search(self):
        if not self.search_running:
            return

        print("Stopping search...")
        self.search_running = False
        self.search_status.configure(text="Stopping...")

        # Set the stop event if it exists
        if hasattr(self, 'search_stop_event'):
            self.search_stop_event.set()

    def run_search(self):
        try:
            # Create a custom stdout to capture search output
            original_stdout = sys.stdout
            custom_stdout = io.StringIO()
            sys.stdout = self.redirect

            # Get search parameters
            is_phone = self.is_phone.get()
            num_searches = self.num_searches.get()
            headless = self.headless_mode.get()

            # Create a stop event for cancellation
            import threading
            stop_event = threading.Event()
            self.search_stop_event = stop_event

            # Add headless option if enabled
            if headless:
                from selenium.webdriver.edge.options import Options
                original_Options = Options

                class HeadlessOptions(Options):
                    def __init__(self, *args, **kwargs):
                        super().__init__(*args, **kwargs)
                        self.add_argument("--headless")

                # Monkey patch the Options class
                import search as search_module
                search_module.Options = HeadlessOptions

            # Define progress callback
            def update_progress(value):
                self.root.after(0, lambda: self.search_progress.configure(value=value))

            # Get selected profiles
            selected_profiles = []
            for profile_name, var in self.profile_vars.items():
                if var.get():
                    selected_profiles.append((profile_name, self.edge_profiles[profile_name]))

            if not selected_profiles:
                print("No profiles selected. Please select at least one profile.")
                return

            print(f"Running search on {len(selected_profiles)} selected profiles")

            # Run the search function for each selected profile
            for i, (profile_name, profile_path) in enumerate(selected_profiles):
                if stop_event.is_set():
                    break

                print(f"\nRunning search on profile: {profile_name} ({i+1}/{len(selected_profiles)})")

                # Run the search function with progress updates
                # Fix for issue: when search count is 1, ensure we still process all profiles
                search(
                    isPhone=is_phone,
                    num_searches_input=num_searches,
                    progress_callback=update_progress,
                    stop_event=stop_event,
                    profile_path=profile_path
                )

                # Reset the stop_event if it was set during the search
                # This ensures the next profile will be processed even if there was an issue
                if stop_event.is_set() and i < len(selected_profiles) - 1:
                    print("Resetting stop event to process next profile...")
                    stop_event.clear()

                # Update progress to 100% after each profile
                update_progress(100)

                # Small delay between profiles
                if i < len(selected_profiles) - 1 and not stop_event.is_set():
                    print("Waiting before starting next profile...")
                    time.sleep(3)

            # Restore original Options
            if headless:
                search_module.Options = original_Options

        except Exception as e:
            print(f"Error in search: {e}")
        finally:
            # Reset UI
            self.search_running = False
            self.root.after(0, self.reset_search_ui)
            sys.stdout = original_stdout

    def reset_search_ui(self):
        self.start_search_button.configure(state=tk.NORMAL)
        self.stop_search_button.configure(state=tk.DISABLED)
        self.search_status.configure(text="Completed")
        self.search_progress['value'] = 100

    def start_quest(self):
        if self.quest_running:
            return

        self.quest_running = True
        self.start_quest_button.configure(state=tk.DISABLED)
        self.stop_quest_button.configure(state=tk.NORMAL)
        self.quest_status.configure(text="Running...")
        self.quest_progress.start(10)

        # Create and start quest thread
        self.quest_thread = threading.Thread(target=self.run_quest)
        self.quest_thread.daemon = True
        self.quest_thread.start()

    def stop_quest(self):
        if not self.quest_running:
            return

        print("Stopping quest...")
        self.quest_running = False
        self.quest_status.configure(text="Stopping...")

        # Set the stop event if it exists
        if hasattr(self, 'quest_stop_event'):
            self.quest_stop_event.set()

    def run_quest(self):
        try:
            # Create a custom stdout to capture quest output
            original_stdout = sys.stdout
            custom_stdout = io.StringIO()
            sys.stdout = self.redirect

            # Get quest parameters
            is_phone = False  # Force desktop mode for quest
            headless = self.headless_mode.get()

            # Create a stop event for cancellation
            import threading
            stop_event = threading.Event()
            self.quest_stop_event = stop_event

            # Add headless option if enabled
            if headless:
                from selenium.webdriver.edge.options import Options
                original_Options = Options

                class HeadlessOptions(Options):
                    def __init__(self, *args, **kwargs):
                        super().__init__(*args, **kwargs)
                        self.add_argument("--headless")

                # Monkey patch the Options class
                import quest as quest_module
                quest_module.Options = HeadlessOptions

            # Define progress callback
            def update_progress(value):
                self.root.after(0, lambda: self.quest_progress.stop())
                self.root.after(0, lambda: self.quest_progress.configure(mode='determinate', value=value))

            # Get selected profiles
            selected_profiles = []
            for profile_name, var in self.profile_vars.items():
                if var.get():
                    selected_profiles.append((profile_name, self.edge_profiles[profile_name]))

            if not selected_profiles:
                print("No profiles selected. Please select at least one profile.")
                return

            print(f"Running quest on {len(selected_profiles)} selected profiles")

            # Run the quest function for each selected profile
            for i, (profile_name, profile_path) in enumerate(selected_profiles):
                if stop_event.is_set():
                    break

                print(f"\nRunning quest on profile: {profile_name} ({i+1}/{len(selected_profiles)})")

                # Run the quest function with progress updates
                quest(
                    isPhone=is_phone,
                    progress_callback=update_progress,
                    stop_event=stop_event,
                    profile_path=profile_path
                )

                # Update progress to 100% after each profile
                update_progress(100)

                # Small delay between profiles
                if i < len(selected_profiles) - 1 and not stop_event.is_set():
                    print("Waiting before starting next profile...")
                    time.sleep(3)

            # Restore original Options
            if headless:
                quest_module.Options = original_Options

        except Exception as e:
            print(f"Error in quest: {e}")
        finally:
            # Reset UI
            self.quest_running = False
            self.root.after(0, self.reset_quest_ui)
            sys.stdout = original_stdout

    def reset_quest_ui(self):
        self.start_quest_button.configure(state=tk.NORMAL)
        self.stop_quest_button.configure(state=tk.DISABLED)
        self.quest_status.configure(text="Completed")
        self.quest_progress.stop()
        self.quest_progress['value'] = 100

    def clear_console(self):
        self.console_text.configure(state="normal")
        self.console_text.delete(1.0, tk.END)
        self.console_text.configure(state="disabled")

    def get_edge_profiles(self):
        """
        Scans the Edge user data directory and returns a list of available profiles.
        Returns a dictionary with profile names as keys and paths as values.
        """
        profiles = {}

        # Path to Edge user data directory
        edge_data_path = os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Edge', 'User Data')

        if os.path.exists(edge_data_path):
            # Add Default profile
            default_profile_path = os.path.join(edge_data_path, 'Default')
            if os.path.exists(default_profile_path) and os.path.isdir(default_profile_path):
                profiles['Default'] = default_profile_path

            # Look for additional profiles (Profile 1, Profile 2, etc.)
            for item in os.listdir(edge_data_path):
                if item.startswith('Profile ') and os.path.isdir(os.path.join(edge_data_path, item)):
                    profiles[item] = os.path.join(edge_data_path, item)

            print(f"Found {len(profiles)} Edge profiles")
        else:
            print(f"Edge user data directory not found at: {edge_data_path}")

        return profiles

    def on_closing(self):
        # Restore stdout
        sys.stdout = sys.__stdout__

        # Stop any running threads
        self.search_running = False
        self.quest_running = False

        # Close the window
        self.root.destroy()

def main():
    root = tk.Tk()
    app = EdgeAutomatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
