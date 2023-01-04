class ValidationError(Exception):
    pass


class TFileError(Exception):
    pass


class ClientNotFoundError(Exception):
    pass


class ClientAlredyExistError(Exception):
    pass


class ClientManagerNotInitialized(Exception):
    pass


class UserIdNoneError(Exception):
    pass
