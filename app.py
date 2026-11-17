
import streamlit as st
from thermo import Chemical

st.set_page_config(
    page_title="Thermo",
    page_icon="🌡️",
    layout="centered"
)

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
    "Entrez le nom d'une molécule "
    "pour déterminer sa température d'ébullition."
)

molecule = st.text_input(
    "Nom de la molécule :",
    placeholder="Exemple : Water, Ethanol, Benzene"
)

if st.button("Rechercher", type="primary"):

    if molecule.strip():

        try:
            produit = Chemical(molecule.strip())

            if produit.Tb is not None:
                temperature_k = produit.Tb
                temperature_c = temperature_k - 273.15

                st.success("Molécule trouvée !")
                st.write("### Résultats")

                st.metric(
                    "Température d'ébullition",
                    f"{temperature_c:.2f} °C"
                )

                st.metric(
                    "Température en Kelvin",
                    f"{temperature_k:.2f} K"
                )

            else:
                st.warning(
                    "Température d'ébullition non disponible."
                )

        except Exception:
            st.error(
                "Molécule introuvable. Vérifiez son nom."
            )

    else:
        st.warning("Veuillez entrer le nom d'une molécule.")

 