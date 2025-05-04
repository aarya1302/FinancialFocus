'''
Mock data following the Up Banking API format
'''

from datetime import datetime, timedelta

accounts_data = {
    "data": [
        {
            "type": "accounts",
            "id": "1001",
            "attributes": {
                "name": "Main Account",
                "balance": {
                    "currencyCode": "AUD",
                    "value": "4325.78",
                    "valueInBaseUnits": 432578
                },
                "accountType": "TRANSACTIONAL"
            }
        },
        {
            "type": "accounts",
            "id": "1002",
            "attributes": {
                "name": "Savings Account",
                "balance": {
                    "currencyCode": "AUD",
                    "value": "2750.42",
                    "valueInBaseUnits": 275042
                },
                "accountType": "SAVER"
            }
        }
    ]
}

transactions_data = {
    "data": [
        {
            "type": "transactions",
            "id": "tx-001",
            "attributes": {
                "description": "Coles Supermarket",
                "message": "Weekly groceries",
                "amount": {
                    "currencyCode": "AUD",
                    "value": "-85.24",
                    "valueInBaseUnits": -8524
                },
                "rawText": "COLES SUPERMARKET",
                "createdAt": "2023-06-01T12:00:00+11:00",
                "settledAt": "2023-06-01T13:00:00+11:00"
            },
            "relationships": {
                "account": { "data": { "type": "accounts", "id": "1001" }},
                "category": { "data": { "type": "categories", "id": "groceries" }},
                "tags": { "data": [ { "type": "tags", "id": "weekly" } ]}
            }
        },
        {
            "type": "transactions",
            "id": "tx-002",
            "attributes": {
                "description": "Netflix",
                "message": "Monthly subscription",
                "amount": {
                    "currencyCode": "AUD",
                    "value": "-15.99",
                    "valueInBaseUnits": -1599
                },
                "rawText": "NETFLIX AU",
                "createdAt": "2023-06-02T10:00:00+11:00",
                "settledAt": "2023-06-02T11:00:00+11:00"
            },
            "relationships": {
                "account": { "data": { "type": "accounts", "id": "1001" }},
                "category": { "data": { "type": "categories", "id": "entertainment" }},
                "tags": { "data": [ { "type": "tags", "id": "subscription" } ]}
            }
        },
        {
            "type": "transactions",
            "id": "tx-003",
            "attributes": {
                "description": "Rent Payment",
                "message": "Monthly rent",
                "amount": {
                    "currencyCode": "AUD",
                    "value": "-1800.00",
                    "valueInBaseUnits": -180000
                },
                "rawText": "RENT TRANSFER",
                "createdAt": "2023-06-03T09:00:00+11:00",
                "settledAt": "2023-06-03T10:00:00+11:00"
            },
            "relationships": {
                "account": { "data": { "type": "accounts", "id": "1001" }},
                "category": { "data": { "type": "categories", "id": "housing" }},
                "tags": { "data": [ { "type": "tags", "id": "monthly" } ]}
            }
        },
        {
            "type": "transactions",
            "id": "tx-004",
            "attributes": {
                "description": "Uber",
                "message": "Trip home",
                "amount": {
                    "currencyCode": "AUD",
                    "value": "-32.50",
                    "valueInBaseUnits": -3250
                },
                "rawText": "UBER AU",
                "createdAt": "2023-06-04T22:00:00+11:00",
                "settledAt": "2023-06-04T23:00:00+11:00"
            },
            "relationships": {
                "account": { "data": { "type": "accounts", "id": "1001" }},
                "category": { "data": { "type": "categories", "id": "transportation" }},
                "tags": { "data": [ { "type": "tags", "id": "travel" } ]}
            }
        },
        {
            "type": "transactions",
            "id": "tx-005",
            "attributes": {
                "description": "Salary",
                "message": "Monthly payment",
                "amount": {
                    "currencyCode": "AUD",
                    "value": "4850.00",
                    "valueInBaseUnits": 485000
                },
                "rawText": "SALARY CREDIT",
                "createdAt": "2023-06-15T09:00:00+11:00",
                "settledAt": "2023-06-15T10:00:00+11:00"
            },
            "relationships": {
                "account": { "data": { "type": "accounts", "id": "1001" }},
                "category": { "data": { "type": "categories", "id": "income" }},
                "tags": { "data": [ { "type": "tags", "id": "salary" } ]}
            }
        },
        {
            "type": "transactions",
            "id": "tx-006",
            "attributes": {
                "description": "Woolworths",
                "message": "Grocery shopping",
                "amount": {
                    "currencyCode": "AUD",
                    "value": "-67.82",
                    "valueInBaseUnits": -6782
                },
                "rawText": "WOOLWORTHS",
                "createdAt": "2023-06-18T15:00:00+11:00",
                "settledAt": "2023-06-18T16:00:00+11:00"
            },
            "relationships": {
                "account": { "data": { "type": "accounts", "id": "1001" }},
                "category": { "data": { "type": "categories", "id": "groceries" }},
                "tags": { "data": [ { "type": "tags", "id": "food" } ]}
            }
        },
        {
            "type": "transactions",
            "id": "tx-007",
            "attributes": {
                "description": "Electricity Bill",
                "message": "Quarterly payment",
                "amount": {
                    "currencyCode": "AUD",
                    "value": "-210.75",
                    "valueInBaseUnits": -21075
                },
                "rawText": "ENERGY AUSTRALIA",
                "createdAt": "2023-06-20T11:00:00+11:00",
                "settledAt": "2023-06-20T12:00:00+11:00"
            },
            "relationships": {
                "account": { "data": { "type": "accounts", "id": "1001" }},
                "category": { "data": { "type": "categories", "id": "utilities" }},
                "tags": { "data": [ { "type": "tags", "id": "bills" } ]}
            }
        },
        {
            "type": "transactions",
            "id": "tx-008",
            "attributes": {
                "description": "Savings Transfer",
                "message": "Monthly savings",
                "amount": {
                    "currencyCode": "AUD",
                    "value": "-500.00",
                    "valueInBaseUnits": -50000
                },
                "rawText": "TRANSFER TO SAVINGS",
                "createdAt": "2023-06-25T08:00:00+11:00",
                "settledAt": "2023-06-25T09:00:00+11:00"
            },
            "relationships": {
                "account": { "data": { "type": "accounts", "id": "1001" }},
                "category": { "data": { "type": "categories", "id": "transfer" }},
                "tags": { "data": [ { "type": "tags", "id": "savings" } ]}
            }
        },
        {
            "type": "transactions",
            "id": "tx-009",
            "attributes": {
                "description": "Savings Deposit",
                "message": "Transfer from main account",
                "amount": {
                    "currencyCode": "AUD",
                    "value": "500.00",
                    "valueInBaseUnits": 50000
                },
                "rawText": "TRANSFER FROM MAIN",
                "createdAt": "2023-06-25T08:00:00+11:00",
                "settledAt": "2023-06-25T09:00:00+11:00"
            },
            "relationships": {
                "account": { "data": { "type": "accounts", "id": "1002" }},
                "category": { "data": { "type": "categories", "id": "transfer" }},
                "tags": { "data": [ { "type": "tags", "id": "savings" } ]}
            }
        },
        {
            "type": "transactions",
            "id": "tx-010",
            "attributes": {
                "description": "Restaurant",
                "message": "Dinner with friends",
                "amount": {
                    "currencyCode": "AUD",
                    "value": "-78.50",
                    "valueInBaseUnits": -7850
                },
                "rawText": "RESTAURANT CHARGE",
                "createdAt": "2023-06-28T20:00:00+11:00",
                "settledAt": "2023-06-28T21:00:00+11:00"
            },
            "relationships": {
                "account": { "data": { "type": "accounts", "id": "1001" }},
                "category": { "data": { "type": "categories", "id": "dining" }},
                "tags": { "data": [ { "type": "tags", "id": "social" } ]}
            }
        }
    ]
}

