from typing import List, Dict, Tuple
import re
from Bio import SeqIO
from Bio.Seq import Seq
import numpy as np
from collections import defaultdict

class SequenceHandler:
    """
    Handles DNA sequence processing and validation for CRISPR guide RNA design
    """
    
    def __init__(self):
        self.valid_bases = set(['A', 'T', 'G', 'C', 'N'])
        self.complementary_bases = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G', 'N': 'N'}
        self.max_off_target_score = 4  # Maximum allowed off-target score

    def clean_sequence(self, sequence: str) -> str:
        """Remove whitespace and convert to uppercase."""
        return ''.join(sequence.strip().split()).upper()
        
    def validate_sequence(self, sequence: str) -> bool:
        
        """
        Validates if the input sequence contains only valid DNA bases
        
        Args:
            sequence (str): Input DNA sequence
            
        Returns:
            bool: True if sequence is valid, False otherwise
        """ 
        sequence = sequence.upper()
        return all(base in self.valid_bases for base in sequence)
    
    def find_pam_sites(self, sequence: str, pam_sequence: str = 'NGG') -> List[Dict]:
        """
        Finds all PAM sites in the given sequence
        
        Args:
            sequence (str): Input DNA sequence
            pam_sequence (str): PAM sequence to look for (default: NGG for SpCas9)
            
        Returns:
            List[Dict]: List of dictionaries containing PAM site information
        """

        sequence = sequence.upper()
        pam_pattern = pam_sequence.replace('N', '[ATGC]')
        pam_sites = []


        # Search for PAM sites on forward strand
        for match in re.finditer(pam_pattern, sequence):
            start = match.start()
            if start >= 20:  # Ensure there's enough sequence for guide RNA
                pam_sites.append({
                    'position': start,
                    'strand': '+',
                    'pam_sequence': sequence[start:start + 3],
                    'guide_sequence': sequence[start - 20:start]
                })
                
        # Search for PAM sites on reverse strand
        reverse_sequence = self.get_reverse_complement(sequence)
        for match in re.finditer(pam_pattern, reverse_sequence):
            start = match.start()
            if start >= 20:
                original_position = len(sequence) - start - 3
                pam_sites.append({
                    'position': original_position,
                    'strand': '-',
                    'pam_sequence': sequence[original_position:original_position + 3],
                    'guide_sequence': self.get_reverse_complement(
                        sequence[original_position + 3:original_position + 23]
                    )
                })
        
        return pam_sites
    
    def get_reverse_complement(self, sequence: str) -> str:
        """
        Returns the reverse complement of a DNA sequence
        
        Args:
            sequence (str): Input DNA sequence
            
        Returns:
            str: Reverse complement sequence
        """
        return ''.join(self.complementary_bases[base] 
                      for base in sequence.upper()[::-1])
    
    def calculate_gc_content(self, sequence: str) -> float:
        """
        Calculates GC content of a sequence
        
        Args:
            sequence (str): Input DNA sequence
            
        Returns:
            float: GC content percentage
        """
        sequence = sequence.upper()
        gc_count = sequence.count('G') + sequence.count('C')
        return (gc_count / len(sequence)) * 100 if sequence else 0
    
    def score_guide_rna(self, guide_sequence: str, sequence: str) -> float:
        """
        Scores a guide RNA sequence based on several criteria:
        - GC content
        - Secondary structure (self-complementarity)
        - Off-target potential
        
        Args:
            guide_sequence (str): Guide RNA sequence
            sequence (str): Full input DNA sequence
            
        Returns:
            float: Guide RNA score (higher is better)
        """
        # GC content score
        gc_content = self.calculate_gc_content(guide_sequence)
        gc_score = 1 - abs(gc_content - 50) / 50
        
        # Secondary structure score
        self_complementarity = self.check_self_complementarity(guide_sequence)
        secondary_structure_score = 1 - self_complementarity
        
        # Off-target score
        off_target_score = self.calculate_off_target_score(guide_sequence, sequence)
        
        # Overall score
        overall_score = gc_score * secondary_structure_score * (1 - off_target_score / self.max_off_target_score)
        return overall_score
    
    def check_self_complementarity(self, sequence: str) -> float:
        """
        Checks the self-complementarity of a DNA sequence.
        Higher self-complementarity indicates the sequence may form secondary structures.
        
        Args:
            sequence (str): DNA sequence
            
        Returns:
            float: Self-complementarity score (0.0 to 1.0)
        """
        reverse_complement = self.get_reverse_complement(sequence)
        matches = 0
        for i in range(len(sequence)):
            if sequence[i] == reverse_complement[i]:
                matches += 1
        return matches / len(sequence)
    
    def calculate_off_target_score(self, guide_sequence: str, sequence: str) -> float:
        
        """
        Calculates the off-target score for a guide RNA sequence.
        The off-target score is based on the number of potential off-target sites and
        the number of mismatches between the guide RNA and the off-target sites.
        
        Args:
            guide_sequence (str): Guide RNA sequence
            sequence (str): Full input DNA sequence
            
        Returns:
            float: Off-target score (0.0 to 1.0, where 0.0 is best)
        """
        off_target_sites = self.find_off_target_sites(guide_sequence, sequence)
        off_target_score = 0
        
        for site in off_target_sites:
            off_target_score += self.calculate_off_target_mismatch_score(guide_sequence, site)
        
        return off_target_score
    
    def find_off_target_sites(self, guide_sequence: str, sequence: str) -> List[str]:
        """
        Finds all potential off-target sites in the input sequence for a given guide RNA.
        
        Args:
            guide_sequence (str): Guide RNA sequence
            sequence (str): Full input DNA sequence
            
        Returns:
            List[str]: List of off-target site sequences
        """
        off_target_sites = []
        
        # Search for off-target sites on the forward strand
        for i in range(len(sequence) - len(guide_sequence) + 1):
            off_target_site = sequence[i:i+len(guide_sequence)]
            if self.count_mismatches(guide_sequence, off_target_site) <= 3:
                off_target_sites.append(off_target_site)
        
        # Search for off-target sites on the reverse strand
        reverse_sequence = self.get_reverse_complement(sequence)
        for i in range(len(reverse_sequence) - len(guide_sequence) + 1):
            off_target_site = reverse_sequence[i:i+len(guide_sequence)]
            if self.count_mismatches(guide_sequence, off_target_site) <= 3 and off_target_site != guide_sequence: off_target_sites.append(off_target_site)
        
        return off_target_sites
    
    def calculate_off_target_mismatch_score(self, guide_sequence: str, off_target_site: str) -> float:
        """
        Calculates the off-target mismatch score for a given guide RNA and off-target site.
        The score is based on the number of mismatches and their positions.
        
        Args:
            guide_sequence (str): Guide RNA sequence
            off_target_site (str): Off-target site sequence
            
        Returns:
            float: Off-target mismatch score (0.0 to 1.0, where 0.0 is best)
        """
        mismatches = self.count_mismatches(guide_sequence, off_target_site)
        score = 1 - (20 - mismatches) / 20
        return score
    
    def count_mismatches(self, sequence1: str, sequence2: str) -> int:
        """
        Counts the number of mismatches between two DNA sequences.
        
        Args:
            sequence1 (str): First DNA sequence
            sequence2 (str): Second DNA sequence
            
        Returns:
            int: Number of mismatches
        """
        return sum(1 for base1, base2 in zip(sequence1, sequence2) if base1 != base2)