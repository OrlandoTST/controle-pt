import streamlit as st
import pandas as pd
from datetime import datetime

# Caminho do arquivo
DATA_FILE = "pts_data.csv"

# Colunas obrigatórias
required_columns = [
    "Numeração", "Tipo", "Setor", "Solicitante", "Descrição do Serviço",
    "Data Emissão", "Devolvida", "Data Devolução", "Recebedor",
    "TST Resp. Liberação em área", "Última Atualização"
]

# Carregar dados
try:
    df = pd.read_csv(DATA_FILE)
    for col in required_columns:
        if col not in df.columns:
            df[col] = ""
except FileNotFoundError:
    df = pd.DataFrame(columns=required_columns)

df = df.reindex(columns=required_columns)

# Notificação de nova PT emitida
if not df.empty:
    ultima_pt = df.iloc[-1]
    ultima_msg = f"🔔 Última PT emitida: {ultima_pt['Numeração']} ({ultima_pt['Data Emissão']})"
    st.info(ultima_msg)

# Atualizar status de devolução
def sinalizar_devolucao(row):
    return "Devolvida" if str(row["Devolvida"]).strip().lower() == "sim" else "Não devolvida"

if not df.empty:
    df["Status"] = df.apply(sinalizar_devolucao, axis=1)

# Gerar próxima numeração
def gerar_numeracao():
    if df.empty:
        return "061-2025"
    nums_existentes = df["Numeração"].dropna().apply(lambda x: int(x.split("-")[0]))
    novo_num = nums_existentes.max() + 1 if not nums_existentes.empty else 61
    return f"{novo_num:03d}-2025"

# Interface
st.title("Controle de Permissão de Trabalho (PT/PTT)")

# Formulário para nova PT
with st.form("nova_pt"):
    numeracao = gerar_numeracao()
    tipo = st.selectbox("Tipo de Permissão", ["PT", "PTT"])
    setor = st.text_input("Setor")
    solicitante = st.text_input("Solicitante")
    descricao_servico = st.text_area("Descrição do Serviço")
    data_emissao = datetime.today().strftime('%Y-%m-%d')
    submit_button = st.form_submit_button("Emitir PT/PTT")

    if submit_button and setor and solicitante:
        nova_linha = {
            "Numeração": numeracao,
            "Tipo": tipo,
            "Setor": setor,
            "Solicitante": solicitante,
            "Descrição do Serviço": descricao_servico,
            "Data Emissão": data_emissao,
            "Devolvida": "Não",
            "Data Devolução": "",
            "Recebedor": "",
            "TST Resp. Liberação em área": "",
            "Última Atualização": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.success(f"✅ PT/PTT {numeracao} emitida com sucesso!")
        st.rerun()

# Tabela com lista de PTs
st.subheader("Lista de PTs Emitidas")

if not df.empty:
    st.dataframe(df[[
        "Numeração", "Tipo", "Setor", "Solicitante",
        "Descrição do Serviço", "Data Emissão", "Status",
        "Data Devolução", "Recebedor", "TST Resp. Liberação em área"
    ]])

# Devolução de PT/PTT
st.subheader("Devolver PT/PTT")

pts_pendentes = df[df["Devolvida"].astype(str).str.strip().str.lower() == "não"]["Numeração"]

if not pts_pendentes.empty:
    num_devolver = st.selectbox("Selecione a PT/PTT para devolver", pts_pendentes)
    recebedor = st.text_input("Quem recebeu a PT?")
    data_devolucao = st.text_input("Data da Devolução (AAAA-MM-DD)", value=datetime.today().strftime('%Y-%m-%d'))
    tst_resp = st.text_input("TST Resp. Liberação em área")

    if st.button("Confirmar Devolução") and recebedor and data_devolucao and tst_resp:
        df.loc[df["Numeração"] == num_devolver, [
            "Devolvida", "Data Devolução", "Recebedor", "TST Resp. Liberação em área"
        ]] = ["Sim", data_devolucao, recebedor, tst_resp]
        df.to_csv(DATA_FILE, index=False)
        st.success(f"✅ PT/PTT {num_devolver} devolvida com sucesso!")
        st.rerun()
else:
    st.info("Nenhuma PT/PTT pendente para devolução.")

# Exportar
st.subheader("Exportar Histórico de PTs")
st.download_button(
    "📁 Baixar Histórico",
    df.to_csv(index=False).encode("utf-8"),
    "historico_pts.csv",
    "text/csv"
)


