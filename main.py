import re  # Regular Expressions for string handling
from contextlib import asynccontextmanager

import pandas as pd
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    test_sequence = "Ac A E C K(FAM) A E C CONH2"
    sim_ions = { 1: 1153, 2: 577, 3: 385, 4: 289, 5: 231, 6: 193, 7: 166, 8: 145, 9: 129, 10: 116, 11: 106 }
    molwt_ions = { 1: 1153.22, 2: 577.11, 3: 385.08, 4: 289.06, 5: 231.45, 6: 193.04, 7: 165.61, 8: 145.03, 9: 129.03, 10: 116.23, 11: 105.75 }
    hrms_ions = { 1: 1152.365, 2: 576.6864, 3: 384.7935, 4: 288.8471, 5: 231.2792, 6: 192.9007, 7: 165.4874, 8: 144.9274, 9: 128.9364, 10: 116.1435, 11: 105.6766 }
    mol_formula = {'C': 51, 'H': 61, 'O': 18, 'N': 9, 'S': 2, 'Cl': 0, 'I': 0, 'P': 0, 'Br': 0}
    features = calc_features(test_sequence)
    if features["MolWt"] - 1152.2096 != 0:
        raise Exception("Implementation Error", "MolWt for test sequence was not calculated correctly")
    if features["Exact"] - 1151.3572 != 0:
        raise Exception("Implementation Error", "Exact mass for test sequence was not calculated correctly")
    if not features["HPLC-SIM Ions"] == sim_ions:
        raise Exception("Implementation Error", "HPLC-SIM ions for test sequence were not calculated correctly")
    if not features["MolWt Ions"] == molwt_ions:
        raise Exception("Implementation Error", "MolWt ions for test sequence were not calculated correctly")
    if not features["HRMS Ions"] == hrms_ions:
        raise Exception("Implementation Error", "HRMS ions for test sequence were not calculated correctly")
    if not features["Mol Formula"] == mol_formula:
        raise Exception("Implementation Error", "Molecular formula for test sequence were not calculated correctly")
    yield

description = """
The PNA-Peptide-Conjucate Feature Calculation API allows you to calculate important features of these molecules!

The source-code of the API is available on [Github](https://www.github.com) (TODO: Add repository URL after publishing to Github)  
A demo instance of the API is available on [Fly.io](https://pepmass.fly.dev/)

"""

app = FastAPI(
    lifespan=lifespan,
    title="PepMass API",
    version="0.1",
    summary="PNA-Peptide-Conjucate Feature Calculation API",
    description=description,
        contact={
        "name": "PartTimeDataScientist",
        "url": "http://data-science-solutions.de/pepmass",
        "email": "pepmass@data-science-solutions.de",
    },
    license_info={
        "name" : "MIT License",
        "identifier": "MIT"}
    )

@app.get("/", tags=["General information"])
async def root():
    """
    Returns some general information about the PNA-Peptide Mass Calculation API.
    """
    return {"info" : "PNA-Peptide Mass Calculation API",
            "version" : "0.1"}

@app.get("/health", tags=["General information"])
async def root():
    """
    Just a simple health endpoint - required e.g. for deployment to fly.io.
    """
    return {"status" : "ok"}

@app.get("/building_blocks", tags=["General information"])
async def building_blocks():
    """
    Returns a list of all supported building blocks for performing calculations.

    **Format of this endpoint is currently WIP and will likely change in the future**
    """
    return (input_monomers().to_markdown(index=False))
    #return (input_monomers().to_string(columns=["Group"], header=True, index=False))

@app.get("/calc/mol_wt", tags=["Feature calculation"])
async def exact(sequence: str):
    """
    This endpoint returns the molecular weight of the given input sequence.
    """
    return calc_features(sequence)["MolWt"]

@app.get("/calc/exact", tags=["Feature calculation"])
async def exact(sequence: str):
    """
    This endpoint returns the monoisotopic exact mass of the given input sequence.
    """

    return calc_features(sequence)["Exact"]

@app.get("/calc/sim_ions", tags=["Feature calculation"])
async def exact(sequence: str):
    """
    This endpoint returns the excpecd SIM ions frequently used e.g. in HPLC-purifications.
    
    **ATTENTION:** Not all of them are expected to be seen, this calculation simply lists all **possible** values
    """
    return calc_features(sequence)["HPLC-SIM Ions"]

@app.get("/calc/molwt_ions", tags=["Feature calculation"])
async def exact(sequence: str):
    """
    This endpoint returns multiply charged veriations of the given input sequence (calculated from the molecular weight). Depending on the ionization method and the used mass spectrometer you might observe these multiply charged variatons.


    **ATTENTION:** Not all of them are expected to be seen, this calculation simply lists all **possible** values
    """
    return calc_features(sequence)["MolWt Ions"]

