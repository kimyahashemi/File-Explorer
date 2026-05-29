# MVC Python File Explorer

A desktop file management application built with Python. This project implements a clean **Model-View-Controller (MVC)** architecture to ensure a modular, scalable, and maintainable codebase.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![GUI](https://img.shields.io/badge/GUI-Tkinter%20/%20ttkbootstrap-orange.svg)
![Pattern](https://img.shields.io/badge/Pattern-MVC-green.svg)

## Features

- **Efficient Navigation**: 
  - Interactive side-bar with lazy-loading directory trees.
  - History-based navigation (Back, Forward, Up).
  - Breadcrumb path entry for direct access.
- **Core File Operations**:
  - Create, Rename, Copy, Cut, Paste, and Delete files/folders.
  - Multi-threaded operations: Large file deletions and pastes happen in the background to keep the UI responsive.
- **Search & Filter**:
  - Real-time search functionality within the current directory.
  - Sort items by Name, Type, Date Modified, or Size.
- **Modern UI**:
  - Built with `ttkbootstrap` for a professional, modern look.
  - In-place renaming (edit filenames directly in the list view).
  - Loading indicators for long-running tasks.
- **Keyboard Shortcuts**:
  - `Ctrl + C` / `Ctrl + V`: Copy and Paste.
  - `Ctrl + Shift + C`: Cut.
  - `Delete`: Delete selected items.

## Architecture: The MVC Pattern

This project strictly follows the **Model-View-Controller** design pattern:

- **Model (`model.py`)**: The data layer. It interacts directly with the OS, handles file system logic, calculates folder sizes, and manages the navigation history.
- **View (`view.py`)**: The presentation layer. Built using Tkinter and `ttkbootstrap`, it defines the layout, buttons, and trees. It remains "dumb" to the logic, only reporting user actions to the Controller.
- **Controller (`controller.py`)**: The brain. It listens for events from the View (clicks, keypresses) and tells the Model what to do. It also manages threading and UI updates.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/kimyahashemi/File-Explorer.git
cd File-Explorer
```
2. Create and activate a virtual environment:

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the application with:

```bash
python main.py
```

The application starts in the user's home directory and launches a graphical file explorer interface.

## Project Structure

```text
File-Explorer/
│
├── main.py
├── model.py
├── view.py
├── controller.py
└── requirements.txt
```

## Future Improvements
- Add dark mode
- Add drag-and-drop
- Add multi-tabs

## Author
Kimya Hashemi
