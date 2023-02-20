import datetime
from typing import List, Optional

from adapters.repositories.common import LoopsRepo
from application import errors
from application.dataclasses.common import (
    LoopInfo,
    OKXResponse,
    LoopProfit,
    BookOrderParsed,
    MethodInfo,
    PlatformInfo,
)
from application.services.okx_parser import OKXExchangeParser


class OKXTradeOnlineParser:
    PLATFORM_NAME = 'OKX'
    METHOD_NAME = 'Trade'

    def get_method(self) -> Optional[MethodInfo]:
        method = LoopsRepo().get_method_info(method_name=self.METHOD_NAME)
        if method:
            return method
        else:
            raise errors.GetCurseError(method=f'{method}')

    def get_platform(self) -> Optional[PlatformInfo]:
        platform = LoopsRepo().get_platform_info(platform_name=self.PLATFORM_NAME)
        if platform:
            return platform
        else:
            raise errors.GerPlatformError(platform=f'{platform}')

    def main(
            self,
            loop_id: int,
            currency_name: Optional[str],
            profit: Optional[float],
            amount: Optional[float]
    ) -> OKXResponse:
        last_profitable_rate = list()
        data = list()
        loop_info = self.get_loop(loop_id=loop_id)
        book_orders = OKXExchangeParser().get_orders_book(
            loop_info=loop_info,
            base_coin=currency_name,
            platform=self.get_platform(),
            method=self.get_method()
        )

        for order in book_orders:
            data.append(
                BookOrderParsed(
                    platform_from=order.platform_from,
                    platform_to=order.platform_to,
                    method=self.METHOD_NAME,
                    currency_from=order.currency_from,
                    currency_to=order.currency_to,
                    rate=order.rate,
                    rule_id=order.rule_id,
                    tax=order.tax,
                    sum_start=order.quantity_for_translation,
                    sum_end=order.quantity_base_currency
                )
            )
            if profit:
                profitable_loop = self.check_profitability_loop(
                    loop_info=loop_info,
                    start_quantity=float(order.total_amount),
                    currency_from=order.currency_to
                )
                if profitable_loop.amount > order.total_amount:
                    if profitable_loop.profit > profit:
                        last_profitable_rate.clear()
                        last_profitable_rate.append(profitable_loop)
                    elif profitable_loop.profit == profit:
                        LoopsRepo().save_loop_info(
                            loop_id=loop_id,
                            spread=profitable_loop.profit,
                            max_flow=profitable_loop.amount,
                            loop_speed=1.0,
                            added=datetime.datetime.now()
                        )
                        return OKXResponse(
                            profit=profitable_loop.profit,
                            amount=profitable_loop.amount,
                            data=data
                        )
                    else:
                        LoopsRepo().save_loop_info(
                            loop_id=loop_id,
                            spread=last_profitable_rate[0].profit,
                            max_flow=last_profitable_rate[0].amount,
                            loop_speed=1.0,
                            added=datetime.datetime.now()
                        )
                        return OKXResponse(
                            profit=last_profitable_rate[0].profit,
                            amount=last_profitable_rate[0].amount,
                            data=data[:-1]
                        )
                else:
                    LoopsRepo().save_loop_info(
                        loop_id=loop_id,
                        spread=profitable_loop.profit,
                        max_flow=profitable_loop.amount,
                        loop_speed=1.0,
                        added=datetime.datetime.now()
                    )
                    return OKXResponse(
                        profit=profitable_loop.profit,
                        amount=profitable_loop.amount,
                        data=data
                    )
            if amount:
                profitable_loop = self.check_profitability_loop(
                    loop_info=loop_info,
                    start_quantity=amount,
                    currency_from=order.currency_to
                )
                last_profitable_rate.clear()
                last_profitable_rate.append(profitable_loop)
                if amount < order.total_amount:
                    LoopsRepo().save_loop_info(
                        loop_id=loop_id,
                        spread=last_profitable_rate[0].profit,
                        max_flow=last_profitable_rate[0].amount,
                        loop_speed=1.0,
                        added=datetime.datetime.now()
                    )
                    return OKXResponse(
                        profit=last_profitable_rate[0].profit,
                        amount=last_profitable_rate[0].amount,
                        data=data
                    )

    @staticmethod
    def get_loop(loop_id: int) -> List[LoopInfo]:
        return LoopsRepo().get_loop_by_id(loop_id)

    def check_profitability_loop(
            self,
            loop_info: List[LoopInfo],
            start_quantity: float,
            currency_from: str
    ) -> LoopProfit:
        result_quantity_list = [start_quantity]
        for loop in loop_info:
            rate = LoopsRepo().get_curses_by_currency_name(
                currency_from=loop.currency_from,
                currency_to=loop.currency_to,
                method_id=self.get_method().method_id,
                platform_id=self.get_platform().platform_id
            )
            if rate:
                quantity = result_quantity_list[0] * rate['rate']
                tax = quantity / 100 * rate['tax']
                quantity_to_change = quantity - tax
                result_quantity_list.clear()
                result_quantity_list.append(quantity_to_change)
            else:
                raise errors.GetCurseError(pair=f'{currency_from}-{loop.currency_to}')
        return self.check_profit(
            start_quantity=start_quantity,
            end_quantity=result_quantity_list[0]
        )

    @staticmethod
    def check_profit(start_quantity: float, end_quantity: float) -> LoopProfit:
        profit = (end_quantity - start_quantity) / 100
        return LoopProfit(
            profit=profit,
            amount=end_quantity
        )
