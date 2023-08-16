-- SQLite
CREATE TABLE katas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    group_name TEXT NOT NULL,
    code_kata_url TEXT NOT NULL,
    kyu TEXT NOT NULL
);