categories_data = {
    "data": [
        {
            "type": "categories",
            "id": "income",
            "attributes": {
                "name": "Income",
                "parent": None
            }
        },
        {
            "type": "categories",
            "id": "housing",
            "attributes": {
                "name": "Housing",
                "parent": None
            }
        },
        {
            "type": "categories",
            "id": "food-and-drink",
            "attributes": {
                "name": "Food & Drink",
                "parent": None
            }
        },
        {
            "type": "categories",
            "id": "groceries",
            "attributes": {
                "name": "Groceries",
                "parent": "food-and-drink"
            }
        },
        {
            "type": "categories",
            "id": "dining",
            "attributes": {
                "name": "Dining Out",
                "parent": "food-and-drink"
            }
        },
        {
            "type": "categories",
            "id": "utilities",
            "attributes": {
                "name": "Utilities",
                "parent": None
            }
        },
        {
            "type": "categories",
            "id": "transportation",
            "attributes": {
                "name": "Transportation",
                "parent": None
            }
        },
        {
            "type": "categories",
            "id": "entertainment",
            "attributes": {
                "name": "Entertainment",
                "parent": None
            }
        },
        {
            "type": "categories",
            "id": "transfer",
            "attributes": {
                "name": "Transfers",
                "parent": None
            }
        }
    ]
}

