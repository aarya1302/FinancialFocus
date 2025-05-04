# Personal Finance Dashboard

A minimalist personal finance dashboard with two key visualizations and research-backed spending recommendations using Streamlit. This dashboard provides insights into your financial health based on transaction data.

## Features

- **Account Summary**: View your total balance and monthly income
- **Spending by Category**: Visualize your spending distribution with an interactive pie chart
- **Monthly Spending Trends**: Track your spending patterns over time with a line chart
- **Research-backed Recommendations**: Get personalized spending limits based on the 50-30-20 rule
- **Financial Health Metrics**: Compare your actual spending to recommended limits

## Data Source

The dashboard is designed to work with the Up Banking API format. Currently, it uses mock data for demonstration purposes, but can be connected to a real Up Banking account by providing an API token.

## Installation

1. Clone this repository
2. Install the required packages:
   ```
   pip install streamlit pandas plotly numpy
   ```
3. Run the application:
   ```
   streamlit run app.py
   ```

## Usage

1. View your account summary and financial metrics in the sidebar
2. Explore the spending visualizations in the main area
3. Check the research-backed spending recommendations based on your income

## Research Background

The spending recommendations are based on well-established financial guidelines:

- **50-30-20 Rule**: 50% of income for needs, 30% for wants, 20% for savings/debt
- **Housing Affordability**: Housing costs should not exceed 30% of monthly income
- **Emergency Fund**: Aim to save 3-6 months of expenses for emergencies
- **Debt Management**: Total debt payments should not exceed 36% of gross income

Research shows that consistent tracking and setting realistic spending limits can lead to better financial outcomes.
