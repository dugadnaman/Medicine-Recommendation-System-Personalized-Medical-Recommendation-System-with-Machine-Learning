import pandas as pd
import numpy as np
from sklearn.svm import SVC
import pickle

def normalize_name(name):
    """Normalize disease names by removing extra spaces and standardizing format"""
    name = str(name).strip()
    name = ' '.join(name.split())  # Remove extra spaces
    
    # Handle special cases
    replacements = {
        'Dimorphic hemmorhoids(piles)': 'Dimorphic hemorrhoids(piles)',
        'Peptic ulcer diseae': 'Peptic ulcer disease',
        'Diabetes ': 'Diabetes',
        'Hypertension ': 'Hypertension',
        '(vertigo) Paroymsal  Positional Vertigo': '(vertigo) Paroymsal Positional Vertigo'
    }
    
    return replacements.get(name, name)

# Load and prepare the training data
print("Loading training data...")
training_data = pd.read_csv('datasets/Training.csv')

# Normalize the disease names in the target variable
training_data['prognosis'] = training_data['prognosis'].apply(normalize_name)

# Prepare features (X) and target (y)
X = training_data.drop('prognosis', axis=1)
y = training_data['prognosis']

print("\nUnique diseases in training data:", sorted(y.unique()))
print(f"Number of features: {X.shape[1]}")
print(f"Number of training samples: {X.shape[0]}")

# Train SVC with probability support
print("\nTraining SVC model with probability support...")
svc_model = SVC(probability=True, random_state=42)
svc_model.fit(X, y)

# Print model classes
print("\nModel classes:", sorted(svc_model.classes_))

# Save the model
print("Saving model...")
with open('models/svc.pkl', 'wb') as f:
    pickle.dump(svc_model, f)

print("Model training completed!")

# Test the model
test_input = np.zeros(X.shape[1])
test_input[0] = 1  # Set first symptom to test
prediction = svc_model.predict([test_input])[0]
probabilities = svc_model.predict_proba([test_input])[0]

print("\nTest prediction:", prediction)
print("Number of classes:", len(svc_model.classes_))
print("Classes:", sorted(svc_model.classes_)) 