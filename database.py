import aiomysql
from datetime import datetime
from config import DB_BASE_CONFIG, ADMIN_MAP

async def get_extended_stats(db_name):
    config = DB_BASE_CONFIG.copy()
    config['db'] = db_name
    conn = await aiomysql.connect(**config)
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT COUNT(*) as cnt FROM lvl_base WHERE lastconnect >= UNIX_TIMESTAMP(CURDATE())")
            today_cnt = (await cursor.fetchone())['cnt']
            
            await cursor.execute("SELECT COUNT(*) as cnt FROM lvl_base WHERE lastconnect >= UNIX_TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 6 DAY))")
            week_cnt = (await cursor.fetchone())['cnt']

            steam_ids = list(ADMIN_MAP.keys())
            online_admins = []
            if steam_ids:
                placeholders = ', '.join(['%s'] * len(steam_ids))
                query = f"SELECT name, steam FROM lvl_base WHERE online > 0 AND steam IN ({placeholders})"
                await cursor.execute(query, steam_ids)
                online_admins = await cursor.fetchall()
            
            return today_cnt, week_cnt, online_admins
    finally:
        conn.close()

async def add_warning(admin_tg_id, reason):
    conn = await aiomysql.connect(**DB_BASE_CONFIG, db='computer67')
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO admin_warnings (admin_tg_id, reason, timestamp) VALUES (%s, %s, %s)",
                (admin_tg_id, reason, datetime.now())
            )
            await conn.commit()
    finally:
        conn.close()

async def init_db():
    conn = await aiomysql.connect(**DB_BASE_CONFIG, db='computer67')
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin_warnings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    admin_tg_id BIGINT NOT NULL,
                    reason TEXT NOT NULL,
                    timestamp DATETIME NOT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            await conn.commit()
    finally:
        conn.close()

async def get_warnings_count(admin_tg_id):
    conn = await aiomysql.connect(**DB_BASE_CONFIG, db='computer67')
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT COUNT(*) FROM admin_warnings WHERE admin_tg_id = %s", (admin_tg_id,))
            res = await cursor.fetchone()
            return res[0] if res else 0
    finally:
        conn.close()