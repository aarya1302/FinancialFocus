import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
import calendar
from up_api_service import (
    format_transactions_for_dashboard, 
    get_monthly_income,
    get_monthly_expenses_by_category,
    get_monthly_spending_trends,
    get_total_balance,
    get_estimated_annual_income, 
  
)
from finance_recommendations import calculate_spending_limits
import up_api_service
import pytz
from streamlit_cookies_manager import EncryptedCookieManager

# Page configuration
st.set_page_config(
    page_title="Personal Finance Dashboard",
    page_icon="💰",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Style for the date picker */
    div[data-testid="stSelectbox"] {border: 1px solid #f0f2f6; border-radius: 10px; padding: 2px;}
    div[data-testid="stSelectbox"] > div:first-child {background-color: #f7f7f7;}
    div[data-testid="stSelectbox"]:hover {border: 1px solid #c0c6d3;}
    
    /* Improve transaction list appearance */
    .transaction-row {padding: 4px 0; border-bottom: 1px solid #f0f2f6;}
    
    /* Make month headers stand out */
    h3 {color: #2c3e50; margin-bottom: 6px;}

    /* Reduce padding/margin for main container */
    .block-container {padding-top: 1rem; padding-bottom: 1rem;}
    section.main > div {padding-top: 0.3rem; padding-bottom: 0.3rem;}

    /* Hide Streamlit footer and hamburger menu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Add this CSS to make the tab content fill the viewport and be scrollable if needed */
    .block-container {
        padding-top: 0.3rem;
        padding-bottom: 0.5rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        margin-bottom: 0;
    }
    .stTabs [data-baseweb="tab-panel"] {
        height: calc(100vh - 120px); /* Adjust 120px if your header is taller/shorter */
        overflow-y: auto;
        padding-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# --- LOGIN PAGE ---
cookies = EncryptedCookieManager(
    prefix="up_finance_",  # Optional: helps avoid collisions
    password="your-very-secret-password"  # Change this to something secret!
)
if not cookies.ready():
    st.stop()

# Check for token in cookie first
if 'UP_API_TOKEN' not in st.session_state:
    st.session_state['UP_API_TOKEN'] = cookies.get('UP_API_TOKEN', '')

if 'USE_MOCK_DATA' not in st.session_state:
    st.session_state['USE_MOCK_DATA'] = cookies.get('USE_MOCK_DATA', False)

if not st.session_state['UP_API_TOKEN'] and not st.session_state['USE_MOCK_DATA']:
    st.title("🔒 Login to Financial Dashboard")
    st.markdown("""
    Please enter your Up Banking API token to access your personal finance dashboard.
    [Get an Up Banking Token](https://api.up.com.au/getting_started)
    """)
    
    # Add mock data mode toggle
    use_mock_data = st.checkbox("Use Mock Data Mode (for testing/development)")
    
    if not use_mock_data:
        api_token_input = st.text_input("Up Banking API Token", type="password")
        if st.button("Login"):
            if api_token_input:
                st.session_state['UP_API_TOKEN'] = api_token_input
                st.session_state['USE_MOCK_DATA'] = False
                cookies['UP_API_TOKEN'] = api_token_input
                cookies['USE_MOCK_DATA'] = False
                cookies.save()
                st.rerun()
            else:
                st.error("Please enter a valid API token.")
    else:
        if st.button("Enter Mock Mode"):
            st.session_state['UP_API_TOKEN'] = ''
            st.session_state['USE_MOCK_DATA'] = True
            cookies['UP_API_TOKEN'] = ''
            cookies['USE_MOCK_DATA'] = True
            cookies.save()
            st.rerun()
    st.stop()

# Add a logout button
if st.button("Logout"):
    st.session_state['UP_API_TOKEN'] = ''
    st.session_state['USE_MOCK_DATA'] = False
    cookies['UP_API_TOKEN'] = ''
    cookies['USE_MOCK_DATA'] = False
    cookies.save()
    st.experimental_rerun()

# Load and process data for visualizations
expenses_df = format_transactions_for_dashboard()

today = datetime.now()
# Find the Monday of the current week
monday = today - timedelta(days=today.weekday())
# List all days in the current week (Monday to Sunday)
week_days = [(monday + timedelta(days=i)).strftime("%a") for i in range(7)]
week_dates = [(monday + timedelta(days=i)).date() for i in range(7)]

# Define the two main sections based on user selection
with st.container():
    cols = st.columns([3, 1, 1])
    with cols[0]:
        st.header("📃 Expense Tracking")
    with cols[1]:
        total_balance = get_total_balance()
        st.metric("Total Balance", f"${total_balance:.2f}")
    with cols[2]:
        donate_url = "https://buy.stripe.com/test_eVq7sNfF8f22g171t5gw000"  # Change to your donation link
        st.markdown(f"""
            <a href="{donate_url}" target="_blank">
                <button style='background-color:#FFD700; color:black; border:none; padding:0.5em 1.2em; border-radius:6px; font-size:1.1em; font-weight:bold; cursor:pointer;'>☕ Donate</button>
            </a>
        """, unsafe_allow_html=True)
    
    # Daily, Weekly, Monthly tabs for expense tracking
    tracking_tab = st.tabs(["Daily Expenses", "Weekly Breakdown", "Monthly Overview"])
    
    # Daily Expenses View
    with tracking_tab[0]:
        try:
            if not expenses_df.empty:
                # Get the current month name and year
                current_month = datetime.now().strftime("%B %Y")
                
                # Calculate the total spent this month
                this_month_expenses = expenses_df[expenses_df['date'].dt.strftime('%Y-%m') == datetime.now().strftime('%Y-%m')].copy()
                total_month = this_month_expenses['amount'].abs().sum()
                
                # Calculate average monthly spending
                previous_months = expenses_df['date'].dt.strftime('%Y-%m').unique()
                if len(previous_months) > 1:
                    usual_spending = this_month_expenses['amount'].abs().sum() / len(this_month_expenses)
                    difference = total_month - usual_spending
                    difference_text = f"${abs(difference):.2f} {'more' if difference > 0 else 'less'} than usual"
                else:
                    difference_text = ""
                
                # Get unique days in the current month with transactions
                unique_days = sorted(this_month_expenses['date'].dt.day.unique())
                if 'selected_day' not in st.session_state:
                    st.session_state['selected_day'] = week_days[today.weekday()]
                selected_day_label = st.session_state['selected_day']
                selected_day_index = week_days.index(selected_day_label)
                selected_date = week_dates[selected_day_index]

                # Filter transactions for the selected day, excluding 'Transfer' and 'Round Up'
                selected_date_df = this_month_expenses[
                    (this_month_expenses['date'].dt.date == selected_date) &
                    (~this_month_expenses['transactionType'].isin(['Transfer', 'Round Up']))
                ]
                day_total = selected_date_df['amount'].sum()
                st.info("Only transactions coming in and out of your bank account are included. Transfers or round ups between savings accounts (e.g., 'Transfer', 'Round Up') are excluded from this view.")
                # Show total spend
                 # Display totals and transaction count in a nice layout
                summary_cols = st.columns([3, 1])
                with summary_cols[0]:
                    st.markdown(f"**{len(selected_date_df)} transactions on selected date**")
                with summary_cols[1]:
                    st.markdown(f"### ${day_total:.2f}")
                
                # Show transaction list with reduced padding
                for idx, row in selected_date_df.iterrows():
                    st.markdown(
                        f"<div style='padding:4px 0; border-bottom:1px solid #eee;'>"
                        f"<b>{row['description']}</b> <span style='float:right;'>${row['amount']:.2f}</span>"
                        f"</div>", unsafe_allow_html=True
                    )
                
            
                
               
               
                
                
               
            else:
                st.info("No transaction data available")
        except Exception as e:
            st.error(f"Error in Daily Expenses view: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
    
    # Weekly Expenses View
    with tracking_tab[1]:
        st.subheader("Weekly Spending Breakdown")
        
        try:
            if not expenses_df.empty:
                perth_tz = pytz.timezone("Australia/Perth")
                # Convert the 'date' column to Perth time zone
                expenses_df['date_perth'] = expenses_df['date'].dt.tz_convert(perth_tz)
                today_perth = datetime.now(perth_tz).date()
                # Set week_start to the most recent Monday and week_end to the upcoming Sunday
                week_start = today_perth - timedelta(days=today_perth.weekday())
                week_end = week_start + timedelta(days=6)
                
                weekly_expenses = expenses_df[
                    (expenses_df['date_perth'].dt.date >= week_start) &
                    (expenses_df['date_perth'].dt.date <= week_end) &
                    (~expenses_df['transactionType'].isin(['Transfer', 'Round Up']))
                ].copy()
   
                if not weekly_expenses.empty:
                    # Add a day column for grouping
                    weekly_expenses['day'] = weekly_expenses['date'].dt.date
                    weekly_expenses['day_name'] = weekly_expenses['date'].dt.strftime('%a')
                    
                    # Before grouping for the chart, filter for expenses only
                    weekly_expenses_expense_only = weekly_expenses[weekly_expenses['amount'] < 0]
                    daily_category_spend = weekly_expenses_expense_only.groupby(['day', 'day_name', 'category'])['amount'].sum().reset_index()
                    daily_category_spend['amount'] = daily_category_spend['amount'].abs()  # Ensure all amounts are positive
                    
                    # Calculate total amount spent for each day
                    daily_totals = daily_category_spend.groupby('day')['amount'].sum().reset_index()
                    daily_totals['total_text'] = daily_totals['amount'].apply(lambda x: f"${x:.2f}")

                    # Create a stacked bar chart showing daily spending by category
                    fig = px.bar(
                        daily_category_spend,
                        x='day',
                        y='amount',
                        color='category',
                        title='Expenses by Day',
                        labels={'day': 'Date', 'amount': 'Amount ($)', 'category': 'Category'},
                        color_discrete_sequence=px.colors.qualitative.Prism,
                        text='category',  # Show category names in the bars
                        barmode='stack'    # Ensure bars are stacked
                    )

                    # Add total amount spent for each day on top of the chart
                    for i, row in daily_totals.iterrows():
                        fig.add_annotation(
                            x=row['day'],
                            y=row['amount'],
                            text=row['total_text'],
                            showarrow=False,
                            yshift=10
                        )
                    
                    # Customize the layout for a cleaner look
                    fig.update_layout(
                        margin=dict(t=40, b=0, l=0, r=0),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        xaxis=dict(title="Day of Week", tickformat="%a, %b %d"),
                        yaxis=dict(title="Amount ($)"),
                        plot_bgcolor='#1E1E1E',
                        bargap=0.2
                    )
                    
                    # Hide category text inside small bars
                    fig.update_traces(textposition='none')

                        # Calculate weekly total
                    weekly_total = weekly_expenses[weekly_expenses['amount'] < 0]['amount'].abs().sum()
                    
                    # Show weekly summary
                    st.metric("Total Weekly Spending", f"${weekly_total:.2f}")
                    
                    # Display the chart
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                    
                    
                  
                    
                    # Add information about the date range
                    st.markdown(f"*Showing data from {week_start.strftime('%B %d, %Y')} to {week_end.strftime('%B %d, %Y')}*")
                    
                    # Get categories shown in the bar chart
                    categories_in_chart = daily_category_spend['category'].unique()
                 
               
                else:
                    st.info("No expenses recorded in the past week.")
            else:
                st.info("No transaction data available")
        except Exception as e:
            st.error(f"Error in Weekly Expenses view: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
    
    # Monthly Expenses View
    with tracking_tab[2]:
        st.subheader("Monthly Spending Overview")
        
        try:
            if not expenses_df.empty:
                # Create columns for visualizations
                col1, col2 = st.columns(2)
                
                # Get monthly expenses by category
                category_expenses = get_monthly_expenses_by_category()

                # Calculate percentage of total
          
                if category_expenses:

                    # Create dataframe for visualization
                    category_data = pd.DataFrame({
                        'category': list(category_expenses.keys()),
                        'amount': list(category_expenses.values())
                    })
                    
                    category_data = category_data.sort_values('amount', ascending=False)
                    total_expenses = category_data['amount'].sum()
                    category_data['percentage'] = (category_data['amount'] / total_expenses * 100).round(1)
                    category_data = category_data.rename(columns={'amount': 'Amount ($)', 'category': 'Category', 'percentage': 'Percentage (%)'})
                    

                    st.metric("Total Monthly Spending", f"${total_expenses:.2f}")
                    # Create pie chart
                    fig = px.pie(
                        category_data, 
                        values='Amount ($)', 
                        names='Category',
                        title='Monthly Spending by Category',
                        color_discrete_sequence=px.colors.qualitative.Pastel,
                        hole=0.4
                    )
                    fig.update_layout(margin=dict(t=40, b=0, l=0, r=0))
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                 
                    
                   
                else:
                    st.info("No expense data available for the current month")
            else:
                st.info("No transaction data available")
        except Exception as e:
            st.error(f"Error in Monthly Expenses view: {str(e)}")
            import traceback
            st.code(traceback.format_exc())

if 'selected_day' not in st.session_state:
    st.session_state['selected_day'] = week_days[today.weekday()]

selected_day_label = st.session_state['selected_day']
selected_day_index = week_days.index(selected_day_label)
selected_date = week_dates[selected_day_index]


