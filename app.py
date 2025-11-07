import streamlit as st
import numpy as np
import pandas as pd

from db_functions import *

#sidebar 
st.sidebar.title("Inventory Management Dashboard")
option=st.sidebar.radio("Select Options",['Basic Information','Operational Tasks'])

#mainspace

st.title("Inventory and Supply Chain Dashboard")

#db connection
db = connected_to_db()
cursor = db.cursor(dictionary=True)

#===================Basic Information Page===================

if option=="Basic Information":
    st.header("Basic Metrices")

    #get Basic Info Message From db_functions
    basic_info = get_basic_info(cursor)

    cols = st.columns(3)
    key = list(basic_info.keys())

    for i in range(3):
        cols[i].metric(label=key[i],value=basic_info[key[i]])
    
    cols = st.columns(3)

    for i in range(3,6):
        cols[i-3].metric(label=key[i],value=basic_info[key[i]])
    
    st.divider()


    #=========================================================

    tables = additional_info(cursor)
    for label,table in tables.items():
        st.header(label)
        st.dataframe(pd.DataFrame(table))
        st.divider()

    
#   =========================================================operational task =========================================================

elif option == "Operational Tasks":
    st.header("Operational Task")
    selected_task = st.selectbox("choose an task",['Add New Product','Product History','Place Reorder','Receive Reorder'])
    # Add New Product
    if selected_task ==  "Add New Product":
        st.header("Add New Product")
        category = get_categories(cursor)
        supplier = get_supplier(cursor)

        with st.form("Add_Product_Form"):
            product_name = st.text_input("Product_Name")
            product_category = st.selectbox("category",category)
            product_price = st.number_input("price",min_value=0.00)
            product_quantity = st.number_input("stock quantity",min_value=0.00)
            product_reorder_level = st.number_input("reorder level",min_value=0.00)

            supplier_ids = [s["supplier_id"] for s in supplier]
            supplier_names = [s['supplier_name'] for s in supplier]

            supplier_id = st.selectbox("supplier",options=supplier_ids,
                                       format_func=lambda x: supplier_names[supplier_ids.index(x)])
            
            submitted = st.form_submit_button("Add Product")
            
            if submitted==True:
                if not product_name:
                    st.error("Please enter the product name")
                else:
                    try:
                        AddNewProductManualID(cursor,
                                              db,product_name,
                                              product_category,
                                              product_price,
                                              product_quantity,
                                              product_reorder_level,supplier_id)
                        st.success(f"product {product_name} added sucessfully")
                    
                    except Exception as e:
                        st.error(f"error adding product {e}")   
#------------------------------------------------------Product Inventory History-------------------------------------------------------
    elif selected_task == "Product History":
        st.header("Product Inventory History")

        #get Product list
        products = get_all_products(cursor)
        product_ids = [p['product_id'] for p in products]
        product_names = [p['product_name'] for p in products]
        
        select_product_name = st.selectbox("select a product",options=product_names)
        
        if select_product_name:
            select_product_id = product_ids[product_names.index(select_product_name)]

            history_data = get_product_history(cursor,select_product_id)

            if history_data:
                df = pd.DataFrame(history_data)
                st.dataframe(df)
            else:
                st.info(f"no data Found for selected product")

# ------------------------------------------------------Place Reorder-------------------------------------------------------
    elif selected_task=="Place Reorder":
        st.header("Place an Reorder")
        products = get_all_products(cursor)
        product_ids = [p['product_id'] for p in products]
        product_names = [p['product_name'] for p in products]

        select_product_name = st.selectbox("Select an product",options=product_names)
        
        reorder_qty = st.number_input("reorder quantity",min_value=1,step=10)
        
        if st.button("place reorder"):

            if not select_product_name:
                st.error("Please Select the Product Name")
            
            elif reorder_qty<10:
                st.error("reorder quantity should be more then or equal to 10")
            
            else:
                select_product_id = product_ids[product_names.index(select_product_name)]
                try:
                    place_reorder(cursor,db,select_product_id,reorder_qty)

                    st.success(f'reorder place successfully')
                
                except Exception as e:
                    st.error(f"error place reorder {e}")
    elif selected_task == "Receive Reorder":
        st.header("Place a Reorder")