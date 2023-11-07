from typing import Dict, Any


class EntityNotFoundError(Exception):
    """
    We do Entity and not Record, cuz we don't want to
    a) expose implementation of a business issue. record is very sqly
    b) tie the requirement to store entities in sql, as that is hypothetically just one implementation, even if that's the one we're definitely gonna use
    """

    properties: Dict[str, Any]

    def __init__(self, message: str = None, properties: Dict[str, Any] = {}):
        if message:
            super().__init__(message)
        self.properties = properties
