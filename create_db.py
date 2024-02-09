import sqlite3

# データベースに接続（データベースが存在しない場合は新規作成）
conn = sqlite3.connect('shopping_list.db')

# カーソルの取得
c = conn.cursor()

# categoriesテーブルの作成（すでに存在する場合は作成しない）
c.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT UNIQUE
    )
""")

# shopping_listテーブルの作成（すでに存在する場合は作成しない）
c.execute("""
    CREATE TABLE IF NOT EXISTS shopping_list (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item TEXT,
        category TEXT,
        purchased INTEGER DEFAULT 0
    )
""")

# 変更をコミット（保存）
conn.commit()

# データベース接続のクローズ
conn.close()
