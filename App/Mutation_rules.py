# --- class 1: Change single molecule ---
SMALL_MODIFICATIONS = [
    ("Add F to Aromatic", '[cH:1]>>[c:1]F'),
    ("Add Cl to Aromatic", '[cH:1]>>[c:1]Cl'),
    ("Add Br to Aromatic", '[cH:1]>>[c:1]Br'),
    ("Add Methyl to Aromatic", '[cH:1]>>[c:1]C'),
    ("Add Ethyl to Aromatic", '[cH:1]>>[c:1]CC'),
    ("Add CF3 to Aromatic", '[cH:1]>>[c:1]C(F)(F)F'),
    ("Remove Methyl", '[C:1]-[C;H3]>>[C:1][H]'),
    ("F to Cl", '[F:1]>>[Cl:1]'),
    ("Cl to F", '[Cl:1]>>[F:1]'),
    ("Cl to Br", '[Cl:1]>>[Br:1]'),
    ("Br to Cl", '[Br:1]>>[Cl:1]'),
    ("Methoxy to Hydroxy", '[c:1][O][C;H3]>>[c:1][O][H]'),
    ("Hydroxy to Methoxy", '[c:1][O;H1]>>[c:1]OC'),
    ("Nitro to Amino", '[c:1][N+](=O)[O-]>>[c:1]N'),
]

# --- class 2: Bioisosteres ---
BIOISOSTERES = [
    ("Carboxylic Acid to Tetrazole", '[C:1](=[O:2])[O;H1]>>[C:1]c1nnn[nH]1'),
    ("Carboxylic Acid to Hydroxamic Acid", '[C:1](=[O:2])[O;H1]>>[C:1](=[O:2])NO'),
    ("Carboxylic Acid to Methyl Ester", '[C:1](=[O:2])[O;H1]>>[C:1](=[O:2])OC'),
    ("Carboxylic Acid to Ethyl Ester", '[C:1](=[O:2])[O;H1]>>[C:1](=[O:2])OCC'),
    ("Carboxylic Acid to Amide", '[C:1](=[O:2])[O;H1]>>[C:1](=[O:2])N'),
    ("Amide to Ester", '[C:1](=[O:2])[N:3]>>[C:1](=[O:2])[O:3]'),
    ("Ester to Amide", '[C:1](=[O:2])[O:3]>>[C:1](=[O:2])[N:3]'),
    ("Ester to Thioester", '[C:1](=[O:2])[O:3][C:4]>>[C:1](=[O:2])[S:3][C:4]'),
    ("Ether to Amine", '[C:1][O:2][C:3]>>[C:1][N:2][C:3]'),
    ("Ether to Thioether", '[C:1][O:2][C:3]>>[C:1][S:2][C:3]'),
    ("Benzene to Pyridine", 'c1ccccc1>>n1ccccc1'),
    ("Hydroxyl to Fluorine", '[C:1][O;H1]>>[C:1]F'),
    ("Hydroxyl to Amine", '[C:1][O;H1]>>[C:1]N'),
    ("Carbonyl to Thiocarbonyl", '[C:1]=[O:2]>>[C:1]=[S:2]'),
]

# --- class 3: Chain Modifications ---
CHAIN_MODS = [
    ("Extend Methyl to Ethyl", '[C:1][C;H3]>>[C:1]CC'),
    ("Extend Methyl to Propyl", '[C:1][C;H3]>>[C:1]CCC'),
    ("Extend Methyl to Isopropyl", '[C:1][C;H3]>>[C:1]C(C)C'),
    ("Shorten Ethyl to Methyl", '[C:1]CC>>[C:1]C'),
    ("Shorten Propyl to Ethyl", '[C:1]CCC>>[C:1]CC'),
    ("Isopropyl to n-Propyl", 'CC(C)[*:1]>>CCC[*:1]'),
    ("Acetyl to Propionyl", '[C:1]C(=O)C>>[C:1]C(=O)CC'),
    ("Acetyl to Butyryl", '[C:1]C(=O)C>>[C:1]C(=O)CCC'),
    ("Acetyl to Benzoyl", '[C:1]C(=O)C>>[C:1]C(=O)c1ccccc1'),
    ("Benzene to Naphthalene", 'c1ccccc1>>c1ccc2ccccc2c1'),
    ("Phenyl to Cyclohexyl", '[c:1]1ccccc1>>[C:1]1CCCCC1'),
]

# --- class 5: Functional Group Additions ---
FUNCTIONAL_GROUPS = [
    ("Add Hydroxyl to Aromatic", '[cH:1]>>[c:1]O'),
    ("Add Amino to Aromatic", '[cH:1]>>[c:1]N'),
    ("Add Nitro to Aromatic", '[cH:1]>>[c:1][N+](=O)[O-]'),
    ("Add Carboxyl to Aromatic", '[cH:1]>>[c:1]C(=O)O'),
    ("Add Aldehyde to Aromatic", '[cH:1]>>[c:1]C=O'),
    ("Add Methoxy to Aromatic", '[cH:1]>>[c:1]OC'),
]
# --- class 4: Scaffold Hopping ---
# Note: These rules significantly change the structure and may greatly affect activity
RING_MODS = [
    ("Cyclopentane to Cyclohexane", '[C:1]1[C:2][C:3][C:4][C:5]1>>[C:1]1[C:2][C:3][C:4][C:5]C1'),
    ("Make Fused Ring (O)", '[c:1][c:2]OC>>[c:1]1[c:2]OCC1'),
]

# --- ALL RULES ---
# Use this variable to run all rules
ALL_RULES = SMALL_MODIFICATIONS + BIOISOSTERES + CHAIN_MODS + RING_MODS