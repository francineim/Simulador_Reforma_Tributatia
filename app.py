import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Entenda com quem entende!", layout="wide")

# ==============================
# TÍTULO E DISCLAIMER
# ==============================
st.title("📘 Entenda com quem entende!")
st.markdown("""
**Disclaimer:** O objetivo da ferramenta é promover uma discussão sobre a reforma tributária, procurar entender os impactos nas empresas, fazer a simulação de cenários e entender como a reforma vai alterar o ambiente de negócios. Orientamos que envolva o seu departamento jurídico e fiscal/tributário nas discussões relacionadas ao tema, lembrando que trata-se de um assunto multidisciplinar, e outras áreas devem ser envolvidas como contabilidade, finanças, comercial e alta gestão.
""")

# ==============================
# INFORMAÇÃO GERAL
# ==============================
st.subheader("ℹ️ Informações Gerais")
st.markdown("A **Lei Complementar nº 214, de 16 de janeiro de 2025**, regulamentou a reforma tributária.")

# ==============================
# BASE LEGAL (leitura do texto completo)
# ==============================
with st.expander("📚 Leia sobre a Base de Cálculo do IBS/CBS e do Imposto Seletivo (IS)"):
    try:
        with open("base_calculo_completa.txt", "r", encoding="utf-8") as f:
            st.markdown(f.read())
    except FileNotFoundError:
        st.warning("Arquivo 'base_calculo_completa.txt' não encontrado. Por favor, inclua-o no repositório.")

# ==============================
# UPLOAD DA PLANILHA
# ==============================
st.subheader("📂 Carregue sua Planilha de Cálculo (opcional)")
uploaded_file = st.file_uploader("Envie um arquivo Excel com os dados da importação:", type=["xlsx"])

if uploaded_file:
    df_planilha = pd.read_excel(uploaded_file)
    st.success("Planilha carregada com sucesso!")
    st.dataframe(df_planilha)

# ==============================
# SIMULADOR
# ==============================
st.subheader("🧮 Simulador Reforma Tributária")
st.markdown("### Alíquotas dos Impostos e Contribuições")

col1, col2, col3 = st.columns(3)

with col1:
    ii = st.number_input("Imposto de Importação (%)", min_value=0.0, max_value=100.0, step=0.01)
    pis = st.number_input("PIS Nacionalização (%)", min_value=0.0, max_value=100.0, step=0.01)
    cofins = st.number_input("COFINS Nacionalização (%)", min_value=0.0, max_value=100.0, step=0.01)

with col2:
    ibs = st.number_input("IBS (%)", min_value=0.0, max_value=100.0, step=0.01)
    cbs = st.number_input("CBS (%)", min_value=0.0, max_value=100.0, step=0.01)
    icms = st.number_input("ICMS (%)", min_value=0.0, max_value=100.0, step=0.01)

with col3:
    ipi = st.number_input("IPI (%)", min_value=0.0, max_value=100.0, step=0.01)
    isel = st.number_input("Imposto Seletivo (IS) (%)", min_value=0.0, max_value=100.0, step=0.01)

# ==============================
# DADOS DE ENTRADA PARA CÁLCULO
# ==============================
st.markdown("### Dados da Operação de Importação")
valor_fob = st.number_input("Valor FOB da mercadoria (em R$)", min_value=0.0, step=0.01)
frete = st.number_input("Valor do frete internacional (em R$)", min_value=0.0, step=0.01)
seguro = st.number_input("Valor do seguro internacional (em R$)", min_value=0.0, step=0.01)
outros = st.number_input("Outros custos aduaneiros (AFRMM, Cide, etc) (em R$)", min_value=0.0, step=0.01)

if st.button("Calcular Tributos"):
    valor_aduaneiro = valor_fob + frete + seguro + outros

    # Pós-reforma
    valor_ii = valor_aduaneiro * (ii / 100)
    valor_pis = valor_aduaneiro * (pis / 100)
    valor_cofins = valor_aduaneiro * (cofins / 100)
    valor_ipi = valor_aduaneiro * (ipi / 100)
    valor_is = valor_aduaneiro * (isel / 100)
    valor_ibs = valor_aduaneiro * (ibs / 100)
    valor_cbs = valor_aduaneiro * (cbs / 100)
    valor_icms = valor_aduaneiro * (icms / 100)

    total_tributos = valor_ii + valor_pis + valor_cofins + valor_ipi + valor_is + valor_ibs + valor_cbs + valor_icms
    custo_total_importacao = valor_aduaneiro + total_tributos

    # Pré-reforma
    valor_ii_old = valor_aduaneiro * (ii / 100)
    valor_pis_old = valor_aduaneiro * (pis / 100)
    valor_cofins_old = valor_aduaneiro * (cofins / 100)
    valor_ipi_old = valor_aduaneiro * (ipi / 100)
    valor_icms_old = valor_aduaneiro * (icms / 100)

    st.success("Cálculo concluído com sucesso!")
    st.markdown(f"**Valor Aduaneiro:** R$ {valor_aduaneiro:,.2f}")
    st.markdown(f"**Custo Total da Importação (com tributos):** R$ {custo_total_importacao:,.2f}")

    st.markdown("### 📊 Tributação Reforma Tributária vs Situação Atual")

    comparativo = pd.DataFrame({
        "Tributo": ["II", "PIS", "COFINS", "IPI", "IS", "IBS", "CBS", "ICMS"],
        "Valor Após Reforma (R$)": [valor_ii, valor_pis, valor_cofins, valor_ipi, valor_is, valor_ibs, valor_cbs, valor_icms],
        "Valor Antes da Reforma (R$)": [valor_ii_old, valor_pis_old, valor_cofins_old, valor_ipi_old, 0.0, 0.0, 0.0, valor_icms_old]
    })

    styled_df = comparativo.style.format("R$ {:,.2f}").set_table_styles([
        {"selector": "th", "props": [("background-color", "#f0f2f6"), ("font-weight", "bold")]},
        {"selector": "td", "props": [("text-align", "right")]},
        {"selector": "tr:nth-child(even)", "props": [("background-color", "#fafafa")]}
    ])

    st.dataframe(styled_df, use_container_width=True)

    # Exportar resultado para Excel
    try:
        import xlsxwriter
        resultado = comparativo.copy()
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            resultado.to_excel(writer, index=False, sheet_name='Comparativo')
            worksheet = writer.sheets['Comparativo']
            worksheet.write('E1', f"Valor Aduaneiro: R$ {valor_aduaneiro:,.2f}")
            worksheet.write('E2', f"Total Tributos Pós-Reforma: R$ {total_tributos:,.2f}")
            worksheet.write('E3', f"Custo Total Importação: R$ {custo_total_importacao:,.2f}")
        st.download_button("📥 Baixar Comparativo em Excel", data=output.getvalue(), file_name="comparativo_tributario.xlsx")
    except ModuleNotFoundError:
        st.error("Erro: a biblioteca 'xlsxwriter' não está instalada. Verifique se 'xlsxwriter' está no seu requirements.txt.")
