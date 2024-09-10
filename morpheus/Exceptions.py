

class CadenceNotFound(Exception):
    def __init__(self, lib, cell,view):
        self.lib = lib
        self.cell = cell
        self.view = view
    def __str__(self):
        return f"The specified cellview lib: {self.lib} cell: {self.cell} view: {self.view} was not found!"