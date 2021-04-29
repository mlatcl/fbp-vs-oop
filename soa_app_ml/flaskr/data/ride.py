from .db import get_db
from datetime import datetime, timedelta


# Insert a new ride request in the database
def insert_ride(ride):
    db = get_db()
    sql = 'INSERT INTO RideRequest (ride_id, user_id, from_lat, from_lon, to_lat, to_lon, last_lat, last_lon, '
    sql = sql + 'request_time, update_time, state) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) '
    sql = sql + 'ON CONFLICT(ride_id) DO UPDATE SET user_id = ?, from_lat = ?, from_lon = ?, to_lat = ?, to_lon = ?, '
    sql = sql + 'last_lat = ?, last_lon = ?, request_time = ?, update_time = ?, state = ?'
    values = [ride['ride_id'], ride['user_id'], ride['from_location']['lat'], ride['from_location']['lon'],
              ride['to_location']['lat'], ride['to_location']['lon'], ride['from_location']['lat'],
              ride['from_location']['lon'], datetime.strptime(ride['request_time'], '%Y-%m-%d %H:%M:%S.%f'),
              datetime.strptime(ride['request_time'], '%Y-%m-%d %H:%M:%S.%f'), ride['state'],
              ride['user_id'], ride['from_location']['lat'], ride['from_location']['lon'],
              ride['to_location']['lat'], ride['to_location']['lon'], ride['from_location']['lat'],
              ride['from_location']['lon'], datetime.strptime(ride['request_time'], '%Y-%m-%d %H:%M:%S.%f'),
              datetime.strptime(ride['request_time'], '%Y-%m-%d %H:%M:%S.%f'), ride['state']]
    cursor = db.execute(sql, values)
    db.commit()
    return cursor.lastrowid


# Insert a list of rides in the database
def insert_rides(rides):
    affected = 0
    for ride in rides:
        affected = insert_ride(ride)
    return affected


# Get list of ride requests
def get_all_rides():
    res = []
    db = get_db()
    sql = 'SELECT * FROM RideRequest'
    cursor = db.execute(sql)
    for ride in cursor:
        from_location = {'lat': ride['from_lat'], 'lon': ride['from_lon']}
        to_location = {'lat': ride['to_lat'], 'lon': ride['to_lon']}
        last_location = {'lat': ride['last_lat'], 'lon': ride['last_lon']}
        r = {'ride_id': ride['ride_id'], 'user_id': ride['user_id'], 'driver_id': ride['driver_id'],
             'from_location': from_location, 'to_location': to_location, 'last_location': last_location,
             'request_time': ride['request_time'].strftime('%Y-%m-%d %H:%M:%S.%f'),
             'allocation_time': ride['allocation_time'].strftime('%Y-%m-%d %H:%M:%S.%f'),
             'update_time': ride['update_time'].strftime('%Y-%m-%d %H:%M:%S.%f'),
             'state': ride['state'], 'event_type': ride['event_type'], 'evaluated':ride['evaluated']}
        res.append(r)
    return res


# Get rides by state:
def get_rides_by_state(state):
    res = []
    db = get_db()
    sql = 'SELECT * FROM RideRequest WHERE state = ?'
    values = [state]
    cursor = db.execute(sql, values)
    for ride in cursor:
        from_location = {'lat': ride['from_lat'], 'lon': ride['from_lon']}
        to_location = {'lat': ride['to_lat'], 'lon': ride['to_lon']}
        last_location = {'lat': ride['last_lat'], 'lon': ride['last_lon']}
        r = {'ride_id': ride['ride_id'], 'user_id': ride['user_id'], 'driver_id': ride['driver_id'],
             'from_location': from_location, 'to_location': to_location, 'last_location': last_location,
             'request_time': ride['request_time'].strftime('%Y-%m-%d %H:%M:%S.%f'),
             'allocation_time': ride['allocation_time'],
             'update_time': ride['update_time'].strftime('%Y-%m-%d %H:%M:%S.%f'),
             'state': ride['state'], 'event_type': ride['event_type']}
        res.append(r)
    return res


