CREATE TABLE IF NOT EXISTS employes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    grade TEXT NOT NULL,
    nombre_factures INTEGER NOT NULL,
    salaire REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS grades (
    grade TEXT PRIMARY KEY,
    quota INTEGER NOT NULL,
    bonus REAL NOT NULL,
    salaire REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

-- Ajoutez un utilisateur par défaut
INSERT INTO users (username, password) VALUES ('admin', '123Soleil.');
