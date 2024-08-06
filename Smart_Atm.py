import tkinter as tk
from tkinter import messagebox
import pandas as pd

class ATM:
    def __init__(self):
        self.admin_pin = 1234
        self.users = {}
        self.current_user = None
        self.max_pin_attempts = 3
        self.pin_attempts = {}

        self.root = tk.Tk()
        self.root.title("ATM")

        # Create GUI elements
        self.label = tk.Label(self.root, text="Welcome to the ATM")
        self.label.pack(pady=10)

        self.button_admin = tk.Button(self.root, text="Admin Login", command=self.admin_login)
        self.button_admin.pack(pady=5)

        self.button_user = tk.Button(self.root, text="User Login", command=self.user_login)
        self.button_user.pack(pady=5)

        self.button_create_account = tk.Button(self.root, text="Create User Account", command=self.create_user_account)
        self.button_create_account.pack(pady=5)

        self.button_exit = tk.Button(self.root, text="Exit", command=self.root.destroy)
        self.button_exit.pack(pady=5)
        try:
            self.load_accounts()
        except FileNotFoundError:
            pass
    def load_accounts(self):
        # Load user accounts from the Excel file into the 'users' attribute
        self.users = pd.read_excel("user_accounts.xlsx", index_col=0).to_dict(orient="index")

    def save_accounts(self):
        # Save user accounts to the Excel file
        df = pd.DataFrame.from_dict(self.users, orient="index")
        if 'level_0' in df.columns:
            df.to_excel("user_accounts.xlsx", index=False)
        else:
            df.reset_index(inplace=True)
            df.to_excel("user_accounts.xlsx", index=False)

        

    def display_menu(self):
        print("1. Log in as Admin")
        print("2. Log in as User")
        print("3. Create a new User Account")
        print("4. Exit")

    def admin_login(self):
        entered_pin = int(input("Enter Admin PIN: "))
        if entered_pin == self.admin_pin:
            messagebox.showinfo("Admin Login", "Admin logged in successfully.")
            self.admin_menu()
        else:
            messagebox.showerror("Admin Login", "Incorrect PIN. Try again.")

    def admin_menu(self):
        while True:
            print("\nAdmin Menu:")
            print("1. View All Users")
            print("2. Exit")
            choice = int(input("Enter your choice: "))
            if choice == 1:
                self.view_all_users()
            elif choice == 2:
                break
            else:
                print("Invalid choice. Try again.")

            messagebox.showinfo("Admin Menu", "Admin menu placeholder.")

    def view_all_users(self):
        print("\nList of Users:")
        for username, user_data in self.users.items():
            print(f"{username}: Balance - ${user_data['balance']}, Currency - {user_data['currency']}")

    def user_login(self):
        username = input("Enter your username: ")
        if username in self.users:
            print("User logged in successfully.")
            self.current_user = username
            self.user_menu()
        else:
            messagebox.showinfo("User Login", "User logged in successfully.")

    def create_user_account(self):
        username = input("Enter your new username: ")
        if username not in self.users:
            initial_balance = float(input("Enter initial balance: $"))
            pin = int(input("Set your PIN: "))
            preferred_currency = input("Enter your preferred currency (e.g., USD): ").upper()
            account_number = input("Enter your bill account number: ")

            self.users[username] = {
                "balance": initial_balance,
                "transactions": [],
                "pin": pin,
                "currency": preferred_currency,
                "account_number": account_number,
            }
            messagebox.showinfo("User Account Created", "User account created successfully.")
            self.save_accounts()
        else:
            messagebox.showerror("User Account Creation", "Username already exists. Please choose a different username.")
   
    def user_menu(self):
        while True:
            print(f"\nWelcome, {self.current_user}!")
            print("1. Check Balance")
            print("2. Deposit Money")
            print("3. Withdraw Money")
            print("4. Currency Conversion")
            print("5. View Transaction History")
            print("6. Log Out")
            choice = int(input("Enter your choice: "))
            if choice == 1:
                self.check_balance()
            elif choice == 2:
                self.deposit_money()
            elif choice == 3:
                self.withdraw_money()
            elif choice == 4:
                self.currency_conversion()
            elif choice == 5:
                self.view_transaction_history()
            elif choice == 6:
                break
           
            else:
                print("Invalid choice. Try again.")

        messagebox.showinfo("User Menu", f"Welcome, {self.current_user}!")

    def check_balance(self):
        print(f"Your current balance is ${self.users[self.current_user]['balance']} {self.users[self.current_user]['currency']}")

    def deposit_money(self):
        if self.is_user_blocked():
            print("Account is blocked. Contact the administrator.")
            return

        if not self.verify_pin():
            return

        amount = float(input("Enter the amount to deposit: $"))
        if amount > 0:
            self.users[self.current_user]["balance"] += amount
            self.users[self.current_user]["transactions"].append(("Deposit", amount))
            print(f"${amount} deposited successfully.")
        else:
            print("Invalid amount. Please enter a positive value.")

    def withdraw_money(self):
        if self.is_user_blocked():
            print("Account is blocked. Contact the administrator.")
            return

        if not self.verify_pin():
            return

        amount = float(input("Enter the amount to withdraw: $"))
        if 0 < amount <= self.users[self.current_user]["balance"]:
            self.users[self.current_user]["balance"] -= amount
            self.users[self.current_user]["transactions"].append(("Withdrawal", amount))
            print(f"${amount} withdrawn successfully.")
        else:
            print("Invalid amount or insufficient funds.")

    def currency_conversion(self):
        if self.is_user_blocked():
            print("Account is blocked. Contact the administrator.")
            return

        if not self.verify_pin():
            return

        currencies = {"USD": 1.0, "EUR": 0.85, "GBP": 0.73}  # Example exchange rates
        print("Available currencies:")
        for currency in currencies:
            print(currency)

        from_currency = input("Enter your currency: ").upper()
        to_currency = input("Enter the currency in which you want to convert: ").upper()

        if from_currency in currencies and to_currency in currencies:
            amount = float(input(f"Enter the amount in {from_currency}: "))
            converted_amount = amount * currencies[from_currency] / currencies[to_currency]

            print(f"{amount} {from_currency} is equivalent to {converted_amount:.2f} {to_currency}")
        else:
            print("Invalid currencies. Please enter valid currency codes.")

    def view_transaction_history(self):
        print("\nTransaction History:")
        for transaction in self.users[self.current_user]["transactions"]:
            print(f"{transaction[0]}: ${transaction[1]}")

    def verify_pin(self):
        entered_pin = int(input("Enter your PIN: "))
        if entered_pin == self.users[self.current_user]["pin"]:
            self.pin_attempts[self.current_user] = 0  # Reset unsuccessful attempts counter on successful PIN entry
            return True
        else:
            print("Incorrect PIN.")
            self.pin_attempts[self.current_user] += 1  # Increment unsuccessful attempts counter
            if self.pin_attempts[self.current_user] >= self.max_pin_attempts:
                print("Too many unsuccessful attempts. Account blocked.")
                del self.users[self.current_user]
            return False

    def is_user_blocked(self):
        return self.current_user in self.users and self.pin_attempts.get(self.current_user, 0) >= self.max_pin_attempts

    def run(self):
        self.root.mainloop()

def main():
    atm = ATM()
    atm.run()

    while True:
        atm.display_menu()
        choice = int(input("Enter your choice: "))

        if choice == 1:
            atm.admin_login()
        elif choice == 2:
            atm.user_login()
        elif choice == 3:
            atm.create_user_account()
        elif choice == 4:
            print("Exiting ATM. Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
