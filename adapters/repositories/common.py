from datetime import datetime
from typing import List, Optional

import psycopg2
from psycopg2.extras import DictCursor

from application.dataclasses import LoopInfo
from application.dataclasses.common import MethodInfo, PlatformInfo
from connection_config import connection_params
from application import interfaces


class LoopsRepo(interfaces.LoopsRepo):

    def get_loop_by_id(self, loop_id: int) -> List[LoopInfo]:
        with psycopg2.connect(**connection_params) as conn:
            cur = conn.cursor(cursor_factory=DictCursor)
            cur.execute(
                f"""select tm.name as method,
                           p_1.name as platform_from,
                           p_2.name as platform_to,
                           cur_1.name as currency_from,
                           cur_2.name as currency_to,
                           c.rule_number,
                           c.tax
                    from loop_path lp
                    inner join courses c on c.id = lp.edge
                    inner join tran_methods tm on tm.id = c.method
                    inner join platforms p_1 on p_1.id = c.platform_from
                    inner join platforms p_2 on p_2.id = c.platform_to
                    inner join currencies cur_1 on c.currency_from = cur_1.id
                    inner join currencies cur_2 on c.currency_to = cur_2.id
                    where loop_id = {loop_id} order by step_number"""
            )
            result = cur.fetchall()

            data = []
            for res in result:
                data.append(
                    LoopInfo(
                        method=res['method'],
                        platform_from=res['platform_from'],
                        platform_to=res['platform_to'],
                        currency_from=res['currency_from'],
                        currency_to=res['currency_to'],
                        rule_id=res['rule_number'],
                        tax=res['tax']
                    )
                )
            return data

    def get_curses_by_currency_name(
            self,
            currency_from: str,
            currency_to: str,
            platform_id: int,
            method_id: int
    ) -> Optional[float]:
        with psycopg2.connect(**connection_params) as conn:
            cur = conn.cursor(cursor_factory=DictCursor)
            cur.execute(
                f"""select c.rate, c.tax from courses c
                inner join currencies cur1 on cur1.id = c.currency_from
                inner join currencies cur2 on cur2.id = c.currency_to
                where c.platform_from = {platform_id}
                and c.method = {method_id}
                and cur1.name = '{currency_from}'
                and cur2.name = '{currency_to}'
                """
            )
            return cur.fetchone()

    def save_loop_info(
            self,
            loop_id: int,
            spread: float,
            max_flow: float,
            loop_speed: float,
            added: datetime
    ) -> None:
        with psycopg2.connect(**connection_params) as conn:
            cur = conn.cursor()
            cur.execute(
                f"""
                insert into loop_info (loop_id, spread, max_flow, loop_speed, frequency, added) 
                values ({loop_id}, {spread}, {max_flow}, {loop_speed}, 's', '{str(added)}')
                """)

    def check_status(self, key: str) -> bool:
        with psycopg2.connect(**connection_params) as conn:
            cur = conn.cursor()
            cur.execute(f"select status from clients cl where cl.key = '{key}'")
            info = cur.fetchall()
            if len(info) == 0 or info[0][0] != 2:
                return False
        return True

    def get_method_info(self, method_name: str) -> Optional[MethodInfo]:
        with psycopg2.connect(**connection_params) as conn:
            cur = conn.cursor()
            cur.execute(f"select id, name from tran_methods where name = '{method_name}'")
            res = cur.fetchone()
            return MethodInfo(
                method_id=res[0],
                method_name=res[1]
            ) if res else None

    def get_platform_info(self, platform_name: str) -> Optional[PlatformInfo]:
        with psycopg2.connect(**connection_params) as conn:
            cur = conn.cursor()
            cur.execute(f"select id, name from platforms where name = '{platform_name}'")
            res = cur.fetchone()
            return PlatformInfo(
                platform_id=res[0],
                platform_name=res[1]
            ) if res else None
