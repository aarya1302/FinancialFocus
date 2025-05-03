import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime
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
    
    st.markdown("---")
    st.markdown("""
    #### 💡 Data Source
    
    This dashboard is using mock data based on the Up Banking API format.
    For real usage, you would connect to your Up Banking account.
    """)


# Main content area
col1, col2 = st.columns(2)

# Process data for visualizations
expenses_df = format_transactions_for_dashboard()

# First visualization: Spending by Category
with col1:
    st.subheader("📊 Spending by Category")
    
    if not expenses_df.empty:
        # Filter for expenses (negative amounts) and make them positive for visualization
        category_expenses = get_monthly_expenses_by_category()
        
        if category_expenses:
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
                color_discrete_sequence=px.colors.qualitative.Pastel,
                hole=0.4
            )
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
            
            # Show the category breakdown in a table
            st.markdown("##### Category Breakdown")
            category_data = category_data.sort_values('amount', ascending=False)
            
            # Calculate percentage of total
            total_expenses = category_data['amount'].sum()
            category_data['percentage'] = (category_data['amount'] / total_expenses * 100).round(1)
            category_data = category_data.rename(columns={'amount': 'Amount ($)', 'category': 'Category', 'percentage': 'Percentage (%)'})
            
            st.dataframe(category_data, use_container_width=True)
        else:
            st.info("No expense data available for the current month")
    else:
        st.info("No transaction data available")

# Second visualization: Monthly Spending Trends
with col2:
    st.subheader("📈 Monthly Spending Trends")
    
    monthly_data = get_monthly_spending_trends()
    
    if not monthly_data.empty:
        # Create the line chart
        fig = px.line(
            monthly_data, 
            x='month', 
            y='amount',
            color='category',
            markers=True,
            labels={'month': 'Month', 'amount': 'Amount ($)', 'category': 'Category'},
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
        
        # Show total monthly spending
        st.markdown("##### Monthly Totals")
        monthly_totals = monthly_data.groupby('month')['amount'].sum().reset_index()
        monthly_totals = monthly_totals.sort_values('month', ascending=False)
        monthly_totals = monthly_totals.rename(columns={'amount': 'Total Spent ($)', 'month': 'Month'})
        
        # Add month-over-month change
        if len(monthly_totals) > 1:
            monthly_totals['Previous Month ($)'] = monthly_totals['Total Spent ($)'].shift(-1)
            monthly_totals['Change (%)'] = ((monthly_totals['Total Spent ($)'] / monthly_totals['Previous Month ($)'] - 1) * 100).round(1)
            monthly_totals = monthly_totals.fillna('-')
        
        st.dataframe(monthly_totals, use_container_width=True)
    else:
        st.info("No transaction data available for monthly trends")


# Research-backed spending recommendations
st.subheader("💡 Research-backed Spending Recommendations")

# Use the monthly income from the Up API data
monthly_income = get_monthly_income()

if monthly_income > 0:
    # Calculate recommended spending limits
    spending_limits = calculate_spending_limits(monthly_income)
    
    # Display the recommendations
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Housing", f"${spending_limits['Housing']:.2f}", "50-30-20 Rule")
        st.metric("Food", f"${spending_limits['Food']:.2f}", "10-15% of income")
        st.metric("Transportation", f"${spending_limits['Transportation']:.2f}", "10-15% of income")
    
    with col2:
        st.metric("Utilities", f"${spending_limits['Utilities']:.2f}", "5-10% of income")
        st.metric("Entertainment", f"${spending_limits['Entertainment']:.2f}", "5-10% of income")
        st.metric("Healthcare", f"${spending_limits['Healthcare']:.2f}", "5-10% of income")
    
    with col3:
        st.metric("Personal", f"${spending_limits['Personal']:.2f}", "5-10% of income")
        st.metric("Savings", f"${spending_limits['Savings']:.2f}", "20% of income")
        st.metric("Debt Repayment", f"${spending_limits['Debt']:.2f}", "15-20% of income")
    
    # Display the financial health explanation
    st.markdown("""
    #### Financial Health Guidelines
    
    The recommendations above are based on well-established financial guidelines:
    
    - **50-30-20 Rule**: 50% of income for needs, 30% for wants, 20% for savings/debt
    - **Housing Affordability**: Housing costs should not exceed 30% of monthly income
    - **Emergency Fund**: Aim to save 3-6 months of expenses for emergencies
    - **Debt Management**: Total debt payments should not exceed 36% of gross income
    
    Research shows that consistent tracking and setting realistic spending limits can lead to better financial outcomes.
    """)
    
    # Show current status compared to recommendations
    if not expenses_df.empty:
        st.subheader("Your Spending vs Recommendations")
        
        # Get monthly expenses by category
        category_expenses = get_monthly_expenses_by_category()
        
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
                
                comparison_data.append({
                    "Category": category,
                    "Recommended Limit ($)": limit,
                    "Current Spending ($)": spent,
                    "Percentage Used (%)": round(percentage, 1),
                    "Status": status
                })
            
            comparison_df = pd.DataFrame(comparison_data)
            
            # Color-code the status column
            def highlight_status(val):
                if val == "Under budget":
                    return 'background-color: #c6ecc6'
                else:
                    return 'background-color: #ffcccc'
            
            st.dataframe(comparison_df.style.applymap(highlight_status, subset=['Status']), use_container_width=True)
        else:
            st.info("No expense data available for the current month")
else:
    st.info("Income data not available to generate personalized spending recommendations")

# Footer with tips
st.markdown("---")
st.markdown("""
#### 💡 Quick Financial Tips:

- **Track consistently**: Regular monitoring is key to financial awareness
- **Review weekly**: Weekly reviews help catch overspending early
- **Adjust as needed**: Adapt your budget as your circumstances change
- **Emergency fund first**: Build 3-6 months of expenses before other financial goals
- **Automate savings**: Set up automatic transfers to savings on payday
""")
