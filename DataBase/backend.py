import mysql.connector
from dotenv import load_dotenv
import os
import bcrypt

# טוען את משתני הסביבה
load_dotenv()

def create_tables():
    """
    יוצר את טבלאות מסד הנתונים במידת הצורך.
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = connection.cursor()

        # יצירת טבלת users
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            password VARCHAR(255),
            id_card VARCHAR(20) UNIQUE,
            monthly_salary FLOAT DEFAULT 0,
            is_profile_complete BOOLEAN DEFAULT FALSE
        );
        """)

        # יצירת טבלת expenses
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            category VARCHAR(255),
            amount FLOAT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """)

        connection.commit()
        print("Tables created successfully.")
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def register_user(name, password, id_card):
    """
    פונקציה לרישום משתמש חדש במסד הנתונים.
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )

        cursor = connection.cursor()

        # הצפנת הסיסמה
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # הוספת משתמש חדש
        sql = "INSERT INTO users (name, password, id_card) VALUES (%s, %s, %s)"
        values = (name, hashed_password.decode('utf-8'), id_card)
        cursor.execute(sql, values)
        connection.commit()

        print(f"User {name} registered successfully!")
        return True  # רישום מוצלח

    except mysql.connector.IntegrityError:
        print("ID Card already exists in the database.")  # תעודת זהות כבר קיימת
        return "ID_EXISTS"

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return False  # שגיאה כללית

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def login_user(id_card, password):
    """
    פונקציה להתחברות משתמש: מאמתת את תעודת הזהות והסיסמה מול מסד הנתונים.
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )

        cursor = connection.cursor()
        cursor.execute("SELECT id, name, password FROM users WHERE id_card = %s", (id_card,))
        result = cursor.fetchone()

        if result:
            user_id, user_name, stored_password = result
            # בדיקת סיסמה מול ההאש
            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                return {"user_id": user_id, "user_name": user_name}  # מחזיר פרטי משתמש
            else:
                return None  # סיסמה שגויה
        else:
            return None  # תעודת זהות לא נמצאה

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return None

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def is_profile_complete(user_id):
    """
    בודק אם פרופיל המשתמש הושלם.
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = connection.cursor()
        cursor.execute("SELECT is_profile_complete FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else False
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def update_profile(user_id, monthly_salary):
    """
    מעדכן את פרופיל המשתמש.
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE users 
            SET monthly_salary = %s, is_profile_complete = TRUE 
            WHERE id = %s
        """, (monthly_salary, user_id))
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def add_expense(user_id, category, amount):
    """
    פונקציה להוספת הוצאה חדשה למשתמש.
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = connection.cursor()
        sql = "INSERT INTO expenses (user_id, category, amount) VALUES (%s, %s, %s)"
        values = (user_id, category, amount)
        cursor.execute(sql, values)
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_expenses(user_id):
    """
    פונקציה לקבלת כל ההוצאות של משתמש מסוים.
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = connection.cursor()
        sql = "SELECT category, SUM(amount) FROM expenses WHERE user_id = %s GROUP BY category"
        cursor.execute(sql, (user_id,))
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_user_details(user_id):
    """
    מחזיר את פרטי המשתמש לפי מזהה משתמש.
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = connection.cursor()
        cursor.execute("SELECT name, monthly_salary FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        if result:
            return {"name": result[0], "monthly_salary": result[1]}
        return None  # אם לא נמצא משתמש
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
def update_expense(user_id, category, old_amount, new_amount):
    """
    מעדכן הוצאה קיימת במסד הנתונים.
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = connection.cursor()

        # עדכון הסכום החדש עבור ההוצאה (משתמש בקטגוריה בלבד ללא בדיקת סכום ישן)
        sql = """
        UPDATE expenses
        SET amount = %s
        WHERE user_id = %s AND category = %s
        """
        values = (new_amount, user_id, category)

        # הדפסה למעקב
        print(f"Executing SQL: {sql}")
        print(f"With values: {values}")

        cursor.execute(sql, values)
        connection.commit()

        if cursor.rowcount > 0:
            print("Expense updated successfully.")
            return True
        else:
            print("No rows updated. Check if the record exists.")
            return False

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return False

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close();        connection.close()