@app.get("/calc/hrms_ions", tags=["Feature calculation"])
async def exact(sequence: str):
    """
    This endpoint returns multiply charged veriations of the given input sequence (calculated from the exact mass). Depending on the ionization method and the used mass spectrometer you might observe these multiply charged variatons.


    **ATTENTION:** Not all of them are expected to be seen, this calculation simply lists all **possible** values
    """
    return calc_features(sequence)["HRMS Ions"]

@app.get("/calc/formula", tags=["Feature calculation"])
async def formula(sequence: str):
    """
    This endpoint returns the molecular formula of the given input sequence.
    """
    return calc_features(sequence)["Mol Formula"]

@app.get("/calc/all_features", tags=["Feature calculation"])
async def all_features(sequence: str):
    """
    This endpoint returns all calculated features in a unified json.
    """
    return calc_features(sequence)

def input_monomers() -> pd.DataFrame:
    # Read properties of monomers from Excel generated .csv-file
    input_monomers = pd.read_csv('Massen.csv', sep=";")
    return input_monomers

def split_sequence(sequence: str) -> list:
    # Split input string at all whitespaces
    seq = re.split("\s+", sequence.strip())
    seq.reverse()
    return(seq)

def calc_multi_ions(mass: float, adduct: str, weight: str, min_wt: int, max_wt: int, digits: int | None = 4) -> dict:
    multi_ions = {}
    adduct_wt = input_monomers().loc[input_monomers()["Group"]==adduct, weight].values[0]
    for i in range(100,0,-1):
        ion = round((mass + (i * adduct_wt))/i, digits)
        if (ion > min_wt and ion < max_wt):
            multi_ions[i] = ion
    return(multi_ions)

def add_building_block(mass: float, formula: dict, building_block: str, weight: str) -> tuple[float, dict]:
    atoms = ['C', 'H', 'O', 'N', 'S', 'Cl', 'I', 'P', 'Br']

    try:
        mass += (input_monomers().loc[input_monomers()["Group"]==building_block, weight].values[0])
        leaving = (input_monomers().loc[input_monomers()["Group"]==building_block, "Leaving"].values[0])
        for atom in atoms:
            formula[atom] += int(input_monomers().loc[input_monomers()["Group"]==building_block, atom].values[0])

        if leaving != "---":
            mass -= (input_monomers().loc[input_monomers()["Group"]==leaving, weight].values[0])
            for atom in atoms:
                formula[atom] -= int(input_monomers().loc[input_monomers()["Group"]==leaving, atom].values[0])
    except IndexError:
        mass += (input_monomers().loc[input_monomers()["Group"]=="UKN", weight].values[0])
        leaving = (input_monomers().loc[input_monomers()["Group"]=="UKN", "Leaving"].values[0])
        for atom in atoms:
            formula[atom] += (input_monomers().loc[input_monomers()["Group"]==building_block, atom].values[0])

        if leaving != "---":
            mass -= (input_monomers().loc[input_monomers()["Group"]==leaving, weight].values[0])
            for atom in atoms:
                formula[atom] -= int(input_monomers().loc[input_monomers()["Group"]==leaving, atom].values[0])

    return mass, formula

def calc_features(sequence: str) -> list:
    dummy = {'C': 0, 'H': 0, 'O': 0, 'N': 0, 'S': 0, 'Cl': 0, 'I': 0, 'P': 0, 'Br': 0}
    mol_wt = 0
    exact = 0
    formula = {'C': 0, 'H': 0, 'O': 0, 'N': 0, 'S': 0, 'Cl': 0, 'I': 0, 'P': 0, 'Br': 0}
    for monomer in split_sequence(sequence):
        # If Monomer contains bracketed statement add the mass of the bracketed monomer as well
        if re.search('\(.*\)', monomer):
            m = re.search('(.*)\((.*)\)', monomer)
            modifier = m.group(2)
            monomer = m.group(1)
            mol_wt, formula = add_building_block(mol_wt, formula, monomer, "MolWt")
            mol_wt, formula = add_building_block(mol_wt, formula, modifier, "MolWt")
            exact, dummy = add_building_block(exact, dummy, monomer, "Exact")
            exact, dummy = add_building_block(exact, dummy, modifier, "Exact")
        # Else only add mass of building block
        else:
            mol_wt, formula = add_building_block(mol_wt, formula, monomer, "MolWt")
            exact, dummy = add_building_block(exact, dummy, monomer, "Exact")

    # TODO: Capture intermediary results for termination sequences

    result = {
        "MolWt": round(mol_wt,4),
        "Exact": round(exact,4),
        "Mol Formula": formula,
        "HPLC-SIM Ions": calc_multi_ions(mol_wt, "Hplus", "MolWt", 100, 50000, 0),
        "MolWt Ions": calc_multi_ions(mol_wt, "Hplus", "MolWt", 100, 50000, 2),
        "HRMS Ions": calc_multi_ions(exact, "Hplus", "Exact", 100, 50000, 4)
    }
    return (result)