# Update ride request status
def update_ride(ride_id, info):
    db = get_db()
    sql = ''
    values = []
    for key, value in info.items():
        sql = sql + ' ' + key + ' = ?,'
        values.append(value)
    sql = sql[:-1]
    sql = 'UPDATE RideRequest SET' + sql + ' WHERE ride_id = ?'
    values.append(ride_id)
    cursor = db.execute(sql, values)
    db.commit()
    if cursor.rowcount > 0:
        return ride_id
    else:
        return None


# Update rides events
def update_rides_events(ride_events):
    affected = 0
    for ride_event in ride_events:
        ride_id = ride_event['ride_id']
        info = {'update_time': datetime.strptime(ride_event['event_time'], '%Y-%m-%d %H:%M:%S.%f'),
                'state': ride_event['ride_status'], 'event_type': ride_event['event_type'],
                'last_lat': ride_event['event_data']['location']['lat'],
                'last_lon': ride_event['event_data']['location']['lon']}
        res = update_ride(ride_id, info)
        if res is not None:
            affected = affected + 1
    return affected


# Update rides infos
def update_rides_infos(ride_infos):
    affected = 0
    for ride_info in ride_infos:
        ride_id = ride_info['ride_id']
        info = {'user_id': ride_info['user_id'], 'driver_id': ride_info['driver_id'],
                'update_time': ride_info['update_time'], 'last_lat': ride_info['last_location']['lat'],
                'last_lon': ride_info['last_location']['lon']}
        res = update_ride(ride_id, info)
        if res is not None:
            affected = affected + 1
    return affected


def update_ride_allocation(ride_allocation):
    affected = 0
    ride_id = ride_allocation['ride_id']
    info = {'driver_id': ride_allocation['driver_id'], 'allocation_time': datetime.now(), 'update_time': datetime.now(),
            'state': ride_allocation['state']}
    res = update_ride(ride_id, info)
    if res is not None:
        affected = affected + 1
    return affected


# Get ride infos
def get_ride_infos():
    ride_infos = []
    assigned = get_rides_by_state('DRIVER_ASSIGNED')
    enroute = get_rides_by_state('ENROUTE')
    for ride in assigned:
        ride_info = {'ride_id': ride['ride_id'], 'user_id': ride['user_id'], 'driver_id': ride['driver_id'],
                     'state': ride['state'], 'update_time': ride['update_time'],
                     'last_location': ride['last_location']}
        ride_infos.append(ride_info)
    for ride in enroute:
        ride_info = {'ride_id': ride['ride_id'], 'user_id': ride['user_id'], 'driver_id': ride['driver_id'],
                     'state': ride['state'], 'update_time': ride['update_time'],
                     'last_location': ride['last_location']}
        ride_infos.append(ride_info)
    return ride_infos


# Get ride wait times
def get_ride_wait_times():
    ride_wait_times = []
    db = get_db()
    sql = 'SELECT * FROM RideRequest WHERE state = ? AND evaluated is NULL'
    values = ['ENROUTE']
    cursor = db.execute(sql, values)
    for ride in cursor:
        wait_duration = ride['allocation_time'] - ride['request_time']
        wait_duration = wait_duration / timedelta(milliseconds=1)
        last_location = {'lat': ride['last_lat'], 'lon': ride['last_lon']}
        ride_wait_time = {'ride_id': ride['ride_id'],
                          'request_time': ride['request_time'].strftime('%Y-%m-%d %H:%M:%S.%f'),
                          'wait_duration': wait_duration, 'location': last_location}
        ride_wait_times.append(ride_wait_time)
        info = {'evaluated': 'done'}
        update_ride(ride['ride_id'], info)
    return ride_wait_times