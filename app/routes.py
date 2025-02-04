from flask import render_template, request, jsonify
from app import app, sequence_handler, guide_rna_analyzer

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze DNA sequence endpoint."""
    try:
        data = request.get_json()
        sequence_input = data.get('sequence', '').strip()
        system = data.get('system', 'SpCas9')
        
        # Process input (handles both FASTA and plain sequence)
        sequence_result = sequence_handler.process_input(sequence_input)
        
        if not sequence_result['valid']:
            return jsonify({
                'error': sequence_result['error']
            }), 400
            
        # For FASTA input, use the first sequence by default
        # Frontend can request specific sequences later
        sequence = sequence_result['sequences'][0]['sequence']
        
        # Analyzing sequence
        results = guide_rna_analyzer.analyze_sequence(sequence, system)
        
        # Adding sequence metadata to results
        results['sequence_info'] = sequence_result['sequences'][0]
        
        return jsonify({
            'success': True,
            'data': results,
            'all_sequences': sequence_result['sequences'] if len(sequence_result['sequences']) > 1 else None
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

@app.route('/analyze_sequence', methods=['POST'])
def analyze_specific_sequence():
    """Analyze a specific sequence from FASTA input."""
    try:
        data = request.get_json()
        sequence = data.get('sequence', '').strip()
        system = data.get('system', 'SpCas9')
        
        if not sequence:
            return jsonify({
                'error': 'No sequence provided'
            }), 400
            
        results = guide_rna_analyzer.analyze_sequence(sequence, system)
        
        return jsonify({
            'success': True,
            'data': results
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500