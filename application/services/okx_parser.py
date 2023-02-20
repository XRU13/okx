"""Module for online parsing okx.com"""
from abc import ABC
from typing import List, Optional

import requests

from adapters.repositories.common import LoopsRepo
from application.dataclasses.common import (
    CurrenciesPairs,
    BookOrder,
    LoopInfo,
    BookOrderConverted, PlatformInfo, MethodInfo
)
from application.dataclasses.constants import OrderTypes
from application import errors


class OKXExchangeParser(ABC):
    """Class for parsing okx.com"""

    def get_orders_book(
            self, loop_info: List[LoopInfo],
            base_coin: str,
            platform: PlatformInfo,
            method: MethodInfo
    ) -> List[BookOrderConverted]:
        loop_data = []
        sorted_loop = self._check_first_step(loop_info=loop_info, currency_from=base_coin)
        for loop in sorted_loop:
            loop_step = []
            pair = loop.get_currencies_pairs
            data_values = requests.get(
                f"https://www.okx.com/api/v5/market/books-lite?instId={pair}"
            ).json().get('data')
            if data_values:
                values = data_values[0][OrderTypes.asks]
                for value in values:
                    loop_step.append(
                        BookOrder(
                            currency_from=loop.currency_from,
                            currency_to=loop.currency_to,
                            rate=float(value[0]),
                            quantity=float(value[1]),
                            rule_id=loop.rule_id
                        )
                    )
            else:
                revert_pair = self._get_revert_currency_pair(loop)
                data_values = requests.get(
                    f"https://www.okx.com/api/v5/market/books-lite?instId={revert_pair.pair_names}"
                ).json().get('data')
                if data_values:
                    values = data_values[0][OrderTypes.bids]
                    for value in values:
                        rate = 1 / float(value[1])
                        loop_step.append(
                            BookOrder(
                                currency_from=loop.currency_to,
                                currency_to=loop.currency_from,
                                rate=rate,
                                quantity=float(value[1]),
                                rule_id=loop.rule_id
                            )
                        )
            if loop_step[0].currency_from == base_coin:
                base_currency_loop_step = []
                amount = 0
                for order in loop_step:
                    amount += order.quantity
                    base_currency_loop_step.append(
                        BookOrderConverted(
                            currency_from=order.currency_from,
                            currency_to=base_coin,
                            rate=1,
                            quantity_for_translation=order.quantity,
                            quantity_base_currency=order.quantity,
                            total_amount=amount,
                            rule_id=order.rule_id,
                            platform_from=platform.platform_name,
                            platform_to=method.method_name,
                            tax=0
                        )
                    )
            else:
                base_currency_loop_step = self._convert_to_base_coin(
                    orders_book=loop_step,
                    base_coin=base_coin,
                    platform=platform,
                    method=method
                )
            loop_data.extend(base_currency_loop_step)
        sorted_loop_data = sorted(loop_data, key=lambda order_book: order_book.total_amount)
        return sorted_loop_data

    def _get_revert_currency_pair(self, currency_pair: LoopInfo) -> CurrenciesPairs:
        pair = currency_pair.get_currencies_pairs.split('-')
        return CurrenciesPairs(pair_names=pair[1] + '-' + pair[0])

    def _convert_to_base_coin(
            self,
            orders_book: List[BookOrder],
            base_coin: str,
            platform: PlatformInfo,
            method: MethodInfo
    ) -> List[BookOrderConverted]:
        new_orders_book = []
        amount = 0
        course = self.get_curses(
            currency_from=orders_book[0].currency_from,
            currency_to=base_coin,
            platform_id=platform.platform_id,
            method_id=method.method_id
        )
        for order in orders_book:
            convert_coin = order.currency_from
            if course:
                quantity_base_currency = order.quantity * course['rate']
                amount += quantity_base_currency
                new_orders_book.append(
                    BookOrderConverted(
                        currency_from=order.currency_from,
                        currency_to=base_coin,
                        rate=course['rate'],
                        quantity_for_translation=order.quantity,
                        quantity_base_currency=quantity_base_currency,
                        total_amount=amount,
                        rule_id=order.rule_id,
                        platform_from=platform.platform_name,
                        platform_to=method.method_name,
                        tax=course['tax']
                    )
                )
            else:
                raise errors.GetCurseError(pair=f'{convert_coin}-{base_coin}')
        return new_orders_book

    @staticmethod
    def get_curses(
            currency_from: str,
            currency_to: str,
            platform_id: int,
            method_id: int
    ) -> Optional[float]:
        return LoopsRepo().get_curses_by_currency_name(
            currency_from=currency_from,
            currency_to=currency_to,
            platform_id=platform_id,
            method_id=method_id
        )

    def _check_first_step(self, loop_info: List[LoopInfo], currency_from: str) -> List[LoopInfo]:
        # Сортируем цепочку, начиная с шага с базовой валютой
        sorted_list = []
        if loop_info[0].currency_from == currency_from:
            return loop_info
        else:
            loop_info.insert(0, loop_info.pop(-1))
            sorted_list.append(loop_info)
        return self._check_first_step(loop_info, currency_from)
