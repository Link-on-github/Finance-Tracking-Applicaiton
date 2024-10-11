# from flask import Flask, render_template, request, redirect, url_for, session, flash
# import pandas as pd
# import os
# from werkzeug.security import generate_password_hash, check_password_hash
# from datetime import datetime
# import json
# import pandas as pd
# import requests



# app = Flask(__name__)
# app.secret_key = os.environ.get('SECRET_KEY') or 'a_strong_secret_key'  # Ensure you set a strong secret key

# DATA_FILE = 'data.xlsx'

# # Initialize Excel file if it doesn't exist
# def init_data_file():
#     if not os.path.exists(DATA_FILE):
#         with pd.ExcelWriter(DATA_FILE) as writer:
#             # Sheet1 for Users
#             df_users = pd.DataFrame(columns=['Username', 'Email', 'Password', 'Balance', 'Parental Control Email'])
#             df_users.to_excel(writer, sheet_name='Sheet1', index=False)
            
#             # Transactions sheet
#             df_transactions = pd.DataFrame(columns=['Username', 'Amount', 'Description'])
#             df_transactions.to_excel(writer, sheet_name='Transactions', index=False)

# # Call initialization function
# init_data_file()

# # Home Page
# @app.route('/')
# def index():
#     return render_template('index.html')

# # User Signup
# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         username = request.form['username'].strip()
#         email = request.form['email'].strip()
#         password = request.form['password']
#         parental_email = request.form.get('parental_email', '').strip()  # Optional field

#         # Input validation
#         if not username or not email or not password:
#             flash('Please fill out all required fields.')
#             return redirect(url_for('signup'))

#         hashed_pw = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
#         initial_balance = 0.0  # Starting balance

#         # Read existing users from Sheet1
#         df_users = pd.read_excel(DATA_FILE, sheet_name='Sheet1')

#         if username in df_users['Username'].values:
#             flash('Username already exists. Please choose a different one.')
#             return redirect(url_for('signup'))
        
#         if email in df_users['Email'].values:
#             flash('An account with this email already exists.')
#             return redirect(url_for('signup'))

#         # Add new user to Sheet1
#         df_new_user = pd.DataFrame([[username, email, hashed_pw, initial_balance, parental_email]], 
#                                    columns=['Username', 'Email', 'Password', 'Balance', 'Parental Control Email'])
#         with pd.ExcelWriter(DATA_FILE, mode='a', if_sheet_exists='overlay') as writer:
#             df_new_user.to_excel(writer, sheet_name='Sheet1', header=False, index=False, startrow=len(df_users)+1)

#         flash('Signup successful! Please log in.')
#         return redirect(url_for('login'))

#     return render_template('signup.html')

# # User Login
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username_or_email = request.form['username_or_email'].strip()
#         password = request.form['password']

#         # Read users from Sheet1
#         df_users = pd.read_excel(DATA_FILE, sheet_name='Sheet1')
#         user = df_users[
#             (df_users['Username'] == username_or_email) | 
#             (df_users['Email'] == username_or_email)
#         ]

#         if user.empty:
#             flash('Username or Email does not exist.')
#             return redirect(url_for('login'))

#         user_record = user.iloc[0]
#         if check_password_hash(user_record['Password'], password):
#             session['username'] = user_record['Username']
#             flash('Logged in successfully.')
#             return redirect(url_for('homepage'))
#         else:
#             flash('Incorrect password.')
#             return redirect(url_for('login'))

#     return render_template('login.html')

# # Homepage (Dashboard)
# def get_category_from_gemini(description):
#     # Example API request (replace with the actual API URL and your key)
#     api_url = 'https://generativelanguage.googleapis.com'
#     api_key = 'AIzaSyDzRsmt1bU4RWYC542rwI9jVDi2MAWhEjo'  # Replace with your actual API key
    
#     # Define the payload for the API request
#     payload = {
#         "description": description
#     }

#     # Add headers if needed, including API key
#     headers = {
#         'Authorization': f'Bearer {api_key}',
#         'Content-Type': 'application/json'
#     }

#     try:
#         # Send the request to the API
#         response = requests.post(api_url, json=payload, headers=headers)
#         response_data = response.json()

#         # Extract the category from the API response
#         if response.status_code == 200 and 'category' in response_data:
#             return response_data['category']
#         else:
#             return 'Uncategorized'  # Fallback in case of API issues
#     except requests.RequestException as e:
#         print(f"Error with API request: {e}")
#         return 'Uncategorized'  # Fallback in case of API failure

