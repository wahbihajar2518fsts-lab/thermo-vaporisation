from math import log
from chemicals.identifiers import search_chemical
from chemicals import Tb, Tc, Pc
from thermo.group_contribution.joback import Joback
from chemicals.phase_change import Riedel

R = 8.314          # J/(mol.K)
P_ATM = 101325.0   # Pa


def identifier(nom):
    """Trouve la molécule (nom anglais, formule, CAS ou SMILES)."""
    try:
        return search_chemical(nom)
    except Exception:
        return None


def tb_normale(mol):
    """Tb à 1 atm : valeur mesurée, sinon estimation Joback."""
    try:
        valeur = Tb(mol.CAS)
        if valeur is not None:
            return valeur, "valeur mesurée (base de données)", None
    except Exception:
        pass
    try:
        est = Joback(mol.smiles).estimate()
        return est["Tb"], "ESTIMATION Joback (approximative, ±10-30 K)", est
    except Exception:
        return None, "impossible de calculer", None


def tb_antoine(mol, P):
    """Équation d'Antoine : log10(P[Pa]) = A - B/(T + C), T en K.
    Retourne la température d'ébullition à la pression P (Pa)."""
    try:
        from chemicals.vapor_pressure import Psat_data_AntoinePoling as D
        ligne = D.loc[mol.CAS]
        A, B, C = float(ligne["A"]), float(ligne["B"]), float(ligne["C"])
        from math import log10
        T = B / (A - log10(P)) - C
        return T, f"Antoine (A={A:.4f}, B={B:.2f}, C={C:.2f})"
    except Exception:
        return None, None


def tb_clausius(mol, tb1, est, P):
    """Clausius-Clapeyron : 1/T2 = 1/T1 - R ln(P2/P1) / Hvap
    Hvap à Tb estimée avec la relation de Riedel."""
    try:
        tc = Tc(mol.CAS) or (est or {}).get("Tc")
        pc = Pc(mol.CAS) or (est or {}).get("Pc")
        if tc is None or pc is None:
            est = Joback(mol.smiles).estimate()
            tc, pc = est["Tc"], est["Pc"]
        hvap = Riedel(tb1, tc, pc)                 # J/mol
        T2 = 1.0 / (1.0 / tb1 - R * log(P / P_ATM) / hvap)
        return T2, f"Clausius-Clapeyron (Hvap = {hvap/1000:.1f} kJ/mol, Riedel)"
    except Exception:
        return None, None


def calcul(nom, P=P_ATM):
    mol = identifier(nom)
    if mol is None:
        return None, "Molécule introuvable (essayez le nom en anglais)."

    tb1, source1, est = tb_normale(mol)
    resultat = {"nom": mol.common_name, "formule": mol.formula,
                "CAS": mol.CAS, "tb_1atm": tb1, "source_1atm": source1}

    if abs(P - P_ATM) < 1:            # pression normale
        resultat["tb"], resultat["methode"] = tb1, source1
        return resultat, None

    # Pression différente de 1 atm : on cherche la meilleure méthode
    T, methode = tb_antoine(mol, P)
    if T is None and tb1 is not None:
        T, methode = tb_clausius(mol, tb1, est, P)
    resultat["tb"], resultat["methode"] = T, methode
    return resultat, None


# ----------------- Programme principal -----------------
UNITES = {"pa": 1.0, "kpa": 1e3, "bar": 1e5, "atm": P_ATM, "mmhg": 133.322}

while True:
    nom = input("\nMolécule (nom/formule/CAS) ou 'q' pour quitter : ").strip()
    if nom.lower() == "q":
        break

    p_txt = input("Pression (ex: 1 atm, 0.5 bar, 760 mmHg) [Entrée = 1 atm] : ").strip()
    P = P_ATM
    if p_txt:
        try:
            val, unite = p_txt.split()
            P = float(val) * UNITES[unite.lower()]
        except Exception:
            print("Format invalide -> pression de 1 atm utilisée.")

    res, erreur = calcul(nom, P)
    if erreur:
        print(erreur)
        continue

    print("\n--- Résultat ---")
    print(f"Molécule : {res['nom']}  ({res['formule']}, CAS {res['CAS']})")
    if res["tb_1atm"] is not None:
        print(f"Tb à 1 atm : {res['tb_1atm']:.2f} K = {res['tb_1atm']-273.15:.2f} °C"
              f"  [{res['source_1atm']}]")
    if res["tb"] is not None and abs(P - P_ATM) >= 1:
        print(f"Tb à {P/1000:.2f} kPa : {res['tb']:.2f} K = {res['tb']-273.15:.2f} °C"
              f"  [{res['methode']}]")
    if res["tb"] is None:
        print("Calcul impossible pour cette molécule.")