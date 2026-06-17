"""
STUDENT STARTER KIT — BB84 Quantum Utilities

🎯 Goal: Implement classical BB84 logic — basis/bit sampling and ideal measurement rules.

Requirements:
  pip install qiskit qiskit-aer numpy
"""

import os
import numpy as np
from typing import Tuple, Optional, List
from qiskit import QuantumCircuit, ClassicalRegister, transpile
from qiskit.qpy import dump, load
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from utils import save_bytes, load_bytes, get_session_root, safe_input

from qiskit_ibm_runtime.fake_provider import FakeVigoV2 

device_backend = FakeVigoV2()






def generate_bb84_circuit(
    n_qubits: int = 256,
    seed: Optional[int] = None
):
    """
    Generate BB84 preparation parameters: bases and bits.

    STUDENT TASK: Fill in the logic below.
    - Bases: 0 = Z-basis, 1 = X-basis → return as uint8 array
    - Bits: 0 or 1 → return as uint8 array
    - Return (None, bases, bits) — circuit generation is in the solution.

    💡 Hint: Use np.random.choice([0,1], size=n_qubits, dtype=np.uint8)
    """
    if seed is not None:
        np.random.seed(seed)
    qc_sequence=[]
    # TODO: Generate bases array (0/1, size n_qubits, dtype uint8)
    
    bases = np.random.randint(0,2, size=n_qubits,dtype=np.uint8)

    # TODO: Generate bits array (0/1, size n_qubits, dtype uint8)
    bits = np.random.randint(0,2, size=n_qubits,dtype=np.uint8)

    for i in range (n_qubits):
        qc=QuantumCircuit(1,1)
        if bits[i]==1: #Codificamos el bit
            qc.x(0)
        if bases[i]==1: #Ponemos la base correcta
            qc.h(0)
        qc_sequence.append(qc)
    
    return qc_sequence, bases, bits



def measure_bb84_circuits(
    circuit_sequence: List[QuantumCircuit],
    n_qubits: int,NoiseModel=None,
    seed: Optional[int] = None):

    """
    Simulate Bob's measurement of Alice's qubits.

    """
    

    if seed is not None:
        np.random.seed(seed)

    # We generate which basis Bob is going to measure.

    basis=np.random.randint(0,2, size=n_qubits,dtype=np.uint8)
    #Z=0,X=1

    measured_bits = np.zeros(n_qubits, dtype=np.uint8)


    # We measure each qubit in a fake_provider.
    backend=FakeVigoV2()

    for i in range(n_qubits):
        if basis[i]==1:
            circuit_sequence[i].h(0)
        circuit_sequence[i].measure(0,0)
        circuit_transpiled = transpile(circuit_sequence[i], backend)
        if NoiseModel==True:
            job=backend.run(circuit_transpiled,shots=1)
        else:
            job=backend.run(circuit_transpiled,noise_model=None,shots=1)
        result=job.result().get_counts() #Esto da un diccionario

        #La siguiente linea extrae el nombre de la única key del diccionario que será nuestra medida (1 shot) y la convierte en entero
        #Convertirlo en lista es un paso intermedio para que Python no se raye, seguro que hay formas mejores de hacerlo
        measured_bits[i]=int(list(result.keys())[0])


    return measured_bits, basis

def eve_interceps(qc_sequence,
    n_qubits: int,
    seed: Optional[int] = None):

    """
    Simulate Eve intercepting qubits
    """

    #We will simulate Eve intercepting the qubit as her measuring Alice's and codyfing the measure in a new base

    if seed is not None:
        np.random.seed(seed)


    #Eve generates her bases 
    eve_bases = np.random.choice([0, 1], size=n_qubits)

    #Eve measures
    eve_bits=np.zeros(n_qubits, dtype=np.uint8)

    backend=FakeVigoV2()

    for i in range(n_qubits):
        if eve_bases[i]==1:
            qc_sequence[i].h(0)
        qc_sequence[i].measure(0,0)
        circuit_transpiled = transpile(qc_sequence[i], backend)
        job=backend.run(circuit_transpiled,noise_model=None,shots=1)
        result=job.result().get_counts() 
        eve_bits[i]=int(list(result.keys())[0])
    #Eve codifies again the qubits
    eve_qubits=[]
    for i in range (n_qubits):
        qc=QuantumCircuit(1,1)
        if eve_bits[i]==1: #Codificamos el bit
            qc.x(0)
        if eve_bases[i]==1: #Ponemos la base correcta
            qc.h(0)
        eve_qubits.append(qc)

    return eve_qubits

# --- I/O Functions ---


def save_qpy_circuit(circuit: QuantumCircuit, path: str) -> None:
    """Save circuit to QPY file using utils-compatible path resolution."""
    abs_path = os.path.abspath(path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "wb") as f:
        dump(circuit, f)


def save_qpy_circuits(circuits: List[QuantumCircuit], path: str) -> None:
    """Save list of circuits to QPY file."""
    abs_path = os.path.abspath(path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "wb") as f:
        dump(circuits, f)


def load_qpy_circuit(path: str) -> QuantumCircuit:
    """Load circuit from QPY file."""
    abs_path = os.path.abspath(path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"QPY file not found: {abs_path}")
    with open(abs_path, "rb") as f:
        circuits = load(f)
    if not circuits:
        raise ValueError(f"Empty or invalid QPY file: {abs_path}")
    return circuits[0]


def load_qpy_circuits(path: str) -> List[QuantumCircuit]:
    """Load list of circuits from QPY file."""
    abs_path = os.path.abspath(path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"QPY file not found: {abs_path}")
    with open(abs_path, "rb") as f:
        circuits = load(f)
    if not circuits:
        raise ValueError(f"Empty or invalid QPY file: {abs_path}")
    return circuits

    