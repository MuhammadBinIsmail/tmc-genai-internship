"""Day 8 - OOP, Modules & File I/O: bank.py"""

import json
import os
DATA_FILE = "accounts.json"

class BankAccount:
    """A basic bank account with deposit/withdraw functionality."""

    def __init__(self, account_number, owner_name, balance=0):
        self.account_number = account_number
        self.owner_name = owner_name
        self.balance = balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.balance += amount

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if amount > self.balance:
            raise ValueError("Insufficient funds.")
        self.balance -= amount

    def to_dict(self):
        # Converts the object into a plain dict so it can be
        # written to JSON (JSON doesn't understand Python objects directly).
        return {
            "type": "BankAccount",
            "account_number": self.account_number,
            "owner_name": self.owner_name,
            "balance": self.balance,
        }

    def __str__(self):
        return f"Account {self.account_number} ({self.owner_name}): ${self.balance:.2f}"

    def __repr__(self):
        return f"BankAccount({self.account_number!r}, {self.owner_name!r}, {self.balance!r})"


class SavingsAccount(BankAccount):
    """A bank account that earns interest. Inherits deposit/withdraw from BankAccount."""

    def __init__(self, account_number, owner_name, balance=0, interest_rate=0.02):
        super().__init__(account_number, owner_name, balance)
        self.interest_rate = interest_rate

    def add_interest(self):
        interest = self.balance * self.interest_rate
        self.balance += interest
        return interest

    def to_dict(self):
        data = super().to_dict()
        data["type"] = "SavingsAccount"
        data["interest_rate"] = self.interest_rate
        return data

    def __str__(self):
        return f"{super().__str__()} (Savings, {self.interest_rate * 100:.1f}% interest)"

    def __repr__(self):
        return (f"SavingsAccount({self.account_number!r}, {self.owner_name!r}, "
                f"{self.balance!r}, {self.interest_rate!r})")

def account_from_dict(data):
    # Rebuilds the correct account type (BankAccount or SavingsAccount)
    # from saved JSON data, based on the "type" field we stored earlier.
    if data["type"] == "SavingsAccount":
        return SavingsAccount(data["account_number"], data["owner_name"],
                               data["balance"], data["interest_rate"])
    return BankAccount(data["account_number"], data["owner_name"], data["balance"])

def save_accounts(accounts, filename=DATA_FILE):
    # Writes all accounts to a JSON file so data survives after the program closes.
    with open(filename, "w") as f:
        json.dump([acc.to_dict() for acc in accounts], f, indent=2)
    print(f"Saved {len(accounts)} account(s) to {filename}.")

def load_accounts(filename=DATA_FILE):
    # Reads accounts back from the JSON file when the program starts.
    # Returns an empty list if no file exists yet (first run).
    if not os.path.exists(filename):
        print(f"No data file found at {filename}. Starting with an empty account list.")
        return []
    with open(filename, "r") as f:
        data = json.load(f)
    return [account_from_dict(entry) for entry in data]

def find_account(accounts, account_number):
    # Searches the in-memory account list by account number.
    for acc in accounts:
        if acc.account_number == account_number:
            return acc
    return None

def create_account(accounts):
    number = input("Enter new account number: ").strip()
    if find_account(accounts, number):
        print("An account with that number already exists.")
        return
    name = input("Enter owner name: ").strip()
    balance = float(input("Enter starting balance: "))
    is_savings = input("Is this a savings account? (y/n): ").strip().lower() == "y"

    if is_savings:
        rate = float(input("Enter interest rate (e.g., 0.02 for 2%): "))
        accounts.append(SavingsAccount(number, name, balance, rate))
    else:
        accounts.append(BankAccount(number, name, balance))

    print("Account created.")

def deposit_to_account(accounts):
    number = input("Enter account number: ").strip()
    acc = find_account(accounts, number)
    if not acc:
        print("Account not found.")
        return
    try:
        amount = float(input("Enter deposit amount: "))
        acc.deposit(amount)
        print(f"New balance: ${acc.balance:.2f}")
    except ValueError as e:
        print(f"Error: {e}")

def withdraw_from_account(accounts):
    number = input("Enter account number: ").strip()
    acc = find_account(accounts, number)
    if not acc:
        print("Account not found.")
        return
    try:
        amount = float(input("Enter withdrawal amount: "))
        acc.withdraw(amount)
        print(f"New balance: ${acc.balance:.2f}")
    except ValueError as e:
        print(f"Error: {e}")

def apply_interest(accounts):
    number = input("Enter savings account number: ").strip()
    acc = find_account(accounts, number)
    if not acc:
        print("Account not found.")
        return
    if not isinstance(acc, SavingsAccount):
        print("This account does not earn interest.")
        return
    interest = acc.add_interest()
    print(f"Interest added: ${interest:.2f}. New balance: ${acc.balance:.2f}")

def view_accounts(accounts):
    if not accounts:
        print("No accounts to display.")
        return
    for acc in accounts:
        print(acc)

def show_menu():
    print("\n--- Bank Account Manager ---")
    print("1. Create Account")
    print("2. Deposit")
    print("3. Withdraw")
    print("4. Apply Interest (Savings only)")
    print("5. View All Accounts")
    print("6. Save to File")
    print("7. Exit")

def main():
    accounts = load_accounts()
    while True:
        show_menu()
        choice = input("Select an option (1-7): ").strip()

        match choice:
            case "1":
                create_account(accounts)
            case "2":
                deposit_to_account(accounts)
            case "3":
                withdraw_from_account(accounts)
            case "4":
                apply_interest(accounts)
            case "5":
                view_accounts(accounts)
            case "6":
                save_accounts(accounts)
            case "7":
                save_accounts(accounts)
                print("Goodbye!")
                break
            case _:
                print("Invalid choice, please select 1-7.")
if __name__ == "__main__":
    main()