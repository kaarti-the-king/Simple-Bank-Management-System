# ────── IMPORT MODULES ──────────────────────────────────────────────────────────────────────────

import os, sys, time, shutil, msvcrt, random, pyfiglet

import numpy as np, pandas as pd, pyinputplus as pyip, mysql.connector as sql

from pyfiglet import Figlet
from datetime import datetime
from tabulate import tabulate
from colorama import Fore, Style

from rich import box
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.progress import track
from rich.console import Console

console = Console()
Print = console.print

# ────── PRE-REQUISITE(Security) ─────────────────────────────────────────────────────────────────

# HIDES THE TYPED PASSWORD WITH (*) SO IT IS NOT VISIBLE TO ANYONE
def masked_input(prompt=""):
    if os.name == 'nt':
        # Windows platform
        print(prompt, end='', flush=True)
        password = []
        while True:
            char = msvcrt.getch()
            if char == b'\r':  # Enter key pressed
                print()
                break
            elif char == b'\x08':  # Backspace key pressed
                if password:
                    password.pop()  # Remove the last character
                    sys.stdout.write('\b \b')  # Clear the character on the screen
                    sys.stdout.flush()
            else:
                password.append(char.decode('utf-8'))
                sys.stdout.write('*')  # Display asterisks instead of characters
                sys.stdout.flush()
        return ''.join(password)
    else:
        # Unix-like platforms
        print(prompt, end='', flush=True)
        password = []
        while True:
            char = sys.stdin.read(1)
            if char == '\n':  # Enter key pressed
                print()
                break
            elif char == '\x08':  # Backspace key pressed
                if password:
                    password.pop()  # Remove the last character
                    sys.stdout.write('\b \b')  # Clear the character on the screen
                    sys.stdout.flush()
            else:
                password.append(char)
                sys.stdout.write('*')  # Display asterisks instead of characters
                sys.stdout.flush()
        return ''.join(password)

# A PRETTY DECORATIVE HORIZONTAL LINE
def print_horizontal_line():
    terminal_width = shutil.get_terminal_size().columns
    horizontal_line = "─" * terminal_width
    print(horizontal_line)

# ────── LINK TO MYSQL (BACKEND) ─────────────────────────────────────────────────────────────────

# RESQUEST'S THE USER TO INPUT CONNECTION DETAILS FOR ESTABLISHING BACKEND CONNECTION
host = masked_input("Enter Host:")
user = masked_input("Enter User:")
password = masked_input("Enter Password:")


# ESTABLISHE'S CONNECTION TO BACKEND (MySQL)
conn = sql.connect(host = str(host),
                   user = str(user),
                   password = str(password))
cursor = conn.cursor()

# CREATE'S THE DATABASE NAMED (BANK) IF IT DOESN'T EXISTS
cursor.execute("CREATE DATABASE IF NOT EXISTS bank")
cursor.close()

# ESTABLISHES CONNECTION DIRECTLY TO BANK DATABASE
idpass = sql.connect(host = str(host),
                   user = str(user),
                   password = str(password),
                     database='bank')
cursor = idpass.cursor()

Print(Panel("[aquamarine1]Connection Success!"), justify = "center")
print_horizontal_line()

# ────── TO CREATE TABLES IN DATABASE ────────────────────────────────────────────────────────────

# TO RECORD THE ACCOUNT NUMBER, BALANCE AND STATUS
def create_account():
    query = '''CREATE TABLE IF NOT EXISTS account (
        acc_number INT PRIMARY KEY,
        balance FLOAT NOT NULL,
        status TINYINT(1) NOT NULL DEFAULT 0)'''
    cursor.execute(query)
    idpass.commit()

# SEPERATE TABLE MAINTAINED FOR PASSWORDS FOR SECURITY REASONS
def create_password():
    query = '''CREATE TABLE IF NOT EXISTS password (
        acc_number INT PRIMARY KEY,
        passcode VARCHAR(30) NOT NULL)'''
    cursor.execute(query)
    idpass.commit()

# STORES CUSTOMERS PERSONAL INFORMATION (DOB, Name, Gender)
def create_customer_detail():
    query = '''CREATE TABLE IF NOT EXISTS customer_detail (
        acc_number INT PRIMARY KEY,
        dob DATE NOT NULL,
        name VARCHAR(30) NOT NULL,
        gender VARCHAR(11) NOT NULL)'''
    cursor.execute(query)
    idpass.commit()

# TO RECORDS ALL THE TRANSACTIONS AND ACTIONS OCCURED ALONG WITH THE
# (id, ToA/Time of (action/transaction), acc_num, type of transaction, amount involved)
def create_log():
    query = '''CREATE TABLE IF NOT EXISTS log (
        id INT AUTO_INCREMENT PRIMARY KEY,
        toa TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        acc_number INT NOT NULL,
        transaction_type VARCHAR(50) NOT NULL,
        amount FLOAT)'''
    cursor.execute(query)
    idpass.commit()

