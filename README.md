# AeroMenu

A lightweight, keyboard-driven application launcher for Linux, built with Python, GTK 3 and GTK Layer Shell.

AeroMenu provides a simple way to find and launch applications using a fuzzy search interface. Start typing, navigate through the results with your keyboard, and select what you need.

The goal is to keep things fast, minimal and visually appealing, with a translucent Aero-inspired interface.

## Features

- **Fuzzy search** – Find applications without needing to type their full names. Matches are ranked based on how closely the characters match.
- **Application icons** – Automatically retrieves application names and icons from installed desktop applications.
- **Keyboard-driven navigation** – Navigate results using the arrow keys, Tab and Shift + Tab.
- **Aero-inspired appearance** – Translucent backgrounds, subtle gradients, borders and highlights.
- **Custom icon themes** – Supports GTK icon themes.
- **Lightweight** – Built with Python and GTK 3, without a heavy application framework.
- **Wayland integration** – Uses GTK Layer Shell to display the launcher as a top-layer surface.

## Requirements

- Python 3
- GTK 3
- PyGObject (`python3-gi`)
- GTK Layer Shell
- A compatible Wayland compositor with layer-shell support

## Installation

On Debian-based distributions, install the required dependencies:

```bash
sudo apt install python3 python3-gi gir1.2-gtk-3.0 gir1.2-gtklayershell-0.1
```

Clone the repository:

```bash
git clone https://github.com/USERNAME/AeroMenu.git
cd AeroMenu
```

## Usage

Run AeroMenu by piping a list of entries into `pydmenu.py`:

```bash
printf "Firefox\nTerminal\nFiles\nSettings\n" | python3 pydmenu.py
```

AeroMenu displays the supplied entries in a searchable launcher. The selected entry is printed to standard output, making it easy to integrate with other scripts and desktop workflows.

### Keyboard shortcuts

| Key | Action |
|---|---|
| Type | Filter entries |
| ↓ / Tab | Select next result |
| ↑ / Shift + Tab | Select previous result |
| Enter | Confirm selection |
| Escape | Close the launcher |

## How it works

AeroMenu uses GTK's application information system (`Gio.AppInfo`) to retrieve installed desktop applications and their associated icons.

Its fuzzy matching algorithm searches for characters in sequence, favouring contiguous matches and shorter gaps between characters. Results are then sorted by relevance.

The interface is built with GTK 3, while GTK CSS handles the visual styling. GTK Layer Shell provides integration with compatible Wayland compositors.

## Customisation

The appearance can be customised through the GTK CSS defined in `pydmenu.py`.

The default icon theme is set to the default GTK Icon theme , with an additional icon search path under:

```text
~/.local/share/icons/
```

Typography, transparency, gradients, borders and selection highlights can all be adjusted in the source.

## Project

AeroMenu is a personal Linux desktop project exploring Python, GTK and Wayland integration, with a focus on creating a simple and visually appealing application launcher.
