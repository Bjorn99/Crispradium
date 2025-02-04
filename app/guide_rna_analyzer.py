import RNA
from typing import Dict, Any

class GuideRNAAnalyzer:
    def __init__(self):
        self.cache = {}
        self.crispr_systems = {
            'SpCas9': {
                'pam_sequence': 'NGG',
                'guide_length': 20,
                'description': 'Streptococcus pyogenes Cas9',
                'citation': 'Jinek et al., Science (2012)',
                'efficiency_weight': 1.0
            },
            'SaCas9': {
                'pam_sequence': 'NNGRRT',
                'guide_length': 21,
                'description': 'Staphylococcus aureus Cas9',
                'citation': 'Ran et al., Nature (2015)',
                'efficiency_weight': 0.9,
                'notes': 'Smaller size, good for AAV delivery'
            },
            'Cas12a': {
                'pam_sequence': 'TTTV',
                'guide_length': 23,
                'description': 'Cpf1, cuts with 5′ overhang',
                'citation': 'Zetsche et al., Cell (2015)',
                'efficiency_weight': 0.95
            },
            'enAsCas12a': {
                'pam_sequence': 'TTTN',
                'guide_length': 23,
                'description': 'Enhanced Acidaminococcus Cas12a',
                'citation': 'Kleinstiver et al., Nature Biotech (2019)',
                'efficiency_weight': 0.98
            },
            'xCas9': {
                'pam_sequence': 'NG',
                'guide_length': 20,
                'description': 'PAM-flexible SpCas9 variant',
                'citation': 'Hu et al., Nature (2018)',
                'efficiency_weight': 0.85,
                'notes': 'Broader PAM recognition, lower activity'
            },
            'Cas9-NG': {
                'pam_sequence': 'NG',
                'guide_length': 20,
                'description': 'SpCas9 variant for NG PAM',
                'citation': 'Nishimasu et al., Science (2018)',
                'efficiency_weight': 0.88,
                'notes': 'Engineered for NG PAM recognition'
            },
            'SpRY': {
                'pam_sequence': 'NRN',
                'guide_length': 20,
                'description': 'SpCas9 variant with minimal PAM',
                'citation': 'Walton et al., Science (2020)',
                'efficiency_weight': 0.82,
                'notes': 'Near-PAMless SpCas9, lower activity'
            }
        }

    def analyze_sequence(self, sequence: str, system: str = 'SpCas9') -> Dict[str, Any]:
        """Analyze sequence and find potential guide RNAs."""
        if system not in self.crispr_systems:
            raise ValueError(f"Unsupported CRISPR system: {system}")
            
        cache_key = f"{sequence}_{system}"
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        guides = self.find_guides(sequence, system)
        
        results = {
            'guides': guides,
            'statistics': self.calculate_statistics(guides),
            'visualization_data': self.prepare_visualization_data(guides),
            'system_info': self.crispr_systems[system]
        }
        
        self.cache[cache_key] = results
        return results
    
    def find_guides(self, sequence: str, system: str = 'SpCas9') -> list:
        """Find all possible guide RNAs in sequence."""
        guides = []
        system_info = self.crispr_systems[system]
        pam_seq = system_info['pam_sequence']
        guide_length = system_info['guide_length']
        efficiency_weight = system_info['efficiency_weight']
        
        # Convert IUPAC codes to regex patterns
        pam_pattern = self._convert_pam_to_regex(pam_seq)
        
        for i in range(len(sequence) - guide_length - len(pam_seq)):
            potential_pam = sequence[i + guide_length:i + guide_length + len(pam_seq)]
            if self._matches_pam(potential_pam, pam_pattern):
                guide = sequence[i:i + guide_length]
                guide_data = {
                    'sequence': guide,
                    'position': i,
                    'pam': potential_pam,
                    'gc_content': self.calculate_gc_content(guide),
                    'structure_score': self.calculate_structure_score(guide),
                }
                # Apply system-specific efficiency weight
                guide_data['efficiency_score'] = self.calculate_efficiency(guide) * efficiency_weight
                guides.append(guide_data)
        
        return guides

    def _convert_pam_to_regex(self, pam: str) -> str:
        """
        Convert IUPAC nucleotide codes to regex patterns.
        Support for more PAM sequences.
        """
        iupac_map = {
            'N': '[ATGC]',
            'R': '[AG]',
            'Y': '[CT]',
            'M': '[AC]',
            'K': '[GT]',
            'S': '[GC]',
            'W': '[AT]',
            'H': '[ACT]',
            'B': '[CGT]',
            'V': '[ACG]',
            'D': '[AGT]'
        }
        return ''.join(iupac_map.get(c, c) for c in pam)
    
    def _matches_pam(self, sequence: str, pattern: str) -> bool:
        """Check if sequence matches PAM pattern."""
        import re
        return bool(re.match(f"^{pattern}$", sequence))
    
    def calculate_gc_content(self, sequence: str) -> float:
        """Calculate GC content percentage."""
        gc_count = sum(1 for base in sequence if base in 'GC')
        return (gc_count / len(sequence)) * 100
    
    def calculate_structure_score(self, sequence: str) -> Dict[str, Any]:
        """Calculate RNA structure score."""
        structure, energy = RNA.fold(sequence)
        normalized_score = min(100, max(0, (abs(energy) / 30) * 100))
        return {
            'structure': structure,
            'energy': energy,
            'score': normalized_score
        }
    
    def calculate_efficiency(self, guide: str) -> float:
        """Calculate guide RNA efficiency score."""
        gc_content = self.calculate_gc_content(guide)
        structure_score = self.calculate_structure_score(guide)['score']
        
        gc_weight = 0.6
        structure_weight = 0.4
        
        gc_score = 100 - min(abs(gc_content - 50), 50)
        
        final_score = (gc_score * gc_weight + structure_score * structure_weight)
        return round(final_score, 2)
    
    def prepare_visualization_data(self, guides: list) -> Dict[str, list]:
        """Prepare data for visualization."""
        return {
            'positions': [g['position'] for g in guides],
            'scores': [g['efficiency_score'] for g in guides],
            'gc_contents': [g['gc_content'] for g in guides]
        }
    
    def calculate_statistics(self, guides: list) -> Dict[str, Any]:
        """Calculate statistics for found guides."""
        if not guides:
            return {
                'total_guides': 0,
                'average_gc': 0,
                'average_efficiency': 0,
                'best_guide': None
            }
            
        return {
            'total_guides': len(guides),
            'average_gc': round(sum(g['gc_content'] for g in guides) / len(guides), 2),
            'average_efficiency': round(sum(g['efficiency_score'] for g in guides) / len(guides), 2),
            'best_guide': max(guides, key=lambda x: x['efficiency_score'])
        }