from pathlib import Path
import string
import random
import json
import streamlit as st


class Bank:
    database = "data.json"
    data = []

    # -------------------------------
    # Load existing data
    # -------------------------------
    @classmethod
    def load_data(cls):
        try:
            if Path(cls.database).exists():
                with open(cls.database, "r") as fs:
                    cls.data = json.load(fs)
            else:
                cls.data = []

        except (json.JSONDecodeError, OSError) as err:
            st.error(f"Error loading database: {err}")
            cls.data = []

    # -------------------------------
    # Update JSON database
    # -------------------------------
    @classmethod
    def __update(cls):
        try:
            with open(cls.database, "w") as fs:
                json.dump(cls.data, fs, indent=4)

        except OSError as err:
            st.error(f"Error updating database: {err}")

    # -------------------------------
    # Generate account number
    # -------------------------------
    @classmethod
    def __createaccountno(cls):

        letters = "".join(
            random.choices(string.ascii_uppercase, k=3)
        )

        numbers = "".join(
            random.choices(string.digits, k=4)
        )

        special = "".join(
            random.choices("!@#$%^&*", k=3)
        )

        account = list(letters + numbers + special)

        random.shuffle(account)

        return "".join(account)

    # -------------------------------
    # Create Account
    # -------------------------------
    @classmethod
    def create_account(cls, name, age, email, pin):

        # Validation
        if not name.strip():
            return False, "Name cannot be empty."

        if age < 18:
            return False, "You must be at least 18 years old."

        if not pin.isdigit() or len(pin) != 4:
            return False, "PIN must contain exactly 4 digits."

        if not email.strip():
            return False, "Email cannot be empty."

        account_no = cls.__createaccountno()

        info = {
            "name": name.strip(),
            "age": age,
            "email": email.strip(),
            "AccountNo": account_no,
            "Pin": pin,
            "Balance": 0
        }

        cls.data.append(info)
        cls.__update()

        return True, info

    # -------------------------------
    # Authenticate User
    # -------------------------------
    @classmethod
    def authenticate(cls, accno, pin):

        for account in cls.data:

            if (
                account["AccountNo"] == accno
                and account["Pin"] == pin
            ):
                return account

        return None

    # -------------------------------
    # Deposit Money
    # -------------------------------
    @classmethod
    def deposit_money(cls, accno, pin, amount):

        account = cls.authenticate(accno, pin)

        if not account:
            return False, "Invalid account number or PIN."

        if amount <= 0:
            return False, "Amount must be greater than ₹0."

        if amount > 10000:
            return False, "Maximum deposit allowed is ₹10,000."

        account["Balance"] += amount

        cls.__update()

        return True, f"₹{amount:,.2f} deposited successfully."

    # -------------------------------
    # Withdraw Money
    # -------------------------------
    @classmethod
    def withdraw_money(cls, accno, pin, amount):

        account = cls.authenticate(accno, pin)

        if not account:
            return False, "Invalid account number or PIN."

        if amount <= 0:
            return False, "Amount must be greater than ₹0."

        if amount > account["Balance"]:
            return False, "Insufficient balance."

        account["Balance"] -= amount

        cls.__update()

        return True, (
            f"₹{amount:,.2f} withdrawn successfully. "
            f"Remaining balance: ₹{account['Balance']:,.2f}"
        )

    # -------------------------------
    # Get Account Details
    # -------------------------------
    @classmethod
    def get_details(cls, accno, pin):

        account = cls.authenticate(accno, pin)

        if not account:
            return None

        return account

    # -------------------------------
    # Update Account
    # -------------------------------
    @classmethod
    def update_details(
        cls,
        accno,
        pin,
        name=None,
        email=None,
        new_pin=None
    ):

        account = cls.authenticate(accno, pin)

        if not account:
            return False, "Invalid account number or PIN."

        if name:
            account["name"] = name.strip()

        if email:
            account["email"] = email.strip()

        if new_pin:

            if not new_pin.isdigit() or len(new_pin) != 4:
                return False, "New PIN must contain exactly 4 digits."

            account["Pin"] = new_pin

        cls.__update()

        return True, "Account details updated successfully."

    # -------------------------------
    # Delete Account
    # -------------------------------
    @classmethod
    def delete_account(cls, accno, pin):

        account = cls.authenticate(accno, pin)

        if not account:
            return False, "Invalid account number or PIN."

        if account["Balance"] != 0:
            return (
                False,
                "Account cannot be deleted while balance is not zero."
            )

        cls.data.remove(account)

        cls.__update()

        return True, "Account deleted successfully."


# =========================================================
# STREAMLIT CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Bank Management System",
    page_icon="🏦",
    layout="centered"
)

# Load JSON data
Bank.load_data()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🏦 Bank Management System")

menu = st.sidebar.radio(
    "Select an option",
    [
        "Create Account",
        "Deposit Money",
        "Withdraw Money",
        "Account Details",
        "Update Details",
        "Delete Account"
    ]
)