# RECORDS IF ANYONE DONATED TO CHARITY WHILE DEPOSITING OR WITHDRAWING
def create_charity():
    query = '''CREATE TABLE IF NOT EXISTS charity(
        transaction_id INT,
        donated_time TIMESTAMP,
        acc_number INT)'''
    cursor.execute(query)
    idpass.commit()

# STORES THE DELETED ACCOUNTS AND RECORDS ALL THE DETAILS IN THE SAME TABLE
def create_past_customer():
    query = '''CREATE TABLE IF NOT EXISTS past_customer (
        deleted_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        acc_number INT PRIMARY KEY,
        dob DATE NOT NULL,
        name VARCHAR(30) NOT NULL,
        gender VARCHAR(11) NOT NULL)'''
    cursor.execute(query)
    idpass.commit()

# ────── CREATING A NEW ACCOUNT ──────────────────────────────────────────────────────────────────

# KEEPS RECORD OF GENERATED ACCOUNT NUMBER TO NEVER REPEAT THEM AGAIN
generated_numbers = set()

# IT ALWAYS GENERATES RANDOM 6 DIGIT ACCOUNT NUMBERS
def generate_random_number():
    while True:
        random_number = random.randint(100000, 999999)
        if random_number not in generated_numbers:
            generated_numbers.add(random_number)
            return random_number

random_number = generate_random_number()

# CREATES AND RECORDS THE NEW ACCOUNTS INTO ALL THE REQUIRED TABLES
def create_new_account(acc_num, name, dob, gender, balance, passcode):

    query = '''INSERT INTO account (acc_number, balance)
    VALUES (%s, %s)'''
    values = (acc_num, balance)
    cursor.execute(query, values)
    idpass.commit()

    query = '''INSERT INTO password (acc_number, passcode)
    VALUES (%s, %s)'''
    values = (acc_num, passcode)
    cursor.execute(query, values)
    idpass.commit()

    dobh = dob.split('/')
    day = int(dobh[0])
    month = int(dobh[1])
    year = int(dobh[2])

    dob_value = datetime(year, month, day).strftime('%Y-%m-%d')

    query = '''INSERT INTO customer_detail  (acc_number, dob, name, gender)
    VALUES (%s, %s, %s, %s)'''
    values = (acc_num, dob_value, name, gender)
    cursor.execute(query, values)
    idpass.commit()

    query = '''INSERT INTO log (acc_number, transaction_type, amount)
    VALUES (%s, %s, %s)'''
    values = (acc_num, 'created account', balance)
    cursor.execute(query, values)
    idpass.commit()

# ────── SECURITY ────────────────────────────────────────────────────────────────────────────────

# CHECKS THE MINIMUM REQUIRMENT FOR PASSSWORDS
# i.e. length 8 or more, 1 uppercase, 1 lowercase, 1 symbol
def password_checker():
    while True:
        password = masked_input("Enter Your New Password: ")

        requirements = [
            len(password) >= 8,
            any(c.islower() for c in password),
            any(c.isupper() for c in password),
            any(c in "!@#$%^&*()_-+=~`|\\{[]}:'\";<>,.?/" for c in password)
        ]
        if all(requirements):
            return password

        else:
            Print(('''[red1]
┌───────────────────────────────────────────────────┐
│                 Invalid password!                 │
│Please make sure your password contains at least:  │
│---> 8 characters                                  │
│---> 1 lowercase letter                            │
│---> 1 uppercase letter                            │
│---> 1 symbol                                      │
└───────────────────────────────────────────────────┘
'''), justify = "center")

# VERIFIES IF THE ENTERED PASSWORD IS CORRECT OR NOT
def authorize_passcode(acc_num):
    query = '''SELECT passcode FROM password
    WHERE acc_number = %s'''
    values = [acc_num]
    cursor.execute(query, values)

    passcode = cursor.fetchone()
    return (passcode[0],)

# IT LOCKS OR UNLOCKS AN ACCOUNT
def account_status(acc_num, status):
    acc = get_ainfo(acc_num)

    # DEACTIVATES THE ACCOUNT AND DISABLES IT FROM BEING USED
    if status == 'locked':
        query = '''UPDATE account SET status = 1
        WHERE acc_number = %s'''
        values = [acc_num]
        cursor.execute(query, values)
        idpass.commit()

        query = '''INSERT INTO log (acc_number, transaction_type, amount)
        VALUES (%s, %s, %s)'''
        values = (acc_num, 'locked', acc[1])
        cursor.execute(query,values)
        idpass.commit()

    # ALLOWS THE ACCOUNT TO BE USED BY REACTIVATING IT
    elif status == 'unlocked':
        query = '''UPDATE account SET status = 0
        WHERE acc_number = %s'''
        values = [acc_num]
        cursor.execute(query, values)
        idpass.commit()

        query = '''INSERT INTO log (acc_number, transaction_type, amount)
        VALUES (%s, %s, %s)'''
        values = (acc_num, 'UnLocked', acc[1])
        cursor.execute(query, values)
        idpass.commit()

