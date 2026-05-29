from ttkbootstrap import (Window, Menu, Frame, Button, Entry, Panedwindow, Scrollbar, Treeview,
                          Label , Toplevel, Progressbar)
from ttkbootstrap.constants import *
from tkinter import Menu as tkMenu
from tkinter import StringVar, BooleanVar

class FileExplorerView(Window):
    def __init__(self, theme_name="flatly"):

        super().__init__(themename=theme_name)

        self.title("Python File Explorer")
        self.geometry("1024x768")
        self.minsize(800, 600)

        self._create_menu()
        self._create_navigation_bar()
        self._create_toolbar()
        self._create_main_body()
        self._create_status_bar()
        self._create_context_menu()

    def _create_menu(self):
        self.menu_bar = Menu(self)

        # File Menu
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="New Window")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.quit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        # View Menu
        self.view_menu = Menu(self.menu_bar, tearoff=0)
        self.view_menu.add_command(label="Refresh")
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)

        self.config(menu=self.menu_bar)

    def _create_navigation_bar(self):
        nav_frame = Frame(self, padding=(10, 5))
        nav_frame.pack(fill=X, side=TOP)

        # Navigation Buttons
        self.btn_back = Button(nav_frame, text="◀", bootstyle=(PRIMARY, OUTLINE), width=3)
        self.btn_back.pack(side=LEFT, padx=(0, 2))

        self.btn_forward = Button(nav_frame, text="▶", bootstyle=(PRIMARY, OUTLINE), width=3)
        self.btn_forward.pack(side=LEFT, padx=(0, 2))

        self.btn_up = Button(nav_frame, text="⬆", bootstyle=(PRIMARY, OUTLINE), width=3)
        self.btn_up.pack(side=LEFT, padx=(0, 10))

        # Address Bar
        self.path_entry = Entry(nav_frame, bootstyle=DEFAULT)
        self.path_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        self.path_entry.bind("<Return>", self._on_path_enter)

        self.search_entry = Entry(nav_frame, bootstyle=INFO)
        self.search_entry.insert(0, "Search...")
        self.search_entry.pack(side=LEFT, fill=X, expand=False)
        self.search_entry.bind("<FocusIn>", lambda args: self.search_entry.delete('0', 'end'))
        self.search_entry.bind("<Return>", self._on_search_enter)

    def _create_toolbar(self):
        toolbar_frame = Frame(self, padding=(10, 5))
        toolbar_frame.pack(fill=X, side=TOP)

        self.btn_new_folder = Button(toolbar_frame, text="New Folder",bootstyle=SUCCESS, width=12)
        self.btn_new_folder.pack(side=LEFT, padx=2)

        self.btn_copy = Button(toolbar_frame, text="Copy", bootstyle=PRIMARY, width=8)
        self.btn_copy.pack(side=LEFT, padx=2)

        self.btn_cut = Button(toolbar_frame, text="Cut", bootstyle=PRIMARY, width=8)
        self.btn_cut.pack(side=LEFT, padx=2)

        self.btn_paste = Button(toolbar_frame,text="Paste", bootstyle=PRIMARY,width=8)
        self.btn_paste.pack(side=LEFT, padx=2)

        self.btn_rename = Button(toolbar_frame, text="Rename", bootstyle=WARNING, width=8)
        self.btn_rename.pack(side=LEFT, padx=2)

        self.btn_delete = Button(toolbar_frame, text="Delete", bootstyle=DANGER, width=8)
        self.btn_delete.pack(side=LEFT, padx=2)

        self.btn_sort = Button(toolbar_frame, text="Sort", bootstyle=INFO, width=8)
        self.btn_sort.pack(side=LEFT, padx=10)
        self.btn_sort.bind("<Button-1>", self.show_sort_menu)
        self._create_sort_menu()

    def show_sort_menu(self, event):
        x = self.btn_sort.winfo_rootx()
        y = self.btn_sort.winfo_rooty() + self.btn_sort.winfo_height()
        self.sort_menu.post(x, y)

    def _create_sort_menu(self):
        self.sort_menu = tkMenu(self, tearoff=0)

        self.sort_criteria_var = StringVar(master=self, value="Name")
        self.sort_order_var = BooleanVar(master=self, value=False)

        self.sort_menu.add_radiobutton(label="Name", variable=self.sort_criteria_var, value="Name")
        self.sort_menu.add_radiobutton(label="Type", variable=self.sort_criteria_var, value="Type")
        self.sort_menu.add_radiobutton(label="Date", variable=self.sort_criteria_var, value="Date")
        self.sort_menu.add_radiobutton(label="Size", variable=self.sort_criteria_var, value="Size")

        self.sort_menu.add_separator()

        self.sort_menu.add_radiobutton(label="Ascending", variable=self.sort_order_var, value=False)
        self.sort_menu.add_radiobutton(label="Descending", variable=self.sort_order_var, value=True)


    def _on_path_enter(self, event):
        if hasattr(self, "controller"):
            self.controller.open_path(self.path_entry.get())

    def _on_search_enter(self, event):
        if hasattr(self, "controller"):
            self.controller.search(self.search_entry.get())

    def _create_main_body(self):
        self.paned_window = Panedwindow(self, orient=HORIZONTAL)
        self.paned_window.pack(fill=BOTH, expand=True, padx=10, pady=(5, 5))

        left_frame = Frame(self.paned_window)
        self.paned_window.add(left_frame, weight=1)

        left_scroll = Scrollbar(left_frame, orient=VERTICAL)
        left_scroll.pack(side=RIGHT, fill=Y)

        self.dir_tree = Treeview(left_frame, selectmode="browse", yscrollcommand=left_scroll.set)
        self.dir_tree.pack(side=LEFT, fill=BOTH, expand=True)
        self.dir_tree.heading("#0", text="Navigation", anchor=W)
        left_scroll.config(command=self.dir_tree.yview)

        # File/Folder Content
        right_frame = Frame(self.paned_window)
        self.paned_window.add(right_frame, weight=3)

        right_scroll = Scrollbar(right_frame, orient=VERTICAL)
        right_scroll.pack(side=RIGHT, fill=Y)

        columns = ("name", "date_modified", "type", "size")
        self.file_tree = Treeview(
            right_frame,
            columns=columns,
            show="headings",
            selectmode="extended",
            yscrollcommand=right_scroll.set,
            bootstyle=PRIMARY)
        self.file_tree.bind("<Button-3>", self._show_context_menu)

        # Define Headings and Columns
        self.file_tree.heading("name", text="Name", anchor=W)
        self.file_tree.heading("date_modified", text="Date modified", anchor=W)
        self.file_tree.heading("type", text="Type", anchor=W)
        self.file_tree.heading("size", text="Size", anchor=E)

        self.file_tree.column("name", width=300, anchor=W)
        self.file_tree.column("date_modified", width=150, anchor=W)
        self.file_tree.column("type", width=100, anchor=W)
        self.file_tree.column("size", width=100, anchor=E)

        self.file_tree.pack(side=LEFT, fill=BOTH, expand=True)
        right_scroll.config(command=self.file_tree.yview)

    def _create_status_bar(self):
        status_frame = Frame(self)
        status_frame.pack(fill=X, side=BOTTOM, padx=10, pady=(0, 5))

        self.status_item_count = Label(status_frame, text="0 items", bootstyle=SECONDARY)
        self.status_item_count.pack(side=LEFT)

        self.status_selected_info = Label(status_frame, text="", bootstyle=SECONDARY)
        self.status_selected_info.pack(side=RIGHT)

    def _create_context_menu(self):

        self.context_menu = Menu(self, tearoff=0)

        self.context_menu.add_command(label="Open", command=self._menu_open)
        self.context_menu.add_separator()

        self.context_menu.add_command(label="Copy", command=self._menu_copy)
        self.context_menu.add_command(label="Cut", command=self._menu_cut)
        self.context_menu.add_command(label="Paste", command=self._menu_paste)

        self.context_menu.add_separator()

        self.context_menu.add_command(label="Delete", command=self._menu_delete)

        self.context_menu.add_separator()

        self.context_menu.add_command(label="Rename", command=self._menu_rename)

        self.context_menu.add_separator()

        self.context_menu.add_command(label="Properties", command=self._menu_properties)

    def _show_context_menu(self, event):

        row = self.file_tree.identify_row(event.y)

        if row:
            self.file_tree.selection_set(row)
            self.file_tree.focus(row)

        self.context_menu.tk_popup(event.x_root, event.y_root)

    def show_properties_window(self, props):
        prop_win = Toplevel(self)
        prop_win.title(f"{props['name']} Properties")
        prop_win.geometry("350x200")
        prop_win.resizable(False, False)

        # Center the window
        prop_win.position_center()

        container = Frame(prop_win, padding=20)
        container.pack(fill=BOTH, expand=True)

        def add_property_row(row, label_text, value_text):
            Label(container, text=label_text, font=("", 10, "bold")).grid(row=row, column=0, sticky=W, pady=5,
                                                                          padx=(0, 10))
            val_label = Entry(container, bootstyle="readonly")
            val_label.insert(0, value_text)
            val_label.configure(state="readonly")
            val_label.grid(row=row, column=1, sticky=EW, pady=5)
            return val_label

        container.columnconfigure(1, weight=1)

        add_property_row(0, "Type:", props["type"])
        add_property_row(1, "Location:", props["location"])
        size_entry = add_property_row(2, "Size:", props["size"])
        add_property_row(3, "Created:", props["created"])
        return size_entry

    def update_properties_size(self, size_entry, new_size):
        try:
            size_entry.configure(state="normal")
            size_entry.delete(0, 'end')
            size_entry.insert(0, new_size)
            size_entry.configure(state="readonly")
        except Exception:
            pass

    def _menu_open(self):
        if hasattr(self, "controller"):
            self.controller.open_file_directory()

    def _menu_copy(self):
        if hasattr(self, "controller"):
            self.controller.copy_file_directory()

    def _menu_cut(self):
        if hasattr(self, "controller"):
            self.controller.cut_file_directory()

    def _menu_paste(self):
        if hasattr(self, "controller"):
            self.controller.paste_file_directory()

    def _menu_delete(self):
        if hasattr(self, "controller"):
            self.controller.delete_file_directory()

    def _menu_rename(self):
        if hasattr(self, "controller"):
            self.controller.rename_file_directory()

    def _menu_properties(self):
        if hasattr(self, "controller"):
            self.controller.context_properties()

    def bind_back(self, callback):
        self.btn_back.config(command=callback)

    def bind_forward(self, callback):
        self.btn_forward.config(command=callback)

    def bind_up(self, callback):
        self.btn_up.config(command=callback)

    def update_button_states(self, can_go_back, can_go_forward):
        # Disable or enable buttons based on history
        self.btn_back.config(state="normal" if can_go_back else "disabled")
        self.btn_forward.config(state="normal" if can_go_forward else "disabled")

    def show_loading_popup(self, message="Processing..."):
        popup = Toplevel(self)
        popup.title("Please Wait")
        popup.geometry("300x100")
        popup.resizable(False, False)
        popup.position_center()
        # Block interaction with the main window while loading
        popup.transient(self)
        popup.grab_set()

        Label(popup, text=message).pack(pady=(20, 10))

        pb = Progressbar(popup, mode='indeterminate')
        pb.pack(fill=X, padx=20)
        pb.start()

        self.update_idletasks()
        return popup

    def hide_loading_popup(self, popup):
        if popup and popup.winfo_exists():
            popup.grab_release()
            popup.destroy()
