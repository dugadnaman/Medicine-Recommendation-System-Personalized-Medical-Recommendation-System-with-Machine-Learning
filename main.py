from flask import Flask, request, render_template, jsonify
import numpy as np
import pandas as pd
import pickle
import traceback
import sys
import os
from sklearn.preprocessing import StandardScaler, LabelEncoder
import warnings
warnings.filterwarnings('ignore')


# flask app
app = Flask(__name__)

# Check if model file exists
model_path = "models/svc.pkl"
if not os.path.exists(model_path):
    print(f"ERROR: Model file not found at {model_path}")
    print("Current working directory:", os.getcwd())
    sys.exit(1)
else:
    print(f"Found model file at {model_path}")

# Define symptoms list
symptoms_list = ['itching', 'skin_rash', 'nodal_skin_eruptions', 'continuous_sneezing', 
                'shivering', 'chills', 'joint_pain', 'stomach_pain', 'acidity', 'ulcers_on_tongue',
                'muscle_wasting', 'vomiting', 'burning_micturition', 'spotting_urination', 'fatigue',
                'weight_gain', 'anxiety', 'cold_hands_and_feets', 'mood_swings', 'weight_loss',
                'restlessness', 'lethargy', 'patches_in_throat', 'irregular_sugar_level', 'cough',
                'high_fever', 'sunken_eyes', 'breathlessness', 'sweating', 'dehydration',
                'indigestion', 'headache', 'yellowish_skin', 'dark_urine', 'nausea',
                'loss_of_appetite', 'pain_behind_the_eyes', 'back_pain', 'constipation',
                'abdominal_pain', 'diarrhoea', 'mild_fever', 'yellow_urine',
                'yellowing_of_eyes', 'acute_liver_failure', 'fluid_overload',
                'swelling_of_stomach', 'swelled_lymph_nodes', 'malaise',
                'blurred_and_distorted_vision', 'phlegm', 'throat_irritation',
                'redness_of_eyes', 'sinus_pressure', 'runny_nose', 'congestion',
                'chest_pain', 'weakness_in_limbs', 'fast_heart_rate',
                'pain_during_bowel_movements', 'pain_in_anal_region', 'bloody_stool',
                'irritation_in_anus', 'neck_pain', 'dizziness', 'cramps',
                'bruising', 'obesity', 'swollen_legs', 'swollen_blood_vessels',
                'puffy_face_and_eyes', 'enlarged_thyroid', 'brittle_nails',
                'swollen_extremeties', 'excessive_hunger', 'extra_marital_contacts',
                'drying_and_tingling_lips', 'slurred_speech', 'knee_pain', 'hip_joint_pain',
                'muscle_weakness', 'stiff_neck', 'swelling_joints', 'movement_stiffness',
                'spinning_movements', 'loss_of_balance', 'unsteadiness', 'weakness_of_one_body_side',
                'loss_of_smell', 'bladder_discomfort', 'foul_smell_of urine',
                'continuous_feel_of_urine', 'passage_of_gases', 'internal_itching',
                'toxic_look_(typhos)', 'depression', 'irritability', 'muscle_pain',
                'altered_sensorium', 'red_spots_over_body', 'belly_pain',
                'abnormal_menstruation', 'dischromic_patches', 'watering_from_eyes',
                'increased_appetite', 'polyuria', 'family_history', 'mucoid_sputum',
                'rusty_sputum', 'lack_of_concentration', 'visual_disturbances',
                'receiving_blood_transfusion', 'receiving_unsterile_injections',
                'coma', 'stomach_bleeding', 'distention_of_abdomen',
                'history_of_alcohol_consumption', 'fluid_overload', 'blood_in_sputum',
                'prominent_veins_on_calf', 'palpitations', 'painful_walking',
                'pus_filled_pimples', 'blackheads', 'scurring', 'skin_peeling',
                'silver_like_dusting', 'small_dents_in_nails', 'inflammatory_nails',
                'blister', 'red_sore_around_nose', 'yellow_crust_ooze']

