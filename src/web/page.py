import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configurar la app
st.set_page_config(page_title="Entrenamiento PPO", layout="wide")

st.title("📊 Monitoreo del Entrenamiento PPO")

# Cargar datos de entrenamiento (se actualiza cada cierto tiempo)
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("ppo_training_log.csv")  # Archivo donde se guardan las recompensas
        return df
    except FileNotFoundError:
        return pd.DataFrame({"Episode": [], "Reward": []})

df = load_data()

# Mostrar estadísticas
if not df.empty:
    st.metric("Última Recompensa", df["Reward"].iloc[-1])
    st.metric("Promedio Últimos 50 Episodios", df["Reward"].rolling(50).mean().iloc[-1])

    # Gráfica de recompensas
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["Episode"], df["Reward"], label="Reward", color="blue")
    ax.set_xlabel("Episodio")
    ax.set_ylabel("Recompensa")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)
else:
    st.warning("Aún no hay datos de entrenamiento.")

st.write("⚡ La gráfica se actualizará cuando haya más episodios registrados.")