# RESETS THE PASSWORD
def reset_passcode(acc_num, new_pass):
    query = '''UPDATE password SET passcode = %s
    WHERE acc_number = %s'''
    values = [new_pass, acc_num]
    cursor.execute(query, values)
    idpass.commit()

# CHECKS WHETHER THE ACCOUNT STATUS IS UNLOCKED OR LOCKED
def return_status(acc_num):
    query = '''SELECT status FROM account
    WHERE acc_number = %s'''
    values = [acc_num]
    cursor.execute(query, values)
    result = cursor.fetchone()
    if result == (1,):
        return 1
    else:
        return 0

# ────── DEPOSIT, WITHDRAW, DONATE ───────────────────────────────────────────────────────────────

def update_balance(acc_num, new_bal, transaction_type, amt):
# it updates the balance

# RECORDS THE WITHDRAWN/DEPOSITED CASH
    query = '''UPDATE account SET balance = %s
    WHERE acc_number = %s'''
    values = (new_bal, acc_num)
    cursor.execute(query, values)
    idpass.commit()

# LOGS THE WITHDRAWN CASH
    if transaction_type == 'withdrawn':
        query = '''INSERT INTO log (acc_number, transaction_type, amount)
        VALUES (%s, %s, %s)'''
        values = (acc_num, 'withdrawn', amt)
        cursor.execute(query, values)
        idpass.commit()

# LOGS THE DEPOSITED CASH
    elif transaction_type == 'deposited':
        query = '''INSERT INTO log (acc_number, transaction_type, amount)
        VALUES (%s, %s, %s)'''
        values = (acc_num, 'deposited', amt)
        cursor.execute(query, values)
        idpass.commit()

# RECORDS IF USER IS DONATING
def donated(acc_num):

    query = '''SELECT id, toa FROM log
    WHERE acc_number = %s
    ORDER BY id DESC
    LIMIT 1'''
    values = (acc_num ,)
    cursor.execute (query, values)
    result = cursor.fetchone()

    query = '''INSERT INTO charity (transaction_id, donated_time, acc_number)
    VALUES (%s, %s, %s)'''
    values = (result[0], result[1], acc_num)
    cursor.execute(query, values)
    idpass.commit()
    print ("Successfully Donated to Charity")

# ────── TRANSFERS ───────────────────────────────────────────────────────────────────────────────

def update_multiple_balance(s_acc_num, r_acc_num, amt, s_bal, r_bal):

    # RECORDING IN THE SOURCE ACCOUNT
    query = '''UPDATE account SET balance = %s
    WHERE acc_number = %s'''
    values = (s_bal, s_acc_num)
    cursor.execute(query, values)
    idpass.commit()

    # RECORDING IN THE DESTINATION ACCOUNT
    query = '''UPDATE account SET balance = %s
    WHERE acc_number = %s'''
    values = (r_bal, r_acc_num)
    cursor.execute(query, values)
    idpass.commit()

    # FIRST LOG ENTRY
    query = '''INSERT INTO log (acc_number, transaction_type, amount)
    VALUES (%s, %s, %s)'''
    values = (s_acc_num, 'transferred from', amt)
    cursor.execute(query, values)
    idpass.commit()

    # SECOND LOG ENTRY
    query = '''INSERT INTO log (acc_number, transaction_type, amount)
    VALUES (%s, %s, %s)'''
    values = (r_acc_num, 'transferred to', amt)
    cursor.execute(query, values)
    idpass.commit()

# ────── RETRIEVING DETAILS ──────────────────────────────────────────────────────────────────────

# GET'S A SINGLE CUSTOMER'S ACCOUNT DETAILS
def get_ainfo(acc_num):
    query = '''SELECT * FROM account
    WHERE acc_number = %s'''
    values = (acc_num,)
    cursor.execute(query, values)
    saccount = cursor.fetchone()
    return saccount

# GET'S A SINGLE CUSTOMER'S PERSONAL INFORMATION
def get_pinfo(acc_num):
    query = '''SELECT * FROM customer_detail
    WHERE acc_number = %s'''
    values = (acc_num,)
    cursor.execute(query, values)
    sper = cursor.fetchone()
    return sper

