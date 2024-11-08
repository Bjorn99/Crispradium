from flask import render_template, request
from app import app
from app.sequence_handler import SequenceHandler

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        sequence = request.form['sequence']
        sequence_handler = SequenceHandler()
        
        # Find PAM sites
        pam_sites = sequence_handler.find_pam_sites(sequence)
        
        # Score guide RNAs
        guide_rnas = []
        for pam_site in pam_sites:
            score = sequence_handler.score_guide_rna(pam_site['guide_sequence'], sequence)
            pam_site['score'] = score
            pam_site['off_target_sites'] = sequence_handler.find_off_target_sites(pam_site['guide_sequence'], sequence)
            pam_site['off_target_score'] = sequence_handler.calculate_off_target_score(pam_site['guide_sequence'], sequence)
            guide_rnas.append(pam_site)
        
        return render_template('index.html', guide_rnas=guide_rnas)
    
    return render_template('index.html')