# @app.route('/homepage', methods=['GET', 'POST'])
# def homepage():
#     if 'username' not in session:
#         flash('Please log in to access this page.')
#         return redirect(url_for('login'))
    
#     username = session['username']

#     # Read users data
#     df_users = pd.read_excel(DATA_FILE, sheet_name='Sheet1')
#     user_record = df_users[df_users['Username'] == username]
#     if user_record.empty:
#         flash('User not found.')
#         return redirect(url_for('login'))
    
#     total_balance = user_record.iloc[0]['Balance']

#     if request.method == 'POST':
#         # Handle adding a transaction
#         try:
#             amount = request.form['amount']
            
#             if not amount:
#                 flash('Please enter an amount.')
#                 return redirect(url_for('homepage'))

#             # Convert the amount to a float
#             amount = float(amount)  # This will raise a ValueError if input is invalid

#             description = request.form['description'].strip()

#             if amount == 0:
#                 flash('Transaction amount cannot be zero.')
#                 return redirect(url_for('homepage'))

#             if not description:
#                 flash('Please provide a description for your transaction.')
#                 return redirect(url_for('homepage'))

#             # Get the current date and time for the transaction
#             transaction_date = datetime.now()

#             # Get the category from Gemini AI or another API
#             category = get_category_from_gemini(description)

#             # Update transactions sheet with the categorized description
#             df_transactions = pd.read_excel(DATA_FILE, sheet_name='Transactions')
#             new_transaction = pd.DataFrame([[username, amount, description, transaction_date, category]], 
#                                            columns=['Username', 'Amount', 'Description', 'Date', 'Category'])

#             with pd.ExcelWriter(DATA_FILE, mode='a', if_sheet_exists='overlay') as writer:
#                 new_transaction.to_excel(writer, sheet_name='Transactions', header=False, index=False, startrow=len(df_transactions)+1)

#             # Update user's balance
#             total_balance += amount
#             df_users.loc[df_users['Username'] == username, 'Balance'] = total_balance
#             with pd.ExcelWriter(DATA_FILE, mode='a', if_sheet_exists='replace') as writer:
#                 df_users.to_excel(writer, sheet_name='Sheet1', index=False)

#             flash('Transaction added successfully, and category determined.')
#             return redirect(url_for('homepage'))
        
#         except ValueError:
#             flash('Invalid amount. Please enter a numeric value.')
#             return redirect(url_for('homepage'))

#     # GET request: Fetch transactions
#     df_transactions = pd.read_excel(DATA_FILE, sheet_name='Transactions')
#     user_transactions = df_transactions[df_transactions['Username'] == username]
#     transactions = user_transactions.to_dict('records')

#     return render_template('homepage.html', total_balance=total_balance, transactions=transactions)

# # Parental Control
# @app.route('/parental_control', methods=['GET', 'POST'])
# def parental_control():
#     if 'username' not in session:
#         flash('Please log in to access this page.')
#         return redirect(url_for('login'))
    
#     username = session['username']
#     df_users = pd.read_excel(DATA_FILE, sheet_name='Sheet1')

#     if request.method == 'POST':
#         parental_email = request.form['parental_email'].strip()

#         if not parental_email:
#             flash('Please enter a valid parental control email.')
#             return redirect(url_for('parental_control'))

#         # Update parental control email
#         df_users.loc[df_users['Username'] == username, 'Parental Control Email'] = parental_email
#         with pd.ExcelWriter(DATA_FILE, mode='a', if_sheet_exists='replace') as writer:
#             df_users.to_excel(writer, sheet_name='Sheet1', index=False)

#         flash('Parental control email updated successfully.')
#         return redirect(url_for('parental_control'))

#     # Retrieve current parental control email
#     user_record = df_users[df_users['Username'] == username]
#     if not user_record.empty:
#         current_parental_email = user_record.iloc[0]['Parental Control Email']
#     else:
#         current_parental_email = ''

#     return render_template('parental_control.html', parental_email=current_parental_email)

# # Goals Page
# @app.route('/goals')
# def goals():
#     if 'username' not in session:
#         flash('Please log in to access this page.')
#         return redirect(url_for('login'))
#     return render_template('goals.html')

# # Tips Page
# @app.route('/tips')
# def tips():
#     if 'username' not in session:
#         flash('Please log in to access this page.')
#         return redirect(url_for('login'))
#     return render_template('tips.html')

# # Stats Page (New Endpoint)

# @app.route('/stats')
# def stats():
#     if 'username' not in session:
#         flash('Please log in to access this page.')
#         return redirect(url_for('login'))
    
#     username = session['username']
#     df_transactions = pd.read_excel(DATA_FILE, sheet_name='Transactions')

