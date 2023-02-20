import enum


class OrderTypes(str, enum.Enum):
    asks = 'asks'
    bids = 'bids'
