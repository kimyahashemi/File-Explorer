# MVC Python File Explorer

A desktop file management application built with Python. This project implements a clean **Model-View-Controller (MVC)** architecture to ensure a modular, scalable, and maintainable codebase.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![GUI](https://img.shields.io/badge/GUI-Tkinter%20/%20ttkbootstrap-orange.svg)
![Pattern](https://img.shields.io/badge/Pattern-MVC-green.svg)

## 🚀 Features

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

## 🏗️ Architecture: The MVC Pattern

This project strictly follows the **Model-View-Controller** design pattern:

- **Model (`model.py`)**: The data layer. It interacts directly with the OS, handles file system logic, calculates folder sizes, and manages the navigation history.
- **View (`view.py`)**: The presentation layer. Built using Tkinter and `ttkbootstrap`, it defines the layout, buttons, and trees. It remains "dumb" to the logic, only reporting user actions to the Controller.
- **Controller (`controller.py`)**: The brain. It listens for events from the View (clicks, keypresses) and tells the Model what to do. It also manages threading and UI updates.
   
