CREATE TABLE IF NOT EXISTS firs (
  fir_id INTEGER PRIMARY KEY,
  date TEXT,
  crime_type TEXT,
  description TEXT,
  location TEXT,
  district TEXT,
  status TEXT
);

CREATE TABLE IF NOT EXISTS persons (
  person_id INTEGER PRIMARY KEY,
  name TEXT,
  role TEXT,
  age INTEGER,
  gender TEXT,
  address TEXT,
  district TEXT
);

CREATE TABLE IF NOT EXISTS involvement (
  involvement_id INTEGER PRIMARY KEY AUTOINCREMENT,
  fir_id INTEGER,
  person_id INTEGER,
  role TEXT,
  FOREIGN KEY(fir_id) REFERENCES firs(fir_id),
  FOREIGN KEY(person_id) REFERENCES persons(person_id)
);