# =========================================================
# HOME / HEADER
# =========================================================

st.title("🏦 Bank Management System")

st.write(
    "A simple banking application built using "
    "**Python, OOP, JSON and Streamlit**."
)

st.divider()


# =========================================================
# CREATE ACCOUNT
# =========================================================

if menu == "Create Account":

    st.header("📝 Create New Account")

    name = st.text_input("Full Name")

    age = st.number_input(
        "Age",
        min_value=1,
        max_value=120,
        value=18
    )

    email = st.text_input("Email")

    pin = st.text_input(
        "Create 4-digit PIN",
        type="password",
        max_chars=4
    )

    if st.button("Create Account", type="primary"):

        success, result = Bank.create_account(
            name,
            age,
            email,
            pin
        )

        if success:

            st.success("🎉 Account created successfully!")

            st.subheader("Your Account Details")

            st.write(f"**Name:** {result['name']}")
            st.write(f"**Age:** {result['age']}")
            st.write(f"**Email:** {result['email']}")

            st.code(
                result["AccountNo"],
                language=None
            )

            st.write(
                f"**PIN:** {result['Pin']}"
            )

            st.write(
                f"**Initial Balance:** ₹{result['Balance']:,.2f}"
            )

            st.warning(
                "⚠️ Save your account number and PIN safely."
            )

        else:
            st.error(result)


# =========================================================
# DEPOSIT
# =========================================================

elif menu == "Deposit Money":

    st.header("💰 Deposit Money")

    accno = st.text_input("Account Number")

    pin = st.text_input(
        "PIN",
        type="password",
        max_chars=4
    )

    amount = st.number_input(
        "Deposit Amount",
        min_value=0.0,
        step=100.0
    )

    if st.button("Deposit Money", type="primary"):

        success, message = Bank.deposit_money(
            accno,
            pin,
            amount
        )

        if success:
            st.success(message)
        else:
            st.error(message)


# =========================================================
# WITHDRAW
# =========================================================

elif menu == "Withdraw Money":

    st.header("💸 Withdraw Money")

    accno = st.text_input("Account Number")

    pin = st.text_input(
        "PIN",
        type="password",
        max_chars=4
    )

    amount = st.number_input(
        "Withdrawal Amount",
        min_value=0.0,
        step=100.0
    )

    if st.button("Withdraw Money", type="primary"):

        success, message = Bank.withdraw_money(
            accno,
            pin,
            amount
        )

        if success:
            st.success(message)
        else:
            st.error(message)


# =========================================================
# ACCOUNT DETAILS
# =========================================================

elif menu == "Account Details":

    st.header("👤 Account Details")

    accno = st.text_input("Account Number")

    pin = st.text_input(
        "PIN",
        type="password",
        max_chars=4
    )

    if st.button("View Details", type="primary"):

        account = Bank.get_details(
            accno,
            pin
        )

        if account:

            st.success("Account found!")

            st.write(f"**Name:** {account['name']}")
            st.write(f"**Age:** {account['age']}")
            st.write(f"**Email:** {account['email']}")
            st.write(f"**Account Number:** {account['AccountNo']}")
            st.write(f"**Balance:** ₹{account['Balance']:,.2f}")

        else:
            st.error(
                "Invalid account number or PIN."
            )


# =========================================================
# UPDATE DETAILS
# =========================================================

elif menu == "Update Details":

    st.header("✏️ Update Account Details")

    st.info(
        "You can update your name, email and PIN. "
        "Age, account number and balance cannot be changed."
    )

    accno = st.text_input("Account Number")

    pin = st.text_input(
        "Current PIN",
        type="password",
        max_chars=4
    )

    new_name = st.text_input(
        "New Name",
        placeholder="Leave empty to keep current name"
    )

    new_email = st.text_input(
        "New Email",
        placeholder="Leave empty to keep current email"
    )

    new_pin = st.text_input(
        "New PIN",
        type="password",
        max_chars=4,
        placeholder="Leave empty to keep current PIN"
    )

    if st.button("Update Details", type="primary"):

        success, message = Bank.update_details(
            accno,
            pin,
            new_name,
            new_email,
            new_pin
        )

        if success:
            st.success(message)
        else:
            st.error(message)


# =========================================================
# DELETE ACCOUNT
# =========================================================

elif menu == "Delete Account":

    st.header("🗑️ Delete Account")

    st.warning(
        "⚠️ Account deletion is permanent."
    )

    accno = st.text_input("Account Number")

    pin = st.text_input(
        "PIN",
        type="password",
        max_chars=4
    )

    confirm = st.checkbox(
        "I understand that my account will be permanently deleted."
    )

    if st.button(
        "Delete Account",
        type="primary",
        disabled=not confirm
    ):

        success, message = Bank.delete_account(
            accno,
            pin
        )

        if success:
            st.success(message)
        else:
            st.error(message)