def normalize_name(name):
    """Normalize disease names by removing extra spaces and standardizing format"""
    name = str(name).strip()
    name = ' '.join(name.split())  # Remove extra spaces
    name = name.rstrip(' ')  # Remove trailing spaces
    
    # Handle special cases
    replacements = {
        'Dimorphic hemmorhoids(piles)': 'Dimorphic hemorrhoids(piles)',
        'Peptic ulcer diseae': 'Peptic ulcer disease',
        'Diabetes ': 'Diabetes',
        'Hypertension ': 'Hypertension',
        '(vertigo) Paroymsal  Positional Vertigo': '(vertigo) Paroymsal Positional Vertigo'
    }
    
    return replacements.get(name, name)

def load_datasets():
    """Load and normalize all datasets"""
    global description, medications, diets, precautions, disease_mapping
    
    print("Loading and normalizing datasets...")
    
    # Load datasets
    description = pd.read_csv("datasets/description.csv")
    medications = pd.read_csv("datasets/medications.csv")
    diets = pd.read_csv("datasets/diets.csv")
    precautions = pd.read_csv("datasets/precautions_df.csv")
    
    # Normalize disease names in all dataframes
    description['Disease'] = description['Disease'].apply(normalize_name)
    medications['Disease'] = medications['Disease'].apply(normalize_name)
    diets['Disease'] = diets['Disease'].apply(normalize_name)
    precautions['Disease'] = precautions['Disease'].apply(normalize_name)
    
    # Create a set of all unique diseases across datasets
    all_diseases = set(description['Disease'].unique()) | \
                  set(medications['Disease'].unique()) | \
                  set(diets['Disease'].unique()) | \
                  set(precautions['Disease'].unique())
    
    print("\nUnique diseases after normalization:", sorted(all_diseases))
    
    # Update disease_mapping to match normalized names
    disease_mapping = [normalize_name(disease) for disease in [
        'Fungal infection', 'Allergy', 'GERD', 'Chronic cholestasis', 'Drug Reaction',
        'Peptic ulcer disease', 'AIDS', 'Diabetes', 'Gastroenteritis', 'Bronchial Asthma',
        'Hypertension', 'Migraine', 'Cervical spondylosis', 'Paralysis (brain hemorrhage)', 'Jaundice',
        'Malaria', 'Chicken pox', 'Dengue', 'Typhoid', 'hepatitis A',
        'Hepatitis B', 'Hepatitis C', 'Hepatitis D', 'Hepatitis E', 'Alcoholic hepatitis',
        'Tuberculosis', 'Common Cold', 'Pneumonia', 'Dimorphic hemorrhoids(piles)', 'Heart attack',
        'Varicose veins', 'Hypothyroidism', 'Hyperthyroidism', 'Hypoglycemia', 'Osteoarthristis',
        'Arthritis', '(vertigo) Paroymsal Positional Vertigo', 'Acne', 'Urinary tract infection', 'Psoriasis',
        'Impetigo'
    ]]
    
    print("\nDisease mapping normalized and updated")
    return disease_mapping

# Load datasets and model
try:
    # Load your datasets
    print("Loading datasets...")
    sym_des = pd.read_csv("datasets/symtoms_df.csv")
    precautions = pd.read_csv("datasets/precautions_df.csv")
    workout = pd.read_csv("datasets/workout_df.csv")
    description = pd.read_csv("datasets/description.csv")
    medications = pd.read_csv('datasets/medications.csv')
    diets = pd.read_csv("datasets/diets.csv")
    print("All datasets loaded successfully")

    # Print unique diseases in each dataset for verification
    print("\nDiseases in description.csv:", sorted(description['Disease'].unique()))
    print("\nDiseases in medications.csv:", sorted(medications['Disease'].unique()))
    print("\nDiseases in diets.csv:", sorted(diets['Disease'].unique()))
    print("\nDiseases in precautions.csv:", sorted(precautions['Disease'].unique()))

    # Load model
    print("\nLoading model...")
    with open('models/svc.pkl', 'rb') as f:
        svc = pickle.load(f)
    print("Model loaded successfully")
    print("Model type:", type(svc))
    print("Model parameters:", svc.get_params())

    # Test prediction with sample data
    test_input = np.zeros(len(symptoms_list))
    test_input[symptoms_list.index('skin_rash')] = 1
    test_pred = svc.predict([test_input])[0]
    test_prob = svc.predict_proba([test_input])[0]
    print("\nTest prediction:", test_pred)
    print("Test probabilities:", test_prob)

