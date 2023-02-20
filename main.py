from flask import Flask, jsonify, request

from adapters.repositories.common import LoopsRepo
from application import errors
from application.services.okx_services import OKXTradeOnlineParser

app = Flask(__name__)


def check_key_status(headers: dict) -> bool:
    key = headers.get('key')
    return LoopsRepo().check_status(key) if key else False


@app.route('/online-parser-okx', methods=['GET', ])
def parser():
    headers = request.json
    if not check_key_status(headers):
        return jsonify({'status': 300, 'ok': False, 'message': 'wrong private key'})
    loop_id = headers.get('loop_id')
    currency_name = headers.get('currency_name')
    profit = headers.get('profit')
    amount = headers.get('amount')

    if loop_id:
        result = OKXTradeOnlineParser().main(
            loop_id=loop_id,
            currency_name=currency_name,
            profit=profit,
            amount=amount
        )
        return jsonify({
            'profit': result.profit,
            'amount': result.amount,
            'data': result.data
        })
    else:
        raise errors.GetLoopError(loop_id=f'{loop_id}')


if __name__ == "__main__":
    app.run(debug=True)
