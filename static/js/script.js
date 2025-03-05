document.addEventListener('DOMContentLoaded', function() {
    // Initialize variables
    const symptomInput = document.querySelector('#symptom-input');
    const selectedSymptomsContainer = document.querySelector('.selected-symptoms');
    let selectedSymptoms = new Set();

    // Available symptoms list (make sure this matches your Python symptoms_list)
    const availableSymptoms = [
        'itching', 'skin_rash', 'nodal_skin_eruptions', 'continuous_sneezing', 'shivering',
        'chills', 'joint_pain', 'stomach_pain', 'acidity', 'ulcers_on_tongue', 'muscle_wasting',
        'vomiting', 'burning_micturition', 'spotting_urination', 'fatigue', 'weight_gain',
        'anxiety', 'cold_hands_and_feets', 'mood_swings', 'weight_loss', 'restlessness',
        'lethargy', 'patches_in_throat', 'irregular_sugar_level', 'cough', 'high_fever',
        'sunken_eyes', 'breathlessness', 'sweating', 'dehydration', 'indigestion', 'headache',
        'yellowish_skin', 'dark_urine', 'nausea', 'loss_of_appetite', 'pain_behind_the_eyes',
        'back_pain', 'constipation', 'abdominal_pain', 'diarrhoea', 'mild_fever', 'yellow_urine',
        'yellowing_of_eyes', 'acute_liver_failure', 'fluid_overload', 'swelling_of_stomach',
        'swelled_lymph_nodes', 'malaise', 'blurred_and_distorted_vision', 'phlegm',
        'throat_irritation', 'redness_of_eyes', 'sinus_pressure', 'runny_nose', 'congestion',
        'chest_pain', 'weakness_in_limbs', 'fast_heart_rate', 'pain_during_bowel_movements',
        'pain_in_anal_region', 'bloody_stool', 'irritation_in_anus', 'neck_pain', 'dizziness',
        'cramps', 'bruising', 'obesity', 'swollen_legs', 'swollen_blood_vessels',
        'puffy_face_and_eyes', 'enlarged_thyroid', 'brittle_nails', 'swollen_extremeties',
        'excessive_hunger', 'extra_marital_contacts', 'drying_and_tingling_lips', 'slurred_speech',
        'knee_pain', 'hip_joint_pain', 'muscle_weakness', 'stiff_neck', 'swelling_joints',
        'movement_stiffness', 'spinning_movements', 'loss_of_balance', 'unsteadiness',
        'weakness_of_one_body_side', 'loss_of_smell', 'bladder_discomfort', 'foul_smell_of_urine',
        'continuous_feel_of_urine', 'passage_of_gases', 'internal_itching', 'toxic_look_(typhos)',
        'depression', 'irritability', 'muscle_pain', 'altered_sensorium', 'red_spots_over_body',
        'belly_pain', 'abnormal_menstruation', 'dischromic_patches', 'watering_from_eyes',
        'increased_appetite', 'polyuria', 'family_history', 'mucoid_sputum', 'rusty_sputum',
        'lack_of_concentration', 'visual_disturbances', 'receiving_blood_transfusion',
        'receiving_unsterile_injections', 'coma', 'stomach_bleeding', 'distention_of_abdomen',
        'history_of_alcohol_consumption', 'fluid_overload', 'blood_in_sputum',
        'prominent_veins_on_calf', 'palpitations', 'painful_walking', 'pus_filled_pimples',
        'blackheads', 'scurring', 'skin_peeling', 'silver_like_dusting', 'small_dents_in_nails',
        'inflammatory_nails', 'blister', 'red_sore_around_nose', 'yellow_crust_ooze'
    ];

    // Function to format symptom display text
    function formatSymptomText(symptom) {
        return symptom.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    // Function to add a symptom
    function addSymptom(symptom) {
        if (!selectedSymptoms.has(symptom)) {
            selectedSymptoms.add(symptom);
            const span = document.createElement('span');
            span.className = 'selected-symptom';
            span.innerHTML = `
                ${formatSymptomText(symptom)}
                <span class="remove-symptom">×</span>
            `;
            
            span.querySelector('.remove-symptom').onclick = function() {
                selectedSymptoms.delete(symptom);
                span.remove();
                updatePredictButton();
            };
            
            selectedSymptomsContainer.appendChild(span);
            updatePredictButton();
        }
    }

    // Function to update predict button state
    function updatePredictButton() {
        const predictBtn = document.querySelector('.predict-btn');
        predictBtn.disabled = selectedSymptoms.size === 0;
        predictBtn.style.opacity = selectedSymptoms.size === 0 ? '0.6' : '1';
    }

    // Initialize autocomplete
    if (symptomInput) {
        let currentFocus;
        
        symptomInput.addEventListener('input', function(e) {
            let val = this.value;
            closeAllLists();
            if (!val) return false;
            currentFocus = -1;

            const matchList = document.createElement('div');
            matchList.setAttribute('id', 'autocomplete-list');
            matchList.setAttribute('class', 'autocomplete-items');
            this.parentNode.appendChild(matchList);

            for (let symptom of availableSymptoms) {
                if (symptom.toLowerCase().includes(val.toLowerCase())) {
                    const item = document.createElement('div');
                    item.innerHTML = formatSymptomText(symptom);
                    item.addEventListener('click', function() {
                        addSymptom(symptom);
                        symptomInput.value = '';
                        closeAllLists();
                    });
                    matchList.appendChild(item);
                }
            }
        });

        function closeAllLists(elmnt) {
            const x = document.getElementsByClassName('autocomplete-items');
            for (let i = 0; i < x.length; i++) {
                if (elmnt != x[i] && elmnt != symptomInput) {
                    x[i].parentNode.removeChild(x[i]);
                }
            }
        }

        document.addEventListener('click', function(e) {
            closeAllLists(e.target);
        });
    }

    // Predict disease function
    window.predictDisease = function() {
        if (selectedSymptoms.size === 0) {
            alert('Please select at least one symptom');
            return false;
        }

        // Show loading
        document.getElementById('loading').style.display = 'block';
        document.getElementById('result').style.display = 'none';

        // Create form data
        const formData = new FormData();
        selectedSymptoms.forEach(symptom => {
            formData.append('symptoms[]', symptom);
        });

        // Make prediction request
        fetch('/predict', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Hide loading
            document.getElementById('loading').style.display = 'none';
            document.getElementById('result').style.display = 'block';

            if (data.error) {
                document.getElementById('result').innerHTML = `
                    <div class="error-message">
                        <i class="fas fa-exclamation-circle"></i>
                        <p>${data.error}</p>
                    </div>`;
                return;
            }

            // Display results
            let resultHTML = `
                <h2><i class="fas fa-clipboard-check"></i> Prediction Results</h2>
                <div class="result-item">
                    <h3><i class="fas fa-disease"></i> Predicted Condition</h3>
                    <p class="prediction">${data.disease}</p>
                </div>
                <div class="result-item">
                    <h3><i class="fas fa-info-circle"></i> Description</h3>
                    <p>${data.description}</p>
                </div>`;

            if (data.precautions && data.precautions.length > 0) {
                resultHTML += `
                    <div class="result-item">
                        <h3><i class="fas fa-shield-alt"></i> Precautions</h3>
                        <ul>
                            ${data.precautions.map(p => `<li>${p}</li>`).join('')}
                        </ul>
                    </div>`;
            }

            if (data.medications && data.medications.length > 0) {
                resultHTML += `
                    <div class="result-item">
                        <h3><i class="fas fa-pills"></i> Medications</h3>
                        <ul>
                            ${data.medications.map(m => `<li>${m}</li>`).join('')}
                        </ul>
                    </div>`;
            }

            if (data.diet && data.diet.length > 0) {
                resultHTML += `
                    <div class="result-item">
                        <h3><i class="fas fa-utensils"></i> Recommended Diet</h3>
                        <ul>
                            ${data.diet.map(d => `<li>${d}</li>`).join('')}
                        </ul>
                    </div>`;
            }

            document.getElementById('result').innerHTML = resultHTML;

            // Smooth scroll to results
            document.getElementById('result').scrollIntoView({ behavior: 'smooth' });
        })
        .catch(error => {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('result').style.display = 'block';
            document.getElementById('result').innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>Error: ${error.message}</p>
                </div>`;
        });

        return false;
    };

    // Initialize predict button state
    updatePredictButton();
}); 