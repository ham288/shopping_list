import streamlit as st
import streamlit_authenticator as stauth
import sqlite3

import yaml
from yaml.loader import SafeLoader

with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

authenticator.login()

if st.session_state["authentication_status"]:
    st.header('買い物リスト')

    # データベースに接続
    conn = sqlite3.connect('shopping_list.db')
    c = conn.cursor()

    # デフォルトカテゴリの存在確認と作成
    c.execute("SELECT category FROM categories WHERE category = 'デフォルト'")
    default_category = c.fetchone()
    if default_category is None:
        c.execute("INSERT INTO categories (category) VALUES ('デフォルト')")
        conn.commit()

    # サイドバーに新しいカテゴリの追加
    with st.sidebar.form(key='category_form', clear_on_submit=True):
        new_category = st.text_input("新しいカテゴリを入力してください")
        submit_category = st.form_submit_button('カテゴリを追加')
        if submit_category and new_category:
            try:
                c.execute("INSERT INTO categories (category) VALUES (?)", (new_category,))
                conn.commit()
            except sqlite3.IntegrityError:  # すでに存在するカテゴリを追加しようとした場合
                st.warning("このカテゴリはすでに存在します")

    # サイドバーに選択中のカテゴリの削除
    with st.sidebar.form(key='delete_category_form', clear_on_submit=True):
        c.execute("SELECT category FROM categories")
        category_list = [row[0] for row in c.fetchall()]  # データベースからカテゴリの一覧を取得
        delete_category = st.selectbox("消去するカテゴリを選択してください", category_list, key='delete_category')  # リストからカテゴリを選択
        submit_delete = st.form_submit_button('選択中のカテゴリを消去')
        if submit_delete and delete_category:
            # 関連するアイテムを削除
            c.execute("DELETE FROM shopping_list WHERE category=?", (delete_category,))
            # カテゴリを削除
            c.execute("DELETE FROM categories WHERE category=?", (delete_category,))
            conn.commit()
            st.rerun()

    # 新しい商品の追加
    with st.expander('＋', expanded=True):
        with st.form(key='item_form', clear_on_submit=True):
            new_item = st.text_input("欲しいもの", key='new_item')
            c.execute("SELECT category FROM categories")
            category_list = [row[0] for row in c.fetchall()]  # データベースからカテゴリの一覧を取得
            if len(category_list) == 0:  # カテゴリが存在しない場合はデフォルトカテゴリを選択
                category = 'デフォルト'
            else:
                category = st.selectbox("カテゴリ", category_list, index=len(category_list)-1)  # 最新のカテゴリをデフォルトで選択
            submit_item = st.form_submit_button('商品を追加', use_container_width=True)
            if submit_item and new_item and category:
                c.execute("INSERT INTO shopping_list (item, category, purchased) VALUES (?, ?, 0)", (new_item, category))
                conn.commit()

    # 買い物リストの表示と更新
    c.execute("SELECT DISTINCT category FROM shopping_list")
    categories = c.fetchall()
    for category in categories:
        if category[0] != 'デフォルト':  # デフォルトカテゴリの場合はカテゴリ名を表示しない
            st.subheader(category[0])
        c.execute("SELECT id, item, purchased FROM shopping_list WHERE category=?", (category[0],))
        items = c.fetchall()
        for id, item, purchased in items:
            key = f"purchased-{id}"  # ユニークなキーを生成
            purchased = st.checkbox(item, value=bool(purchased), key=key)  # キーを指定
            c.execute("UPDATE shopping_list SET purchased = ? WHERE id = ?", (int(purchased), id))
            conn.commit()

    # チェック済みのアイテムを全消去
    if st.button('✓Clear'):
        c.execute("DELETE FROM shopping_list WHERE purchased=1")
        conn.commit()
        st.rerun()

    # データベース接続のクローズ
    conn.close()

elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')