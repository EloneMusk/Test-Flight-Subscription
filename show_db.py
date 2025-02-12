import sqlite3

with sqlite3.connect('testflight.db') as conn:
    print('\nSubscriptions Table:')
    print('-' * 80)
    cursor = conn.execute('SELECT id, email, url, datetime(created_at, \'localtime\') as created_at FROM subscriptions')
    columns = [description[0] for description in cursor.description]
    print(' | '.join(columns))
    print('-' * 80)
    for row in cursor:
        print(' | '.join(str(value) for value in row))

    print('\nStatus History Table:')
    print('-' * 80)
    cursor = conn.execute('SELECT id, url, is_accepting, datetime(checked_at, \'localtime\') as checked_at FROM status_history')
    columns = [description[0] for description in cursor.description]
    print(' | '.join(columns))
    print('-' * 80)
    for row in cursor:
        print(' | '.join(str(value) for value in row))