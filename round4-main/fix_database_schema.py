import sqlite3

def fix_database():
    print("Fixing database schema...")
    conn = sqlite3.connect('hospital_queries.db')
    cursor = conn.cursor()
    
    # Check current schema
    cursor.execute("PRAGMA table_info(queries)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    print(f"Current columns: {column_names}")
    
    # Add missing columns
    if 'urgency_score' not in column_names:
        cursor.execute('ALTER TABLE queries ADD COLUMN urgency_score INTEGER DEFAULT 0')
        print("✅ Added urgency_score column")
    
    if 'extracted_entities' not in column_names:
        cursor.execute('ALTER TABLE queries ADD COLUMN extracted_entities TEXT')
        print("✅ Added extracted_entities column")
    
    # Check knowledge_base table
    cursor.execute("SELECT COUNT(*) FROM knowledge_base")
    count = cursor.fetchone()[0]
    print(f"Knowledge base has {count} entries")
    
    if count == 0:
        print("Adding knowledge base entries...")
        medical_knowledge = [
            ('chest_pain', 'chest pain, chest pressure, heart attack', 
             '⚠️ EMERGENCY: Chest pain could indicate a heart attack. Please call 911 immediately. Do not drive yourself. Chew an aspirin if available and not allergic.',
             'myocardial infarction, angina', 'aspirin, nitroglycerin', 'EMERGENCY - CALL 911', 'emergency'),
            
            ('fever', 'fever, temperature, high temp, hot', 
             'For fever of {temperature}°F: Rest and hydrate. Take acetaminophen or ibuprofen as directed. If fever exceeds 103°F or persists beyond 3 days, seek medical attention.',
             'fever, viral infection', 'acetaminophen, ibuprofen', 'Stay hydrated, monitor temperature', 'general'),
            
            ('headache', 'headache, head pain, migraine', 
             'For headache: Rest in a dark room. Apply cold compress. Take over-the-counter pain relievers. If severe or with stiff neck, seek care.',
             'migraine, tension headache', 'ibuprofen, acetaminophen', 'Rest, avoid bright lights', 'neurology'),
            
            ('cough', 'cough, coughing', 
             'For cough: Stay hydrated and rest. Honey can help with dry cough. If cough persists beyond 2 weeks or with blood, seek care.',
             'bronchitis, cold', 'dextromethorphan', 'Rest, use humidifier', 'respiratory'),
            
            ('diabetes', 'diabetes, blood sugar', 
             'For blood sugar concerns: Monitor regularly. Take medication as prescribed. If below 70 or above 300, seek immediate help.',
             'diabetes', 'insulin, metformin', 'Regular monitoring', 'endocrinology')
        ]
        
        for cat, keywords, template, conditions, meds, precautions, dept in medical_knowledge:
            cursor.execute('''
                INSERT INTO knowledge_base 
                (category, keywords, response_template, medical_conditions, medications, precautions, department)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (cat, keywords, template, conditions, meds, precautions, dept))
        
        print(f"✅ Added {len(medical_knowledge)} knowledge base entries")
    
    conn.commit()
    conn.close()
    print("Database fix complete!")

if __name__ == "__main__":
    fix_database()