import sqlite3
import os
import csv

DB_PATH = os.path.join(os.path.dirname(__file__), "crime_data.sqlite")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

firs_data = [
    (101, "2026-01-10", "Theft", "Car stolen from parking lot near MG Road. Victim reports vehicle missing at 8 PM.", "MG Road, Bengaluru", "Bengaluru Urban", "Open"),
    (102, "2026-01-12", "Burglary", "House break-in reported near Mysore Palace. Cash and jewelry stolen.", "Mysore Palace Road, Mysuru", "Mysuru", "Closed"),
    (103, "2026-01-15", "Assault", "Man attacked on MG Road near Commercial Street. Suspect fled on foot.", "MG Road, Bengaluru", "Bengaluru Urban", "Open"),
    (104, "2026-01-20", "Theft", "Pickpocketing incident at Banashankari Bus Stand. Mobile phone stolen.", "Banashankari, Bengaluru", "Bengaluru Urban", "Closed"),
    (105, "2026-02-05", "Vehicle Theft", "Two-wheeler stolen from outside Mall of Mysuru.", "Mall of Mysuru, Mysuru", "Mysuru", "Open"),
    (106, "2026-02-10", "Fraud", "Online fraud case. Victim duped of Rs 50,000 via phishing call.", "Jayanagar, Bengaluru", "Bengaluru Urban", "Open"),
    (107, "2026-02-18", "Burglary", "Shop break-in at KR Market. Electronics worth Rs 2 lakh stolen.", "KR Market, Bengaluru", "Bengaluru Urban", "Open"),
    (108, "2026-03-01", "Assault", "Road rage incident on NH-75 near Tumkur. Both parties injured.", "NH-75, Tumkur", "Tumkur", "Closed"),
    (109, "2026-03-05", "Theft", "Bicycle theft reported at Vidhana Soudha parking area.", "Vidhana Soudha, Bengaluru", "Bengaluru Urban", "Open"),
    (110, "2026-03-10", "Robbery", "Bus robbery at Majestic Bus Stand. Cash and phones taken from passengers.", "Majestic, Bengaluru", "Bengaluru Urban", "Open"),
    (111, "2026-03-12", "Vehicle Theft", "Car stolen from BTM Layout residential area overnight.", "BTM Layout, Bengaluru", "Bengaluru Urban", "Open"),
    (112, "2026-03-15", "Fraud", "Bank fraud case in Mangaluru. Unauthorized withdrawal of Rs 1 lakh.", "Mangaluru", "Dakshina Kannada", "Open"),
    (113, "2026-03-18", "Burglary", "Flat burglary in Indiranagar. Laptop and watches stolen.", "Indiranagar, Bengaluru", "Bengaluru Urban", "Closed"),
    (114, "2026-03-20", "Assault", "Chain snatching incident in Hubli. Victim injured during snatching.", "Hubli", "Dharwad", "Open"),
    (115, "2026-04-01", "Theft", "Luggage theft at Yeshwanthpur Railway Station.", "Yeshwanthpur, Bengaluru", "Bengaluru Urban", "Open"),
]

