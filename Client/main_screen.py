import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.simpledialog import askfloat
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from DataBase.backend import add_expense, get_user_details, get_expenses, update_expense
from Client.settings import show_profile_screen


def show_main_screen(main_frame, user_id):
    """
    מסך ראשי להצגת המשכורת החודשית, יתרת ההוצאות והגרף.
    """
    for widget in main_frame.winfo_children():
        widget.destroy()

    # שליפת נתוני המשתמש
    user_details = get_user_details(user_id)
    monthly_salary = user_details["monthly_salary"] if user_details else 0

    # תווית להצגת המשכורת החודשית
    tk.Label(main_frame, text=f"Monthly Salary: {monthly_salary:.2f}", font=("Arial", 14)).pack(pady=5)

    # תווית להצגת יתרת הכסף
    remaining_label = tk.Label(main_frame, text="", font=("Arial", 14))
    remaining_label.pack(pady=5)

    # כפתור להגדרות
    tk.Button(main_frame, text="Settings", command=lambda: show_profile_screen(main_frame, user_id), bg="lightblue").pack(pady=10)

    # טבלה להצגת ההוצאות
    tree = ttk.Treeview(main_frame, columns=("Category", "Amount", "Action"), show="headings", height=10)
    tree.heading("Category", text="Category")
    tree.heading("Amount", text="Amount")
    tree.heading("Action", text="Action")
    tree.column("Action", width=100)
    tree.pack(pady=10)

    # פונקציה לעדכון יתרת הכסף והגרף
    def update_summary_and_chart():
        # קבלת הוצאות
        expenses = get_expenses(user_id)

        # ניקוי הטבלה
        for row in tree.get_children():
            tree.delete(row)

        # חישוב ההוצאות הכוללות
        total_expenses = 0
        for category, amount in expenses:
            # הוספת שורה עם כפתור עריכה
            tree.insert("", "end", values=(category, f"{amount:.2f}", "Edit"))
            total_expenses += amount

        # חישוב יתרת הכסף
        remaining = monthly_salary - total_expenses
        remaining_label.config(
            text=f"Remaining Balance: {remaining:.2f}",
            fg="red" if remaining < 0 else "green"
        )

        # עדכון גרף העוגה
        chart.clear()
        if expenses:
            labels = [row[0] for row in expenses] + ["Remaining"]
            values = [row[1] for row in expenses] + [remaining if remaining > 0 else 0]
            chart.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
            chart.set_title("Expenses Breakdown")
        else:
            chart.text(0.5, 0.5, "No expenses yet", ha="center", va="center", fontsize=12)
        canvas.draw()

    # פונקציה לעריכת הוצאה
    def edit_expense(user_id, category, old_amount, refresh_function):
        """
        עריכת שורה בטבלה.
        """
        print(f"Editing expense for user_id={user_id}, category={category}, old_amount={old_amount}")
        new_amount = askfloat("Edit Expense", f"Enter new amount for {category}:")
        if new_amount is None:
            return  # המשתמש ביטל את הפעולה

        # עדכון ההוצאה במסד הנתונים
        success = update_expense(user_id, category, old_amount, new_amount)
        if success:
            messagebox.showinfo("Success", f"Expense for {category} updated to {new_amount:.2f}.")
            refresh_function()  # רענון הטבלה והגרף
        else:
            messagebox.showerror("Error", "Failed to update expense.")

    # פונקציה לטיפול בלחיצה על שורה
    def on_tree_select(event):
        selected_item = tree.selection()
        if selected_item:
            values = tree.item(selected_item, "values")
            category = values[0]
            old_amount = float(values[1])
            edit_expense(user_id, category, old_amount, update_summary_and_chart)

    # חיבור הפונקציה לעמודת Action
    tree.bind("<Double-1>", on_tree_select)

    # גרף עוגה
    figure = Figure(figsize=(5, 5), dpi=100)
    chart = figure.add_subplot(111)
    canvas = FigureCanvasTkAgg(figure, master=main_frame)
    canvas.get_tk_widget().pack()

    # הוספת הוצאה חדשה
    tk.Label(main_frame, text="Add New Expense:").pack(pady=5)
    categories = ["Shopping", "Rent", "Utilities", "Groceries", "Entertainment"]
    category_var = tk.StringVar(value=categories[0])
    category_menu = ttk.Combobox(main_frame, textvariable=category_var, values=categories)
    category_menu.pack(pady=5)

    amount_entry = tk.Entry(main_frame)
    amount_entry.pack(pady=5)

    def add_new_expense():
        category = category_var.get()
        amount = amount_entry.get()
        if not amount.replace(".", "").isdigit():
            messagebox.showerror("Error", "Please enter a valid amount.")
            return
        add_expense(user_id, category, float(amount))
        amount_entry.delete(0, tk.END)
        update_summary_and_chart()

    tk.Button(main_frame, text="Add Expense", command=add_new_expense).pack(pady=10)

    # אתחול התצוגה
    update_summary_and_chart()
