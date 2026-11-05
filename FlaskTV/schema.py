from sqlalchemy import inspect, text


def ensure_page_logo_column(engine):
    """Upgrade existing databases; newly created tables use the model default."""
    with engine.begin() as connection:
        inspector = inspect(connection)
        if inspector.has_table('page'):
            columns = {column['name'] for column in inspector.get_columns('page')}
            if 'splash_enabled' not in columns:
                connection.execute(text(
                    'ALTER TABLE page ADD COLUMN splash_enabled BOOLEAN NOT NULL DEFAULT TRUE'
                ))
