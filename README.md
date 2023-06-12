# README

Simple UI to track matches of table football across Amazon buildings.

Testing
```bash
 streamlit run --server.runOnSave True app.py
```

## Updating the database

The database is stored in SQLite format to `./database.db`.

The database structure is managed via the [Alembic library](https://alembic.sqlalchemy.org/en/latest/), which organizes updates into migrations (pieces of code run once, in order, to update an existing database).

To create a migration, you need to use the following command line from a Terminal:

```bash
python -m alembic revision -m "add created_by fields"
```

This will create a file into `database/versions`, which you may edit to contain raw SQL or Alembic-commands to work on the database.

Update of the database can be done via Alembic itself or the Admin page of the UI.