from typing import List, Dict, Union, Optional
from Bio import SeqIO
from Bio.Seq import Seq
from io import StringIO

class SequenceHandler:
    def __init__(self):
        self.valid_bases = set(['A', 'T', 'G', 'C', 'N'])
        self.complementary_bases = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G', 'N': 'N'}
        self.max_off_target_score = 4
        self.min_sequence_length = 20
        self.max_sequence_length = 200000  # 200kb

    def process_input(self, sequence_input: str) -> Dict[str, Union[bool, str, List[Dict]]]:
        """
        Process input sequence, handling both FASTA and plain sequence formats.
        Returns validation results and processed sequences.
        """
        sequence_input = sequence_input.strip()
        
        # Check if input is in FASTA format
        if sequence_input.startswith('>'):
            return self.process_fasta(sequence_input)
        else:
            return self.process_plain_sequence(sequence_input)

    def process_fasta(self, fasta_input: str) -> Dict[str, Union[bool, str, List[Dict]]]:
        """
        Process FASTA format input.
        Returns dictionary with validation status and processed sequences.
        """
        try:
            fasta_handle = StringIO(fasta_input)
            sequences = []
            
            # Parsing FASTA using BioPython
            for record in SeqIO.parse(fasta_handle, "fasta"):
                sequence = str(record.seq).upper()
                
                # Validate sequence
                validation_result = self.validate_sequence(sequence)
                if not validation_result['valid']:
                    return {
                        'valid': False,
                        'error': f"Invalid sequence in FASTA entry '{record.id}': {validation_result['error']}"
                    }
                
                sequences.append({
                    'id': record.id,
                    'description': record.description,
                    'sequence': sequence,
                    'length': len(sequence),
                    'gc_content': self.calculate_gc_content(sequence)
                })
            
            if not sequences:
                return {
                    'valid': False,
                    'error': 'No valid sequences found in FASTA input'
                }
            
            return {
                'valid': True,
                'format': 'fasta',
                'sequences': sequences
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Error parsing FASTA format: {str(e)}'
            }

    def process_plain_sequence(self, sequence: str) -> Dict[str, Union[bool, str, Dict]]:
        """
        Process plain sequence input.
        Returns dictionary with validation status and processed sequence.
        """
        sequence = self.clean_sequence(sequence)
        validation_result = self.validate_sequence(sequence)
        
        if not validation_result['valid']:
            return validation_result
        
        return {
            'valid': True,
            'format': 'plain',
            'sequences': [{
                'id': 'input_sequence',
                'description': 'User input sequence',
                'sequence': sequence,
                'length': len(sequence),
                'gc_content': self.calculate_gc_content(sequence)
            }]
        }

    def validate_sequence(self, sequence: str) -> Dict[str, Union[bool, str]]:
        if not sequence:
            return {'valid': False, 'error': 'Empty sequence'}
            
        if len(sequence) < self.min_sequence_length:
            return {
                'valid': False, 
                'error': f'Sequence too short (minimum {self.min_sequence_length} bases)'
            }
            
        if len(sequence) > self.max_sequence_length:
            return {
                'valid': False, 
                'error': f'Sequence too long (maximum {self.max_sequence_length} bases)'
            }
            
        invalid_chars = set(sequence.upper()) - self.valid_bases
        if invalid_chars:
            return {
                'valid': False,
                'error': f'Invalid characters found: {", ".join(sorted(invalid_chars))}'
            }
            
        return {'valid': True}

    def clean_sequence(self, sequence: str) -> str:
        """Remove whitespace and convert to uppercase."""
        return ''.join(sequence.strip().split()).upper()
        
    def get_reverse_complement(self, sequence: str) -> str:
        """Return reverse complement of DNA sequence."""
        return ''.join(self.complementary_bases[base] 
                      for base in sequence.upper()[::-1])
    
    def calculate_gc_content(self, sequence: str) -> float:
        """Calculate GC content percentage."""
        sequence = sequence.upper()
        gc_count = sequence.count('G') + sequence.count('C')
        return (gc_count / len(sequence)) * 100 if sequence else 0
    
    def find_off_target_sites(self, guide_sequence: str, sequence: str) -> List[str]:
        """Find potential off-target sites."""
        off_target_sites = []
        
        # Search forward strand
        for i in range(len(sequence) - len(guide_sequence) + 1):
            site = sequence[i:i+len(guide_sequence)]
            if self.count_mismatches(guide_sequence, site) <= 3:
                off_target_sites.append(site)
        
        # Search reverse strand
        reverse_sequence = self.get_reverse_complement(sequence)
        for i in range(len(reverse_sequence) - len(guide_sequence) + 1):
            site = reverse_sequence[i:i+len(guide_sequence)]
            if self.count_mismatches(guide_sequence, site) <= 3 and site != guide_sequence:
                off_target_sites.append(site)
        
        return off_target_sites
    
    def count_mismatches(self, sequence1: str, sequence2: str) -> int:
        """Count mismatches between two sequences."""
        return sum(1 for base1, base2 in zip(sequence1, sequence2) if base1 != base2)
    
    def score_guide_rna(self, guide_sequence: str, sequence: str) -> float:
        """Score guide RNA based on various criteria."""
        gc_content = self.calculate_gc_content(guide_sequence)
        gc_score = 1 - abs(gc_content - 50) / 50
        
        self_complementarity = self.check_self_complementarity(guide_sequence)
        secondary_structure_score = 1 - self_complementarity
        
        off_target_score = self.calculate_off_target_score(guide_sequence, sequence)
        
        return gc_score * secondary_structure_score * (1 - off_target_score / self.max_off_target_score)
    
    def check_self_complementarity(self, sequence: str) -> float:
        """Check sequence self-complementarity."""
        reverse_complement = self.get_reverse_complement(sequence)
        matches = sum(1 for i in range(len(sequence)) if sequence[i] == reverse_complement[i])
        return matches / len(sequence)
    
    def calculate_off_target_score(self, guide_sequence: str, sequence: str) -> float:
        """Calculate off-target score."""
        off_target_sites = self.find_off_target_sites(guide_sequence, sequence)
        return sum(1 - (20 - self.count_mismatches(guide_sequence, site)) / 20 
                  for site in off_target_sites)