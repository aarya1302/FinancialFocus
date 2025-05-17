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
    debug_up_api_service
)
from finance_recommendations import calculate_spending_limits
import up_api_service
import pytz

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
    div[data-testid="stSelectbox"] {border: 1px solid #f0f2f6; border-radius: 10px; padding: 5px;}
    div[data-testid="stSelectbox"] > div:first-child {background-color: #f7f7f7;}
    div[data-testid="stSelectbox"]:hover {border: 1px solid #c0c6d3;}
    
    /* Improve transaction list appearance */
    .transaction-row {padding: 10px 0; border-bottom: 1px solid #f0f2f6;}
    
    /* Make month headers stand out */
    h3 {color: #2c3e50; margin-bottom: 10px;}
</style>
""", unsafe_allow_html=True)

# App title and description
st.title("💰 Personal Finance Dashboard")
st.markdown("""
This minimalist dashboard helps you track your finances and stay on budget.
Research shows that regular tracking and visual feedback can significantly improve financial habits.
""")

# Sidebar for account summary and total balance
with st.sidebar:
    st.header("💵 Account Summary")
    
    # Display total balance
    total_balance = get_total_balance()
    st.metric("Total Balance", f"${total_balance:.2f}")
    
    # Get monthly income (salary only)
    monthly_income = get_monthly_income()
    st.metric("Monthly Income", f"${monthly_income:.2f}")
    
    # Calculate estimated annual income (salary only, based on most recent month * 12)
    
    
    annual_income_data = get_estimated_annual_income()
    st.metric("Annual Income", f"${annual_income_data:.2f}")
    
    st.caption("Monthly Income: Sum of all transactions with transactionType 'salary' for the current month.\nEstimated Annual Income: Sum of all 'salary' transactions for the previous month × 12.")

    
    # Add a note about how these are calculated
    st.caption("Monthly Income: Sum of all transactions with transactionType 'salary' for the current month.\nEstimated Annual Income: Sum of all 'salary' transactions for the most recent month × 12.")
    
    # Navigation tabs in sidebar
    view_selection = st.radio(
        "Dashboard Views:",
        ["Expense Tracking", "Budgeting & Forecasting"]
    )
    
    # Add a separator
    st.markdown("---")
    
    # Check for Up Banking API token
    import os
    if not os.environ.get('UP_API_TOKEN'):
        st.warning("""
        ⚠️ **You're viewing mock data**
        
        For real banking data, you'll need an Up Banking API token.
        Add the token to your environment variables as `UP_API_TOKEN`.
        
        [Get an Up Banking Token](https://api.up.com.au/getting_started)
        """)
    else:
        st.success("✅ Connected to Up Banking API")
        
    # Add link to documentation    
    st.markdown("""
    ---
    ### Documentation
    * [Up Banking API Reference](https://developer.up.com.au)
    * [Financial Guidelines](https://www.investopedia.com/terms/1/50-30-20-budget-rule.asp)
    """)
    
    st.markdown("---")
    st.markdown("""
    #### 💡 Data Source
    
    This dashboard is using mock data based on the Up Banking API format.
    For real usage, you would connect to your Up Banking account.
    """)

    # Add a debug toggle to the sidebar
    debug_mode = st.checkbox('Enable Debug View')

# Load and process data for visualizations
expenses_df = format_transactions_for_dashboard()

today = datetime.now()
# Find the Monday of the current week
monday = today - timedelta(days=today.weekday())
# List all days in the current week (Monday to Sunday)
week_days = [(monday + timedelta(days=i)).strftime("%a") for i in range(7)]
week_dates = [(monday + timedelta(days=i)).date() for i in range(7)]

# Define the two main sections based on user selection
if view_selection == "Expense Tracking":
    st.header("📃 Expense Tracking")
    
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
                    
                    # Create a stacked bar chart showing daily spending by category
                    fig = px.bar(
                        daily_category_spend,
                        x='day',
                        y='amount',
                        color='category',
                        title='Expenses by Day',
                        labels={'day': 'Date', 'amount': 'Amount ($)', 'category': 'Category'},
                        color_discrete_sequence=px.colors.qualitative.Bold,
                        text='category',  # Show category names in the bars
                        barmode='stack'    # Ensure bars are stacked
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
                    st.plotly_chart(fig, use_container_width=True)
                    
                    
                  
                    
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
                
                if category_expenses:
                    with col1:
                        # Create dataframe for visualization
                        category_data = pd.DataFrame({
                            'category': list(category_expenses.keys()),
                            'amount': list(category_expenses.values())
                        })
                        
                        # Create pie chart
                        fig = px.pie(
                            category_data, 
                            values='amount', 
                            names='category',
                            title='Monthly Spending by Category',
                            color_discrete_sequence=px.colors.qualitative.Pastel,
                            hole=0.4
                        )
                        fig.update_layout(margin=dict(t=40, b=0, l=0, r=0))
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        # Get monthly spending trends for line chart
                        monthly_data = get_monthly_spending_trends()
                        
                        if not monthly_data.empty:
                            # Create the line chart
                            fig = px.line(
                                monthly_data, 
                                x='month', 
                                y='amount',
                                color='category',
                                markers=True,
                                title='Monthly Spending Trends',
                                labels={'month': 'Month', 'amount': 'Amount ($)', 'category': 'Category'},
                                color_discrete_sequence=px.colors.qualitative.Pastel
                            )
                            fig.update_layout(margin=dict(t=40, b=0, l=0, r=0))
                            st.plotly_chart(fig, use_container_width=True)
                    
                    # Show the category breakdown in a table
                    st.subheader("Monthly Category Breakdown")
                    category_data = category_data.sort_values('amount', ascending=False)
                    
                    # Calculate percentage of total
                    total_expenses = category_data['amount'].sum()
                    category_data['percentage'] = (category_data['amount'] / total_expenses * 100).round(1)
                    category_data = category_data.rename(columns={'amount': 'Amount ($)', 'category': 'Category', 'percentage': 'Percentage (%)'})
                    
                    st.dataframe(category_data, use_container_width=True)
                    st.metric("Total Monthly Spending", f"${total_expenses:.2f}")
                    
                    # Show month-over-month comparison if we have multiple months of data
                    monthly_totals = monthly_data.groupby('month')['amount'].sum().reset_index()
                    if len(monthly_totals) > 1:
                        st.subheader("Month-over-Month Comparison")
                        monthly_totals = monthly_totals.sort_values('month', ascending=False)
                        
                        # Create a custom formatted table for display
                        st.markdown("#### Monthly Spending Comparison")
                        
                        # Display header
                        cols = st.columns([2, 2, 2, 2])
                        cols[0].markdown("**Month**")
                        cols[1].markdown("**Total Spent**")
                        cols[2].markdown("**Previous Month**")
                        cols[3].markdown("**Change**")
                        
                        # Display data rows
                        for i in range(len(monthly_totals)):
                            row = monthly_totals.iloc[i]
                            current_month = row['month']
                            current_amount = row['amount']
                            
                            prev_amount = monthly_totals[monthly_totals['month'] == current_month]['amount'].iloc[0] if i < len(monthly_totals)-1 else None
                            
                            # Calculate change
                            change_pct = 0
                            if i < len(monthly_totals)-1:
                                prev_amount = monthly_totals.iloc[i+1]['amount']
                                if prev_amount > 0:
                                    change_pct = ((current_amount / prev_amount) - 1) * 100
                            
                            # Create row
                            cols = st.columns([2, 2, 2, 2])
                            cols[0].markdown(f"{current_month}")
                            cols[1].markdown(f"${current_amount:.2f}")
                            
                            if i < len(monthly_totals)-1:
                                cols[2].markdown(f"${prev_amount:.2f}")
                                
                                # Format change
                                if change_pct > 0:
                                    cols[3].markdown(f":red[+{change_pct:.1f}%]")
                                elif change_pct < 0:
                                    cols[3].markdown(f":green[{change_pct:.1f}%]")
                                else:
                                    cols[3].markdown(f"{change_pct:.1f}%")
                            else:
                                cols[2].markdown(f"N/A")
                                cols[3].markdown(f"N/A")
                            
                            st.markdown("---") if i < len(monthly_totals)-1 else None
                else:
                    st.info("No expense data available for the current month")
            else:
                st.info("No transaction data available")
        except Exception as e:
            st.error(f"Error in Monthly Expenses view: {str(e)}")
            import traceback
            st.code(traceback.format_exc())

else:  # Budgeting & Forecasting view
    st.header("💱 Budgeting & Forecasting")
    
    # Get monthly income and expenses data
    monthly_income = get_monthly_income()
    category_expenses = get_monthly_expenses_by_category()
    expenses_df_for_forecast = format_transactions_for_dashboard()
    
    # Recommendations vs Actual Spending
    st.subheader("Spending Recommendations vs Actual Spending")
    
    if monthly_income > 0:
        # Calculate recommended spending limits
        spending_limits = calculate_spending_limits(monthly_income)
        
        # Display recommendations vs actuals side by side
        if category_expenses:
            # Create comparison data
            comparison_data = []
            for category, limit in spending_limits.items():
                # Try to map our category names to Up API category names (simplified approach)
                spent = 0
                for up_category, amount in category_expenses.items():
                    # Simple mapping based on substring matching
                    if category.lower() in up_category.lower() or up_category.lower() in category.lower():
                        spent += amount
                        break
                
                percentage = (spent / limit * 100) if limit > 0 else 0
                status = "Under budget" if spent <= limit else "Over budget"
                difference = limit - spent
                
                comparison_data.append({
                    "Category": category,
                    "Recommended Limit ($)": limit,
                    "Actual Spending ($)": spent,
                    "% of Limit": round(percentage, 1),
                    "Difference ($)": round(difference, 2),
                    "Status": status
                })
            
            comparison_df = pd.DataFrame(comparison_data)
            
            # Create a bar chart comparing recommended vs actual spending
            chart_data = comparison_df.copy()
            chart_data = chart_data.sort_values('Recommended Limit ($)', ascending=False)
            
            # Reorganize data for grouped bar chart
            bar_data = pd.DataFrame({
                'Category': chart_data['Category'],
                'Recommended': chart_data['Recommended Limit ($)'],
                'Actual': chart_data['Actual Spending ($)']
            })
            
            # Melt the data for easier plotting
            bar_data_melted = pd.melt(bar_data, 
                                     id_vars=['Category'],
                                     value_vars=['Recommended', 'Actual'],
                                     var_name='Type', 
                                     value_name='Amount')
            
            # Create bar chart
            fig = px.bar(bar_data_melted, 
                         x='Category', 
                         y='Amount',
                         color='Type',
                         barmode='group',
                         title='Recommended vs Actual Spending by Category',
                         labels={'Amount': 'Amount ($)'},
                         color_discrete_map={'Recommended': '#A9D18E', 'Actual': '#83C9FF'})
            
            fig.update_layout(margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
            
            # Display detailed table with color coding
            st.subheader("Detailed Budget Analysis")
            
            # Color-code the status column
            def highlight_status(val):
                if val == "Under budget":
                    return 'background-color: #c6ecc6'
                else:
                    return 'background-color: #ffcccc'
            
            st.dataframe(comparison_df.style.map(highlight_status, subset=['Status']), use_container_width=True)
            
            # Calculate total recommended and actual spending
            total_recommended = chart_data['Recommended Limit ($)'].sum()
            total_actual = chart_data['Actual Spending ($)'].sum()
            difference = total_recommended - total_actual
            status = "Under budget" if difference >= 0 else "Over budget"
            
            # Show overall budget status
            if status == "Under budget":
                st.success(f"Overall Budget Status: 👍 You're under budget by ${difference:.2f}")
            else:
                st.error(f"Overall Budget Status: ⚠️ You're over budget by ${abs(difference):.2f}")
        else:
            st.info("No expense data available for the current month")
    else:
        st.info("Income data not available to generate personalized spending recommendations")
    
    # Savings Forecast Section
    st.subheader("Savings Forecast")
    
    if monthly_income > 0 and not expenses_df_for_forecast.empty:
        # Calculate average monthly spending
        expenses_df_for_forecast['month'] = expenses_df_for_forecast['date'].dt.strftime('%Y-%m')
        expenses_df_for_forecast['amount_abs'] = expenses_df_for_forecast['amount'].abs()
        monthly_spending = expenses_df_for_forecast.groupby('month')['amount_abs'].sum().reset_index()
        avg_monthly_spending = monthly_spending['amount_abs'].mean()
        
        # Calculate monthly savings
        monthly_savings = monthly_income - avg_monthly_spending
        
        # Calculate recommended spending limits
        spending_limits = calculate_spending_limits(monthly_income)
        recommended_monthly_spending = sum(spending_limits.values()) - spending_limits['Savings']
        recommended_monthly_savings = spending_limits['Savings']
        
        # Create forecast for current and next 11 months (1 year total)
        months = []
        current_savings = []
        recommended_savings = []
        
        # Initialize with current month
        current_month = datetime.now().strftime('%Y-%m')
        current_month_date = datetime.strptime(current_month, '%Y-%m')
        
        # Current total savings (assume started at 0 at beginning of data)
        start_savings = 0
        
        # Generate monthly forecast
        for i in range(12):  # 12 months forecast
            month_date = current_month_date + timedelta(days=30*i)
            month_str = month_date.strftime('%Y-%m')
            months.append(month_str)
            
            # For current path (actual spending rates)
            if i == 0:
                current_savings.append(start_savings + monthly_savings)
            else:
                current_savings.append(current_savings[-1] + monthly_savings)
            
            # For recommended path (following budget recommendations)
            if i == 0:
                recommended_savings.append(start_savings + recommended_monthly_savings)
            else:
                recommended_savings.append(recommended_savings[-1] + recommended_monthly_savings)
        
        # Create dataframe for forecast chart
        forecast_data = pd.DataFrame({
            'Month': months,
            'Current Path': current_savings,
            'Recommended Path': recommended_savings
        })
        
        # Convert to long format for plotting
        forecast_long = pd.melt(forecast_data, 
                              id_vars=['Month'],
                              value_vars=['Current Path', 'Recommended Path'],
                              var_name='Savings Path', 
                              value_name='Savings Amount ($)')
        
        # Create forecast line chart
        fig = px.line(forecast_long, 
                     x='Month', 
                     y='Savings Amount ($)',
                     color='Savings Path',
                     markers=True,
                     title='12-Month Savings Forecast',
                     labels={'Month': 'Month', 'Savings Amount ($)': 'Savings Amount ($)'},
                     color_discrete_map={'Current Path': '#83C9FF', 'Recommended Path': '#A9D18E'})
        
        fig.update_layout(margin=dict(t=40, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
        
        # Display key metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Current Monthly Savings", f"${monthly_savings:.2f}", f"{(monthly_savings/monthly_income)*100:.1f}% of income")
        
        with col2:
            st.metric("Recommended Monthly Savings", f"${recommended_monthly_savings:.2f}", f"{(recommended_monthly_savings/monthly_income)*100:.1f}% of income")
        
        with col3:
            annual_difference = (recommended_savings[-1] - current_savings[-1])
            st.metric("Annual Savings Difference", 
                     f"${abs(annual_difference):.2f}",
                     f"{'+' if annual_difference > 0 else '-'}{abs(annual_difference/recommended_savings[-1])*100:.1f}% difference")
        
        # Insights about savings forecast
        st.subheader("Savings Insights")
        
        if monthly_savings < 0:
            st.error("⚠️ Your current spending exceeds your income, resulting in negative savings. Consider reducing expenses.")
        elif monthly_savings < recommended_monthly_savings:
            st.warning(f"⚠️ Your current savings rate of ${monthly_savings:.2f} per month is below the recommended ${recommended_monthly_savings:.2f}. Increasing your savings rate could significantly improve your financial future.")
        else:
            st.success(f"👍 Great job! Your current savings rate of ${monthly_savings:.2f} per month exceeds the recommended ${recommended_monthly_savings:.2f}.")
        
        # Add general savings advice
        st.info("""
        💡 **Savings Tips:**
        * An emergency fund covering 3-6 months of expenses is essential for financial security
        * Automating savings transfers can make it easier to stick to your savings goals
        * Consider increasing savings rates when you receive income boosts or bonuses
        """)
    else:
        st.info("Insufficient data to generate savings forecast. Please add income and expense data.")


if debug_mode:
    st.header('🐞 Debug View')
    debug_up_api_service()
    st.subheader('Environment Info')
    api_token = getattr(up_api_service, 'API_TOKEN', None)
    st.write({'API_TOKEN (masked)': api_token[:6] + '...' if api_token else None,
              'USE_MOCK_DATA': getattr(up_api_service, 'USE_MOCK_DATA', None)})

    st.subheader('Raw API Data')
    st.write('Accounts:')
    st.json(up_api_service.get_accounts())
    st.write('Categories:')
    st.json(up_api_service.get_categories())
    st.write('Transactions:')
    st.json(up_api_service.get_transactions())
    st.write("Annual Income:")
    st.write(up_api_service.get_estimated_annual_income())
    st.subheader('Processed DataFrames')
    st.write('expenses_df:')
    st.write(expenses_df)

if 'selected_day' not in st.session_state:
    st.session_state['selected_day'] = week_days[today.weekday()]

selected_day_label = st.session_state['selected_day']
selected_day_index = week_days.index(selected_day_label)
selected_date = week_dates[selected_day_index]

selected_date_df = this_month_expenses[
    (this_month_expenses['date'].dt.date == selected_date) &
    (~this_month_expenses['transactionType'].isin(['Transfer', 'Round Up']))
]

 

