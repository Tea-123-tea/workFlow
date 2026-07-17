import sqlite3

conn = sqlite3.connect("ecom_shop.db")
cursor = conn.cursor()

# 商品表
cursor.execute('''
CREATE TABLE IF NOT EXISTS product (
    product_id TEXT PRIMARY KEY,
    name TEXT,
    stock INTEGER
)
''')

# 订单表
cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    product_id TEXT,
    amount REAL,
    user_msg TEXT
)
''')

# 插入测试数据
cursor.execute("INSERT OR IGNORE INTO product VALUES ('P001', '纯棉短袖T恤', 42)")
cursor.execute("INSERT OR IGNORE INTO product VALUES ('P002', '冰丝牛仔裤', 12)")
cursor.execute("INSERT OR IGNORE INTO orders VALUES ('OD2026001', 'P001', 269, '衣服有破损')")
cursor.execute("INSERT OR IGNORE INTO orders VALUES ('OD2026002', 'P002', 99, '尺码偏小')")

conn.commit()
conn.close()
print("✅ 数据库初始化完成！")