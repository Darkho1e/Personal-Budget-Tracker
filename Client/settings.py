from DataBase.backend import update_profile, get_user_details
import tkinter as tk
from tkinter import messagebox


def show_profile_screen(main_frame, user_id):
    """
    מסך להשלמת פרופיל המשתמש.
    """
    for widget in main_frame.winfo_children():
        widget.destroy()

    # שליפת פרטי המשתמש
    user_details = get_user_details(user_id)
    user_name = user_details["name"] if user_details else "User"
    monthly_salary = user_details["monthly_salary"] if user_details else 0

    # כותרת עם שם המשתמש
    tk.Label(main_frame, text=f"Hello, {user_name}!", font=("Arial", 16)).pack(pady=10)
    tk.Label(main_frame, text=f"Current Monthly Salary: {monthly_salary:.2f}", font=("Arial", 12)).pack(pady=5)

    # שדה לעדכון משכורת
    tk.Label(main_frame, text="Update Monthly Salary:").pack(pady=5)
    salary_entry = tk.Entry(main_frame)
    salary_entry.pack(pady=5)

    def save_profile():
        salary = salary_entry.get()
        if not salary.replace(".", "").isdigit():
            messagebox.showerror("Error", "Please enter a valid salary.")
            return
        # עדכון פרופיל המשתמש
        update_profile(user_id, float(salary))
        messagebox.showinfo("Success", "Profile updated successfully!")

        # ייבוא דינמי של show_main_screen כדי למנוע מעגליות
        from Client.main_screen import show_main_screen
        show_main_screen(main_frame, user_id)  # מעבר למסך הראשי

    tk.Button(main_frame, text="Save", command=save_profile).pack(pady=10)
