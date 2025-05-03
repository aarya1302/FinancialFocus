def calculate_spending_limits(income):
    """
    Calculate recommended spending limits based on established financial guidelines.
    
    Uses the 50-30-20 rule as a baseline:
    - 50% for needs (housing, food, utilities, etc.)
    - 30% for wants (entertainment, etc.)
    - 20% for savings and debt repayment
    
    Parameters:
    income (float): Monthly income
    
    Returns:
    dict: Recommended spending limits for each category
    """
    # Basic needs (50%)
    needs = income * 0.5
    
    # Housing should be no more than 30% of income (research-backed guideline)
    housing = income * 0.3
    
    # Food should be 10-15% of income
    food = income * 0.12
    
    # Transportation should be 10-15% of income
    transportation = income * 0.12
    
    # Utilities should be 5-10% of income
    utilities = income * 0.07
    
    # Wants (30%)
    wants = income * 0.3
    
    # Entertainment should be 5-10% of income
    entertainment = income * 0.07
    
    # Personal expenses
    personal = income * 0.08
    
    # Healthcare
    healthcare = income * 0.06
    
    # Savings and debt repayment (20%)
    savings_debt = income * 0.2
    
    # Savings should be at least 10% of income
    savings = income * 0.1
    
    # Debt repayment should be no more than 15-20% of income
    debt = income * 0.1
    
    return {
        'Housing': housing,
        'Food': food,
        'Transportation': transportation,
        'Utilities': utilities,
        'Entertainment': entertainment,
        'Healthcare': healthcare,
        'Personal': personal,
        'Savings': savings,
        'Debt': debt,
        'Other': income * 0.05  # Buffer for miscellaneous expenses
    }

def get_financial_health_score(income, expenses):
    """
    Calculate a financial health score based on spending patterns.
    
    Parameters:
    income (float): Monthly income
    expenses (dict): Dictionary of expenses by category
    
    Returns:
    float: Financial health score (0-100)
    str: Description of financial health
    """
    if income <= 0:
        return 0, "Please enter your income for a financial health assessment"
    
    # Calculate recommended limits
    limits = calculate_spending_limits(income)
    
    # Calculate score based on how close to recommendations
    score = 100
    total_expenses = sum(expenses.values())
    
    # Check if total expenses exceed income
    if total_expenses > income:
        score -= 30
    
    # Check individual categories
    for category, limit in limits.items():
        if category in expenses:
            if expenses[category] > limit:
                # Deduct points for exceeding limit
                overage_percent = (expenses[category] - limit) / limit
                score -= min(15, overage_percent * 100)
    
    # Check savings rate
    savings_rate = (income - total_expenses) / income if income > 0 else 0
    if savings_rate < 0.1:  # Less than 10% savings
        score -= 20
    
    # Ensure score is within 0-100
    score = max(0, min(100, score))
    
    # Determine financial health category
    if score >= 80:
        description = "Excellent financial health"
    elif score >= 60:
        description = "Good financial health"
    elif score >= 40:
        description = "Fair financial health"
    else:
        description = "Needs improvement"
    
    return score, description

def get_spending_advice(income, expenses):
    """
    Generate specific spending advice based on current patterns.
    
    Parameters:
    income (float): Monthly income
    expenses (dict): Dictionary of expenses by category
    
    Returns:
    list: List of specific advice items
    """
    advice = []
    
    if income <= 0:
        return ["Please enter your income to receive personalized advice"]
    
    # Calculate recommended limits
    limits = calculate_spending_limits(income)
    
    # Total expenses
    total_expenses = sum(expenses.values())
    
    # Check if total expenses exceed income
    if total_expenses > income:
        advice.append("Your expenses exceed your income. Look for ways to reduce spending or increase income.")
    
    # Check individual categories
    for category, limit in limits.items():
        if category in expenses:
            if expenses[category] > limit * 1.2:  # 20% over limit
                advice.append(f"Your {category.lower()} expenses are significantly over the recommended limit. Consider reducing spending in this area.")
            elif expenses[category] > limit:
                advice.append(f"Your {category.lower()} expenses are slightly over the recommended limit.")
    
    # Check savings rate
    savings_rate = (income - total_expenses) / income if income > 0 else 0
    if savings_rate < 0.1:  # Less than 10% savings
        advice.append("Try to save at least 10% of your income for emergencies and future goals.")
    elif savings_rate < 0.2:  # Less than 20% savings
        advice.append("Consider increasing your savings rate to 20% for long-term financial security.")
    
    # If no specific issues, give general advice
    if not advice:
        advice.append("Your spending patterns align well with financial recommendations. Keep up the good work!")
    
    return advice
