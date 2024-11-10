from typing import List, Dict
import re
from Bio.Seq import Seq

class SequenceHandler:
    def __init__(self):
        self.valid_bases = set(['A', 'T', 'G', 'C', 'N'])
        self.complementary_bases = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G', 'N': 'N'}
        self.max_off_target_score = 4

    def clean_sequence(self, sequence: str) -> str:
        """Remove whitespace and convert to uppercase."""
        return ''.join(sequence.strip().split()).upper()
        
    def validate_sequence(self, sequence: str) -> bool:
        """Validate if sequence contains only valid DNA bases."""
        sequence = sequence.upper()
        return all(base in self.valid_bases for base in sequence)
    
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