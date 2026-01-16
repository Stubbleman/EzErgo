class VialError(RuntimeError):
    pass


class HidNotAvailableError(VialError):
    pass


class VialProtocolError(VialError):
    pass


class VialTimeoutError(VialError):
    pass


