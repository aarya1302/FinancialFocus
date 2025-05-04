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
    get_total_balance
)
from finance_recommendations import calculate_spending_limits

# Page configuration
st.set_page_config(
    page_title="Personal Finance Dashboard",
    page_icon="💰",
    layout="wide"
)

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
    
    # Get monthly income
    monthly_income = get_monthly_income()
    st.metric("Monthly Income", f"${monthly_income:.2f}")
    
    # Calculate estimated annual income
    st.metric("Estimated Annual Income", f"${monthly_income * 12:.2f}")
    
    # Navigation tabs in sidebar
    view_selection = st.radio(
        "Dashboard Views:",
        ["Expense Tracking", "Budgeting & Forecasting"]
    )
    
    st.markdown("---")
    st.markdown("""
    #### 💡 Data Source
    
    This dashboard is using mock data based on the Up Banking API format.
    For real usage, you would connect to your Up Banking account.
    """)

# Load and process data for visualizations
expenses_df = format_transactions_for_dashboard()

# Define the two main sections based on user selection
if view_selection == "Expense Tracking":
    st.header("📃 Expense Tracking")
    
    # Daily, Weekly, Monthly tabs for expense tracking
    tracking_tab = st.tabs(["Daily Expenses", "Weekly Breakdown", "Monthly Overview"])
    
    # Daily Expenses View
    with tracking_tab[0]:
        st.subheader("Today's Expenses")
        
        if not expenses_df.empty:
            # Filter for today's date
            today = datetime.now().date()
            today_expenses = expenses_df[expenses_df['date'].dt.date == today]
            
            if not today_expenses.empty:
                # Show today's expenses in a table
                today_expenses_display = today_expenses[['description', 'amount', 'category']].copy()
                today_expenses_display['amount'] = today_expenses_display['amount'].abs()
                today_expenses_display = today_expenses_display.rename(
                    columns={'description': 'Description', 'amount': 'Amount ($)', 'category': 'Category'}
                )
                today_expenses_display = today_expenses_display.sort_values('Amount ($)', ascending=False)
                
                st.dataframe(today_expenses_display, use_container_width=True)
                
                # Show total spent today
                total_today = today_expenses_display['Amount ($)'].sum()
                st.metric("Total Spent Today", f"${total_today:.2f}")
            else:
                # If no expenses today, show recent expenses from last 3 days
                three_days_ago = today - timedelta(days=3)
                recent_expenses = expenses_df[(expenses_df['date'].dt.date >= three_days_ago) & 
                                              (expenses_df['date'].dt.date <= today)]
                
                if not recent_expenses.empty:
                    st.info("No expenses recorded today. Here are your recent expenses:")
                    
                    recent_expenses_display = recent_expenses[['date', 'description', 'amount', 'category']].copy()
                    recent_expenses_display['amount'] = recent_expenses_display['amount'].abs()
                    recent_expenses_display = recent_expenses_display.rename(
                        columns={'date': 'Date', 'description': 'Description', 'amount': 'Amount ($)', 'category': 'Category'}
                    )
                    recent_expenses_display = recent_expenses_display.sort_values('Date', ascending=False)
                    
                    st.dataframe(recent_expenses_display, use_container_width=True)
                else:
                    st.info("No recent expenses found. Add some expenses to see them here.")
        else:
            st.info("No transaction data available")
    
    # Weekly Expenses View
    with tracking_tab[1]:
        st.subheader("Weekly Spending Breakdown")
        
        if not expenses_df.empty:
            # Get the current week's data (last 7 days)
            week_start = datetime.now().date() - timedelta(days=7)
            week_end = datetime.now().date()
            weekly_expenses = expenses_df[(expenses_df['date'].dt.date >= week_start) & 
                                       (expenses_df['date'].dt.date <= week_end)].copy()
            
            if not weekly_expenses.empty:
                # Make amounts positive for visualization
                weekly_expenses['amount'] = weekly_expenses['amount'].abs()
                
                # Add a day column for grouping
                weekly_expenses['day'] = weekly_expenses['date'].dt.date
                
                # Group by day and category
                daily_category_spend = weekly_expenses.groupby(['day', 'category'])['amount'].sum().reset_index()
                
                # Create a stacked bar chart showing daily spending by category
                fig = px.bar(
                    daily_category_spend,
                    x='day',
                    y='amount',
                    color='category',
                    title='Daily Spending by Category',
                    labels={'day': 'Date', 'amount': 'Amount ($)', 'category': 'Category'},
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig.update_layout(margin=dict(t=40, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)
                
                # Calculate weekly total
                weekly_total = weekly_expenses['amount'].sum()
                
                # Show category breakdown for the week
                st.subheader("Category Breakdown for This Week")
                weekly_by_category = weekly_expenses.groupby('category')['amount'].sum().reset_index()
                weekly_by_category = weekly_by_category.sort_values('amount', ascending=False)
                weekly_by_category['percentage'] = (weekly_by_category['amount'] / weekly_total * 100).round(1)
                weekly_by_category = weekly_by_category.rename(
                    columns={'amount': 'Amount ($)', 'category': 'Category', 'percentage': 'Percentage (%)'}
                )
                
                st.dataframe(weekly_by_category, use_container_width=True)
                st.metric("Total Weekly Spending", f"${weekly_total:.2f}")
            else:
                st.info("No expenses recorded in the past week.")
        else:
            st.info("No transaction data available")
    
    # Monthly Expenses View
    with tracking_tab[2]:
        st.subheader("Monthly Spending Overview")
        
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
                    monthly_totals = monthly_totals.rename(columns={'amount': 'Total Spent ($)', 'month': 'Month'})
                    
                    # Add month-over-month change
                    monthly_totals['Previous Month ($)'] = monthly_totals['Total Spent ($)'].shift(-1)
                    monthly_totals['Change (%)'] = ((monthly_totals['Total Spent ($)'] / monthly_totals['Previous Month ($)'] - 1) * 100).round(1)
                    monthly_totals = monthly_totals.fillna('-')
                    
                    st.dataframe(monthly_totals, use_container_width=True)
            else:
                st.info("No expense data available for the current month")
        else:
            st.info("No transaction data available")

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

# Footer with quick tips
st.markdown("---")
st.markdown("""
#### 💡 Quick Financial Tips:

- **Track consistently**: Regular monitoring is key to financial awareness
- **Review weekly**: Weekly reviews help catch overspending early
- **Adjust as needed**: Adapt your budget as your circumstances change
- **Emergency fund first**: Build 3-6 months of expenses before other financial goals
- **Automate savings**: Set up automatic transfers to savings on payday
""")