except Exception as e:
    print(f"Error during initialization: {str(e)}")
    traceback.print_exc()
    sys.exit(1)



#============================================================
# custome and helping functions
#==========================helper funtions================
def helper(dis):
    desc = description[description['Disease'] == dis]['Description']
    desc = " ".join([w for w in desc])

    pre = precautions[precautions['Disease'] == dis][['Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4']]
    pre = [col for col in pre.values]

    med = medications[medications['Disease'] == dis]['Medication']
    med = [med for med in med.values]

    die = diets[diets['Disease'] == dis]['Diet']
    die = [die for die in die.values]

    wrkout = workout[workout['disease'] == dis] ['workout']


    return desc,pre,med,die,wrkout

# Model Prediction function
def get_predicted_value(patient_symptoms):
    input_vector = np.zeros(len(symptoms_list))
    for item in patient_symptoms:
        input_vector[symptoms_list.index(item)] = 1
    return disease_mapping[svc.predict([input_vector])[0]]




# creating routes========================================


@app.route("/")
def index():
    print("Symptoms list:", symptoms_list)  # Debug print
    return render_template("index.html", symptoms_list=symptoms_list)

# Define a route for the home page
@app.route('/predict', methods=['POST'])
def predict():
    try:
        selected_symptoms = request.form.getlist('symptoms[]')
        print(f"\nReceived symptoms: {selected_symptoms}")

        if not selected_symptoms:
            return jsonify({'error': 'No symptoms selected'}), 400

        # Create input array
        input_data = np.zeros(len(symptoms_list))
        for symptom in selected_symptoms:
            if symptom in symptoms_list:
                index = symptoms_list.index(symptom)
                input_data[index] = 1

        # Make prediction
        predicted_disease = svc.predict([input_data])[0]
        print(f"Predicted disease: {predicted_disease}")

        # Get disease information
        disease_info = {
            'disease': predicted_disease,
            'description': 'No description available',
            'precautions': [],
            'medications': [],
            'diet': []
        }

        # Get description
        desc_row = description[description['Disease'] == predicted_disease]
        if not desc_row.empty:
            disease_info['description'] = desc_row['Description'].iloc[0]
            print("Found description")

        # Get precautions
        prec_row = precautions[precautions['Disease'] == predicted_disease]
        if not prec_row.empty:
            precs = prec_row[['Precaution_1', 'Precaution_2', 
                    'Precaution_3', 'Precaution_4']].values.tolist()[0]
            disease_info['precautions'] = [p for p in precs if pd.notna(p) and str(p).strip()]
            print("Found precautions")

        # Get medications
        med_row = medications[medications['Disease'] == predicted_disease]
        if not med_row.empty:
            med_str = med_row['Medication'].iloc[0]
            try:
                disease_info['medications'] = eval(med_str) if isinstance(med_str, str) else [med_str]
            except:
                disease_info['medications'] = [med_str]
            print("Found medications")

        # Get diet
        diet_row = diets[diets['Disease'] == predicted_disease]
        if not diet_row.empty:
            diet_str = diet_row['Diet'].iloc[0]
            try:
                disease_info['diet'] = eval(diet_str) if isinstance(diet_str, str) else [diet_str]
            except:
                disease_info['diet'] = [diet_str]
            print("Found diet")

        print("Final disease_info:", disease_info)
        return jsonify(disease_info)

    except Exception as e:
        print("Error in prediction:", str(e))
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500



# about view funtion and path
@app.route('/about')
def about():
    return render_template("about.html")
# contact view funtion and path
@app.route('/contact')
def contact():
    return render_template("contact.html")

# developer view funtion and path
@app.route('/developer')
def developer():
    return render_template("developer.html")

# about view funtion and path
@app.route('/blog')
def blog():
    return render_template("blog.html")


if __name__ == '__main__':
    disease_mapping = load_datasets()  # Load and normalize datasets before starting the server
    app.run(debug=True)