# Edge Automator

A tool for automating Microsoft Edge browser tasks, including Bing searches and Microsoft Rewards quests.

## Overview

Edge Automator helps you automate repetitive tasks in Microsoft Edge, such as:
- Performing Bing searches with random search terms
- Completing Microsoft Rewards quests and activities
- Automating browser interactions with human-like behavior

The tool offers both a command-line interface (CLI) and a graphical user interface (GUI) for ease of use.

## Requirements

- Windows operating system
- Microsoft Edge browser installed
- Python 3.6 or higher
- Required Python packages (see Installation)

## Installation

1. Clone or download this repository
2. Install the required Python packages:
   ```
   pip install selenium tkinter
   ```
3. Make sure you have Microsoft Edge installed on your system

## Usage

### Command Line Interface (CLI)

You can run Edge Automator from the command line with various options:

```
python main.py [options]
```

Options:
- `--mode {search,quest,gui}`: Run in specific mode
  - `search`: Perform automated searches
  - `quest`: Complete quests and activities
  - `gui`: Launch graphical user interface
- `--phone`: Run in phone mode (iPhone 10 emulation)
- `--interactive`: Launch in interactive mode to choose options

Examples:
```
# Run in interactive mode
python main.py --interactive

# Run search mode with phone emulation
python main.py --mode search --phone

# Launch the GUI
python main.py --mode gui
```

### Graphical User Interface (GUI)

To launch the GUI, either:
1. Run `python gui.py`
2. Or run `python main.py --mode gui`

The GUI has four main sections:

#### 1. Search Tab
- Select device mode (Desktop or Phone)
- Set the number of searches to perform
- Start/Stop search operations
- View progress in real-time

#### 2. Quest Tab
- Start/Stop quest operations
- View progress in real-time
- Note: Quest mode only works properly in desktop mode

#### 3. Console Tab
- View real-time logs of operations
- Clear console output

#### 4. Misc Tab
- Toggle headless mode (run browser without UI)

## Features

### Search Mode
- Performs automated Bing searches with random search terms
- Configurable number of searches
- Human-like behavior with random delays and scrolling
- Works in both desktop and phone modes

### Quest Mode
- Automatically completes Microsoft Rewards quests and activities
- Clicks through cards on the rewards dashboard
- Works best in desktop mode

### GUI Features
- Dark blue theme for comfortable viewing
- Real-time progress tracking
- Console output for monitoring operations
- Ability to stop operations mid-execution
- Headless mode for background operation

## Troubleshooting

### Browser Closes Unexpectedly
- Make sure you have the latest version of Microsoft Edge installed
- Update the selenium package: `pip install selenium --upgrade`

### Search/Quest Not Working
- Check your internet connection
- Ensure you're logged into your Microsoft account in Edge
- Try running in non-headless mode to see what's happening

### GUI Issues
- Make sure you have tkinter installed: `pip install tk`
- For Linux users, install tkinter via your package manager

## License

See the LICENSE file for details.
