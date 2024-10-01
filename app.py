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
    flash('Logged out successfully.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
