import os
from pathlib import Path
import threading
from ttkbootstrap.dialogs import Messagebox
from tkinter import Entry

class FileExplorerController:
    def __init__(self, view, model):
        self.view = view
        self.model = model

        self._load_drives()
        self.open_directory()

        # Tree navigation
        self.view.dir_tree.bind("<<TreeviewOpen>>", self.on_tree_expand)
        self.view.dir_tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        # double-click in the main panel to open files and folders
        self.view.file_tree.bind("<Double-1>", self.open_file_directory)
        #clipboard for copy and paste
        self.clipboard_paths = []
        self.clipboard_operation = None

        #Binding toolbar buttons to controller
        self.view.btn_new_folder.config(command = self.create_new_folder)
        self.view.btn_copy.config(command=self.copy_file_directory)
        self.view.btn_cut.config(command=self.cut_file_directory)
        self.view.btn_paste.config(command=self.paste_file_directory)
        self.view.btn_delete.config(command=self.delete_file_directory)
        self.view.btn_rename.config(command=self.rename_file_directory)

        # Binding view buttons to controller
        self.view.bind_back(self.on_back_clicked)
        self.view.bind_forward(self.on_forward_clicked)
        self.view.bind_up(self.on_up_clicked)

        self.view.sort_criteria_var.set(self.model.sort_by)
        self.view.sort_order_var.set(self.model.sort_reverse)
        self._bind_sort_menu()

        #Hot Keys
        view.bind("<Control-c>", lambda event: self.copy_file_directory())
        view.bind("<Control-Shift-C>", lambda event: self.cut_file_directory())
        view.bind("<Control-v>", lambda event: self.paste_file_directory())
        view.bind("<Delete>", lambda event: self.delete_file_directory())

    def _bind_sort_menu(self):
        if hasattr(self.view, 'sort_menu'):
            self.view.sort_menu.entryconfig("Name", command=lambda: self.set_sort_criteria("Name"))
            self.view.sort_menu.entryconfig("Type", command=lambda: self.set_sort_criteria("Type"))
            self.view.sort_menu.entryconfig("Date", command=lambda: self.set_sort_criteria("Date"))
            self.view.sort_menu.entryconfig("Size", command=lambda: self.set_sort_criteria("Size"))
            self.view.sort_menu.entryconfig("Ascending", command=lambda: self.set_sort_order(False))
            self.view.sort_menu.entryconfig("Descending", command=lambda: self.set_sort_order(True))

    def set_sort_criteria(self, criteria):
        self.model.sort_by = criteria
        self.open_directory()

    def set_sort_order(self, reverse):
        self.model.sort_reverse = reverse
        self.open_directory()

    def _load_drives(self):
        drives = self.model.get_drives()

        for drive in drives:
            node = self.view.dir_tree.insert("", "end", text=drive, values=[drive])
            self.view.dir_tree.insert(node, "end")  # dummy child for lazy loading

    def on_tree_expand(self, event):

        node = self.view.dir_tree.focus()
        path = self.get_node_path(node)

        self.view.dir_tree.delete(*self.view.dir_tree.get_children(node))

        folders = self.model.get_folders(path)

        for folder in folders:

            child = self.view.dir_tree.insert(
                node,
                "end",
                text=folder.name,
                values=[str(folder)]
            )

            if self._has_subfolders(folder):
                self.view.dir_tree.insert(child, "end")

    def on_tree_select(self, event):
        node = self.view.dir_tree.focus()
        path = self.get_node_path(node)
        self.open_directory(path)

    def open_directory(self, path_to_navigate_to=None):
        if path_to_navigate_to:
            if not os.path.isdir(path_to_navigate_to):
                Messagebox.show_warning(
                    f"Cannot open: '{path_to_navigate_to}' is not a valid directory or does not exist.", "Invalid Path")
                return
            # updating the history
            self.model.change_path(path_to_navigate_to)

        current_display_path = self.model.current_path

        # Update path bar entry
        self.view.path_entry.delete(0, "end")
        self.view.path_entry.insert(0, current_display_path)

        # Update navigation button states based on history
        self.view.update_button_states(
            self.model.can_go_back(),
            self.model.can_go_forward())

        # Clear file list
        for item in self.view.file_tree.get_children():
            self.view.file_tree.delete(item)

        content = self.model.get_directory_content(current_display_path)

        # Populate file tree
        for item in content:
            self.view.file_tree.insert("","end", values=(item["name"], item["date_modified"], item["type"], item["size"]),
                tags=(item["path"], item["is_dir"]))

        self.view.status_item_count.config(text=f"{len(content)} items")

    def get_selected_path(self):
        selected = self.view.file_tree.focus()
        if not selected:
            return None
        item = self.view.file_tree.item(selected)
        return item["tags"][0]

    def open_file_directory(self, event = None):

        path = self.get_selected_path()
        if not path:
            return

        if os.path.isdir(path):
            self.open_directory(path)
        else:
            os.startfile(path)

    def expand_tree_to_path(self, path):

        parts = Path(path).parts

        parent = ""
        node = ""

        for part in parts:
            current = parent + part
            children = self.view.dir_tree.get_children(node)
            found = None

            for child in children:
                if self.get_node_path(child) == current:
                    found = child
                    break

            if not found:
                return

            node = found
            parent = current + "\\"

            self.view.dir_tree.item(node, open=True)

    def get_node_path(self, node):

        values = self.view.dir_tree.item(node, "values")

        if values:
            return values[0]

        return self.view.dir_tree.item(node, "text")

    def _has_subfolders(self, path):
        try:
            for item in Path(path).iterdir():
                if item.is_dir():
                    return True
        except PermissionError:
            pass

        return False

    def on_back_clicked(self):
        if self.model.go_back():
            self.open_directory()

    def on_forward_clicked(self):
        if self.model.go_forward():
            self.open_directory()

    def on_up_clicked(self):
        if self.model.go_up():
            self.open_directory()

    def search(self, query):

        query = query.strip().lower()
        if not query:
            self.open_directory()
            return

        results = self.model.search_in_directory(self.model.current_path, query)

        # clear current table
        for item in self.view.file_tree.get_children():
            self.view.file_tree.delete(item)

        for item in results:
            self.view.file_tree.insert("", "end",
                values=(item["name"], item["date_modified"], item["type"], item["size"]),
                tags=(item["path"], item["is_dir"]))

        self.view.status_item_count.config(text=f"{len(results)} results")

    def create_new_folder(self):
        current_display_path = self.model.current_path
        if not current_display_path:
            return
        try:
            new_folder_path = self.model.create_new_folder(current_display_path)
        except Exception as e:
            Messagebox.show_error(str(e), "Error")
            return

        # Refresh directory
        self.open_directory()

        # Automatically select the new folder to rename
        for item in self.view.file_tree.get_children():
            values = self.view.file_tree.item(item)["values"]

            if values and values[0] == os.path.basename(new_folder_path):
                self.view.file_tree.selection_set(item)
                self.view.file_tree.focus(item)
                self.rename_file_directory()
                break

    def copy_file_directory(self):
        selected_items = self.view.file_tree.selection()
        if not selected_items:
            Messagebox.show_error("Please select a file or folder first.", "Nothing Selected")
            return

        self.clipboard_paths = []

        for item in selected_items:
            data = self.view.file_tree.item(item)
            self.clipboard_paths.append(data["tags"][0])

        self.clipboard_operation = "copy"

    def cut_file_directory(self):

        selected_items = self.view.file_tree.selection()

        if not selected_items:
            Messagebox.show_error("Please select a file or folder first.", "Nothing Selected")
            return

        self.clipboard_paths = []

        for item in selected_items:
            data = self.view.file_tree.item(item)
            self.clipboard_paths.append(data["tags"][0])

        self.clipboard_operation = "cut"

    def paste_file_directory(self):
        if not self.clipboard_paths:
            Messagebox.show_error("Nothing to paste.", "Clipboard Empty")
            return
        path = self.model.current_path
        self.loading_popup = self.view.show_loading_popup("Pasting files...")
        thread = threading.Thread(target=self._paste_worker, args=(path,), daemon=True)
        thread.start()

    def _paste_worker(self, refresh_path):

        if not self.clipboard_paths or not self.model.current_path:
            return

        selected_path = self.get_selected_path()

        if selected_path and os.path.isdir(selected_path):
            destination = selected_path
        else:
            destination = self.model.current_path

        if not os.path.isdir(destination):
            return

        self.model.paste_items(self.clipboard_paths, destination, self.clipboard_operation)

        if self.clipboard_operation == "cut":
            self.clipboard_paths = []
            self.clipboard_operation = None

        self.view.after(0, self._on_paste_complete, refresh_path)

    def _on_paste_complete(self, refresh_path):
        self.view.hide_loading_popup(self.loading_popup)
        self.open_directory(refresh_path)

    # if a file/folder with the same name exists
    def _generate_new_name(self, path):

        base, ext = os.path.splitext(path)
        counter = 1

        new_path = f"{base} ({counter}){ext}"

        while os.path.exists(new_path):
            counter += 1
            new_path = f"{base} ({counter}){ext}"

        return new_path

    def delete_file_directory(self):
        selected_items = self.view.file_tree.selection()
        if not selected_items:
            Messagebox.show_error("Please select a file or folder to delete.", "Nothing Selected")
            return
        paths = []

        for item in selected_items:
            data = self.view.file_tree.item(item)
            paths.append(str(data["tags"][0]))

        confirm = Messagebox.yesno("Are you sure you want to delete the selected item(s)?", "Confirm Delete")
        if confirm != "Yes":
            return

        # Show loading popup
        self.loading_popup = self.view.show_loading_popup("Deleting files...")

        # Run delete in a thread so the UI doesn't freeze
        thread = threading.Thread(target=self._delete_worker, args=(paths,), daemon=True)
        thread.start()

    def _delete_worker(self, paths):
        self.model.delete_items(paths)

        # Hide popup and refresh on the main thread
        self.view.after(0, self._on_delete_complete)

    def _on_delete_complete(self):
        self.view.hide_loading_popup(getattr(self, 'loading_popup', None))
        self.open_directory()

    def rename_file_directory(self):
        selected = self.view.file_tree.focus()
        if not selected:
            Messagebox.show_error("Please select a file or folder first.", "Nothing Selected")
            return

        item = self.view.file_tree.item(selected)
        old_name = item["values"][0]
        old_path = item["tags"][0]

        # Get bounding box of "name" column
        bbox = self.view.file_tree.bbox(selected, column="name")
        if not bbox:
            return

        x, y, width, height = bbox

        # Create entry on top of filename
        entry = Entry(self.view.file_tree)
        entry.place(x=x, y=y, width=width, height=height)

        entry.insert(0, old_name)

        name, ext = os.path.splitext(old_name)
        entry.selection_range(0, len(name))
        entry.focus_set()

        def confirm(event=None):

            new_name = entry.get().strip()

            if not new_name:
                entry.destroy()
                return
            try:
                self.model.rename_item(old_path, new_name)
            except FileExistsError:
                Messagebox.show_error("File or folder already exists.", "Error")
            except Exception as e:
                Messagebox.show_error(str(e), "Error")

            entry.destroy()
            self.open_directory()

        def cancel(event=None):
            entry.destroy()

        entry.bind("<Return>", confirm)
        entry.bind("<Escape>", cancel)
        entry.bind("<FocusOut>", confirm)

    def context_properties(self):
        path = self.get_selected_path()
        if not path:
            return

        properties = self.model.get_item_properties(path)
        if properties:
            size_entry = self.view.show_properties_window(properties)
            if properties.get("is_dir"):
                threading.Thread( target=self._background_calculate_size, args=(properties["path"], size_entry),
                    daemon=True).start()

    def _background_calculate_size(self, path, size_entry):
        # in order to avoid the UI freezing
        final_size = self.model._calculating_folder_size(path)
        self.view.after(0, lambda: self.view.update_properties_size(size_entry, final_size))

