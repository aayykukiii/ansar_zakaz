import sqlite3


def get_categories():
    with sqlite3.connect("bron.db") as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM categories")
        return cur.fetchall()

def add_category(name: str):
    with sqlite3.connect("bron.db") as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        conn.commit()

def get_products_by_category(category_id: int, subcategory: str = None):
    with sqlite3.connect("bron.db") as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        if subcategory:
            cur.execute(
                "SELECT * FROM products WHERE category_id = ? AND subcategory = ?",
                (category_id, subcategory)
            )
        else:
            cur.execute("SELECT * FROM products WHERE category_id = ?", (category_id,))
        rows = cur.fetchall()
        return [dict(row) for row in rows]

def get_product(product_id: int):
    with sqlite3.connect("bron.db") as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        row = cur.fetchone()
        if row:
            return dict(row)
        return None

def create_order(user_id: int, name: str, phone: str, product_id: int, comment: str):
    with sqlite3.connect("bron.db") as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO orders (user_id, name, phone, product_id, comment)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, name, phone, product_id, comment))
        conn.commit()
