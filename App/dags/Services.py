from time import time
from datetime import datetime
import random
import string
from rdkit import Chem
from rdkit.Chem import AllChem
from App.Mutation_rules import ALL_RULES
from rdkit.Chem import Descriptors, Crippen, Lipinski, QED

async def generate_mutants(smiles: str, max_mutants: int = 50) -> dict:
    initial_smiles = [smiles]
    mutant = []
    applied_rules = []
    all_seen = set(initial_smiles)
    current_generation = initial_smiles.copy()
    generation = 1

    while len(mutant) < max_mutants:
        next_generation = []
        generation_mutants = 0

        for rule_name, smarts in ALL_RULES:
            if len(mutant) >= max_mutants:
                break

            rnx = AllChem.ReactionFromSmarts(smarts)
            rule_applied = False

            for smi_input in current_generation:
                try:
                    mol = Chem.MolFromSmiles(smi_input)
                    if mol is None:
                        continue

                    products = rnx.RunReactants((mol,))

                    if products:
                        rule_applied = True
                        for product_set in products:
                            for product in product_set:
                                try:
                                    smi = Chem.MolToSmiles(product)
                                    if smi not in all_seen:
                                        mutant.append(smi)
                                        all_seen.add(smi)
                                        next_generation.append(smi)
                                        generation_mutants += 1
                                        # print(f"  Gen{generation} - {rule_name}: {smi}")
                                        if len(mutant) >= max_mutants:
                                            break
                                except:
                                    continue
                            if len(mutant) >= max_mutants:
                                break
                except Exception as e:
                    continue

                if len(mutant) >= max_mutants:
                    break

            if rule_applied and rule_name not in applied_rules:
                applied_rules.append(rule_name)

        current_generation = next_generation
        generation += 1

        if generation_mutants == 0:
            print("No new mutants generated in this generation. Stopping.")
            break

    return {
        "input_smiles": smiles,
        "mutants": mutant,
        "total_mutants": len(mutant),
    }

async def calculate_properties(smiles: str) -> dict | None:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    
    threshold = {
        'MW': 500,
        'LogP': 5,
        'HBD': 5,
        'HBA': 10,
        'TPSA': 140
    }

    mw = Chem.Descriptors.MolWt(mol)
    logp = Chem.Crippen.MolLogP(mol)
    hbd = Chem.Lipinski.NumHDonors(mol)
    hba = Chem.Lipinski.NumHAcceptors(mol)
    tpsa = Chem.Descriptors.TPSA(mol)

    violations = 0
    if mw > threshold['MW']:
        violations += 1
    if logp > threshold['LogP']:
        violations += 1
    if hbd > threshold['HBD']:
        violations += 1
    if hba > threshold['HBA']:
        violations += 1
    if tpsa > threshold['TPSA']:
        violations += 1

    if violations <= 1:
        qed = Chem.QED.qed(mol)
        print(f"Calculated properties for {smiles}: MW={mw}, LogP={logp}, HBD={hbd}, HBA={hba}, TPSA={tpsa}, QED={qed}, Violations={violations}")
        score = qed - (violations * 0.1)
        return {
            "smiles": smiles,
            "score": score}
    
    return None