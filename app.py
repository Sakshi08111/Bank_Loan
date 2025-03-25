import streamlit as st
import numpy as np
import pickle
import mysql.connector
from mysql.connector import Error
import pandas as pd
import os
import traceback


    

def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='',
            database='bankloan'
        )
        if connection.is_connected():
            print("Connected to MySQL")
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None

connection = create_connection()

# Load the model safely - use this instead of your current code
try:
    # Try to find the model in several possible locations
    possible_paths = [
        "build.pkl",  # Same directory
        os.path.join(os.path.dirname(__file__), "build.pkl"),  # Next to script
        r"C:\Users\A2Z\Desktop\Cloud\build.pkl"  # Your original path
    ]
    
    model = None
    for model_path in possible_paths:
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    model = pickle.load(f)
                st.success(f"Model loaded successfully from {model_path}")
                break
            except Exception as e:
                st.warning(f"Found model at {model_path} but couldn't load: {e}")
    
    if model is None:
        st.error("Could not find or load model file in any of these locations:\n" + 
                "\n".join(possible_paths))
        st.stop()
        
except Exception as e:
    st.error(f"Error loading model: {e}\n{traceback.format_exc()}")
    st.stop()
st.title('Loan Approval Prediction')
st.write('Enter the details below to check your loan approval status.')

# Ensure correct feature names and align with model training data
input_data = pd.DataFrame([[
    customer_age, family_member, income, loan_amount, cibil_score, tenure,
    gender, married, education, self_employed, previous_loan_taken,
    property_area, customer_bandwidth
]], columns=[
    'Age', 'Dependents', 'ApplicantIncome', 'LoanAmount', 'Cibil_Score', 'Tenure',
    'Gender', 'Married', 'Education', 'Self_Employed', 'Previous_Loan_Taken',
    'Property_Area', 'Customer_Bandwith'  # Ensure correct spelling
])

# Map categorical data to numeric values (if necessary)
input_data['Gender'] = input_data['Gender'].map({'Male': 0, 'Female': 1})
input_data['Married'] = input_data['Married'].map({'Yes': 1, 'No': 0})
input_data['Education'] = input_data['Education'].map({'Graduate': 1, 'Not Graduate': 0})
input_data['Self_Employed'] = input_data['Self_Employed'].map({'Yes': 1, 'No': 0})
input_data['Previous_Loan_Taken'] = input_data['Previous_Loan_Taken'].map({'Yes': 1, 'No': 0})
input_data['Property_Area'] = input_data['Property_Area'].map({'Urban': 2, 'Semiurban': 1, 'Rural': 0})
input_data['Customer_Bandwith'] = input_data['Customer_Bandwith'].map({'Low': 0, 'Medium': 1, 'High': 2})

# Perform prediction
# Perform prediction
            prediction = model.predict(input_data)
            result = 'Loan Approved' if prediction[0] == 0 else 'Loan Rejected'
            st.success(result)

            # Save to MySQL
            conn = create_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO loan_applications 
                    (customer_age, family_member, income, loan_amount, cibil_score, tenure, gender, married, education, self_employed, previous_loan_taken, property_area, customer_bandwidth, prediction)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (customer_age, family_member, income, loan_amount, cibil_score, tenure, gender, married, education, self_employed, previous_loan_taken, property_area, customer_bandwidth, result))
                conn.commit()
                st.success("Data saved to database.")
                cursor.close()
                conn.close()
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.error("Model is not loaded. Please check the model file.")
