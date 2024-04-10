#!/usr/bin/env python3

import sqlite3
from collections import namedtuple


OrderElement = namedtuple('OrderElement', ['product_number', 'quantity'])


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


def add_product(connection, Name, Description, Price):
    '''enter a new product into the database'''

    cursor = connection.cursor()
    id_max = cursor.execute('SELECT MAX(ProductNumber) FROM Products').fetchone()[0]
    if id_max is None:
        id_max = 0
    values = [id_max + 1, Name, Description, Price]
    value_string = ', '.join(convert_list_for_insertion(values))
    cursor.execute(f'INSERT INTO Products VALUES({value_string})')
    connection.commit()
    return


def create_new_order(connection, customer, items):
    '''place a new order in the database

    connection: Connection object to an SQL database
    customer: customer ID. If the ID is not in the Customers table,
        a RuntimeError is raised
    items: list of OrderElement named tuples
    '''
    cursor = connection.cursor()

    # check that the customer actually exists
    customer_record = cursor.execute(f'SELECT * FROM Customers WHERE ID={customer}').fetchone()
    if customer_record is None:
        raise RuntimeError(f'Customer ID {customer} is not found in database!')

    # create a table containing this particular order
    id_max = cursor.execute('SELECT MAX(OrderNumber) FROM Orders').fetchone()[0]
    if id_max is None:
        id_max = 0
    order_id = id_max + 1
    cursor.execute(f'CREATE TABLE Order_{order_id}(ProductNumber, Quantity, TotalPrice)')
    for item in items:
        price = cursor.execute(
            f'SELECT Price FROM Products WHERE ProductNumber={item.product_number}'
        ).fetchone()[0]
        cursor.execute(
            f'INSERT INTO Order_{order_id} VALUES({item.product_number}, {item.quantity}, {price*item.quantity})'
        )

    # insert order into general list of orders
    total_price = cursor.execute(f'SELECT SUM(TotalPrice) FROM Order_{order_id}').fetchone()[0]
    cursor.execute(f'INSERT INTO Orders VALUES({order_id}, {customer}, {total_price}, "in_preparation")')
    connection.commit()

    return

if __name__ == '__main__':
    con = sqlite3.connect('database.db')
    create_customer(con, Name='Erika Mustermann', Road='Zum Beispiel',
                    HouseNumber=1, PostCode=42838, Town='Bielefeld')
    create_customer(con, Name='Hans Wurst', PostCode=27895, Town='Irgendwo')
    create_customer(con, Name='Otto Normalbürger', Road='Standardstraße', HouseNumber=2, PostCode=84901, Town='DINslaken')
    add_product(con, Name='Popel', Description='süß und saftig', Price=1.8)
    add_product(con, Name='Taschentuch', Description='sanft und sicher, 10 Stück je Packung', Price=0.3)
    create_new_order(con, 3, [OrderElement(1, 3), OrderElement(2, 1)])
    con.close()
