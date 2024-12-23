class InvalidAssetsException(Exception):
    assets: list[str]
    reason: str

    def __init__(self, assets: list[str], reason: str) -> None:
        self.assets = assets
        self.reason = reason


class InvalidItemsException(Exception):
    items: list[str]
    reason: str

    def __init__(self, items: list[str], reason: str) -> None:
        self.items = items
        self.reason = reason


class InternalError(Exception):
    component: str
    msg: str
    reason: str

    def __init__(self, component: str, msg: str, reason: str) -> None:
        self.component = component
        self.reason = reason
        self.msg = msg
