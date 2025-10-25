"""use bank_demo_db;
select*from accounts;"""


import mysql.connector
from mysql.connector import errorcode
from datetime import datetime

DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "Suriya!36"
DB_NAME = "bank_demo_db"

def setup_database():
    """Ensure database and accounts table exist."""
    conn = None
    cur = None
    try:
        # Connect to MySQL server without selecting a database
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cur.execute(f"USE {DB_NAME}")
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS accounts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            account_holder VARCHAR(100) NOT NULL,
            balance DECIMAL(10,2) NOT NULL,
            pin CHAR(4) NOT NULL,
            created_at DATETIME NOT NULL,
            UNIQUE KEY unique_holder (account_holder)
        )"""
        cur.execute(create_table_sql)
        conn.commit()
    except mysql.connector.Error as err:
        print("Data base connected successfully!")
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Database setup error: Access denied (check DB_USER/DB_PASSWORD).")
        else:
            print(f"Database setup error: {err}")
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_connection():
    """Return a connection to the application database or None on failure."""
    try:
        return mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
    except mysql.connector.Error as err:
        print("Could not connect to MySQL:")
        print("Error:", err)
        return None

def create_account():
    try:
        name = input("Enter account holder name: ").strip()
        initial_deposit_text = input("Enter initial deposit amount: ").strip()
        pin = input("Enter 4-digit PIN: ").strip()

        if not name or not initial_deposit_text.replace('.','',1).isdigit():
            print("Please provide a name and a valid number for initial deposit.")
            return
        if not pin.isdigit() or len(pin) != 4:
            print("Please provide a valid 4-digit PIN.")
            return

        initial_deposit = float(initial_deposit_text)
        if initial_deposit < 0:
            print("Initial deposit cannot be negative.")
            return

        conn = get_connection()
        if not conn: return
        cur = conn.cursor()

        # Duplicate name check
        cur.execute("SELECT id FROM accounts WHERE account_holder = %s", (name,))
        if cur.fetchone():
            print("Error: An account with this name already exists.")
            return

        sql = """INSERT INTO accounts (account_holder, balance, pin, created_at)
                 VALUES (%s, %s, %s, %s)"""
        values = (name, initial_deposit, pin, datetime.now())
        cur.execute(sql, values)
        conn.commit()
        print("Account created successfully! ID:", cur.lastrowid)
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

def view_accounts():
    try:
        conn = get_connection()
        if not conn: return
        cur = conn.cursor()
        cur.execute("SELECT id, account_holder, balance, created_at FROM accounts ORDER BY id")
        rows = cur.fetchall()
        if not rows:
            print("No accounts found.")
            return
        print("\n--- Accounts ---")
        for r in rows:
            print(f"ID: {r[0]} | Holder: {r[1]} | Balance: ${r[2]:.2f} | Created: {r[3]}")
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

def update_account():
    try:
        id_text = input("Enter account ID to update: ").strip()
        pin = input("Enter account PIN: ").strip()
        if not id_text.isdigit():
            print("Please enter a valid ID number.")
            return

        conn = get_connection()
        if not conn: return
        cur = conn.cursor()

        # Verify account and pin
        cur.execute("SELECT id FROM accounts WHERE id=%s AND pin=%s", (id_text, pin))
        if not cur.fetchone():
            print("Invalid account ID or PIN.")
            return

        new_name = input("Enter new account holder name (or press Enter to skip): ").strip()
        new_balance_text = input("Enter new balance (or press Enter to skip): ").strip()

        updates = []
        params = []

        if new_name:
            # Duplicate name check (exclude current id)
            cur.execute("SELECT id FROM accounts WHERE account_holder=%s AND id!=%s", (new_name, id_text))
            if cur.fetchone():
                print("Error: An account with this name already exists.")
                return
            updates.append("account_holder=%s")
            params.append(new_name)

        if new_balance_text:
            if not new_balance_text.replace('.','',1).isdigit():
                print("Invalid balance amount.")
                return
            new_balance = float(new_balance_text)
            if new_balance < 0:
                print("Balance cannot be negative.")
                return
            updates.append("balance=%s")
            params.append(new_balance)

        if not updates:
            print("No changes requested.")
            return

        params.extend([id_text, pin])
        sql = f"UPDATE accounts SET {', '.join(updates)} WHERE id=%s AND pin=%s"
        cur.execute(sql, params)
        conn.commit()
        if cur.rowcount > 0:
            print("Account updated successfully.")
        else:
            print("Update failed.")
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

def delete_account():
    try:
        id_text = input("Enter account ID to delete: ").strip()
        pin = input("Enter account PIN: ").strip()
        if not id_text.isdigit():
            print("Please enter a valid ID number.")
            return
        confirm = input("Are you sure you want to delete this account? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Deletion cancelled.")
            return

        conn = get_connection()
        if not conn: return
        cur = conn.cursor()
        cur.execute("DELETE FROM accounts WHERE id=%s AND pin=%s", (id_text, pin))
        conn.commit()
        if cur.rowcount > 0:
            print("Account deleted successfully.")
        else:
            print("No account found with that ID and PIN.")
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

def deposit():
    try:
        id_text = input("Enter account ID: ").strip()
        pin = input("Enter account PIN: ").strip()
        amount_text = input("Enter amount to deposit: ").strip()
        if not id_text.isdigit():
            print("Please enter a valid ID number.")
            return
        if not amount_text.replace('.','',1).isdigit():
            print("Please enter a valid amount.")
            return
        amount = float(amount_text)
        if amount <= 0:
            print("Deposit amount must be positive.")
            return

        conn = get_connection()
        if not conn: return
        cur = conn.cursor()
        cur.execute("SELECT balance FROM accounts WHERE id=%s AND pin=%s", (id_text, pin))
        row = cur.fetchone()
        if not row:
            print("Invalid account ID or PIN.")
            return
        prev = float(row[0])
        new = prev + amount
        cur.execute("UPDATE accounts SET balance=%s WHERE id=%s", (new, id_text))
        conn.commit()
        print(f"Deposit successful. Previous: ${prev:.2f}  Deposited: ${amount:.2f}  New: ${new:.2f}")
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

def withdraw():
    try:
        id_text = input("Enter account ID: ").strip()
        pin = input("Enter account PIN: ").strip()
        amount_text = input("Enter amount to withdraw: ").strip()
        if not id_text.isdigit():
            print("Please enter a valid ID number.")
            return
        if not amount_text.replace('.','',1).isdigit():
            print("Please enter a valid amount.")
            return
        amount = float(amount_text)
        if amount <= 0:
            print("Withdrawal amount must be positive.")
            return

        conn = get_connection()
        if not conn: return
        cur = conn.cursor()
        cur.execute("SELECT balance FROM accounts WHERE id=%s AND pin=%s", (id_text, pin))
        row = cur.fetchone()
        if not row:
            print("Invalid account ID or PIN.")
            return
        prev = float(row[0])
        if amount > prev:
            print("Insufficient funds.")
            return
        new = prev - amount
        cur.execute("UPDATE accounts SET balance=%s WHERE id=%s", (new, id_text))
        conn.commit()
        print(f"Withdrawal successful. Previous: ${prev:.2f}  Withdrawn: ${amount:.2f}  New: ${new:.2f}")
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

def main():
    print("Bank Account Management System\n")
    setup_database()

    while True:
        print("\nChoose an option:")
        print("1) Create new account")
        print("2) View all accounts")
        print("3) Update account")
        print("4) Delete account")
        print("5) Deposit")
        print("6) Withdraw")
        print("7) Exit")

        choice = input("Your choice (1-7): ").strip()
        if choice == "1":
            create_account()
        elif choice == "2":
            view_accounts()
        elif choice == "3":
            update_account()
        elif choice == "4":
            delete_account()
        elif choice == "5":
            deposit()
        elif choice == "6":
            withdraw()
        elif choice == "7":
            print("Goodbye.")
            break
        else:
            print("Please choose a valid option (1-7).")

if __name__== "__main__":
    main()
# ...existing code...1
