'''
Service to handle Up Banking API operations and format conversions
'''

import pandas as pd
from datetime import datetime
import os
import json
from mock_data import get_accounts_data, get_transactions_data, get_categories_data
import streamlit as st

def get_accounts():
    """Get accounts data from Up API or mock data"""
    if st.session_state.get('USE_MOCK_DATA', False):
        return get_accounts_data()
    
    # Use real API
    import requests
    
    url = "https://api.up.com.au/api/v1/accounts"
    headers = {
        "Authorization": f"Bearer {st.session_state['UP_API_TOKEN']}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
    except Exception as e:
        print(f"Error fetching accounts: {str(e)}")
        # Fallback to mock data if API fails
        return get_accounts_data()

def get_transactions():
    """Get transactions data from Up API or mock data"""
    if st.session_state.get('USE_MOCK_DATA', False):
        return get_transactions_data()
    
    # Use real API
    import requests
    
    url = "https://api.up.com.au/api/v1/transactions?page[size]=100"
    headers = {
        "Authorization": f"Bearer {st.session_state['UP_API_TOKEN']}"
    }
    
    try:
        # Initial request
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        all_transactions = data['data']
        
        # Fetch additional pages if available
        while 'next' in data['links'] and data['links']['next']:
            response = requests.get(data['links']['next'], headers=headers)
            response.raise_for_status()
            data = response.json()
            all_transactions.extend(data['data'])
            
            # Limit to 500 transactions to avoid excessive API calls
            if len(all_transactions) >= 500:
                break
        
        # Return in the same format as mock data
        return {'data': all_transactions}
    except Exception as e:
        print(f"Error fetching transactions: {str(e)}")
        # Fallback to mock data if API fails
        return get_transactions_data()

def get_categories():
    """Get categories data from Up API or mock data"""
    if st.session_state.get('USE_MOCK_DATA', False):
        return get_categories_data()
    
    # Use real API
    import requests
    
    url = "https://api.up.com.au/api/v1/categories"
    headers = {
        "Authorization": f"Bearer {st.session_state['UP_API_TOKEN']}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching categories: {str(e)}")
        # Fallback to mock data if API fails
        return get_categories_data()

def get_total_balance():
    """Calculate total balance across all accounts"""
    accounts = get_accounts()
    total = 0.0
    
    for account in accounts['data']:
        total += float(account['attributes']['balance']['value'])
    
    return total

def format_transactions_for_dashboard():
    """Convert Up Banking transaction format to a format suitable for the dashboard"""
    transactions = get_transactions()
    categories = get_categories()
    
    # Create a lookup dictionary for category names
    category_lookup = {}
    for category in categories['data']:
        category_lookup[category['id']] = category['attributes']['name']
    
    # Process transaction data
    formatted_data = []
    for transaction in transactions['data']:
        # Skip internal transfers between accounts to avoid double counting
        if transaction['relationships']['category']['data'] and transaction['relationships']['category']['data']['id'] == 'transfer':
            continue
            
        category_id = None
        if transaction['relationships']['category']['data']:
            category_id = transaction['relationships']['category']['data']['id']
        
        category_name = category_lookup.get(category_id, 'Uncategorized') if category_id else 'Uncategorized'
        
        # Include the full datetime and message field
        settled_at = transaction['attributes'].get('settledAt')
        created_at = transaction['attributes'].get('createdAt')
        date_value = settled_at or created_at or None
        transaction_data = {
            'date': pd.to_datetime(date_value, utc=True) if date_value else None,
            'description': transaction['attributes']['description'],
            'amount': float(transaction['attributes']['amount']['value']),
            'category': category_name,
            'account_id': transaction['relationships']['account']['data']['id'],
            'raw_text': transaction['attributes'].get('rawText', ''),
            'tags': [tag['id'] for tag in transaction['relationships'].get('tags', {}).get('data', [])] if 'tags' in transaction['relationships'] else [],
            'transactionType': transaction['attributes'].get('transactionType', '')
        }
        
        # Add message if available
        if 'message' in transaction['attributes'] and transaction['attributes']['message']:
            transaction_data['message'] = transaction['attributes']['message']
        
        formatted_data.append(transaction_data)
    
    # Convert to DataFrame for easier processing
    df = pd.DataFrame(formatted_data)
    
    # Add a month column for grouping
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.strftime('%Y-%m')
    
    return df

def get_monthly_income():
    """Calculate monthly income from salary transactions only"""
    df = format_transactions_for_dashboard()
    if df.empty:
        return 0.0
    # Only include salary transactions for the current month
    current_month = datetime.now().strftime('%Y-%m')
    salary_df = df[(df['transactionType'] == 'Salary') & (df['month'] == current_month)]
    monthly_income = salary_df['amount'].sum()
    return monthly_income

def get_estimated_annual_income():
    """Estimate annual income by summing all salary transactions for the previous month and multiplying by 12"""
    df = format_transactions_for_dashboard()
    if df.empty:
        return 0.0, 0.0, [], pd.DataFrame(), None
    # Only include salary transactions
    salary_df = df[df['transactionType'] == 'Salary']
   
    # Find the previous month with salary
    all_months = sorted(salary_df['month'].unique())
    if len(all_months) < 2:
        # Not enough data for previous month, fallback to most recent
        prev_month = all_months[-1]
    else:
        prev_month = all_months[-2]
    prev_salary_df = salary_df[salary_df['month'] == prev_month]
    monthly_salary = prev_salary_df['amount'].sum()
    return monthly_salary * 12

def get_monthly_expenses_by_category():
    """Get monthly expenses grouped by category"""
    df = format_transactions_for_dashboard()
    
    if df.empty:
        return {}
    
    # Filter expense transactions (negative amounts) and make them positive for easier processing
    expenses_df = df[(df['amount'] < 0) & (~df['transactionType'].isin(['Transfer', 'Round Up']))].copy()
    expenses_df['amount'] = expenses_df['amount'].abs()
    
    # Get current month's expenses
    current_month = datetime.now().strftime('%Y-%m')
    current_month_df = expenses_df[expenses_df['month'] == current_month]
    
    # If no data for current month, use most recent month
    if current_month_df.empty and not expenses_df.empty:
        most_recent_month = expenses_df['month'].max()
        current_month_df = expenses_df[expenses_df['month'] == most_recent_month]
    
    # Group by category
    if not current_month_df.empty:
        category_expenses = current_month_df.groupby('category')['amount'].sum()
        return category_expenses.to_dict()
    
    return {}

def get_monthly_spending_trends():
    """Get monthly spending trends over time"""
    df = format_transactions_for_dashboard()
    
    if df.empty:
        return pd.DataFrame()
    
    # Filter expense transactions (negative amounts) and make them positive for easier processing
    expenses_df = df[df['amount'] < 0].copy()
    expenses_df['amount'] = expenses_df['amount'].abs()
    
    # Group by month and category
    monthly_data = expenses_df.groupby(['month', 'category'])['amount'].sum().reset_index()
    
    return monthly_data

def debug_up_api_service():
    st.header("🐞 up_api_service.py Debug View")
    df = format_transactions_for_dashboard()
    st.subheader("All Transactions DataFrame")
    st.write(df)
    st.subheader("Salary Transactions DataFrame")
    salary_df = df[df['transactionType'] == 'Salary']
    st.write(salary_df)
    current_month = datetime.now().strftime('%Y-%m')
    st.write(df[(df['transactionType'] == 'Salary') & (df['month'] == current_month)])

    st.subheader("All Months with Salary Transactions")
    all_months = sorted(salary_df['month'].unique())
    st.write(all_months)
    st.subheader("Previous Month Used for Annual Income")
    if len(all_months) < 2:
        prev_month = all_months[-1] if all_months else None
    else:
        prev_month = all_months[-2]
    st.write(prev_month)
    st.subheader("Annual Income Calculation")
    if prev_month:
        prev_salary_df = salary_df[salary_df['month'] == prev_month]
        monthly_salary = prev_salary_df['amount'].sum()
        st.write({
            "monthly_salary": monthly_salary,
            "estimated_annual_income": monthly_salary * 12
        })
    else:
        st.write("No salary data available for annual income calculation.")