persons_data = [
    (1, "Ravi Kumar", "Victim", 45, "Male", "MG Road, Bengaluru", "Bengaluru Urban"),
    (2, "Aisha Khan", "Accused", 30, "Female", "Mysuru City", "Mysuru"),
    (3, "Manjunath Gowda", "Victim", 50, "Male", "Banashankari, Bengaluru", "Bengaluru Urban"),
    (4, "Suresh Reddy", "Accused", 25, "Male", "Koramangala, Bengaluru", "Bengaluru Urban"),
    (5, "Lakshmi Devi", "Victim", 35, "Female", "Jayanagar, Bengaluru", "Bengaluru Urban"),
    (6, "Venkatesh Rao", "Accused", 42, "Male", "Malleshwaram, Bengaluru", "Bengaluru Urban"),
    (7, "Priya Sharma", "Victim", 28, "Female", "Indiranagar, Bengaluru", "Bengaluru Urban"),
    (8, "Ahmed Hussain", "Accused", 38, "Male", "Majestic, Bengaluru", "Bengaluru Urban"),
    (9, "Kiran P", "Witness", 33, "Male", "BTM Layout, Bengaluru", "Bengaluru Urban"),
    (10, "Sunita Patil", "Victim", 55, "Female", "Hubli", "Dharwad"),
    (11, "Ramesh Shetty", "Accused", 29, "Male", "Mangaluru", "Dakshina Kannada"),
    (12, "Anitha K", "Victim", 40, "Female", "Tumkur", "Tumkur"),
    (13, "Deepak Jain", "Victim", 32, "Male", "KR Market, Bengaluru", "Bengaluru Urban"),
    (14, "Mohan Das", "Witness", 60, "Male", "Mysuru City", "Mysuru"),
    (15, "Kavitha N", "Victim", 27, "Female", "Vidhana Soudha, Bengaluru", "Bengaluru Urban"),
    (16, "Siddharth M", "Accused", 35, "Male", "Yeshwanthpur, Bengaluru", "Bengaluru Urban"),
    (17, "Geetha R", "Victim", 48, "Female", "BTM Layout, Bengaluru", "Bengaluru Urban"),
    (18, "Prakash B", "Accused", 22, "Male", "Mysuru City", "Mysuru"),
    (19, "Naveen Kumar", "Victim", 31, "Male", "Hubli", "Dharwad"),
    (20, "Shweta M", "Witness", 26, "Female", "Indiranagar, Bengaluru", "Bengaluru Urban"),
]

involvement_data = [
    (101, 1, "Victim"),
    (101, 2, "Accused"),
    (102, 14, "Victim"),
    (102, 18, "Accused"),
    (103, 3, "Victim"),
    (103, 4, "Accused"),
    (104, 3, "Victim"),
    (104, 4, "Accused"),
    (105, 2, "Victim"),
    (105, 18, "Accused"),
    (106, 5, "Victim"),
    (106, 6, "Accused"),
    (107, 13, "Victim"),
    (107, 6, "Accused"),
    (108, 12, "Victim"),
    (109, 15, "Victim"),
    (109, 16, "Accused"),
    (110, 8, "Accused"),
    (110, 7, "Victim"),
    (111, 17, "Victim"),
    (111, 16, "Accused"),
    (112, 5, "Victim"),
    (112, 11, "Accused"),
    (113, 7, "Victim"),
    (114, 10, "Victim"),
    (114, 19, "Victim"),
    (115, 15, "Victim"),
    (115, 16, "Accused"),
]

def generate_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open(SCHEMA_PATH, 'r') as f:
        cursor.executescript(f.read())

    cursor.executemany("INSERT OR REPLACE INTO firs VALUES (?,?,?,?,?,?,?)", firs_data)
    cursor.executemany("INSERT OR REPLACE INTO persons VALUES (?,?,?,?,?,?,?)", persons_data)
    cursor.executemany("INSERT OR REPLACE INTO involvement VALUES (?,?,?,?)",
                       [(i+1, *r) for i, r in enumerate(involvement_data)])

    conn.commit()
    conn.close()
    print(f"Database created at {DB_PATH}")

def generate_csvs():
    base = os.path.dirname(__file__)
    for name, data, headers in [
        ("firs.csv", firs_data, ["fir_id", "date", "crime_type", "description", "location", "district", "status"]),
        ("persons.csv", persons_data, ["person_id", "name", "role", "age", "gender", "address", "district"]),
        ("involvement.csv", involvement_data, ["fir_id", "person_id", "role"]),
    ]:
        path = os.path.join(base, name)
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(data)
        print(f"Created {path}")

if __name__ == "__main__":
    generate_database()
    generate_csvs()
