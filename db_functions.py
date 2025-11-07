import numpy as np
import pandas as pd
import mysql.connector

def connected_to_db():
    return mysql.connector.connect(host="localhost",
                               user="root",
                               password="123456",
                               database="supplychain")

print(connected_to_db().is_connected())


def get_basic_info(cursor):
    queries = {
        "Total Suppliers": """
            SELECT count(*) as total_suppliers 
            FROM suppliers;
        """,
    
        "Total Products": """
            SELECT count(*) as total_products 
            FROM products;
        """,
    
        "Total Categories Dealing": """
            SELECT count(distinct category) as total_category 
            FROM products;
        """,
    
        "Total Sales Value in Last 3 Months": """
            SELECT ROUND(SUM(ABS(se.change_quantity) * p.price), 2) AS total_sales_value_in_last_3_months
            FROM stock_entries AS se
            JOIN products p ON p.product_id = se.product_id
            WHERE se.change_type = 'Sale'
            AND se.entry_date >= (
                SELECT DATE_SUB(MAX(entry_date), INTERVAL 3 MONTH) 
                FROM stock_entries WHERE change_type="sale"               
            );
        """,
    
        "Total Restock Value in Last 3 Months": """
            SELECT ROUND(SUM(ABS(t2.change_quantity) * t1.price), 2) AS total_restock_value_in_last_3_months
            FROM products t1
            JOIN stock_entries t2 ON t1.product_id = t2.product_id
            WHERE t2.change_type = 'Restock'
            AND t2.entry_date >= (
                SELECT DATE_SUB(MAX(entry_date), INTERVAL 3 MONTH) 
                FROM stock_entries
            );
        """,
    
        "Products to Restock": """
            SELECT count(*) AS items_to_restock
            FROM products p
            WHERE p.stock_quantity < p.reorder_level
            AND p.product_id NOT IN (
                SELECT DISTINCT product_id 
                FROM reorders 
                WHERE status = 'Pending'
            );    
        """
    }
    result = {}

    for label,querie in queries.items():
        cursor.execute(querie)
        row = cursor.fetchone()
        result[label]=list(row.values())[0]
    return result

#======================================================================================================================

def additional_info(cursor):
    queries = {
         "supplier contact details":
    
    """SELECT supplier_name,contact_name,email,phone  FROM suppliers;""",
    
    "Product With there Supplier and Current stock":"""SELECT product_name,supplier_name,stock_quantity as current_stock_quantity,reorder_level   FROM suppliers t1
    JOIN products t2
    ON t1.supplier_id = t2.supplier_id
    ORDER BY product_name;
    """,
    
    "Product needing Reorder":"""SELECT product_id,product_name,stock_quantity,reorder_level from products 
    WHERE stock_quantity<reorder_level;"""
    
    
    }

    result = {}
    for label,querie in queries.items():
        cursor.execute(querie)
        row = cursor.fetchall()
        result[label]=row

    return result
    

#=========================================================Operational Task ================================================================


# Add new product

def  AddNewProductManualID(cursor,db,p_name,p_category,p_price,p_stock,p_reorder,p_supplier):
    proc_call = "call  AddNewProductManualID(%s, %s, %s, %s, %s, %s)"
    params = p_name,p_category,p_price,p_stock,p_reorder,p_supplier
    cursor.execute(proc_call, params)
    db.commit()


def get_categories(cursor):
    k="SELECT DISTINCT category FROM products ORDER BY category"
    cursor.execute(k)
    rows=cursor.fetchall()
    mylist = []
    for row in rows:
        #print(row['category'])
        mylist.append(row['category'])
    return mylist


def get_supplier(cursor):
    cursor.execute("SELECT supplier_id,supplier_name from suppliers order by supplier_name")
    return cursor.fetchall()

#--------------------------------------------------------Product History---------------------------------------------------------

def get_all_products(cursor):
    query = """SELECT product_id,product_name FROM products 
               ORDER BY product_name"""
    
    cursor.execute(query)
    return cursor.fetchall()

def get_product_history(cursor,product_id):

    query = """SELECT * FROM product_inventory_history 
               WHERE product_id = %s 
               ORDER BY record_date DESC"""
    
    cursor.execute(query,(product_id,))  ### check - execute works with tuple not a single integer
    return cursor.fetchall()

def place_reorder(cursor,db,product_id,reorder_quantity):
    query = """
               insert into reorders(reorder_id,product_id,reorder_quantity,reorder_date,status)
               SELECT MAX(reorder_id)+1,
               %s, %s,
               curdate(),
               "ordered"
               FROM reorders
               """
    cursor.execute(query,(product_id,reorder_quantity))
    db.commit()


