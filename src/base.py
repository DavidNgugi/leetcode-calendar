from logger import logger

class BaseClass:
    def __init__(self, dry: bool = False, verbose: bool = False) -> None:
        self.logger = logger
        self.dry = dry
        self.verbose = verbose

    def __str__(self):
        return "BaseClass(dry={}, verbose={})".format(self.dry, self.verbose)

    def log(self, message: str):
        if self.verbose:
            self.logger.debug(message)