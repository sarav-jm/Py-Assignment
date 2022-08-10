import argparse
import os
from etl_process import extract_load_transform
#Testing
from flask import Flask, jsonify
from flask_restx import Api, Resource, reqparse, inputs

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('--csv-file', dest='csv_file',
                    default=None, help='Absolute path for input CSV file')
parser.add_argument('--db-file', required=True, dest='db_file',
                    help='Absolute path for Sqlite DB file')
# parser.add_argument('--debug', default=False, dest='debug', help='Enable or Disable Debugging', action=argparse.BooleanOptionalAction)
args = parser.parse_args()
if not vars(args):
    parser.print_help()
    parser.exit(0)

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


api = Api(
    app, version='1.0', title='orders API',
    description='A simple orders API',
)


ns = api.namespace('orders', description='orders operations')

order_parser = reqparse.RequestParser(bundle_errors=True)
order_parser.add_argument('date_from', type=inputs.date_from_iso8601,
                          required=True, help='(eg: 2020-12-01)', location='args')
order_parser.add_argument('date_to', type=inputs.date_from_iso8601,
                          required=True, help='(eg: 2020-12-31)', location='args')
order_parser.add_argument(
    'ticker', type=str, required=True, help='(eg: OBJY)', location='args')

select_order_table_cols = ', '.join([
    'order_id', 'ticker', 'side', 'amount', 'create_date_time', 'security_name', 'filled_amount'
])
select_fill_table_cols = ', '.join([
    'order_id', 'fill_price', 'fill_amount', 'fill_as_of_date_time'
])


@ns.route('/search')
class OrdersList(Resource):
    '''Shows a list of all orders by date_from and date_to range with or without ticker values'''
    @ns.doc('list_orders')
    @api.expect(order_parser)
    def get(self):
        '''List all orders by date range and ticker'''
        data = order_parser.parse_args()
        date_from = data['date_from']
        date_to = data['date_to']
        ticker = data['ticker']
        where_clause = []
        if date_from is not None:
            if date_to is not None:
                where_clause.append(
                    'create_date_time between "%s" and "%s"' % (date_from, date_to))
            else:
                where_clause.append('create_date_time = "%s"' % date_from)
        if ticker is not None:
            where_clause.append(' ticker = "%s"' % ticker)
        if not where_clause:
            api.abort(
                400, "Missing query params `date_from=2021-12-01&date_to=2021-12-31` or `ticker=OBJY` or combine them both")

        _o_df = pd.read_sql_query(
            'SELECT %s FROM order_table where %s' % (select_order_table_cols, ' and '.join(where_clause)), disk_engine)
        order_ids = ', '.join(map(str, _o_df['order_id'].unique()))
        _f_df = pd.read_sql_query(
            'SELECT %s FROM fill_table where order_id in (%s)' % (select_fill_table_cols,order_ids), disk_engine)
        r_json = []

        for o_dict in _o_df.to_dict(orient='records'):
            fills_dict = _f_df[_f_df['order_id'] ==
                                    o_dict['order_id']].drop('order_id', axis=1).to_dict(orient='records')
            o_dict['fills'] = fills_dict
            r_json.append(o_dict)
        return jsonify(r_json)


@ns.route('/get/<int:id>')
@ns.response(404, 'Order not found')
@ns.param('id', 'The order identifier')
class Order(Resource):

    @ns.doc('get_order')
    def get(self, id):
        '''Fetch order by given order id'''
        _o_df = pd.read_sql_query(
            'SELECT %s FROM order_table where order_id = %s' % (select_order_table_cols, str(id)), disk_engine)
        _f_df = pd.read_sql_query(
            'SELECT %s FROM fill_table where order_id = %s' % (select_fill_table_cols, str(id)), disk_engine)
        try:
            r_json = _o_df.to_dict(orient='records')[0]
            r_json['fills'] = _f_df.drop('order_id', axis=1).to_dict(orient='records')
            return jsonify(r_json)
        except IndexError as ie:
            return api.abort(404, "Order {} doesn't exist".format(id))


summay_parser = order_parser.copy()
summay_parser.add_argument(
    'order_id', type=str, required=True, help='(eg: 3520557)', location='args')


@ns.route('/summary')
@ns.response(404, 'Order not found')
class OrderSummary(Resource):

    '''Shows a summary of an order by date_from and date_to range with order_id and ticker values'''
    @ns.doc('summary_order')
    @api.expect(summay_parser)
    def get(self):
        '''Summary of an order by date_from and date_to range with order_id and ticker values'''
        data = summay_parser.parse_args()
        order_id = data['order_id']
        date_from = data['date_from']
        date_to = data['date_to']
        ticker = data['ticker']
        where_clause = []
        if order_id is not None:
            where_clause.append('order_id = %s' % order_id)
        if date_from is not None:
            if date_to is not None:
                where_clause.append(
                    'create_date_time between "%s" and "%s"' % (date_from, date_to))
            else:
                where_clause.append('create_date_time = "%s"' % date_from)
        if ticker is not None:
            where_clause.append(' ticker = "%s"' % ticker)
        if not where_clause:
            api.abort(
                400, "Missing query params `date_from=2021-12-01&date_to=2021-12-31` or `ticker=GUT` or combine them both")

        _o_df = pd.read_sql_query(
            'SELECT order_id, ticker, status, create_date_time FROM order_table where %s' % ' and '.join(where_clause), disk_engine)
        order_ids = ', '.join(map(str, _o_df['order_id'].unique()))
        if not order_ids:
            api.abort(404, f"Order doesn't exist in the given date range", params=dict(
                order_id=order_id, ticker=ticker, date_range={"from": str(date_from), "to": str(date_to)}))
        _f_df = pd.read_sql_query(
            'SELECT order_id, ticker, fill_price, fill_as_of_date_time FROM fill_table where order_id in (%s)' % order_ids, disk_engine)
        _f_df_desc = _f_df.describe().round(4)

        if _o_df['status'][0] == 'Part-filled':
            fill_duration = None
        else:
            fill_duration = (pd.to_datetime(_f_df['fill_as_of_date_time'].max(
            )) - pd.to_datetime(_o_df['create_date_time'])[0]).total_seconds()

        r_json = {
            'order_id': int(order_ids),
            "ticker": _o_df['ticker'].values.tolist()[0],
            "average_price": _f_df_desc['fill_price']['mean'],
            "std_price": _f_df_desc['fill_price']['std'],
            "fill_duration": fill_duration
        }
        return jsonify(r_json)


if __name__ == '__main__':
    csv_file_path = args.csv_file
    sqlite_db_path = args.db_file
    is_db_found = True
    if not os.path.isfile(sqlite_db_path) and not csv_file_path:
        is_db_found = False
        raise SQLAlchemyError(
            'Sqlite DB is not found! Verify the path[%s]' % sqlite_db_path)

    disk_engine = create_engine(f'sqlite:///{sqlite_db_path}')

    if csv_file_path is not None:
        if os.path.isfile(csv_file_path):
            extract_load_transform(csv_file_path, disk_engine, is_db_found)
        else:
            raise FileNotFoundError(csv_file_path)

    app.run(port=4444, host='0.0.0.0')
