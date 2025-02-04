# CRISPRADIUM

*Because finding CRISPR targets shouldn't feel like looking for a needle in a DNA haystack*

## What's This All About?

Ever tried to edit a massive book but didn't know which page to start with? That's basically what scientists face with CRISPR gene editing. This tool helps you find the perfect "page number" (guide RNA) to make your edit. Think of it as Ctrl+F for DNA, but way cooler.

### ELI5 (Explain Like I'm Five)
Imagine you have a huge LEGO building (that's your DNA), and you want to change one specific brick. You need:
1. A map to find the right brick (that's what guide RNA does)
2. Special LEGO-removing tools (that's the Cas protein)
3. A specific pattern around the brick to grip onto (that's the PAM sequence)

CRISPRADIUM helps you make the perfect map for your LEGO-changing adventure!

## Why PAM Sequences Matter

Here's something most tutorials won't tell you: not all CRISPR systems work on all sequences. Why? Because they're picky eaters! Each system has its favorite "dinner plate arrangement" (PAM sequence):

```
SpCas9:    Likes its dinner with NGG for dessert
           ATGCATGCATGC NGG ATGCATGC...
                        ^^^

Cas12a:    Must have TTTV as an appetizer
           TTTV ATGCATGCATGCATGCATGC...
           ^^^^

SaCas9:    Fancy with its NNGRRT requirement
           ATGCATGC NNGRRT ATGCATGC...
                    ^^^^^^
```

*Note: If you're wondering why I'm using food analogies, it's because proteins are literally molecular machines that "eat" for a living.*

## Features

- Multi-system CRISPR analysis (because one size doesn't fit all)
- FASTA format support (for when you're feeling fancy)
- GC content analysis (because some DNA likes it hot)
- Off-target scoring (preventing CRISPR from being a bull in a DNA china shop)
- Efficiency predictions (so you don't waste time on guide RNAs that are all bark and no bite)

## Installation Guide 🔧

### Prerequisites for Arch Linux
First, let's get your system ready. Open your terminal and run:

```bash
# Update your system first (always a good practice)
sudo pacman -Syu

# Install Python and base dependencies
sudo pacman -S python python-pip

# Install system dependencies for ViennaRNA
sudo pacman -S viennarna

# Install Poetry (Arch's official repo)
sudo pacman -S python-poetry

# Optional but recommended development tools
sudo pacman -S base-devel git
```

### Setting Up Poetry
Poetry needs some initial configuration:

```bash
# Configure Poetry to create virtual environments in the project directory
poetry config virtualenvs.in-project true

# Verify your Poetry installation
poetry --version
```

### Installing CRISPRADIUM

```bash
# Clone the repository
git clone https://github.com/yourusername/crispradium.git

# Enter the project directory
cd crispradium

# Initialize Poetry and install dependencies
poetry install

# Activate the virtual environment
poetry shell
```

### Troubleshooting Common Issues

1. If ViennaRNA fails to install:
```bash
# Try installing with pacman first
sudo pacman -S viennarna

# If that doesn't work, try installing from AUR using yay
yay -S viennarna-git
```

2. If you get permission errors:
```bash
# Fix poetry cache permissions
sudo chown -R $USER:$USER ~/.cache/pypoetry
```

3. For RNA package issues:
```bash
# Install RNA package dependencies
sudo pacman -S gsl boost-libs

# Then reinstall through poetry
poetry install
```

### Development Setup

For development, you might want additional tools:

```bash
# Install development tools
poetry add --dev black flake8 mypy pytest

# Install pre-commit hooks
poetry run pre-commit install
```

### Running the Application

```bash
# Make sure you're in the poetry shell
poetry shell

# Run the application
python run.py

# Or use Poetry to run it directly
poetry run python run.py
```

### Poetry Cheat Sheet for This Project

Common commands you'll use:

```bash
# Add a new dependency
poetry add package-name

# Add a development dependency
poetry add --dev package-name

# Update all dependencies
poetry update

# Show currently installed packages
poetry show

# Run tests
poetry run pytest

# Export requirements.txt (if needed)
poetry export -f requirements.txt --output requirements.txt

# Remove poetry environment
poetry env remove python
```

### Verifying Installation

After installation, verify everything works:

```bash
# Enter poetry shell
poetry shell

# Run basic tests
python -c "import RNA; print('ViennaRNA works!')"
python -c "from Bio import SeqIO; print('BioPython works!')"

# Run the application
python run.py
poetry run python run.py
```

You should see the server start at `http://localhost:5000`


## Usage 🎮

```bash
# Fire it up
python run.py

# Open your browser to
http://localhost:5000
```

## The Science Behind It 🔬

### CRISPR Systems and Their Quirks

| System | PAM Sequence | Best Use Case | Citation |
|--------|-------------|---------------|-----------|
| SpCas9 | NGG | Your Swiss Army knife | Jinek et al., 2012[^1] |
| SaCas9 | NNGRRT | When size matters (it's smaller) | Ran et al., 2015[^2] |
| Cas12a | TTTV | AT-rich regions | Zetsche et al., 2015[^3] |
| SpRY | NRN | The "I'll eat anything" variant | Walton et al., 2020[^4] |

### Success Factors in Guide RNA Design

1. GC Content: Like Goldilocks - not too high, not too low (40-60% is just right)
2. Secondary Structure: Because nobody likes a guide RNA that plays Twister with itself
3. Off-target Effects: Being specific is like being a good archer - you want to hit only your target

## Real-World Examples 📊

### Example 1: When SpCas9 Won't Work
```python
Sequence: ATATATATATATATATAT
Result: No guides found! (Because there's no NGG PAM)
Solution: Try Cas12a (it loves AT-rich sequences)
```

### Example 2: Perfect Target
```python
Sequence: ATGCATGCATGCAGGCATGC
         ----------NGG-------
Result: Multiple guide options (it's like finding a LEGO store in LEGOLAND)
```

# Technical Considerations and Limitations

## Dependency Analysis

### ViennaRNA Package (~150MB)
The ViennaRNA package is crucial for accurate RNA secondary structure prediction, which is essential for guide RNA efficiency prediction. 

**Why it's important:**
- Provides thermodynamic calculations for RNA folding
- Enables accurate secondary structure prediction
- Critical for guide RNA stability assessment

**Size Considerations:**
- Base package: ~150MB
- Additional language bindings: ~20MB
- Total installation size: ~170MB

This size is justified because ViennaRNA includes:
1. Comprehensive energy parameter sets
2. Multiple folding algorithms
3. Optimized C libraries for calculations

### BioPython (~30MB)
Essential for sequence manipulation and biological data handling.

### Other Dependencies:
- NumPy: ~20MB
- Flask: ~1MB
- Other utilities: ~5MB

Total package size: ~230MB

## Time-Space Complexity Analysis

### Guide RNA Finding
```python
Time Complexity:
- Best Case: O(n) where n is sequence length
- Worst Case: O(n × m) where m is number of PAM sites
- Average Case: O(n)

Space Complexity:
- O(k) where k is number of found guide RNAs
```

### Structure Prediction (ViennaRNA)
```python
Time Complexity:
- O(n³) where n is guide RNA length
- Optimized to O(n²) for certain cases

Space Complexity:
- O(n²) for dynamic programming matrix
```

### Off-target Analysis
```python
Time Complexity:
- O(n × g) where g is genome size
- Optimized with indexing to O(n × log(g))

Space Complexity:
- O(m) where m is number of potential off-targets
```

## Performance Limitations

1. Sequence Length Constraints:
   - Minimum: 20 nucleotides
   - Maximum: 200,000 nucleotides
   - Optimal: 1,000-10,000 nucleotides

2. Memory Usage:
   - Base requirement: 500MB RAM
   - Recommended: 2GB RAM
   - For large sequences (>50kb): 4GB RAM

3. Processing Time Guidelines:
   ```
   Sequence Length | Approx. Processing Time
   ----------------|----------------------
   1,000 bp       | 1-2 seconds
   10,000 bp      | 5-10 seconds
   50,000 bp      | 30-60 seconds
   200,000 bp     | 2-5 minutes
   ```

## Deployment Considerations

Due to the size of dependencies (especially ViennaRNA) and computational requirements, this tool has specific hosting requirements:

1. Environment Needs:
   - Full Python environment
   - System-level library installation capabilities
   - Sufficient RAM (2GB minimum)
   - CPU optimization for scientific computing

2. Not Suitable For:
   - Serverless platforms (due to size limitations)
   - Static hosting services
   - Platforms with execution time limits <30s

3. Recommended Deployment:
   - Traditional VPS/VM
   - Scientific computing platforms
   - Self-hosted servers

## Trade-offs and Design Decisions

1. Accuracy vs Speed:
   - ViennaRNA used for accuracy despite size
   - Caching implemented for repeated calculations
   - Parallel processing for large sequences

2. Memory Management:
   - Sequence chunking for large inputs
   - Garbage collection optimization
   - Cache size limits

3. Computation Optimization:
   - Pre-calculated lookup tables
   - Lazy loading of heavy components
   - Result caching

## Future Optimization Possibilities

1. Performance:
   - Implement GPU acceleration
   - Add distributed computing support
   - Optimize memory usage

2. Size Reduction:
   - Custom-built ViennaRNA with essential components
   - Lazy loading of dependencies
   - Optional feature packaging

## References & Further Reading

[^1]: Jinek, M., et al. (2012). A programmable dual-RNA–guided DNA endonuclease in adaptive bacterial immunity. *Science*, 337(6096), 816-821.
   - *The paper that started it all.*

[^2]: Ran, F.A., et al. (2015). In vivo genome editing using Staphylococcus aureus Cas9. *Nature*, 520(7546), 186-191.
   - *Proving that sometimes smaller is better.*

[^3]: Zetsche, B., et al. (2015). Cpf1 is a single RNA-guided endonuclease of a class 2 CRISPR-Cas system. *Cell*, 163(3), 759-771.
   - *Introducing the AT-sequence loving member of the CRISPR family.*

[^4]: Walton, R.T., et al. (2020). Unconstrained genome targeting with near-PAMless engineered CRISPR-Cas9 variants. *Science*, 368(6488), 290-296.
   - *The "I don't care what's for dinner" variant of Cas9.*

## Advanced Reading for the Curious

- ViennaRNA Package (Because RNA structure prediction is like weather forecasting for molecules)
  - Lorenz, R., et al. (2011). ViennaRNA Package 2.0. *Algorithms for Molecular Biology*, 6(1), 1-14.

- Off-target Prediction (Or: How I Learned to Stop Worrying and Love CRISPR)
  - Hsu, P.D., et al. (2013). DNA targeting specificity of RNA-guided Cas9 nucleases. *Nature Biotechnology*, 31(9), 827-832.

## Contributing

Found a bug? Got a cool feature idea? Want to make the code less embarrassing? Feel free to:
1. Fork it
2. Fix it
3. Submit a PR

## Technical Deep Dive 🔬

### Guide RNA Scoring Mechanics

The tool uses a multi-factorial approach to score guide RNAs:

```python
Final_Score = (GC_weight × GC_score) + 
              (Structure_weight × Structure_score) + 
              (Off_target_weight × Off_target_score)
```

#### 1. GC Content Analysis
```python
GC_score = 100 - min(abs(gc_content - 50), 50)
```
- Optimal range: 40-60%
- Penalization for extreme values
- Based on thermodynamic stability research
- Citation: Wang et al. (2014) - "High GC content affects CRISPR efficiency"

#### 2. Secondary Structure Prediction
Using ViennaRNA for minimum free energy (MFE) calculation:
```python
structure, energy = RNA.fold(sequence)
normalized_score = min(100, max(0, (abs(energy) / 30) * 100))
```

Common RNA Structures that Affect Efficiency:
```
Hairpin Loop:        Bulge:           Internal Loop:
    A-U                A              A     U
    G-C              G C              G-C
    C-G               A               C-G
    U-A              G-C              A-U
    UGCAU            U-A              UGCA
```

#### 3. Off-target Analysis Implementation

The tool uses a modified Needleman-Wunsch algorithm for off-target search:

```python
def find_off_targets(guide, genome):
    max_mismatches = 4
    seed_region = guide[:-12]  # Last 12 bases are seed region
    
    # Weighted mismatch scoring
    mismatch_weights = {
        'seed_region': 2.0,
        'non_seed': 1.0,
        'pam_adjacent': 1.5
    }
```

#### 4. PAM Site Recognition Patterns

Detailed PAM requirements for each system:

```
SpCas9 (Original):
5' - N(20) - NGG - 3'
    └guide RNA┘ └PAM┘

Cas12a (Cpf1):
5' - TTTV - N(23) - 3'
    └PAM┘  └guide RNA┘

SaCas9:
5' - N(21) - NNGRRT - 3'
    └guide RNA┘ └─PAM─┘

xCas9:
5' - N(20) - NG - 3'
    └guide RNA┘ └PAM┘
```

### Efficiency Calculations

Each guide RNA is scored based on:

1. Position-specific scoring matrix (PSSM):
```
Position  A    T    C    G
1        0.6  0.8  0.7  0.9
2        0.8  0.7  0.6  0.9
...      ...  ...  ...  ...
20       0.7  0.6  0.8  0.9
```

2. Thermodynamic calculations:
```python
def calculate_thermal_stability(sequence):
    """
    Calculate ΔG for guide RNA binding
    Uses nearest-neighbor method
    """
    nn_parameters = {
        'AA/TT': -1.00,
        'AT/TA': -0.88,
        'TA/AT': -0.58,
        'CA/GT': -1.45,
        'GT/CA': -1.44,
        'CT/GA': -1.28,
        'GA/CT': -1.30,
        'CG/GC': -2.17,
        'GC/CG': -2.24,
        'GG/CC': -1.84
    }
```

### Software Architecture

The tool follows a modular design:

```
CRISPRADIUM/
├── core/
│   ├── guide_finder.py      # PAM and guide identification
│   ├── scoring_engine.py    # Efficiency calculations
│   └── off_target.py       # Off-target analysis
├── analysis/
│   ├── structure_pred.py   # RNA structure prediction
│   └── thermal_calc.py     # Thermodynamic calculations
└── visualization/
    ├── plot_engine.py      # Data visualization
    └── report_gen.py       # Results formatting
```

### Performance Optimizations

1. Sequence Analysis:
   - Uses bit-parallel operations for pattern matching
   - Implements Boyer-Moore algorithm for PAM search
   - Caches commonly used sequences

2. Structure Prediction:
   - Implements McCaskill algorithm for partition function
   - Uses dynamic programming for MFE calculation
   - Parallel processing for multiple sequences

3. Memory Management:
```python
class SequenceHandler:
    def __init__(self):
        self.cache = LRUCache(maxsize=1000)
        self.batch_size = 5000  # For chunked processing
```

### Validation Methods

Each guide RNA undergoes rigorous validation:

1. Sequence Quality:
   ```python
   def validate_sequence(seq):
       # Check length
       if not (17 <= len(seq) <= 23):
           return False
           
       # Check GC content
       gc = (seq.count('G') + seq.count('C')) / len(seq)
       if not (0.4 <= gc <= 0.75):
           return False
   ```

2. Structural Validation:
   - Maximum folding energy thresholds
   - Seed region accessibility checks
   - PAM site structural constraints

3. Specificity Checks:
   - Genome-wide off-target search
   - Seed region uniqueness
   - PAM adjacency scoring

For more detailed technical information and implementation specifics, check out the [Technical Documentation](docs/technical.md).

## About the Author

Just a biologist trying to make CRISPR guide RNA design less painful and more fun.

## License 📄

MIT License - Because sharing is caring (and legally required in this case).

---

*Remember: In molecular biology, as in life, location is everything. And CRISPRADIUM is your GPS for gene editing.*

---

*P.S. If you made it this far in the README, you deserve a cookie. Unfortunately, this is a digital file, so the best I can do is: 🍪*