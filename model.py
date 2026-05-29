import os
from pathlib import Path
from datetime import datetime
import fnmatch
import shutil
from send2trash import send2trash

class FileExplorerModel:
    def __init__(self, start_path):
        self.history = [os.path.abspath(start_path)]
        self.history_index = 0
        # Default sort criteria
        self.sort_by = "Name"
        self.sort_reverse = False

    @property
    def current_path(self):
        return self.history[self.history_index]

    def change_path(self, new_path):
        new_path = os.path.abspath(new_path)
        if new_path == self.current_path:
            return

        # If we went back and then navigate to a new folder clear forward history
        self.history = self.history[:self.history_index + 1]
        self.history.append(new_path)
        self.history_index += 1

    def go_back(self):
        if self.can_go_back():
            self.history_index -= 1
            return True
        return False

    def go_forward(self):
        if self.can_go_forward():
            self.history_index += 1
            return True
        return False

    def go_up(self):
        parent_dir = os.path.dirname(self.current_path)
        if parent_dir != self.current_path:
            self.change_path(parent_dir)
            return True
        return False

    def can_go_back(self):
        return self.history_index > 0

    def can_go_forward(self):
        return self.history_index < len(self.history) - 1

    def get_drives(self):
        drives = []
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                drives.append(drive)
        return drives

    def get_folders(self, path):
        folders = []
        try:
            for item in Path(path).iterdir():
                if item.is_dir():
                    folders.append(item)
        except PermissionError:
            pass
        return folders

    def _format_size(self, size_bytes):

        if size_bytes < 1024:
            return f"{size_bytes} B"

        elif size_bytes < 1024 ** 2:
            return f"{size_bytes / 1024:.2f} KB"

        elif size_bytes < 1024 ** 3:
            return f"{size_bytes / (1024 ** 2):.2f} MB"

        else:
            return f"{size_bytes / (1024 ** 3):.2f} GB"

    def sort_items(self, items):
        def get_sort_key(item):
            # keep folders at the top
            folder_prefix = "0_" if item.get('is_dir') else "1_"

            if self.sort_by == "Name":
                return folder_prefix + str(item.get('name', '')).lower()
            elif self.sort_by == "Type":
                return folder_prefix + str(item.get('type', '')).lower()
            elif self.sort_by == "Date":
                return folder_prefix + str(item.get('date_modified', ''))
            elif self.sort_by == "Size":
                size = item.get('size_bytes', 0)
                return folder_prefix + f"{size:015d}"

            return folder_prefix + str(item.get('name', '')).lower()

        return sorted(items, key=get_sort_key, reverse=self.sort_reverse)

    def get_directory_content(self, path):
        content = []

        try:
            for item in Path(path).iterdir():
                try:
                    stat = item.stat()

                    if item.is_dir():
                        file_type = "Folder"
                        size = ""
                        size_bytes = 0
                    else:
                        file_type = item.suffix
                        size_bytes = stat.st_size
                        size = self._format_size(size_bytes)

                    content.append({
                        "name": item.name,
                        "date_modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                        "type": file_type,
                        "size": size,
                        "size_bytes": size_bytes,
                        "path": str(item),
                        "is_dir": item.is_dir()
                    })
                except (PermissionError, FileNotFoundError):
                    pass

        except PermissionError:
            pass

        return self.sort_items(content)

    def search_in_directory(self, path, query):

        results = []

        try:
            for item in Path(path).iterdir():

                name = item.name.lower()

                if query in name or fnmatch.fnmatch(name, query):

                    stat = item.stat()

                    if item.is_dir():
                        file_type = "Folder"
                        size = ""
                        size_bytes = 0
                    else:
                        file_type = item.suffix
                        size_bytes = stat.st_size
                        size = self._format_size(size_bytes)

                    results.append({
                        "name": item.name,
                        "date_modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                        "type": file_type,
                        "size": size,
                        "size_bytes": size_bytes,
                        "path": str(item),
                        "is_dir": item.is_dir()
                    })

        except PermissionError:
            pass

        return self.sort_items(results)

    def create_new_folder(self, directory):
        base = "New Folder"
        new_path = os.path.join(directory, base)

        counter = 1

        while os.path.exists(new_path):
            new_path = os.path.join(directory, f"{base} ({counter})")
            counter += 1

        os.mkdir(new_path)

        return new_path

    def paste_items(self, sources, destination, operation):

        for src in sources:

            name = os.path.basename(src)
            dest = os.path.join(destination, name)

            src_abs = os.path.abspath(src)
            dest_abs = os.path.abspath(dest)

            if src_abs == dest_abs:
                continue

            try:
                if os.path.isdir(src_abs) and os.path.commonpath([src_abs, dest_abs]) == src_abs:
                    continue
            except ValueError:
                pass

            try:
                if operation == "copy":

                    if os.path.isdir(src):
                        if os.path.exists(dest):
                            dest = self._generate_new_name(dest)
                        shutil.copytree(src, dest)

                    else:
                        if os.path.exists(dest):
                            dest = self._generate_new_name(dest)
                        shutil.copy2(src, dest)

                elif operation == "cut":

                    if os.path.exists(dest):
                        dest = self._generate_new_name(dest)

                    shutil.move(src, dest)

            except Exception as e:
                print("Paste error:", e)

    def delete_items(self, paths):
        for path in paths:
            try:
                send2trash(path)
            except Exception as e:
                print("Delete error:", path, e)

    def _generate_new_name(self, path):

        base, ext = os.path.splitext(path)
        counter = 1

        new_path = f"{base} ({counter}){ext}"

        while os.path.exists(new_path):
            counter += 1
            new_path = f"{base} ({counter}){ext}"

        return new_path

    def rename_item(self, old_path: str, new_name: str) -> str:
        directory = os.path.dirname(old_path)
        new_path = os.path.join(directory, new_name)

        # If nothing changed
        if old_path == new_path:
            return old_path

        # Prevent overwrite
        if os.path.exists(new_path):
            raise FileExistsError("A file or folder with this name already exists.")

        os.rename(old_path, new_path)

        return new_path

    def get_item_properties(self, path):
        item = Path(path)
        try:
            stat = item.stat()
            is_dir = item.is_dir()

            file_type = "File Folder" if is_dir else (item.suffix.upper() + " File" if item.suffix else "File")

            if not is_dir:
                size = self._format_size(stat.st_size)
            else:
                size = "Calculating..."

            created_date = datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")

            return {"name": item.name, "type": file_type, "location": str(item.parent), "size": size,
                    "created": created_date, "is_dir": is_dir, "path": path }
        except Exception:
            return None

    def _calculating_folder_size(self, path):
        total_size = 0
        try:
            for root, dirs, files in os.walk(path, onerror=lambda e: None):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                    except Exception:
                        pass
        except Exception:
            pass

        return self._format_size(total_size)

