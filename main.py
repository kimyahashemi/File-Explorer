import os
from view import FileExplorerView
from controller import FileExplorerController
from model import  FileExplorerModel


def main():
    view = FileExplorerView()
    start_path = os.path.expanduser("~")
    model = FileExplorerModel(start_path)
    controller = FileExplorerController(view, model)
    view.controller = controller
    view.mainloop()


if __name__ == "__main__":
    main()