# GET'S A SINGLE CUSTOMER'S LOG ENTRIES
def get_linfo(acc_num):
    query = '''SELECT * FROM log
    WHERE acc_number = %s'''
    values = (acc_num,)
    cursor.execute(query, values)
    column_names = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    return column_names, rows

# GET'S THE ACCOUNT DETAILS AND PERSONAL DETAILS OF ALL THE CUSTOMER'S IN THE BANK
def get_all_infos(acc_num):
    query = '''SELECT account.acc_number, customer_detail.dob,
    customer_detail.name, customer_detail.gender,
    account.balance, account.status
    FROM account
    INNER JOIN customer_detail
    ON account.acc_number = customer_detail.acc_number
    WHERE account.acc_number = %s'''
    values = (acc_num,)
    cursor.execute(query, values)

    column_names = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    return column_names, rows

# GET'S THE ACCOUNT DETAILS AND PERSONAL DETAILS OF ALL THE CUSTOMER'S IN THE BANK
def get_all_info():
    query = '''
    SELECT account.acc_number, customer_detail.dob,
    customer_detail.name, customer_detail.gender,
    account.balance, account.status
    FROM account
    INNER JOIN customer_detail
    WHERE account.acc_number = customer_detail.acc_number
    '''
    cursor.execute(query, )
    column_names = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    return column_names, rows

# CALCULATES THE TOTAL AMOUNT OF CASH IN THE BANK
def get_total_balance():
    query = 'SELECT * FROM account'
    cursor.execute(query)
    result = cursor.fetchall()
    df = pd.DataFrame(result, columns=['account_id', 'balance', 'status'])
    balance_list = df['balance'].tolist()

    # Convert the 'balance_list' to a list of numbers
    balance_list = [float(value) for value in balance_list]

    # Calculate the sum of all elements in the 'balance_list'
    total_balance = sum(balance_list)
    return total_balance

    # GET'S ALL CUSTOMER'S LOG ENTRIES
def get_all_linfo():
    query = 'SELECT * FROM log'
    cursor.execute(query,)
    column_names = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    return column_names, rows

# GET'S ALL PAST CUSTOMERS
def pcust_info():
    query = 'SELECT * FROM past_customer'
    cursor.execute(query,)
    column_names = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    return column_names, rows

# ────── DELETING AN ACCOUNT ─────────────────────────────────────────────────────────────────────

def del_acc(acc_num):
    a = get_ainfo(acc_num)
    p = get_pinfo(acc_num)

    # RECORDS ALL DATA IN PAST CUSTOMERS TABLE
    query = '''
    INSERT INTO past_customer(acc_number, dob, name, gender)
    VALUES (%s, %s, %s, %s)
    '''
    values = (a[0], p[1], p[2], p[3])

    # Execute the SQL query and commit the transaction
    cursor.execute(query, values)
    idpass.commit()

    # RECORDS IN LOG
    query = '''
    INSERT INTO log (acc_number, transaction_type, amount)
    VALUES (%s, %s, %s)
    '''
    values = (acc_num, 'withdrawn and deleted', a[1],)

    # Execute the SQL query and commit the transaction
    cursor.execute(query, values)
    idpass.commit()

    # DELETE THE ACCOUNT'S PASSWORD
    query = "DELETE FROM password WHERE acc_number = %s"
    values = (acc_num,)

    # Execute the SQL query and commit the transaction
    cursor.execute(query, values)
    idpass.commit()

    # DELETE THE ACCOUNT FROM BANK
    query = "DELETE FROM account WHERE acc_number = %s"
    values = (acc_num,)

    # Execute the SQL query and commit the transaction
    cursor.execute(query, values)
    idpass.commit()

# ────── INTERFACE TOOLS ─────────────────────────────────────────────────────────────────────────

def clean_terminal_screen():
    """
    Cleans the terminal screen by performing a system
    clear command. Cls on windows and Clear on UNIX ones.
    """
    os.system('cls' if os.name == 'nt' else 'clear')

f = Figlet(font='Standard')

def DrawText(text, center=True):
    if center:
        lines = [x.center(shutil.get_terminal_size().columns) for x
                 in f.renderText(text).split("\n")]
    else:
        lines = f.renderText(text).split("\n")
    return lines