#     # Ensure the 'Date' column is in datetime format
#     df_transactions['Date'] = pd.to_datetime(df_transactions['Date'], errors='coerce')

#     # Filter user transactions
#     user_transactions = df_transactions[df_transactions['Username'] == username]

#     # Make sure the 'Amount' column is numeric
#     user_transactions['Amount'] = pd.to_numeric(user_transactions['Amount'], errors='coerce')

#     # Compute daily, weekly, and monthly totals
#     daily_data = user_transactions.groupby(user_transactions['Date'].dt.date)['Amount'].sum().reset_index()
#     weekly_data = user_transactions.groupby(user_transactions['Date'].dt.to_period('W'))['Amount'].sum().reset_index()
#     monthly_data = user_transactions.groupby(user_transactions['Date'].dt.to_period('M'))['Amount'].sum().reset_index()

#     # Prepare data for Chart.js
#     daily_data = {
#         'labels': daily_data['Date'].astype(str).tolist(),
#         'values': daily_data['Amount'].tolist()
#     }
#     weekly_data = {
#         'labels': weekly_data['Date'].astype(str).tolist(),
#         'values': weekly_data['Amount'].tolist()
#     }
#     monthly_data = {
#         'labels': monthly_data['Date'].astype(str).tolist(),
#         'values': monthly_data['Amount'].tolist()
#     }

#     # Compute overall stats
#     total_transactions = len(user_transactions)
#     total_amount = user_transactions['Amount'].sum()  # Ensure this is treated as numeric
#     average_transaction = user_transactions['Amount'].mean() if total_transactions > 0 else 0

#     stats_data = {
#         'total_transactions': total_transactions,
#         'total_amount': total_amount,
#         'average_transaction': average_transaction
#     }

#     # Pass data as JSON to the template
#     return render_template(
#         'stats.html', 
#         stats=stats_data, 
#         daily_data=json.dumps(daily_data), 
#         weekly_data=json.dumps(weekly_data), 
#         monthly_data=json.dumps(monthly_data)
#     )

# # Logout
# @app.route('/logout')
# def logout():
#     session.pop('username', None)
#     flash('You have been logged out.')
#     return redirect(url_for('index'))

# if __name__ == '__main__':
#     app.run(debug=True)










from flask import Flask, render_template, request, redirect, url_for, session, flash
import pandas as pd
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import requests

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or 'a_strong_secret_key'

DATA_FILE = 'data.xlsx'

def init_data_file():
    if not os.path.exists(DATA_FILE):
        with pd.ExcelWriter(DATA_FILE) as writer:
            # Sheet1 for Users
            df_users = pd.DataFrame(columns=['Username', 'Email', 'Password', 'Balance', 'Parental Control Email'])
            df_users.to_excel(writer, sheet_name='Sheet1', index=False)
            
            # Transactions sheet
            df_transactions = pd.DataFrame(columns=['Username', 'Amount', 'Description', 'Date', 'Category'])
            df_transactions.to_excel(writer, sheet_name='Transactions', index=False)

init_data_file()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        parental_email = request.form.get('parental_email', '').strip()

        if not username or not email or not password:
            flash('Please fill out all required fields.')
            return redirect(url_for('signup'))

        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        initial_balance = 0.0

        df_users = pd.read_excel(DATA_FILE, sheet_name='Sheet1')

        if username in df_users['Username'].values:
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('signup'))
        
        if email in df_users['Email'].values:
            flash('An account with this email already exists.')
            return redirect(url_for('signup'))

        df_new_user = pd.DataFrame([[username, email, hashed_pw, initial_balance, parental_email]],
                                   columns=['Username', 'Email', 'Password', 'Balance', 'Parental Control Email'])
        with pd.ExcelWriter(DATA_FILE, mode='a', if_sheet_exists='overlay') as writer:
            df_new_user.to_excel(writer, sheet_name='Sheet1', header=False, index=False, startrow=len(df_users)+1)

        flash('Signup successful! Please log in.')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form['username_or_email'].strip()
        password = request.form['password']

        df_users = pd.read_excel(DATA_FILE, sheet_name='Sheet1')
        user = df_users[
            (df_users['Username'] == username_or_email) | 
            (df_users['Email'] == username_or_email)
        ]

        if user.empty:
            flash('Username or Email does not exist.')
            return redirect(url_for('login'))

        user_record = user.iloc[0]
        if check_password_hash(user_record['Password'], password):
            session['username'] = user_record['Username']
            flash('Logged in successfully.')
            return redirect(url_for('homepage'))
        else:
            flash('Incorrect password.')
            return redirect(url_for('login'))

    return render_template('login.html')

