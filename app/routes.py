from flask import render_template, request, jsonify
from app import app, sequence_handler, guide_rna_analyzer

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze DNA sequence endpoint."""
    data = request.get_json()
    sequence = data.get('sequence', '').upper()
    system = data.get('system', 'SpCas9')
    
    if not sequence_handler.validate_sequence(sequence):
        return jsonify({
            'error': 'Invalid DNA sequence. Please use only A, T, G, C, or N.'
        }), 400
    
    cleaned_sequence = sequence_handler.clean_sequence(sequence)
    
    try:
        results = guide_rna_analyzer.analyze_sequence(cleaned_sequence, system)
        return jsonify({
            'success': True,
            'data': results
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/systems', methods=['GET'])
def get_systems():
    """Get available CRISPR systems."""
    return jsonify({
        'systems': guide_rna_analyzer.crispr_systems
    })