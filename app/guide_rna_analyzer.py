import RNA
from typing import Dict, Any

class GuideRNAAnalyzer:
    def __init__(self):
        self.cache = {}
        self.crispr_systems = {
            'SpCas9': {
                'pam_sequence': 'NGG',
                'guide_length': 20,
                'description': 'Streptococcus pyogenes Cas9'
            },
            'Cas12a': {
                'pam_sequence': 'TTTV',
                'guide_length': 23,
                'description': 'Cpf1, cuts with 5′ overhang'
            }
        }

    def analyze_sequence(self, sequence: str, system: str = 'SpCas9') -> Dict[str, Any]:
        """Analyze sequence and find potential guide RNAs."""
        cache_key = f"{sequence}_{system}"
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        guides = self.find_guides(sequence, system)
        
        results = {
            'guides': guides,
            'statistics': self.calculate_statistics(guides),
            'visualization_data': self.prepare_visualization_data(guides)
        }
        
        self.cache[cache_key] = results
        return results
    
    def find_guides(self, sequence: str, system: str = 'SpCas9') -> list:
        """Find all possible guide RNAs in sequence."""
        guides = []
        system_info = self.crispr_systems[system]
        pam_seq = system_info['pam_sequence']
        guide_length = system_info['guide_length']
        
        pam_pattern = pam_seq.replace('N', '[ATGC]').replace('V', '[ACG]')
        
        for i in range(len(sequence) - guide_length - len(pam_seq)):
            potential_pam = sequence[i + guide_length:i + guide_length + len(pam_seq)]
            if self._matches_pam(potential_pam, pam_pattern):
                guide = sequence[i:i + guide_length]
                guides.append({
                    'sequence': guide,
                    'position': i,
                    'pam': potential_pam,
                    'gc_content': self.calculate_gc_content(guide),
                    'structure_score': self.calculate_structure_score(guide),
                    'efficiency_score': self.calculate_efficiency(guide)
                })
        
        return guides
    
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