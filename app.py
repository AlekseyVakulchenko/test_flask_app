import psycopg2

from flask import Flask, render_template, redirect, url_for, request
from collections import namedtuple


conn = psycopg2.connect("dbname=flask_db user=postgres")
cursor = conn.cursor()


app = Flask(__name__)


@app.route('/')
def index():
    """
    Redirect to main endpoint
    :return:
    """
    return redirect(url_for('real_estate_objects'))


def named_tuple_fetch_all(curs):
    """
    Return all rows from a cursor as a namedtuple
    :param curs:
    :return:
    """

    desc = curs.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in curs.fetchall()]


@app.route('/object_list')
@app.route('/object_list/<int:object_id>')
def real_estate_objects(object_id=None):
    """
    Response list of real estate objects or detail information about real estate object
    :param object_id:
    :return:
    """
    if object_id:
        get_object_info = ("SELECT real_estate_object.real_estate_object_name  as name, address, floor, square, "
                           "array(select station.station_name FROM station "
                           "inner join real_estate_object_station "
                           "on station.station_id = real_estate_object_station.station_id "
                           "inner join real_estate_object "
                           "on real_estate_object.real_estate_object_id = real_estate_object_station.real_estate_object_id "
                           "where real_estate_object.real_estate_object_id = %s) as stations "
                           "FROM real_estate_object where real_estate_object.real_estate_object_id = %s")
        cursor.execute(get_object_info, [object_id, object_id])
        object_info = named_tuple_fetch_all(cursor)
        return render_template('real_estate_object.html', object_info=object_info)
    else:
        square = request.args.get('square')
        floor = request.args.get('floor')
        metro = request.args.get('metro', '')
        cur_filter = ''
        params = []
        filter_params = {
            'square': square,
            'floor': floor,
            'metro': metro,
        }

        if square:
            cur_filter += 'where square = %s'
            params.append(int(square))

        if floor:
            params.append(floor)
            if cur_filter:
                cur_filter += ' and floor = %s'
            else:
                cur_filter += 'where floor = %s'

        if metro:
            get_station = "SELECT station.station_id FROM station  where station.station_name ilike %s"
            cursor.execute(get_station, ['%{}%'.format(metro)])
            station_ids = named_tuple_fetch_all(cursor)
            tuple_of_station_id = tuple(row.station_id for row in station_ids)

            get_real_estate_object_id = ("SELECT real_estate_object_station.real_estate_object_id "
                                         "FROM real_estate_object_station "
                                         "where real_estate_object_station.station_id in %s")

            cursor.execute(get_real_estate_object_id, [tuple_of_station_id])
            real_estate_object_id = named_tuple_fetch_all(cursor)

            tuple_real_estate_object_id = tuple(row.real_estate_object_id for row in real_estate_object_id if row.real_estate_object_id)
            if not tuple_real_estate_object_id:
                return render_template('real_estate_objects.html', filter_params=filter_params)
            params.append(tuple_real_estate_object_id)

            if cur_filter:
                cur_filter += ' and real_estate_object_id in %s'
            else:
                cur_filter += 'where real_estate_object_id in %s'

        get_list_of_objects = ("SELECT real_estate_object.real_estate_object_name as name, "
                               "real_estate_object.real_estate_object_id as id FROM real_estate_object ")
        if cur_filter:
            get_list_of_objects += cur_filter
            cursor.execute(get_list_of_objects, params)
        else:
            cursor.execute(get_list_of_objects)
        object_list = named_tuple_fetch_all(cursor)

        return render_template('real_estate_objects.html', object_list=object_list, filter_params=filter_params)


if __name__ == '__main__':
    app.run()
