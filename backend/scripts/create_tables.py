#!/usr/bin/env python3
"""
Utility script to ensure all SQLAlchemy tables are created in the current SQLite DB.
Intended for development use only. It imports all models and calls db.create_all().
Additionally, it patches legacy tables (e.g., vehicles) by adding missing columns
when the existing database schema is older than the current model definitions.
"""

import os
import sys
from typing import List, Tuple

# Ensure project root (backend) is on sys.path so `import app` works when run from anywhere
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import create_app
from app.extensions import db
from sqlalchemy import inspect, text


def patch_vehicles_table() -> List[str]:
    """
    Patch the existing 'vehicles' table by adding any missing columns required by the current model.
    This is primarily for SQLite development environments where historical DBs may be missing fields.

    Returns:
        List[str]: Names of columns that were added.
    """
    added: List[str] = []
    engine = db.engine

    # Only attempt PRAGMA on SQLite
    if engine.dialect.name != 'sqlite':
        print(f"Skip patch on non-sqlite engine: {engine}")
        return added

    with engine.connect() as conn:
        # 打印当前 vehicles 表列信息
        try:
            rows = list(conn.execute(text("PRAGMA table_info('vehicles')")))
            print("vehicles existing columns:", [r[1] for r in rows])
        except Exception as e:
            print("inspect vehicles failed:", e)

        # PRAGMA table_info returns: cid, name, type, notnull, dflt_value, pk
        rows = list(conn.execute(text("PRAGMA table_info('vehicles')")))
        existing_cols = {row[1] for row in rows}

        # Desired columns from the Vehicle model with SQLite-compatible types and optional defaults
        desired: List[Tuple[str, str, str]] = [
            ("task_id", "TEXT", None),
            ("manifest_number", "TEXT", None),
            ("dispatch_number", "TEXT", None),
            ("license_plate", "TEXT", None),
            ("carriage_number", "TEXT", None),
            ("created_at", "TEXT", None),
            ("notes", "TEXT", None),
            ("actual_volume", "REAL", None),
            ("volume_photo_url", "TEXT", None),
            ("volume_modified_by", "INTEGER", None),
            ("required_volume", "REAL", None),
            ("confirmed_volume", "REAL", None),
            ("vehicle_type", "TEXT", None),
            ("supplier_id", "INTEGER", None),
            ("supplier_type", "TEXT", None),
            ("driver_name", "TEXT", None),
            ("driver_phone", "TEXT", None),
            ("driver_id_card", "TEXT", None),
            ("status", "TEXT", "'待确认'"),
            ("confirmed_by", "INTEGER", None),
            ("confirmed_at", "TEXT", None),
            ("is_merged", "INTEGER", "0"),
            ("is_downgraded", "INTEGER", "0"),
            ("original_capacity", "REAL", None),
            ("updated_at", "TEXT", None),
        ]

        for name, col_type, default in desired:
            if name not in existing_cols:
                if default is None:
                    sql = f"ALTER TABLE vehicles ADD COLUMN {name} {col_type}"
                else:
                    sql = f"ALTER TABLE vehicles ADD COLUMN {name} {col_type} DEFAULT {default}"
                conn.execute(text(sql))
                print("added column:", name)
                added.append(name)

    return added


def main() -> None:
    app = create_app()
    with app.app_context():
        engine = db.engine
        print("DB URL:", str(engine.url))
        inspector = inspect(engine)
        before = set(inspector.get_table_names())
        print("Existing tables before:", sorted(before))

        # Create any missing tables first
        db.create_all()

        # Patch legacy tables to add missing columns
        added_cols = patch_vehicles_table()
        if added_cols:
            print("Patched vehicles table, added columns:", sorted(added_cols))

        inspector = inspect(engine)
        after = set(inspector.get_table_names())
        print("Existing tables after:", sorted(after))
        created = after - before
        if created:
            print("Newly created:", sorted(created))
        else:
            print("No new tables created.")


if __name__ == "__main__":
    main()