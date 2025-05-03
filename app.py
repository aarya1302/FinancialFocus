import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime
import calendar
from utils import load_data, save_data
from finance_recommendations import calculate_spending_limits

# Page configuration
st.set_page_config(
    page_title="Personal Finance Dashboard",
    page_icon="💰",
    layout="wide"
)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = load_data()

# App title and description
st.title("💰 Personal Finance Dashboard")
st.markdown("""
This minimalist dashboard helps you track your finances and stay on budget.
Research shows that regular tracking and visual feedback can significantly improve financial habits.
""")

# Sidebar for data input
with st.sidebar:
    st.header("💵 Income & Expenses")
    
    # Income input
    st.subheader("Monthly Income")
    income = st.number_input("Enter your monthly income ($)", 
                            min_value=0.0, 
                            value=float(st.session_state.data['income']) if 'income' in st.session_state.data else 0.0,
                            step=100.0)
    
    # Expense input
    st.subheader("Add Expense")
    expense_date = st.date_input("Date", datetime.now())
    expense_category = st.selectbox(
        "Category",
        ["Housing", "Food", "Transportation", "Utilities", "Entertainment", "Healthcare", "Personal", "Debt", "Other"]
    )
    expense_amount = st.number_input("Amount ($)", min_value=0.0, step=10.0)
    expense_description = st.text_input("Description (optional)")
    
    if st.button("Add Expense"):
        # Update expenses data
        new_expense = {
            'date': expense_date.strftime('%Y-%m-%d'),
            'category': expense_category,
            'amount': expense_amount,
            'description': expense_description
        }
        
        if 'expenses' not in st.session_state.data:
            st.session_state.data['expenses'] = []
        
        st.session_state.data['expenses'].append(new_expense)
        st.session_state.data['income'] = income
        save_data(st.session_state.data)
        st.success("Expense added successfully!")
        st.rerun()

# Main content area
col1, col2 = st.columns(2)

# Process data for visualizations
expenses_df = pd.DataFrame()
if 'expenses' in st.session_state.data and st.session_state.data['expenses']:
    expenses_df = pd.DataFrame(st.session_state.data['expenses'])
    expenses_df['date'] = pd.to_datetime(expenses_df['date'])
    expenses_df['month'] = expenses_df['date'].dt.strftime('%Y-%m')

# First visualization: Spending by Category
with col1:
    st.subheader("📊 Spending by Category")
    
    if not expenses_df.empty:
        # Group expenses by category
        category_data = expenses_df.groupby('category')['amount'].sum().reset_index()
        
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
        st.info("Add expenses to see your spending by category")

# Second visualization: Monthly Spending Trends
with col2:
    st.subheader("📈 Monthly Spending Trends")
    
    if not expenses_df.empty:
        # Group by month and category
        monthly_data = expenses_df.groupby(['month', 'category'])['amount'].sum().reset_index()
        
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
        monthly_totals = expenses_df.groupby('month')['amount'].sum().reset_index()
        monthly_totals = monthly_totals.sort_values('month', ascending=False)
        monthly_totals = monthly_totals.rename(columns={'amount': 'Total Spent ($)', 'month': 'Month'})
        
        # Add month-over-month change
        if len(monthly_totals) > 1:
            monthly_totals['Previous Month ($)'] = monthly_totals['Total Spent ($)'].shift(-1)
            monthly_totals['Change (%)'] = ((monthly_totals['Total Spent ($)'] / monthly_totals['Previous Month ($)'] - 1) * 100).round(1)
            monthly_totals = monthly_totals.fillna('-')
        
        st.dataframe(monthly_totals, use_container_width=True)
    else:
        st.info("Add expenses to see your monthly spending trends")

# Research-backed spending recommendations
st.subheader("💡 Research-backed Spending Recommendations")

if 'income' in st.session_state.data and st.session_state.data['income'] > 0:
    income = st.session_state.data['income']
    
    # Calculate recommended spending limits
    spending_limits = calculate_spending_limits(income)
    
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
        
        # Get current month expenses
        current_month = datetime.now().strftime('%Y-%m')
        current_month_df = expenses_df[expenses_df['month'] == current_month]
        
        if not current_month_df.empty:
            current_spending = current_month_df.groupby('category')['amount'].sum().to_dict()
            
            # Create comparison data
            comparison_data = []
            for category, limit in spending_limits.items():
                spent = current_spending.get(category, 0)
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
            st.info(f"No expense data for the current month ({current_month})")
else:
    st.info("Enter your monthly income to get personalized spending recommendations")

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
