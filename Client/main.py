import tkinter as tk
from tkinter import messagebox
import sys
from os.path import abspath, dirname

# הוספת נתיב לתיקיית DataBase לנתיב החיפוש
sys.path.append(abspath(dirname(dirname(__file__))))

from DataBase.backend import login_user, register_user, is_profile_complete
from Client.main_screen import show_main_screen
from Client.settings import show_profile_screen  # מסך פרופיל


def show_register_frame():
    for widget in main_frame.winfo_children():
        widget.destroy()

    tk.Label(main_frame, text="Username").grid(row=0, column=0, pady=5)
    tk.Label(main_frame, text="Password").grid(row=1, column=0, pady=5)
    tk.Label(main_frame, text="ID Card").grid(row=2, column=0, pady=5)

    entry_name = tk.Entry(main_frame)
    entry_password = tk.Entry(main_frame, show="*")
    entry_id_card = tk.Entry(main_frame)

    entry_name.grid(row=0, column=1, pady=5)
    entry_password.grid(row=1, column=1, pady=5)
    entry_id_card.grid(row=2, column=1, pady=5)

    tk.Button(main_frame, text="Register", command=lambda: register(entry_name, entry_password, entry_id_card)).grid(
        row=3, columnspan=2, pady=10)
    tk.Button(main_frame, text="Back to Main Menu", command=show_main_menu).grid(row=4, columnspan=2, pady=5)


def show_login_frame():
    for widget in main_frame.winfo_children():
        widget.destroy()

    tk.Label(main_frame, text="ID Card").grid(row=0, column=0, pady=5)
    tk.Label(main_frame, text="Password").grid(row=1, column=0, pady=5)

    entry_id_card = tk.Entry(main_frame)
    entry_password = tk.Entry(main_frame, show="*")

    entry_id_card.grid(row=0, column=1, pady=5)
    entry_password.grid(row=1, column=1, pady=5)

    tk.Button(main_frame, text="Login", command=lambda: login(entry_id_card, entry_password)).grid(row=2, columnspan=2,
                                                                                                   pady=10)
    tk.Button(main_frame, text="Back to Main Menu", command=show_main_menu).grid(row=3, columnspan=2, pady=5)


def show_main_menu():
    for widget in main_frame.winfo_children():
        widget.destroy()

    tk.Button(main_frame, text="Register", command=show_register_frame, bg='lightgreen').pack(pady=10)
    tk.Button(main_frame, text="Login", command=show_login_frame, bg='lightblue').pack(pady=10)


def register(entry_name, entry_password, entry_id_card):
    name = entry_name.get()
    password = entry_password.get()
    id_card = entry_id_card.get()

    result = register_user(name, password, id_card)
    if result == True:
        messagebox.showinfo("Success", "Registration successful!")
        show_main_menu()
    elif result == "ID_EXISTS":
        messagebox.showerror("Error", "ID Card already exists. Please try again.")
    else:
        messagebox.showerror("Error", "Error during registration.")

def login(entry_id_card, entry_password):
    id_card = entry_id_card.get()
    password = entry_password.get()

    user_data = login_user(id_card, password)

    if user_data:
        user_id = user_data["user_id"]
        user_name = user_data["user_name"]

        if not is_profile_complete(user_id):
            # אם הפרופיל לא הושלם, להעביר למסך ההגדרות
            messagebox.showinfo("Welcome", f"Hi {user_name}, please complete your profile.")
            show_profile_screen(main_frame, user_id)  # מעבר למסך פרופיל
        else:
            # אם הפרופיל הושלם, מעבר ישיר למסך הראשי
            show_main_screen(main_frame, user_id)
    else:
        messagebox.showerror("Error", "Incorrect ID or Password.")


# יצירת חלון ראשי
window = tk.Tk()
window.title("User System")
window.geometry("400x300")

main_frame = tk.Frame(window)
main_frame.pack(fill="both", expand=True)

show_main_menu()

window.mainloop()
