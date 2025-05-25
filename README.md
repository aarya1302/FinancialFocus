# Personal Finance Dashboard
https://dashup.streamlit.app/
<img width="1275" alt="image" src="https://github.com/user-attachments/assets/5212e6ea-47fd-4dae-8418-b8ae4c8e1894" />

A minimalist personal finance dashboard. This dashboard provides insights into your financial health based on transaction data.

## Features

- **Account Summary**: View your total balance and monthly income
- **Spending by Category**: Visualize your spending distribution with an interactive pie chart
- **Monthly Spending Trends**: Track your spending patterns over time with a line chart


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


Research shows that consistent tracking and setting realistic spending limits can lead to better financial outcomes.

## 🔒 Security & API Key Storage

**Where is the API key stored?**
- The API key is stored in `st.session_state['UP_API_TOKEN']` for the current Streamlit session.
- If you use the `streamlit-cookies-manager` package, the API key is also stored in an encrypted browser cookie (on your device, not on a server).
- The API key is NOT stored on the server, in a database, or in any file by default.

**Is this secure?**
- The key is only available in your session (in memory, on the server, for your connection). When the session ends, the key is gone.
- If using cookies, the key is stored in your browser as an encrypted cookie. The encryption password is in the app code, so it's only as secure as your app's deployment and the secrecy of that password.

**Security Considerations:**
- Always use HTTPS when deploying the app so the API key is encrypted in transit.
- The API key is not visible to other users, but if you share your browser or computer, someone could access it if your session is open.
- Never print or log the API key in the app.
- Never hard-code your real API key in the source code.

**Recommendations:**
- For personal use or trusted users, this approach is generally safe.
- For public deployment:
    - Use HTTPS.
    - Use the logout button to clear your session and cookie.
    - Never log or display the API key.
    - If using cookies, keep the encryption password secret and rotate it if needed.
    - For advanced security, consider OAuth or a backend proxy to handle API calls.
