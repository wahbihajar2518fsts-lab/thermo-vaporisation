
import streamlit as st
from PROJET import calcul

# Configuration
st.set_page_config(page_title="Thermo", page_icon="🌡️")

# Protection par mot de passe
def login():
    st.title("🔐 Thermo")
    st.subheader("Accès réservé")

    password = st.text_input(
        "Entrez le mot de passe :",
        type="password"
    )

    if st.button("Se connecter", type="primary"):
        if password == st.secrets["APP_PASSWORD"]:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect.")


if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login()
    st.stop()


# Application Thermo
st.title("🌡️ Thermo")
st.subheader("Recherche des propriétés thermodynamiques")

st.write(
    "Entrez le nom d'une molécule pour calculer "
    "sa température d'ébullition selon la pression."
)

molecule = st.text_input(
    "Nom de la molécule :",
    placeholder="Water, Ethanol, Benzene..."
)

st.write("### Conditions de calcul")

unites = {
    "Pa": 1.0,
    "kPa": 1000.0,
    "bar": 100000.0,
    "atm": 101325.0,
    "mmHg": 133.322
}

unite = st.selectbox(
    "Unité de pression :",
    list(unites.keys()),
    index=3
)

pression = st.number_input(
    "Valeur de la pression :",
    min_value=0.001,
    value=1.0,
    step=0.1
)

if st.button("Calculer", type="primary"):

    if molecule.strip():

        try:
            P = pression * unites[unite]

            resultat, erreur = calcul(molecule.strip(), P)

            if erreur:
                st.error(erreur)

            else:
                st.success("Molécule trouvée !")

                st.write("### Informations sur la molécule")
                st.write("**Nom :**", resultat["nom"])
                st.write("**Formule :**", resultat["formule"])
                st.write("**CAS :**", resultat["CAS"])

                st.write("### Résultats")

                if resultat["tb_1atm"] is not None:
                    tb1 = resultat["tb_1atm"]

                    st.metric(
                        "Température d'ébullition à 1 atm",
                        f"{tb1 - 273.15:.2f} °C"
                    )

                    st.write(
                        f"Température en Kelvin : {tb1:.2f} K"
                    )

                    st.caption(resultat["source_1atm"])

                if resultat["tb"] is not None:

                    tb = resultat["tb"]

                    st.metric(
                        "Température d'ébullition à la pression choisie",
                        f"{tb - 273.15:.2f} °C"
                    )

                    st.write(
                        f"Température en Kelvin : {tb:.2f} K"
                    )

                    st.info(
                        f"Méthode utilisée : {resultat['methode']}"
                    )

                else:
                    st.warning(
                        "Calcul impossible à cette pression."
                    )

        except Exception as e:
            st.error(f"Erreur de calcul : {e}")

    else:
        st.warning("Veuillez entrer le nom d'une molécule.")

 
 
