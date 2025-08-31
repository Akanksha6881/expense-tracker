
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

APP_DB = "expenses.db"

def init_db():
    conn = sqlite3.connect(APP_DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item TEXT NOT NULL,
                    amount REAL NOT NULL,
                    created_at TEXT NOT NULL
                )''')
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(APP_DB)
    return conn

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# initialize DB on start
init_db()

@app.route('/')
def index():
    # show summary + latest 5
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, item, amount, created_at FROM expenses ORDER BY created_at DESC LIMIT 5")
    recent = cur.fetchall()
    # total
    cur.execute("SELECT SUM(amount) FROM expenses")
    total = cur.fetchone()[0] or 0.0
    conn.close()
    return render_template('index.html', recent=recent, total=total)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/add', methods=['GET','POST'])
def add_expense():
    if request.method == 'POST':
        item = request.form.get('item')
        amount = request.form.get('amount')
        if item and amount:
            try:
                amt = float(amount)
            except:
                amt = 0.0
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO expenses (item, amount, created_at) VALUES (?,?,?)",
                        (item, amt, created_at))
            conn.commit()
            conn.close()
        return redirect(url_for('view_expenses'))
    return render_template('add_expense.html')

@app.route('/view')
def view_expenses():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, item, amount, created_at FROM expenses ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return render_template('view_expenses.html', expenses=rows)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_expense(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('view_expenses'))


if __name__ == '__main__':
    app.run(debug=True)
