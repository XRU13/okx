from typing import List, Optional

from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass
class CurrencyPairInfo:
    currency_from: str = Field(description='Currency from which we transfer')
    currency_to: str = Field(description='currency in which we transfer')
    rule_id: int = Field(description='Id rule')


@dataclass
class StepLoopInfo(CurrencyPairInfo):
    platform_from: str = Field(description='Platform from which we transfer')
    platform_to: str = Field(description='Platform in which we transfer')
    tax: float = Field(description='Tax')


@dataclass
class LoopInfo(StepLoopInfo):
    method: str = Field(description='Transaction method')

    @property
    def get_currencies_pairs(self) -> str:
        return f'{self.currency_from}-{self.currency_to}'


@dataclass
class BookOrderConverted(StepLoopInfo):
    rate: float = Field(description='Rate of exchange')
    quantity_for_translation: float = Field(description='Quantity at the price')
    quantity_base_currency: float = Field(description='Quantity at the price')
    total_amount: float = Field(description='Total number of sentences in the glass at the current rate')


@dataclass
class CurrenciesPairs:
    pair_names: str = Field(description='Currencies name pair')


@dataclass
class BookOrder(CurrencyPairInfo):
    rate: float = Field(description='Rate of exchange')
    quantity: float = Field(description='Quantity at the price')


@dataclass
class BookOrderParsed(LoopInfo):
    rate: float = Field(description='Rate of exchange')
    sum_start: float = Field(description='Sum of the first currency')
    sum_end: float = Field(description='Sum of the second currency')


@dataclass
class LoopProfit:
    amount: Optional[float] = Field(description='Amount of currency')
    profit: Optional[float] = Field(description='Minimum profitability of the loop')


@dataclass
class LoopProfitAndTax(LoopProfit):
    tax: float = Field(description='Tax')


@dataclass
class OKXResponse(LoopProfit):
    data: List[BookOrderParsed] = Field(description='Data from the sales book')


@dataclass
class MethodInfo:
    method_id: int = Field(description='Method id')
    method_name: str = Field(description='Method name')


@dataclass
class PlatformInfo:
    platform_id: int = Field(description='Platform id')
    platform_name: str = Field(description='Platform name')
