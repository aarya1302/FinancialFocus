import json
import os
import streamlit as st
from datetime import datetime

# File to store the application data
DATA_FILE = "finance_data.json"

def load_data():
    """Load financial data from storage or return empty data structure"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        else:
            # Return default data structure
            return {
                'income': 0,
                'expenses': []
            }
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return {
            'income': 0,
            'expenses': []
        }

def save_data(data):
    """Save financial data to storage"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")
        return False

def get_current_month_data(data):
    """Extract the expenses for the current month"""
    current_month = datetime.now().strftime('%Y-%m')
    
    if 'expenses' not in data:
        return []
    
    current_month_expenses = []
    for expense in data['expenses']:
        expense_date = datetime.strptime(expense['date'], '%Y-%m-%d')
        if expense_date.strftime('%Y-%m') == current_month:
            current_month_expenses.append(expense)
    
    return current_month_expenses

def calculate_monthly_total(expenses):
    """Calculate total expenses for a list of expenses"""
    if not expenses:
        return 0
    
    return sum(expense['amount'] for expense in expenses)
