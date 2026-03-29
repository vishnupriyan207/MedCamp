import sqlite3
import re
from datetime import datetime

class RAG_AI_Engine:
    """
    Retrieval-Augmented Generation (RAG) AI Engine
    Retrieves relevant medical knowledge and generates personalized responses
    """
    
    def __init__(self):
        self.conn = sqlite3.connect('hospital_queries.db')
        self.conn.row_factory = sqlite3.Row
    
    def extract_medical_entities(self, query_text):
        """Extract medical terms, symptoms, medications from query"""
        query_lower = query_text.lower()
        
        entities = {
            'symptoms': [],
            'conditions': [],
            'medications': [],
            'body_parts': [],
            'measurements': [],
            'urgency': 0
        }
        
        # Symptom keywords
        symptoms = {
            'fever': ['fever', 'temperature', 'hot', 'chills'],
            'pain': ['pain', 'ache', 'hurt', 'sore'],
            'cough': ['cough', 'coughing'],
            'headache': ['headache', 'migraine'],
            'nausea': ['nausea', 'vomit', 'sick'],
            'fatigue': ['tired', 'fatigue', 'exhausted'],
            'dizziness': ['dizzy', 'dizziness', 'lightheaded'],
            'rash': ['rash', 'hives', 'skin irritation'],
            'swelling': ['swelling', 'swollen', 'inflamed'],
            'bleeding': ['bleeding', 'blood', 'hemorrhage']
        }
        
        for symptom, keywords in symptoms.items():
            if any(k in query_lower for k in keywords):
                entities['symptoms'].append(symptom)
        
        # Check for urgency
        urgency_keywords = ['emergency', 'severe', 'unbearable', 'cannot breathe', 
                           'chest pain', 'unconscious', 'stroke', 'heart attack']
        for word in urgency_keywords:
            if word in query_lower:
                entities['urgency'] = 5
                break
        
        # Extract numbers (like temperature, dosage)
        numbers = re.findall(r'\d+', query_text)
        if numbers:
            entities['measurements'] = numbers
        
        return entities
    
    def retrieve_knowledge(self, query_text, entities):
        """Retrieve relevant medical knowledge from database"""
        cursor = self.conn.cursor()
        query_lower = query_text.lower()
        
        # Split query into keywords
        keywords = query_lower.split()
        
        # Search knowledge base
        cursor.execute('''
            SELECT * FROM knowledge_base
        ''')
        
        all_knowledge = cursor.fetchall()
        relevant_responses = []
        
        for knowledge in all_knowledge:
            score = 0
            kb_keywords = knowledge['keywords'].split(', ')
            
            # Check if any symptom matches
            for symptom in entities['symptoms']:
                if symptom in kb_keywords:
                    score += 3
            
            # Check keyword matches
            for keyword in keywords:
                if len(keyword) > 3:  # Ignore small words
                    if keyword in knowledge['keywords'].lower():
                        score += 1
                    if keyword in knowledge['medical_conditions'].lower():
                        score += 2
            
            if score > 0:
                relevant_responses.append({
                    'knowledge': knowledge,
                    'score': score
                })
        
        # Sort by relevance score
        relevant_responses.sort(key=lambda x: x['score'], reverse=True)
        
        return [r['knowledge'] for r in relevant_responses[:3]]  # Top 3 most relevant
    
    def get_patient_context(self, patient_id):
        """Get complete patient context"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT p.*, u.name, u.email 
            FROM patients p
            JOIN users u ON p.user_id = u.id
            WHERE p.id = ?
        ''', (patient_id,))
        
        return cursor.fetchone()
    
    def personalize_response(self, template, patient_info, entities, query_text):
        """Fill template with patient-specific information"""
        
        # Default values
        replacements = {
            '{medication}': 'acetaminophen',
            '{hours}': '4-6',
            '{days}': '3',
            '{type}': 'your',
            '{severity}': 'mild',
            '{remedy}': 'rest and hydration',
            '{temperature}': entities['measurements'][0] if entities['measurements'] else '100.5',
            '{condition}': 'your condition',
            '{doctor}': 'your doctor',
            '{timeframe}': '2 weeks',
            '{slots}': 'Monday 9am, Wednesday 2pm, Friday 11am',
            '{systolic}': '130',
            '{diastolic}': '85',
            '{action}': 'monitor closely',
            '{inhaler}': 'your rescue inhaler',
            '{minutes}': '10',
            '{medication1}': 'medication',
            '{medication2}': 'medication',
            '{interaction}': 'may interact',
            '{recommendation}': 'Consult your doctor',
            '{test_name}': 'blood test',
            '{value}': '150',
            '{unit}': 'mg/dL',
            '{normal_range}': '70-100 mg/dL',
            '{interpretation}': 'it is elevated',
            '{symptom}': 'symptoms',
            '{temp}': '101',
            '{technique}': 'use calming techniques',
            '{vaccine}': 'the',
            '{information}': 'is recommended',
            '{date}': 'next month',
            '{diet}': 'a balanced',
            '{good_foods}': 'fruits, vegetables',
            '{bad_foods}': 'processed foods',
            '{exercise_type}': 'light walking',
            '{duration}': '30',
            '{frequency}': '5 times per week',
            '{warning_signs}': 'pain or shortness of breath',
            '{joint}': 'joint',
            '{size}': 'small',
            '{degree}': 'first-degree',
            '{eye_condition}': 'eye irritation',
            '{surgery_type}': 'your',
            '{time}': '2-4 weeks',
            '{warning_signs}': 'fever, increased pain, redness',
            '{followup_date}': '2 weeks',
            '{medication_name}': 'medication'
        }
        
        # Personalize based on patient info
        if patient_info:
            if patient_info['medical_history']:
                if 'diabetes' in patient_info['medical_history'].lower():
                    replacements['{medication}'] = 'metformin'
                if 'hypertension' in patient_info['medical_history'].lower():
                    replacements['{medication}'] = 'lisinopril'
                if 'asthma' in patient_info['medical_history'].lower():
                    replacements['{inhaler}'] = 'albuterol inhaler'
            
            if patient_info['allergies'] and patient_info['allergies'] != 'None':
                replacements['{medication}'] = f"AVOID ALLERGENS. Patient allergic to {patient_info['allergies']}. Use alternative."
        
        # Personalize based on query
        query_lower = query_text.lower()
        if 'baby' in query_lower or 'infant' in query_lower:
            replacements['{medication}'] = 'infant acetaminophen'
        if 'severe' in query_lower or 'terrible' in query_lower:
            replacements['{severity}'] = 'severe'
            replacements['{action}'] = 'seek immediate medical attention'
        
        # Fill template
        response = template
        for key, value in replacements.items():
            response = response.replace(key, str(value))
        
        return response
    
    def generate_ai_suggestion(self, query_id, patient_id, query_text):
        """Main RAG function to generate AI response"""
        
        print(f"\n{'='*60}")
        print(f"RAG AI ENGINE PROCESSING QUERY")
        print(f"{'='*60}")
        print(f"Query: {query_text[:100]}...")
        
        # Step 1: Extract medical entities
        entities = self.extract_medical_entities(query_text)
        print(f"Step 1 - Entities extracted: {entities['symptoms']}")
        print(f"Urgency level: {entities['urgency']}")
        
        # Step 2: Retrieve relevant knowledge
        relevant_knowledge = self.retrieve_knowledge(query_text, entities)
        print(f"Step 2 - Found {len(relevant_knowledge)} relevant knowledge items")
        
        # Step 3: Get patient context
        patient_info = self.get_patient_context(patient_id)
        if patient_info:
            print(f"Step 3 - Patient context retrieved: {patient_info['name']}")
            print(f"  Medical history: {patient_info['medical_history']}")
            print(f"  Allergies: {patient_info['allergies']}")
        
        # Step 4: Generate response
        if relevant_knowledge:
            # Use most relevant knowledge
            best_knowledge = relevant_knowledge[0]
            template = best_knowledge['response_template']
            print(f"Step 4 - Using template from: {best_knowledge['category']}")
            
            # Personalize
            suggestion = self.personalize_response(template, patient_info, entities, query_text)
            
            # Add disclaimer for emergency
            if entities['urgency'] >= 5:
                suggestion = "⚠️ URGENT: " + suggestion + "\n\nThis appears urgent. Please prioritize this response."
        else:
            # Fallback response
            suggestion = f"Thank you for your query about {', '.join(entities['symptoms']) if entities['symptoms'] else 'your health'}. A staff member will respond shortly with personalized information based on your medical history."
        
        # Add greeting
        if patient_info:
            greeting = f"Dear {patient_info['name']},\n\n"
            full_suggestion = greeting + suggestion
        else:
            full_suggestion = "Dear Patient,\n\n" + suggestion
        
        # Add confidence note
        full_suggestion += f"\n\n---\n🤖 AI-generated draft based on your medical history and hospital guidelines. Staff will review."
        
        print(f"\nGenerated suggestion: {full_suggestion[:200]}...")
        
        # Save to database
        cursor = self.conn.cursor()
        
        # Update query with intent and entities
        intent = best_knowledge['category'] if relevant_knowledge else 'general'
        cursor.execute('''
            UPDATE queries 
            SET intent = ?, urgency_score = ?
            WHERE id = ?
        ''', (intent, entities['urgency'], query_id))
        
        # Save AI suggestion
        existing = cursor.execute('SELECT id FROM responses WHERE query_id = ?', (query_id,)).fetchone()
        
        if existing:
            cursor.execute('''
                UPDATE responses 
                SET ai_suggestion = ?
                WHERE query_id = ?
            ''', (full_suggestion, query_id))
        else:
            cursor.execute('''
                INSERT INTO responses (query_id, ai_suggestion)
                VALUES (?, ?)
            ''', (query_id, full_suggestion))
        
        self.conn.commit()
        print(f"Step 5 - AI suggestion saved to database")
        print(f"{'='*60}\n")
        
        return {
            'suggestion': full_suggestion,
            'intent': intent,
            'urgency': entities['urgency'],
            'entities': entities,
            'knowledge_used': len(relevant_knowledge)
        }
    
    def close(self):
        self.conn.close()