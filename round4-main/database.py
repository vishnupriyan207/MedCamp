# save this as reset_database.py
import sqlite3
import hashlib
import os

def reset_database():
    # Delete old database
    if os.path.exists('hospital_queries.db'):
        os.remove('hospital_queries.db')
        print("🗑️ Deleted old database")
    
    conn = sqlite3.connect('hospital_queries.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Create tables with all required columns
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            phone TEXT,
            date_of_birth TEXT,
            medical_history TEXT,
            allergies TEXT,
            current_medications TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            department TEXT,
            position TEXT,
            employee_id TEXT UNIQUE,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            patient_name TEXT NOT NULL,
            query_text TEXT NOT NULL,
            intent TEXT,
            extracted_entities TEXT,
            urgency_score INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query_id INTEGER UNIQUE,
            staff_id INTEGER,
            ai_suggestion TEXT,
            final_response TEXT,
            staff_notes TEXT,
            edited_by_staff BOOLEAN DEFAULT 0,
            sent_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (query_id) REFERENCES queries (id),
            FOREIGN KEY (staff_id) REFERENCES staff (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE knowledge_base (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            keywords TEXT,
            response_template TEXT,
            medical_conditions TEXT,
            medications TEXT,
            precautions TEXT,
            department TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert sample knowledge base
    medical_knowledge = [
        ('fever', 'fever, temperature, high temp, hot', 
         'For fever {temperature}°F: Take {medication} every {hours} hours. Drink plenty of fluids. Rest. If fever persists beyond {days} days or exceeds 103°F, seek immediate care.',
         'fever, viral infection', 'acetaminophen, ibuprofen', 'Stay hydrated, monitor temperature', 'general'),
        
        ('headache', 'headache, head pain, migraine', 
         'For {type} headache: Rest in dark room. Apply cold compress. Take {medication}. If accompanied by stiff neck, confusion, or severe pain, seek emergency care.',
         'migraine, tension headache, sinusitis', 'ibuprofen, acetaminophen, sumatriptan', 'Avoid bright lights, rest', 'neurology'),
        
        ('cough', 'cough, coughing, dry cough, wet cough', 
         'For {type} cough: {remedy}. Use honey for dry cough. For wet cough, expectorants help. If coughing blood or difficulty breathing, seek care.',
         'bronchitis, common cold, pneumonia', 'dextromethorphan, guaifenesin', 'Stay hydrated, use humidifier', 'respiratory'),
        
        ('chest_pain', 'chest pain, chest pressure, heart attack', 
         '⚠️ EMERGENCY WARNING: Chest pain could indicate heart attack. STOP reading. Call 911 immediately. Chew aspirin if available. DO NOT drive yourself.',
         'myocardial infarction, angina', 'aspirin, nitroglycerin', 'EMERGENCY - CALL 911', 'emergency'),
        
        ('diabetes', 'diabetes, blood sugar, glucose, diabetic', 
         'For blood sugar {level} mg/dL: {action}. Monitor every {hours} hours. Take {medication} as prescribed. If below 70 or above 300, seek immediate help.',
         'type 1 diabetes, type 2 diabetes', 'insulin, metformin', 'Regular monitoring, diet control', 'endocrinology')
    ]
    
    for category, keywords, template, conditions, meds, precautions, dept in medical_knowledge:
        cursor.execute('''
            INSERT INTO knowledge_base 
            (category, keywords, response_template, medical_conditions, medications, precautions, department)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (category, keywords, template, conditions, meds, precautions, dept))
    
    # Create users
    def hash_password(password):
        return hashlib.md5(password.encode()).hexdigest()
    
    password_hash = hash_password('password123')
    
    # Add patients
    patients_data = [
        ('john_doe', password_hash, 'patient', 'John Doe', 'john@email.com', '555-0101', '1980-01-01', 
         'Diabetes Type 2, Hypertension', 'None', 'Metformin 500mg, Lisinopril 10mg'),
        ('jane_smith', password_hash, 'patient', 'Jane Smith', 'jane@email.com', '555-0102', '1985-05-15',
         'Asthma, Allergies (penicillin)', 'Penicillin', 'Albuterol inhaler'),
        ('bob_wilson', password_hash, 'patient', 'Bob Wilson', 'bob@email.com', '555-0103', '1975-10-20',
         'None', 'None', 'None')
    ]
    
    for username, pwd, role, name, email, phone, dob, history, allergies, meds in patients_data:
        cursor.execute('''
            INSERT INTO users (username, password, role, name, email)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, pwd, role, name, email))
        
        user_id = cursor.lastrowid
        
        cursor.execute('''
            INSERT INTO patients (user_id, phone, date_of_birth, medical_history, allergies, current_medications)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, phone, dob, history, allergies, meds))
    
    # Add staff
    staff_data = [
        ('dr_adams', password_hash, 'staff', 'Dr. Sarah Adams', 'dr.adams@hospital.com', 'Cardiology', 'Senior Cardiologist', 'DOC001'),
        ('nurse_brown', password_hash, 'staff', 'Nurse Mike Brown', 'mike.brown@hospital.com', 'Emergency', 'Head Nurse', 'NUR001'),
    ]
    
    for username, pwd, role, name, email, dept, pos, emp_id in staff_data:
        cursor.execute('''
            INSERT INTO users (username, password, role, name, email)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, pwd, role, name, email))
        
        user_id = cursor.lastrowid
        
        cursor.execute('''
            INSERT INTO staff (user_id, department, position, employee_id)
            VALUES (?, ?, ?, ?)
        ''', (user_id, dept, pos, emp_id))
    
    # Add sample queries
    cursor.execute('SELECT id FROM patients')
    patients = cursor.fetchall()
    
    if patients:
        sample_queries = [
            (patients[0]['id'], 'John Doe', 'When will my blood test results be ready?', 'lab_report', 0, 'pending'),
            (patients[1]['id'], 'Jane Smith', 'I have severe chest pain and difficulty breathing', 'emergency', 5, 'pending'),
            (patients[2]['id'], 'Bob Wilson', 'What should I do if I miss my medication?', 'medication', 2, 'pending'),
        ]
        
        for patient_id, name, query, intent, urgency, status in sample_queries:
            cursor.execute('''
                INSERT INTO queries (patient_id, patient_name, query_text, intent, urgency_score, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (patient_id, name, query, intent, urgency, status))
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*50)
    print("✅ DATABASE RESET COMPLETE!")
    print("="*50)
    print("Tables created:")
    print("  - users")
    print("  - patients")
    print("  - staff")
    print("  - queries (with urgency_score)")
    print("  - responses")
    print("  - knowledge_base")
    print("\nLogin credentials:")
    print("  Patients: john_doe / password123")
    print("  Staff: dr_adams / password123")
    print("="*50)

if __name__ == "__main__":
    reset_database()