def get_category_from_gemini(description):
    api_url = 'https://api.gemini.com/v1/classify'
    api_key = 'AIzaSyDzRsmt1bU4RWYC542rwI9jVDi2MAWhEjo'
    
    prompt = f"Imagine you are a finance manager, your client has spent money on an item that he briefly calls as '{description}'. Under which broad category of spending does this fall, for example food, shopping, education etx?"
    
    payload = {
        "prompt": prompt,
        "max_tokens": 50,
        "temperature": 0.5,
    }

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response_data = response.json()

        if response.status_code == 200 and 'category' in response_data:
            return response_data['category']
        else:
            print(f"API Response Error: {response_data}")
            return 'Uncategorized'
    except requests.RequestException as e:
        print(f"Error with API request: {e}")
        return 'Uncategorized'

@app.route('/homepage', methods=['GET', 'POST'])
def homepage():
    if 'username' not in session:
        flash('Please log in to access this page.')
        return redirect(url_for('login'))
    
    username = session['username']

    df_users = pd.read_excel(DATA_FILE, sheet_name='Sheet1')
    user_record = df_users[df_users['Username'] == username]
    if user_record.empty:
        flash('User not found.')
        return redirect(url_for('login'))
    
    total_balance = user_record.iloc[0]['Balance']

    if request.method == 'POST':
        try:
            amount = request.form['amount']
            
            if not amount:
                flash('Please enter an amount.')
                return redirect(url_for('homepage'))

            amount = float(amount)

            description = request.form['description'].strip()

            if amount == 0:
                flash('Transaction amount cannot be zero.')
                return redirect(url_for('homepage'))

            if not description:
                flash('Please provide a description for your transaction.')
                return redirect(url_for('homepage'))

            transaction_date = datetime.now()

            category = get_category_from_gemini(description)

            df_transactions = pd.read_excel(DATA_FILE, sheet_name='Transactions')
            new_transaction = pd.DataFrame([[username, amount, description, transaction_date, category]], 
                                           columns=['Username', 'Amount', 'Description', 'Date', 'Category'])

            with pd.ExcelWriter(DATA_FILE, mode='a', if_sheet_exists='overlay') as writer:
                new_transaction.to_excel(writer, sheet_name='Transactions', header=False, index=False, startrow=len(df_transactions)+1)

            total_balance += amount
            df_users.loc[df_users['Username'] == username, 'Balance'] = total_balance
            with pd.ExcelWriter(DATA_FILE, mode='a', if_sheet_exists='replace') as writer:
                df_users.to_excel(writer, sheet_name='Sheet1', index=False)

            flash('Transaction added successfully, and category determined.')
            return redirect(url_for('homepage'))
        
        except ValueError:
            flash('Invalid amount. Please enter a numeric value.')
            return redirect(url_for('homepage'))

    df_transactions = pd.read_excel(DATA_FILE, sheet_name='Transactions')

    # Ensure the 'Date' column is in datetime format
    df_transactions['Date'] = pd.to_datetime(df_transactions['Date'], errors='coerce')

    # Filter user transactions
    user_transactions = df_transactions[df_transactions['Username'] == username]
    transactions = user_transactions.to_dict('records')

    return render_template('homepage.html', total_balance=total_balance, transactions=transactions)

@app.route('/parental_control', methods=['GET', 'POST'])
def parental_control():
    if 'username' not in session:
        flash('Please log in to access this page.')
        return redirect(url_for('login'))
    
    username = session['username']
    df_users = pd.read_excel(DATA_FILE, sheet_name='Sheet1')

    if request.method == 'POST':
        parental_email = request.form['parental_email'].strip()

        if not parental_email:
            flash('Please enter a valid parental control email.')
            return redirect(url_for('parental_control'))

        df_users.loc[df_users['Username'] == username, 'Parental Control Email'] = parental_email
        with pd.ExcelWriter(DATA_FILE, mode='a', if_sheet_exists='replace') as writer:
            df_users.to_excel(writer, sheet_name='Sheet1', index=False)

        flash('Parental control email updated successfully.')
        return redirect(url_for('parental_control'))

    user_record = df_users[df_users['Username'] == username]
    if not user_record.empty:
        current_parental_email = user_record.iloc[0]['Parental Control Email']
    else:
        current_parental_email = ''

    return render_template('parental_control.html', parental_email=current_parental_email)

@app.route('/goals')
def goals():
    if 'username' not in session:
        flash('Please log in to access this page.')
        return redirect(url_for('login'))

    return render_template('goals.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
