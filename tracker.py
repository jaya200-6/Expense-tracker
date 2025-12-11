import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st


# --- 1. Session State Initialization ---
# We verify if 'expenses' exists in the session state; if not, we initialize it.
if 'expenses' not in st.session_state:
    st.session_state['expenses'] = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Description'])

# Initialize monthly income state
if 'monthly_income' not in st.session_state:
    st.session_state['monthly_income'] = 0.0 

# --- 2. Define Functions (No changes needed here for the new feature) ---

def add_expense(date, category, amount, description):
    """Creates a new dataframe row and appends it to the session state."""
    new_expense = pd.DataFrame([[date, category, amount, description]], 
                               columns=['Date', 'Category', 'Amount', 'Description'])
    
    # Concatenate the new data with the existing data in session state
    st.session_state['expenses'] = pd.concat([st.session_state['expenses'], new_expense], ignore_index=True)
    st.success("Expense Added!")

def save_expenses():
    """Saves the current expense dataframe to a CSV file."""
    st.session_state['expenses'].to_csv("expenses.csv", index=False)
    st.success("Expense Saved Successfully")

def load_expenses():
    """Loads a CSV file uploaded by the user into the session state."""
    uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        st.session_state['expenses'] = pd.read_csv(uploaded_file)
        st.sidebar.success("Expenses Loaded Successfully")

def visualize_expenses():
    """Creates a bar chart using Seaborn to visualize expenses by category."""
    if not st.session_state['expenses'].empty:
        # Create a figure and axis for the plot
        fig, ax = plt.subplots(figsize=(10, 5))
        
        # Aggregate expenses by category for a cleaner chart
        expense_summary = st.session_state['expenses'].groupby('Category')['Amount'].sum().reset_index()
        
        # Create the bar plot: X-axis = Category, Y-axis = Sum of Amount
        sns.barplot(data=expense_summary, x='Category', y='Amount', ax=ax)
        
        # Set title and rotate x-axis labels
        ax.set_title('Expense Breakdown by Category')
        plt.xticks(rotation=45)
        plt.xlabel('Expense Category')
        plt.ylabel('Total Amount Spent')
        
        # Display the plot in Streamlit
        st.pyplot(fig)
    else:
        st.warning("No expenses to visualize")

# --- 3. UI Layout & Main Application Flow ---

# Title of the App
st.title(" Expense & Savings Tracker 💸")

# --- NEW: Monthly Income Input ---
# This input sets the budget for savings calculation
new_income = st.number_input("Enter Your Total Monthly Income/Salary:", 
                             min_value=0.0, 
                             value=st.session_state['monthly_income'], 
                             step=500.0, 
                             format="%.2f",
                             key='salary_input')

# Update the session state when the input changes
if new_income != st.session_state['monthly_income']:
    st.session_state['monthly_income'] = new_income
    
# --- NEW: Financial Summary Section ---

# Check if data exists and income is set to perform calculations
if st.session_state['monthly_income'] > 0 and not st.session_state['expenses'].empty:
    
    # Calculate Total Expenses
    total_expenses = st.session_state['expenses']['Amount'].sum()
    
    # Calculate Savings/Remaining Amount
    remaining_amount = st.session_state['monthly_income'] - total_expenses
    
    st.header("Financial Summary")
    
    # Display key metrics using Streamlit's columns and metric element
    col1, col2, col3 = st.columns(3)
    
    col1.metric("Total Monthly Income", f"₹ {st.session_state['monthly_income']:,.2f}")
    
    col2.metric("Total Expenses (Tracked)", f"₹ {total_expenses:,.2f}")
    
    # Conditional coloring for Savings Goal
    if remaining_amount >= 0:
        # Green for positive balance (Savings)
        col3.metric("Remaining Savings Goal", f"₹ {remaining_amount:,.2f}", 
                    delta="Within Budget", delta_color="normal")
    else:
        # Red for negative balance (Over budget)
        col3.metric("Remaining Savings Goal", f"₹ {remaining_amount:,.2f}", 
                    delta=f"Over Budget: ₹ {abs(remaining_amount):,.2f}", delta_color="inverse")

    st.markdown("---") 

# --- Sidebar Configuration (Remains the same) ---
with st.sidebar:
    st.header("Add Expense")
    
    # Input fields for new expense
    date = st.date_input("Date")
    category = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Utilities", "Other"])
    amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    description = st.text_input("Description")
    
    # Button to trigger add_expense function
    if st.button("Add"):
        # Ensure amount is not zero before adding
        if amount > 0:
            add_expense(date, category, amount, description)
        else:
            st.warning("Expense amount must be greater than zero.")

    st.header("File Operations")
    
    # Button to save data
    if st.button("Save Expenses"):
        save_expenses()
        
    # Section to load data
    st.write("Load Expenses:")
    load_expenses() 

# --- Main Page Display (Remains the same) ---

# Display the Data Table
st.header("Expense Details")
st.write(st.session_state['expenses'])

# Display Visualization
st.header("Visualization")
if st.button("Visualize Expenses"):
    visualize_expenses()