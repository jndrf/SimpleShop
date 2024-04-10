#!/usr/bin/env python3

import sqlite3

con = sqlite3.connect('database.db')
cur = con.cursor()

cur.execute('CREATE TABLE Customers(ID, Name, Road, HouseNumber, PostCode, Town);')
cur.execute('CREATE TABLE Products(ProductNumber, Name, Description, Price)')
cur.execute('CREATE TABLE Orders(OrderNumber, CustomerID, Cost, Status);')

cur.close()
con.commit()
con.close()