def get_accounts_data():
    """Return mock accounts data"""
    return accounts_data

def get_transactions_data():
    """Return mock transactions data with some transactions having current dates"""
    # Create a copy of the original data
    current_data = transactions_data.copy()
    
    # Get current date and time
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%dT%H:%M:%S+11:00")
    yesterday_str = (now - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S+11:00")
    two_days_ago_str = (now - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S+11:00")
    three_days_ago_str = (now - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%S+11:00")
    four_days_ago_str = (now - timedelta(days=4)).strftime("%Y-%m-%dT%H:%M:%S+11:00")
    five_days_ago_str = (now - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%S+11:00")
    
    # Add transactions with current dates
    current_month = now.strftime("%Y-%m")
    start_of_month_str = f"{current_month}-01T09:00:00+11:00"
    
    current_transactions = [
        # Add current month salary for income calculation
        {
            "type": "transactions",
            "id": "tx-current-income",
            "attributes": {
                "description": "Monthly Salary",
                "message": "May 2025 payment",
                "amount": {
                    "currencyCode": "AUD",
                    "value": "4850.00",
                    "valueInBaseUnits": 485000
                },
                "rawText": "SALARY CREDIT",
                "createdAt": start_of_month_str,
                "settledAt": start_of_month_str
            },
            "relationships": {
                "account": { "data": { "type": "accounts", "id": "1001" }},
                "category": { "data": { "type": "categories", "id": "income" }},
                "tags": { "data": [ { "type": "tags", "id": "salary" } ]}
            }
        },
        {
            "type": "transactions",
            "id": "tx-current-1",
            "attributes": {
                "description": "Today's Coffee",
                "message": "Morning coffee",
                "amount": {
                    "currencyCode": "AUD",
                    "value": "-4.50",
                    "valueInBaseUnits": -450
                },
                "rawText": "COFFEE SHOP",
                "createdAt": today_str,
                "settledAt": today_str
            },
            "relationships": {
                "account": { "data": { "type": "accounts", "id": "1001" }},
                "category": { "data": { "type": "categories", "id": "dining" }},
                "tags": { "data": [ { "type": "tags", "id": "coffee" } ]}
            }
        },
        {
            "type": "transactions",
            "id": "tx-current-2",
            "attributes": {
                "description": "Today's Lunch",
                "message": "Lunch break",
                "amount": {
                    "currencyCode": "AUD",
                    "value": "-15.75",
                    "valueInBaseUnits": -1575
                },
                "rawText": "RESTAURANT",
                "createdAt": today_str,
                "settledAt": today_str
            },
            "relationships": {
                "account": { "data": { "type": "accounts", "id": "1001" }},
                "category": { "data": { "type": "categories", "id": "dining" }},
                "tags": { "data": [ { "type": "tags", "id": "lunch" } ]}
            }
        },
        {
            "type": "transactions",
            "id": "tx-current-3",
            "attributes": {
                "description": "Yesterday's Groceries",
                "message": "Weekly shopping",
                "amount": {
                    "currencyCode": "AUD",
                    "value": "-82.35",
                    "valueInBaseUnits": -8235
                },
                "rawText": "SUPERMARKET",
                "createdAt": yesterday_str,
                "settledAt": yesterday_str
            },
            "relationships": {
                "account": { "data": { "type": "accounts", "id": "1001" }},
                "category": { "data": { "type": "categories", "id": "groceries" }},
                "tags": { "data": [ { "type": "tags", "id": "weekly" } ]}
            }
        },
        {
            "type": "transactions",
            "id": "tx-current-4",
            "attributes": {
                "description": "Two Days Ago Transport",
                "message": "Bus fare",
                "amount": {
                    "currencyCode": "AUD",
                    "value": "-3.50",
                    "valueInBaseUnits": -350
                },
                "rawText": "PUBLIC TRANSPORT",
                "createdAt": two_days_ago_str,
                "settledAt": two_days_ago_str
            },
            "relationships": {
                "account": { "data": { "type": "accounts", "id": "1001" }},
                "category": { "data": { "type": "categories", "id": "transportation" }},
                "tags": { "data": [ { "type": "tags", "id": "transport" } ]}
            }
        },
        {
            "type": "transactions",
            "id": "tx-current-5",
            "attributes": {
                "description": "Three Days Ago Movie",
                "message": "Cinema ticket",
                "amount": {
                    "currencyCode": "AUD",
                    "value": "-22.00",
                    "valueInBaseUnits": -2200
                },
                "rawText": "CINEMA",
                "createdAt": three_days_ago_str,
                "settledAt": three_days_ago_str
            },
            "relationships": {
                "account": { "data": { "type": "accounts", "id": "1001" }},
                "category": { "data": { "type": "categories", "id": "entertainment" }},
                "tags": { "data": [ { "type": "tags", "id": "movie" } ]}
            }
        },
        {
            "type": "transactions",
            "id": "tx-current-6",
            "attributes": {
                "description": "Four Days Ago Dinner",
                "message": "Dinner with friends",
                "amount": {
                    "currencyCode": "AUD",
                    "value": "-45.80",
                    "valueInBaseUnits": -4580
                },
                "rawText": "RESTAURANT",
                "createdAt": four_days_ago_str,
                "settledAt": four_days_ago_str
            },
            "relationships": {
                "account": { "data": { "type": "accounts", "id": "1001" }},
                "category": { "data": { "type": "categories", "id": "dining" }},
                "tags": { "data": [ { "type": "tags", "id": "social" } ]}
            }
        },
        {
            "type": "transactions",
            "id": "tx-current-7",
            "attributes": {
                "description": "Five Days Ago Gas",
                "message": "Fuel for car",
                "amount": {
                    "currencyCode": "AUD",
                    "value": "-65.25",
                    "valueInBaseUnits": -6525
                },
                "rawText": "GAS STATION",
                "createdAt": five_days_ago_str,
                "settledAt": five_days_ago_str
            },
            "relationships": {
                "account": { "data": { "type": "accounts", "id": "1001" }},
                "category": { "data": { "type": "categories", "id": "transportation" }},
                "tags": { "data": [ { "type": "tags", "id": "car" } ]}
            }
        }
    ]
    
    # Add the current transactions to the data
    current_data['data'] = current_transactions + current_data['data']
    
    return current_data

def get_categories_data():
    """Return mock categories data"""
    return categories_data
