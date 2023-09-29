class SelectionBoxException(Exception):
    def __init__(self, *args: object) -> None:
        self.type = "morpheus"
        super().__init__(*args)
    pass
    def handle(self,ex):
        pass