def box1():
    # Draw the text "Phoenix Bank" and add it to a Panel
    phoenix_bank_text = DrawText("Phoenix Bank")
    phoenix_bank_panel = Text("\n".join(phoenix_bank_text), style="dark_goldenrod")
    # Create a Table for Main Menu
    table = Table(title="Main Menu", title_style="medium_spring_green", style="yellow4"
                  , box=box.ROUNDED)
    table.add_column("Option", header_style="orange3", style="royal_blue1")
    table.add_column("Opt_Num", justify="left", header_style="orange3"
                     , style="hot_pink3")
    # Add rows to the table
    options = [("Create new account", "1"),
        ("View account details", "2"),
        ("Deposit", "3"),
        ("Withdraw", "4"),
        ("Transfer", "5"),
        ("Manager's menu", "6"),
        ("Delete account", "7"),
        ("Exit", "8")]
    for option in options:
        table.add_row(*option)
    # Print the title and then the table
    Print(phoenix_bank_panel)
    Print(table, justify="center")

# DISPLAYS THE MAIN DETAILS OF A SINGLE ACCOUNT
def disp_single_acc_info(acc_num):
    account = get_ainfo(acc_num)
    name = get_pinfo(acc_num)
    account_number = str(account[0])
    account_balance = str(account[1])
    table = Table(show_header=False,
                  title="[dark_olive_green2]Your Account Details:")
    table.add_column("[dark_goldenrod]Field", style="bold")
    table.add_column("[dark_goldenrod]Value")
    table.add_row("[sandy_brown]Account Number", account_number)
    table.add_row("[sandy_brown]Account Holder", name[2])
    table.add_row("[sandy_brown]Balance", account_balance)
    Print(table, justify="center")
    print_horizontal_line()

# DISPLAYS THE CURRENT BALANCE WHEN WITHDRAWN, DEPOSITED AND TRANSFERED
def disp_curr_balance(acc_num):
    account = get_ainfo(acc_num)
    Print(Panel("[dark_goldenrod]Your Current Balance --->", account[2])
                  , justify = "center")

def locked():
        Print(('''[red1]
┌─────────────────────────────────────────────────┐
│        Exceeded Maximum Number of Tries         │
│             Your Account is Locked.             │
└─────────────────────────────────────────────────┘'''),justify = "center")

def box4():

    # Draw the text "Phoenix Bank" and add it to a Panel
    title_text = DrawText("Phoenix Bank")
    title_panel = Text("\n".join(title_text), style="dark_goldenrod")

    # Create a Table for Manager's Menu
    table = Table(title="Manager's Menu", title_style="medium_spring_green"
                  , style="yellow4", box=box.ROUNDED)
    table.add_column("Option", header_style="orange3", style="royal_blue1")
    table.add_column("Opt_Num", justify="left", header_style="orange3"
                     , style="hot_pink3")

    # Add rows to the table
    options = [("View Account Details", "1"),
        ("View All Accounts", "2"),
        ("View All Previous Accounts", "3"),
        ("View Log Entries", "4"),
        ("View Total Cash(Bank)", "5"),
        ("Reset Password", "6"),
        ("Exit", "7")]

    for option in options:
        table.add_row(*option)
    # Print the title and then the table
    Print(title_panel)
    Print(table, justify="center")

# DISPLAY'S THE DATA PROVIDED IN FANCY GRID TABLE FORMAT
def display_tabulated_data(column_names, rows):
    table = tabulate(rows, headers=column_names, tablefmt="fancy_grid")

    # Get terminal width using shutil
    terminal_width, _ = shutil.get_terminal_size()
    Print(table, justify="center")
# ────── EXITING PHOENIX BANK MANAGEMENT SYSTEM ──────────────────────────────────────────────────

def break_Off():
    cursor.close()
    clean_terminal_screen()
    sys.exit()

# ────── MAIN PROGRAM ────────────────────────────────────────────────────────────────────────────

# CREATING/MAKING SURE THAT ALL THE REQUIRED TABLES ARE CREATED
create_account(), create_customer_detail(), create_password(),
create_log(), create_charity(), create_past_customer()

# MAIN BANKING MENU
while True:
    box1()
    print()
    choice = console.input("[magenta1]Enter your Choice: ")
# ────── choice 1 ────────────────────────────────────────────────────────────────────────────────
    # CREATES A NEW ACCOUNT WITH A RANDOM ACCOUNT NUMBER
    if choice == '1':
        
        # COLLECTS ALL THE INFORMATION REQUIRED FOR A NEW ACCOUNT
        acc_num = generate_random_number()
        name = pyip.inputStr(
            f"{Fore.LIGHTBLUE_EX}Enter Your Name: {Style.RESET_ALL}")
        dob = input(
            f"{Fore.LIGHTBLUE_EX}Enter Your Date of Birth (dd/mm/year): {Style.RESET_ALL}")
        gender = input(
            f"{Fore.LIGHTBLUE_EX}Enter Your Gender: {Style.RESET_ALL}")
        passcode = password_checker()
        balance = pyip.inputFloat(
            f"{Fore.LIGHTBLUE_EX}Enter Initial Balance: {Style.RESET_ALL}")

        # REGISTER'S THE ACCOUNT BY ENTERING THE COLLECTED INFORMATION INTO TABLES
        create_new_account(acc_num, name, dob, gender, balance, passcode)
        Print(Panel("[deep_pink4]Account Created Successfully!")
                      , justify = "center")

    # PRINTS THE MAIN DETAILS OF THE CREATED ACCOUNT TO THE USER
        disp_single_acc_info(acc_num)

