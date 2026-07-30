"""
Легка система авто-міграцій без Alembic — той самий підхід, що
використовувався в StoryLore. При старті застосунку перевіряємо, чи існують
усі очікувані колонки в таблицях, і додаємо ті, яких бракує.

Це не замінює повноцінні міграції для великих проєктів, але для
одного розробника й невеликої БД дозволяє спокійно додавати нові поля
(наприклад, майбутні поля для блогу) без ручних ALTER TABLE.
"""
from sqlalchemy import inspect, text

from .database import engine

# BLOB (SQLite) vs BYTEA (Postgres) — тип бінарної колонки залежить від БД.
_BINARY_TYPE = "BYTEA" if engine.dialect.name == "postgresql" else "BLOB"

# Формат: "таблиця": [("колонка", "SQL-тип", "DEFAULT-вираз або None"), ...]
COLUMNS_TO_ENSURE = {
    "patterns": [
        ("description", "TEXT", None),
        ("is_new", "BOOLEAN", "0"),
        ("sort_order", "INTEGER", "0"),
        ("image_data", _BINARY_TYPE, None),
        ("image_content_type", "TEXT", None),
    ],
    "posts": [
        ("youtube_url", "TEXT", None),
        ("is_published", "BOOLEAN", "0"),
    ],
    "subscribers": [
        ("unsubscribed", "BOOLEAN", "0"),
    ],
}


def run_auto_migrations():
    """⚠️ Ця функція НІКОЛИ не повинна кидати виняток назовні — вона тепер
    викликається на рівні імпорту модуля (main.py), тож будь-яка неперехоплена
    помилка тут зупинила б запуск усього застосунку. Особливо важливо це на
    хостингу, де одночасно стартує кілька копій процесу (типово для
    Passenger/cPanel): якщо дві копії одночасно виконують ALTER TABLE для
    тієї самої колонки, одна з них отримає помилку "колонка вже існує" —
    це нормально й очікувано, просто пропускаємо конкретну колонку."""
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        for table, columns in COLUMNS_TO_ENSURE.items():
            if table not in existing_tables:
                # Таблиці ще немає — Base.metadata.create_all() створить її
                # з нуля з усіма колонками, міграція тут не потрібна.
                continue

            existing_columns = {c["name"] for c in inspector.get_columns(table)}
            for column_name, column_type, default in columns:
                if column_name in existing_columns:
                    continue
                default_clause = f" DEFAULT {default}" if default is not None else ""
                try:
                    with engine.begin() as conn:
                        conn.execute(
                            text(f"ALTER TABLE {table} ADD COLUMN {column_name} {column_type}{default_clause}")
                        )
                    print(f"[migrations] додано колонку {table}.{column_name}")
                except Exception as e:
                    # Найімовірніша причина — інша копія процесу вже додала цю
                    # колонку буквально щойно (перегонка при паралельному
                    # старті кількох воркерів). Це не помилка, яку варто
                    # зупиняти застосунок — просто логуємо й ідемо далі.
                    print(f"[migrations] пропущено {table}.{column_name}: {e}")
    except Exception as e:
        # Навіть якщо щось пішло геть не так (наприклад, немає з'єднання з
        # БД на секунду старту) — не валимо запуск застосунку через це.
        print(f"[migrations] загальна помилка авто-міграції (застосунок все одно запускається): {e}")
