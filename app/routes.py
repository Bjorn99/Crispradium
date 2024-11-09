from flask import render_template, request
from app import app
from app.sequence_handler import SequenceHandler

@app.route('/', methods=['GET', 'POST'])
def index():
    guide_rnas = []
    if request.method == 'POST':
        sequence = request.form['sequence']
        sequence_handler = SequenceHandler()
        
        #clean the input sequence
        cleaned_sequence = sequence_handler.clean_sequence(sequence)

        # Debugging line to print the cleaned sequence
        print(f"Cleaned Sequence: {cleaned_sequence}")  # This will output the cleaned sequence to the console

        # Validate cleaned sequence
        if not sequence_handler.validate_sequence(cleaned_sequence):
            return render_template('index.html', error="Invalid DNA sequence.")


        # Find PAM sites
        pam_sites = sequence_handler.find_pam_sites(cleaned_sequence)
        
        # Score guide RNAs
        #guide_rnas = []
        for pam_site in pam_sites:
            score = sequence_handler.score_guide_rna(pam_site['guide_sequence'], cleaned_sequence)
            pam_site['score'] = score
            pam_site['off_target_sites'] = sequence_handler.find_off_target_sites(pam_site['guide_sequence'], cleaned_sequence)
            pam_site['off_target_score'] = sequence_handler.calculate_off_target_score(pam_site['guide_sequence'], cleaned_sequence)
            guide_rnas.append(pam_site)
        
        return render_template('index.html', guide_rnas=guide_rnas)
    
    return render_template('index.html')