# ────── choice 2 ────────────────────────────────────────────────────────────────────────────────
    # ALLOWS THE CUSTOMER's TO VIEW THE BALANCE LEFT IN THEIR ACCOUNTS
    elif choice == '2':

        acc_num = pyip.inputInt(
            f"{Fore.LIGHTBLUE_EX}Enter Account Number: {Style.RESET_ALL}")
        acc = get_ainfo(acc_num)
        
        # CHECKS IF THE ACCOUNT IS VALID AND UNLOCKED
        if not acc:
            Print(Panel("[red1]Account Not found!"), justify = "center")

        elif return_status(acc_num) == 1:
            locked()
            Print("[red1]Contact Bank Manager to Unlock", justify = "center")
            
        # AUTHENTICATES THE PASSWORD
        else:
            max_tries = 3
            for _ in range(max_tries):
                passc = masked_input("Enter Your Password: ")

                # PRINTS THE DETAILS IF CORRECT PASSWORD IS ENTERED
                if authorize_passcode(acc_num) == (passc,):
                    disp_single_acc_info(acc_num)
                    break
                else:
                    Print(Panel("[red1]Wrong Password"), justify = "center")

            # ACCOUNT IS LOCKED IF WRONG PASSWORD IS ENTERED 3 TIMES
            else:
                locked()
                account_status(acc_num, 'locked')

# ────── choice 3 ────────────────────────────────────────────────────────────────────────────────
    # ALLOWS THE CUSTOMER's TO DEPOSIT MONEY
    elif choice == '3':
        acc_num = pyip.inputInt(
            f"{Fore.LIGHTBLUE_EX}Enter Account Number: {Style.RESET_ALL}")
        acc = get_ainfo(acc_num,)
        # CHECKS IF THE ACCOUNT IS VALID
        if acc:
            amt = pyip.inputInt(
                f"{Fore.LIGHTBLUE_EX}Enter Amount to Deposit: {Style.RESET_ALL}")
            Print('''[orange_red1]
┌─────────────────────────────────────────┐
│Would You Like to Donate 1 AED to Charity│
│          1.Yes          2.No            │
└─────────────────────────────────────────┘''', justify="center")
            c = int(input(":"))
            transaction_type = 'deposited'
            new_bal = np.add(amt, acc[1])

            if c == 1:
                amt = np.subtract(amt, 1)
                new_bal = np.subtract(new_bal, 1)
                update_balance(acc_num, new_bal.item(), transaction_type, amt.item())
                acc = get_ainfo(acc_num)
                donated(acc_num)
                Print(Panel("[deep_pink4]Amount Deposited Successfully!")
                      , justify="center")
                Print("[deep_pink4]Your Current Balance is --->", acc[1]
                      , "[deep_pink4]Dhs", justify="center")

            elif c == 2:
                update_balance(acc_num, new_bal.item(), transaction_type, amt)
                acc = get_ainfo(acc_num)
                Print(Panel("[deep_pink4]Amount Deposited Successfully!")
                      , justify = "center")
                Print("[deep_pink4]Your Current Balance is --->", acc[1]
                      , "[deep_pink4]Dhs", justify = "center")
            else:
                Print(Panel('[red1]Invalid Choice'), justify = "center")

# ────── choice 4 ────────────────────────────────────────────────────────────────────────────────
    # ALLOWS THE CUSTOMER's TO WITHDRAW THEIR MONEY
    elif choice == '4':

        acc_num = pyip.inputInt(
            f"{Fore.LIGHTBLUE_EX}Enter Account Number: {Style.RESET_ALL}")
        acc = get_ainfo(acc_num)

        # CHECKS IF THE ACCOUNT IS VALID AND UNLOCKED
        if not acc:
            Print(Panel("[red1]Account Not Found!"), justify = "center")
        elif return_status(acc_num) == 1:
            locked()
            Print("[red1]Contact Bank Manager to Unlock", justify = "center")

        # AUTHENTICATES THE PASSWORD
        else:
            for _ in range(3):
                passc = masked_input("Enter Your Password: ")

                # ALLOWS CUSTOMER's TO WITHDRAW IF CORRECT PASSWORD IS ENTERED
                if authorize_passcode(acc_num) == (passc,):

                    amt = pyip.inputInt(
                        f"{Fore.LIGHTBLUE_EX}Enter Amount To Withdraw: {Style.RESET_ALL}")
                    transaction_type = 'withdrawn'

                    if acc[1] > amt:
                        new_bal = np.subtract(acc[1], amt)
                        update_balance(acc_num, new_bal.item(), transaction_type, amt)
                        Print(Panel("[deep_pink4]Amount Withdrawn Successfully!")
                              , justify = "center")
                        Print("[deep_pink4]Your Current Balance is --->", new_bal, "Dhs"
                              , justify = "center")
                        break
                    elif acc[1] == amt:
                        p = '[cornflower_blue]Close Account To Withdraw All Money From Account'
                        Print(Panel(p)
                              , justify = "center")
                        break
                    else:
                        Print(Panel("[red1]Insufficient Balance!"), justify = "center")
                        Print("[red1]You Have Only --->", acc[1], "Dhs In Your Account"
                              , justify = "center")
                        break
                else:
                    Print(Panel("[red1]Wrong Password"), justify = "center")

            # ACCOUNT IS LOCKED IF WRONG PASSWORD IS ENTERED 3 TIMES
            else:
                locked()
                account_status(acc_num, 'locked')

