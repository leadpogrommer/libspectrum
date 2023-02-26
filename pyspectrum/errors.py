class LoadError(Exception):
    def __int__(self, path: str):
        super().__init__(f'File {path} is not valid')


