#!/usr/bin/env python3

import sqlite3


def convert_list_for_insertion(items):
    '''utility function to properly quote the strings'''
    stringified_items = []
    for item in items:
        if type(item) == str:
            conv = f'"{str(item)}"'
            stringified_items.append(conv)
        elif type(item) in [int, float]:
            stringified_items.append(str(item))

    return stringified_items


def create_customer(connection, **kwargs):
    '''insert a new customer into the database

    Customer ID is determined automatically,
    kwargs needs to contain column names of the Customer table of the DB.
    Note that entries can be omitted.

    connection: Connection object to an SQL database.
    '''
    cursor = connection.cursor()
    keys = ['Name', 'Road', 'HouseNumber', 'PostCode', 'Town']
    insert_keys = [key for key in kwargs.keys() if key in keys]
    insert_keys.insert(0, 'ID')
    key_string = ', '.join(insert_keys)
    values = [kwargs.get(key, None) for key in keys]
    id_max = cursor.execute('SELECT MAX(ID) FROM Customers').fetchone()[0]
    if id_max is None:          # Handle creation of first customer
        id_max = 0              # he'll get ID 1
    values.insert(0, id_max + 1)
    value_string = ', '.join(convert_list_for_insertion(values))
    cursor.execute(f'INSERT INTO Customers({key_string}) VALUES({value_string})')
    connection.commit()


def search_customers(connection, logic='and', **kwargs):
    '''search for customer ID

    connection: Connection object to an SQL database
    logic: either AND or OR, whether any or all search criteria need to be fulfilled.
    kwargs: column names in the Customer table to match

    returns: a list of customer IDs
    '''

    logic = logic.upper()

    # form column=value pairs

    stringified_values = convert_list_for_insertion(kwargs.values())
    pairs = [f'{k}={v}' for k, v in zip(kwargs.keys(), stringified_values)]
    pairs = f' {logic} '.join(pairs)

    cursor = connection.cursor()
    result = cursor.execute(f'SELECT ID FROM Customers WHERE {pairs}')

    return [item[0] for item in result.fetchall()]


if __name__ == '__main__':
    con = sqlite3.connect('database.db')
    # create_customer(con, Name='Erika Mustermann', Road='Zum Beispiel',
    #                 HouseNumber=1, PostCode=42838, Town='Bielefeld')
    # create_customer(con, Name='Hans Wurst', PostCode=27895, Town='Irgendwo')
    # create_customer()
    print(search_customers(con, logic='or', Town='Irgendwo', HouseNumber=1))
    con.close()