# ────── choice 5 ────────────────────────────────────────────────────────────────────────────────
    # ALLOWS THE CUSTOMER's TO PERFORM BANK TRANSFERS
    elif choice == '5':
        s_acc_num = pyip.inputInt(
            f"{Fore.LIGHTBLUE_EX}Enter Your Account Number: {Style.RESET_ALL}")
        s_acc = get_ainfo(s_acc_num)

        # CHECKS IF THE SOURCE ACCOUNT IS VALID AND UNLOCKED
        if s_acc:
            if return_status(s_acc_num) == 1:
                locked()
                Print("[red1]Contact Bank Manager to Unlock", justify = "center")

            # AUTHENTICATES THE PASSWORD
            else:
                max_tries = 3
                for _ in range(max_tries):
                    passc = masked_input("Enter Your Password: ")

                    # CHECKS IF THE DESTINATION ACCOUNT IS VALID
                    if authorize_passcode(s_acc_num) == (passc,):
                        r_acc_num = pyip.inputInt(
                            f"{Fore.LIGHTBLUE_EX}Enter Destination Account: {Style.RESET_ALL}")
                        r_acc = get_ainfo(r_acc_num)
                        if r_acc:
                            amt = pyip.inputFloat(
                                f"{Fore.LIGHTBLUE_EX}Enter Amount to Transfer: {Style.RESET_ALL}")
                            
                            # TRANSFERS THE AMOUNT IF SOURCE ACCOUNT HAS SUFFICIENT BALANCE
                            if s_acc[1] >= amt:
                                s_bal = np.subtract(s_acc[1] ,amt)
                                r_bal = np.add(r_acc[1], amt)
                                update_multiple_balance(s_acc_num, r_acc_num, amt
                                                        , s_bal.item(), r_bal.item())
                                Print(Panel("[deep_pink4]Bank Transfer Successful!")
                                      , justify = "center")
                                s_acc = get_ainfo(s_acc_num)
                                Print("[deep_pink4]Remaining Balance is ---> ", s_acc[1]
                                      , "[deep_pink4]Dhs", justify ="center")
                                break
                            
                            else:
                                Print(Panel("[red1]Insufficient Balance")
                                      , justify = "center")
                                s_acc = get_ainfo(s_acc_num)
                                Print("[red1]You Have Only ---> ", s_acc[1]
                                      , "[red1]Dhs in Your Account", justify = "center")
                                break
                        else:
                            Print(Panel("[red1]Destination Account Not Found!")
                                  , justify = "center")
                    else:
                        Print(Panel("[red1]Wrong Password"), justify = "center")
                # ACCOUNT IS LOCKED IF WRONG PASSWORD IS ENTERED 3 TIMES
                else:
                    locked()
                    account_status(s_acc_num, 'locked')
        else:
            Print(Panel("[red1]Source Account Not Found"), justify = "center")

