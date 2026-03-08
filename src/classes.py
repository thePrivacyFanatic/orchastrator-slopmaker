from datetime import datetime
from enum import IntEnum


class Transaction:
    """a class representing a message from the orchastrator instance in a server interprable format"""

    content: str
    timestamp: datetime
    sender: int
    mtype: int

    def __init__(
        self, content: str, timestamp: datetime, sender: int, mtype: int
    ) -> None:
        self.content = content
        self.timestamp = timestamp
        self.sender = sender
        self.mtype = mtype

    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        """creates a transaction object from a dictionary

        :param data: a dict to create the transaction from
        :type data: dict
        :return: the created transaction object
        :rtype: Transaction
        """
        return cls(
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            sender=data["sender"],
            mtype=data["mtype"],
        )


class Privilege(IntEnum):
    """an enum representing different user privilege levels"""

    BANNED = 0
    LISTENER = 1
    PUBLISHER = 2
    MODERATOR = 3
    ADMIN = 4


class User:
    """a class representing an orchastrator user"""

    username: str
    privilege: Privilege

    def __init__(self, username: str, privilege: Privilege) -> None:
        self.username = username
        self.privilege = privilege
