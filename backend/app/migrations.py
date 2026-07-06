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

# Формат: "таблиця": [("колонка", "SQL-тип", "DEFAULT-вираз або None"), ...]
COLUMNS_TO_ENSURE = {
    "patterns": [
        ("description", "TEXT", None),
        ("is_new", "BOOLEAN", "0"),
        ("sort_order", "INTEGER", "0"),
    ],
    "posts": [
        ("youtube_url", "TEXT", None),
        ("is_published", "BOOLEAN", "0"),
    ],
}


def run_auto_migrations():
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    with engine.begin() as conn:
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
                conn.execute(
                    text(f"ALTER TABLE {table} ADD COLUMN {column_name} {column_type}{default_clause}")
                )
                print(f"[migrations] додано колонку {table}.{column_name}")
