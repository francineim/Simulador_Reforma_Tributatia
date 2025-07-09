import streamlit as st
import pandas as pd
import io
from fpdf import FPDF

st.set_page_config(page_title="Entenda com quem entende!", layout="wide")

st.title("📘 Entenda com quem entende!")
st.markdown("""
**Disclaimer:** O objetivo da ferramenta é promover uma discussão sobre a reforma tributária, procurar entender os impactos nas empresas, fazer a simulação de cenários e entender como a reforma vai alterar o ambiente de negócios. Orientamos que envolva o seu departamento jurídico e fiscal/tributário nas discussões relacionadas ao tema, lembrando que trata-se de um assunto multidisciplinar, e outras áreas devem ser envolvidas como contabilidade, finanças, comercial e alta gestão.
""")

st.subheader("ℹ️ Informações Gerais")
st.markdown("A **Lei Complementar nº 214, de 16 de janeiro de 2025**, regulamentou a reforma tributária.")

with st.expander("📚 Leia sobre a Base de Cálculo do IBS/CBS e do Imposto Seletivo (IS)"):
    try:
        with open("base_calculo_completa.txt", "r", encoding="utf-8") as f:
            st.markdown(f.read())
    except FileNotFoundError:
        st.warning("Arquivo 'base_calculo_completa.txt' não encontrado. Por favor, inclua-o no repositório.")

st.subheader("📂 Carregue sua Planilha de Cálculo (opcional)")
uploaded_file = st.file_uploader("Envie um arquivo Excel com os dados da importação:", type=["xlsx"])
if uploaded_file:
    df_planilha = pd.read_excel(uploaded_file)
    st.success("Planilha carregada com sucesso!")
    st.dataframe(df_planilha)

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

st.markdown("### Dados da Operação de Importação")
valor_fob = st.number_input("Valor FOB da mercadoria (em R$)", min_value=0.0, step=0.01)
frete = st.number_input("Valor do frete internacional (em R$)", min_value=0.0, step=0.01)
seguro = st.number_input("Valor do seguro internacional (em R$)", min_value=0.0, step=0.01)
outros = st.number_input("Outros custos aduaneiros (AFRMM, Cide, etc) (em R$)", min_value=0.0, step=0.01)

if st.button("Calcular Tributos"):
    valor_aduaneiro = valor_fob + frete + seguro + outros

    valor_ii = valor_aduaneiro * (ii / 100)
    valor_pis = valor_aduaneiro * (pis / 100)
    valor_cofins = valor_aduaneiro * (cofins / 100)
    valor_ipi = valor_aduaneiro * (ipi / 100)
    valor_is = valor_aduaneiro * (isel / 100)
    valor_ibs = valor_aduaneiro * (ibs / 100)
    valor_cbs = valor_aduaneiro * (cbs / 100)
    valor_icms = valor_aduaneiro * (icms / 100)

    total_tributos = sum([valor_ii, valor_pis, valor_cofins, valor_ipi, valor_is, valor_ibs, valor_cbs, valor_icms])
    custo_total_importacao = valor_aduaneiro + total_tributos

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

    st.dataframe(comparativo.style.format({
        "Valor Após Reforma (R$)": "R$ {:,.2f}",
        "Valor Antes da Reforma (R$)": "R$ {:,.2f}"
    }), use_container_width=True)

    # Geração do PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Simulação Tributária - Reforma", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Valor Aduaneiro: R$ {valor_aduaneiro:,.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Custo Total da Importação: R$ {custo_total_importacao:,.2f}", ln=True)
    pdf.ln(5)

    for index, row in comparativo.iterrows():
        linha = f"{row['Tributo']}: Pós-Reforma: R$ {row['Valor Após Reforma (R$)']:.2f} | Antes: R$ {row['Valor Antes da Reforma (R$)']:.2f}"
        pdf.cell(200, 10, txt=linha, ln=True)

    # Exportar PDF corretamente
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    st.download_button("📄 Baixar Relatório em PDF", data=pdf_bytes, file_name="simulacao_tributaria.pdf")
