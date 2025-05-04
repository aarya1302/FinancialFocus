'''
Service to handle Up Banking API operations and format conversions
'''

import pandas as pd
from datetime import datetime
import os
import json
from mock_data import get_accounts_data, get_transactions_data, get_categories_data

# Check if we have an API token or should use mock data
API_TOKEN = os.environ.get('UP_API_TOKEN')
USE_MOCK_DATA = API_TOKEN is None

def get_accounts():
    """Get accounts data from Up API or mock data"""
    if USE_MOCK_DATA:
        return get_accounts_data()
    
    # Use real API
    import requests
    
    url = "https://api.up.com.au/api/v1/accounts"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}"
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
    if USE_MOCK_DATA:
        return get_transactions_data()
    
    # Use real API
    import requests
    
    url = "https://api.up.com.au/api/v1/transactions?page[size]=100"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}"
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
    if USE_MOCK_DATA:
        return get_categories_data()
    
    # Use real API
    import requests
    
    url = "https://api.up.com.au/api/v1/categories"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}"
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
        
        formatted_data.append({
            'date': transaction['attributes']['settledAt'][:10],  # Use just the date part
            'description': transaction['attributes']['description'],
            'amount': float(transaction['attributes']['amount']['value']),
            'category': category_name,
            'account_id': transaction['relationships']['account']['data']['id'],
        })
    
    # Convert to DataFrame for easier processing
    df = pd.DataFrame(formatted_data)
    
    # Add a month column for grouping
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.strftime('%Y-%m')
    
    return df

def get_monthly_income():
    """Calculate monthly income from transactions"""
    df = format_transactions_for_dashboard()
    
    if df.empty:
        return 0.0
    
    # Filter income transactions (positive amounts)
    income_df = df[df['amount'] > 0]
    
    # Get current month's income or most recent month if current month has no data
    current_month = datetime.now().strftime('%Y-%m')
    monthly_income = income_df[income_df['month'] == current_month]['amount'].sum()
    
    # If no income for current month, use most recent month with income
    if monthly_income == 0 and not income_df.empty:
        most_recent_month = income_df['month'].max()
        monthly_income = income_df[income_df['month'] == most_recent_month]['amount'].sum()
    
    return monthly_income

def get_monthly_expenses_by_category():
    """Get monthly expenses grouped by category"""
    df = format_transactions_for_dashboard()
    
    if df.empty:
        return {}
    
    # Filter expense transactions (negative amounts) and make them positive for easier processing
    expenses_df = df[df['amount'] < 0].copy()
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