# ────── choice 6 ────────────────────────────────────────────────────────────────────────────────
    # ALLOWS THE MANAGER TO MANAGE PHOENIX BANK
    elif choice == '6':
        Print(Panel("[dodger_blue2]Only Bank Manager is Allowed to Access the Manager's Menu")
              , justify = "center")
        max_tries = 3
        password_verified = False
        for tries_left in range(max_tries, 0, -1):
            if not password_verified:
                password = masked_input("Enter the Bank Manager's Password: ")
                if password == "123":
                    password_verified = True
                    Print(Panel("[slate_blue3]IDENTITY VERIFIED"), justify = "center")

                    while True:
                        print_horizontal_line()
                        box4()
                        ch = console.input("[magenta1]Enter your choice:")

                        if ch == '1':
                            acc_num = pyip.inputInt(
                                f"{Fore.LIGHTBLUE_EX}Enter Account Number: {Style.RESET_ALL}")
                            column_names, rows = get_all_infos(acc_num)
                            display_tabulated_data(column_names, rows)
                            column_names, rows = get_linfo(acc_num)
                            display_tabulated_data(column_names, rows)

                        elif ch == '2':
                            column_names, rows = get_all_info()
                            display_tabulated_data(column_names, rows)

                        elif ch == '3':
                            column_names, rows = pcust_info()
                            display_tabulated_data(column_names, rows)

                        elif ch == '4':
                            column_names, rows = get_all_linfo()
                            display_tabulated_data(column_names, rows)

                        elif ch == '5':
                            tbal = get_total_balance()
                            Print("[deep_pink4]Total Cash Available Now Is -->", tbal
                                  , "[deep_pink4]DHS Only", justify = "center")

                        elif ch == '6':
                            acc_num = pyip.inputInt(
                                f"{Fore.LIGHTBLUE_EX}Enter Account Number: {Style.RESET_ALL}")
                            acc = get_ainfo(acc_num)
                            if acc:
                                np1 = password_checker()
                                np2 = masked_input("Re-Enter Your New Password: ")

                                if np1 == np2:
                                    new_pass = np2
                                    status = 'unlocked'
                                    account_status(acc_num, status)
                                    reset_passcode(acc_num, new_pass)
                                    Print("Account Password Changed and is now Usable!")
                                else:
                                    Print("Passwords Don't Match.")
                            else:
                                Print("Account Does Not Exist.")

                        # EXIT THE MANAGER's MENU
                        elif ch == '7':
                            Print("Exiting the Manager's Menu...")
                            print_horizontal_line()
                            input("Press Enter to Exit Manager's Menu...")
                            print()
                            clean_terminal_screen()
                            break
                        else:
                            Print("Invalid Choice")
                            print_horizontal_line()
                            input("Press Enter to Continue...")
                            print()
                            clean_terminal_screen()
                    break
                elif password == '@':
                    break

                # CALLS THE POLICE IF THE WRONG MANAGER's PASSWORD IS ENTERED 3 TIMES
                else:
                    Print(Panel("[red1]Incorrect password"), justify = "center")
                    Print('[red1]Tries left:', tries_left - 1, justify = "center")

        if tries_left == 1:
            Print("[bright_red]Unauthorized access detected. Calling the police..."
                  , justify = "center")
            print_horizontal_line()
            input("PRESS ENTER TO CONTINUE...")
            clean_terminal_screen()
            break_Off()

# ────── choice 7 ────────────────────────────────────────────────────────────────────────────────
    elif choice == '7':

        acc_num = pyip.inputInt(
            f"{Fore.LIGHTBLUE_EX}Enter Account Number To Delete: {Style.RESET_ALL}")
        acc = get_ainfo(acc_num)

        # CHECKS IF THE ACCOUNT IS VALID AND UNLOCKED
        if not acc:
            Print(Panel("[red1]Account Not found!"), justify = "center")

        elif return_status(acc_num) == 1:
            locked()
            Print("[red1]Contact Bank Manager to Unlock", justify = "center")

        # AUTHENTICATES THE PASSWORD
        else:
            max_tries = 3
            for _ in range(max_tries):
                passc = masked_input("Enter Your Password: ")

                if authorize_passcode(acc_num) == (passc,):
                    del_acc(acc_num)
                    Print(Panel("[wheat4]Account Deleted Successfully")
                          , justify = "center")
                    Print(Panel("[dark_olive_green2]sad to see you go")
                          , justify = "center")
                    break
                else:
                    Print(Panel("[red1]Wrong Password"), justify = "center")

            # ACCOUNT IS LOCKED IF WRONG PASSWORD IS ENTERED 3 TIMES
            else:
                locked()
                account_status(acc_num, 'locked')

# ────── choice 8 ────────────────────────────────────────────────────────────────────────────────
    # TO EXIT THE PHOENIX BANK MANAGEMENT SYSTEM
    elif choice == '8':
        input("PRESS ENTER TO EXIT ")
        print_horizontal_line()
        title = pyfiglet.figlet_format('Thank You!', font ='Standard')
        Print(f'[bold blue]{title}',justify ='center')

        for i in track(
            range(3), description = Print("[chartreuse2]Exiting the application...")):
            time.sleep(1)
        break_Off()
    else:
        Print(Panel("[bold red]Error!"),justify ='center')
        Print(Panel("[bold red]Invalid Choice"), justify = "center")

    print_horizontal_line()
    input("PRESS ENTER TO CONTINUE...")
    clean_terminal_screen()
