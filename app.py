import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime
from io import BytesIO
import altair as alt
from fpdf import FPDF
import base64

# ===================== Configuração da Página =====================
st.set_page_config(page_title="Entendendo a Reforma Tributária", layout="wide")

# ===================== Cabeçalho =====================
st.title("📊 Entendendo a Reforma Tributária")
st.markdown("""
**Disclaimer:**  
O objetivo da ferramenta é promover uma discussão sobre a reforma tributária, entender os impactos nas empresas e simular cenários.  
Recomenda-se envolver **jurídico, fiscal, contabilidade, finanças e gestão** nas análises.
""")
st.divider()

# ===================== Informações Gerais =====================
st.subheader("📚 Informações Gerais")
st.markdown("""
A **Reforma Tributária do Consumo** está alterando profundamente a estrutura de tributos indiretos no Brasil, 
substituindo tributos como **PIS, Cofins, ICMS e ISS** por novos tributos de caráter mais uniforme: **IBS, CBS e IS**.

**Marcos regulatórios importantes:**
- **Portaria RFB nº 549/2025** – Institui o Piloto da Reforma Tributária do Consumo referente à CBS.  
- **Lei Complementar nº 214/2025** – Cria o Imposto sobre Bens e Serviços (IBS), CBS e Imposto Seletivo (IS).  
- **Projeto de Lei Complementar nº 108/2024** – Normas para o Comitê Gestor do IBS.  
- **Emenda Constitucional nº 132/2023** – Reforma Tributária do Consumo.

A partir de 2027, o IPI terá **alíquota reduzida a zero**, com exceção dos produtos da Zona Franca de Manaus.
""")

with st.expander("🔎 Leia sobre a Base de Cálculo do IBS/CBS e do Imposto Seletivo (IS)"):
    st.markdown("""
    **Base de cálculo IBS/CBS:**  
    Valor Aduaneiro + II + IS + Outros Custos Aduaneiros.

    **Base de cálculo ICMS:**  
    \[
    ICMS = \frac{(VA + II + IS + IBS + CBS + Outros)}{(1 - Alíquota ICMS)}
    \]

    **Base de cálculo PIS/COFINS:**  
    (Valor Total do Item - ICMS) x Alíquota PIS/COFINS.
    """)

st.divider()

# ===================== O que muda =====================
st.subheader("🔄 O que muda")
st.markdown("""
#### **Tributos que passarão a existir:**
- **CBS**: Contribuição sobre Bens e Serviços (Federal)
- **IBS**: Imposto sobre Bens e Serviços (Estadual e Municipal)
- **IS**: Imposto Seletivo (Federal)

#### **Tributos que deixarão de existir:**
- **PIS/PASEP**, **Cofins**, **ICMS**, **ISSQN**

#### **Imposto Seletivo (IS):**
- Criado para desestimular consumo de bens/serviços nocivos à saúde ou ao meio ambiente.
- Incide sobre produção, comercialização ou importação de itens definidos por lei.

#### **IPI:**
- A partir de 2027, alíquota reduzida a zero (exceto para Zona Franca de Manaus).
""")
st.divider()

# ===================== Variáveis globais =====================
comparativo_simulacao = None
df_resumo_xml = None
df_xml = None

# ===================== Abas =====================
aba_simulacao, aba_xml, aba_export = st.tabs(["🧮 Simulação Reforma Tributária", "📂 Importar XML de NF-e", "📥 Exportações"])

# ===================== Aba 1: Simulação =====================
with aba_simulacao:
    st.subheader("🧮 Simulador de Importação")
    st.markdown("Preencha as **alíquotas de tributos** e **valores da operação** para calcular o impacto antes e depois da reforma.")

    col1, col2, col3 = st.columns(3)
    with col1:
        ii = st.number_input("Imposto de Importação (%)", min_value=0.0, max_value=100.0, step=0.01, key="ii_sim")
        pis = st.number_input("PIS Nacionalização (%)", min_value=0.0, max_value=100.0, step=0.01, key="pis_sim")
        cofins = st.number_input("COFINS Nacionalização (%)", min_value=0.0, max_value=100.0, step=0.01, key="cofins_sim")
    with col2:
        ibs = st.number_input("IBS (%)", min_value=0.0, max_value=100.0, step=0.01, key="ibs_sim")
        cbs = st.number_input("CBS (%)", min_value=0.0, max_value=100.0, step=0.01, key="cbs_sim")
        icms = st.number_input("ICMS (%)", min_value=0.0, max_value=100.0, step=0.01, key="icms_sim")
    with col3:
        ipi = st.number_input("IPI (%)", min_value=0.0, max_value=100.0, step=0.01, key="ipi_sim")
        isel = st.number_input("Imposto Seletivo (IS) (%)", min_value=0.0, max_value=100.0, step=0.01, key="isel_sim")

    st.markdown("### **Valores da Operação de Importação**")
    valor_fob = st.number_input("Valor FOB da mercadoria (R$)", min_value=0.0, step=0.01, key="fob_sim")
    frete = st.number_input("Valor do frete internacional (R$)", min_value=0.0, step=0.01, key="frete_sim")
    seguro = st.number_input("Valor do seguro internacional (R$)", min_value=0.0, step=0.01, key="seguro_sim")
    outros = st.number_input("Outros custos aduaneiros (AFRMM, Cide, etc) (R$)", min_value=0.0, step=0.01, key="outros_sim")

    if st.button("Calcular Tributos", key="btn_simulacao"):
        valor_aduaneiro = valor_fob + frete + seguro + outros
        valor_ii = valor_aduaneiro * (ii / 100)
        valor_is = valor_aduaneiro * (isel / 100)

        base_ibs_cbs = valor_aduaneiro + valor_ii + valor_is + outros
        valor_ibs = base_ibs_cbs * (ibs / 100)
        valor_cbs = base_ibs_cbs * (cbs / 100)
        valor_ipi = valor_aduaneiro * (ipi / 100)

        base_icms = (valor_aduaneiro + valor_ii + valor_is + valor_ibs + valor_cbs + outros) / (1 - icms / 100)
        valor_icms = base_icms * (icms / 100)

        valor_pis = valor_aduaneiro * (pis / 100)
        valor_cofins = valor_aduaneiro * (cofins / 100)

        comparativo_simulacao = pd.DataFrame({
            "Tributo": ["II", "PIS", "COFINS", "IPI", "IS", "IBS", "CBS", "ICMS"],
            "Valor Após Reforma (R$)": [valor_ii, valor_pis, valor_cofins, valor_ipi, valor_is, valor_ibs, valor_cbs, valor_icms],
            "Valor Antes da Reforma (R$)": [valor_ii, valor_pis, valor_cofins, valor_ipi, 0.0, 0.0, 0.0, valor_aduaneiro * (icms / 100)]
        })
        comparativo_simulacao.loc[len(comparativo_simulacao)] = [
            "TOTAL",
            comparativo_simulacao["Valor Após Reforma (R$)"].sum(),
            comparativo_simulacao["Valor Antes da Reforma (R$)"].sum()
        ]

        st.success(f"**Valor Aduaneiro:** R$ {valor_aduaneiro:,.2f}")
        st.info(f"**Custo Total da Importação (com tributos):** R$ {valor_aduaneiro + valor_ii + valor_pis + valor_cofins + valor_ipi + valor_icms:,.2f}")
        st.markdown("### **Comparativo: Reforma vs Situação Atual**")
        st.dataframe(comparativo_simulacao.style.format("R$ {:,.2f}"), use_container_width=True)

        # Gráficos
        tributos_grafico = comparativo_simulacao[comparativo_simulacao["Tributo"] != "TOTAL"].melt("Tributo", var_name="Cenário", value_name="Valor")
        st.markdown("### **Gráficos de Comparativo (Antes x Depois)**")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("**Distribuição em Barras**")
            bar_chart = alt.Chart(tributos_grafico).mark_bar().encode(x="Tributo:N", y="Valor:Q", color="Cenário:N")
            st.altair_chart(bar_chart, use_container_width=True)
        with col_g2:
            st.markdown("**Distribuição em Pizza (Após Reforma)**")
            pie_chart = alt.Chart(comparativo_simulacao[comparativo_simulacao["Tributo"] != "TOTAL"]).mark_arc(innerRadius=50).encode(
                theta="Valor Após Reforma (R$):Q",
                color="Tributo:N"
            )
            st.altair_chart(pie_chart, use_container_width=True)

# ===================== Aba 2: Importação de XML =====================
with aba_xml:
    st.subheader("📂 Importar XML de NF-e")
    st.markdown("Preencha as alíquotas para recalcular os tributos com base nos dados do XML.")

    colx1, colx2, colx3 = st.columns(3)
    with colx1:
        ipi_xml = st.number_input("IPI (%)", min_value=0.0, max_value=100.0, step=0.01, key="ipi_xml")
        pis_xml = st.number_input("PIS (%)", min_value=0.0, max_value=100.0, step=0.01, key="pis_xml")
    with colx2:
        cofins_xml = st.number_input("COFINS (%)", min_value=0.0, max_value=100.0, step=0.01, key="cofins_xml")
        icms_xml = st.number_input("ICMS (%)", min_value=0.0, max_value=100.0, step=0.01, key="icms_xml")
    with colx3:
        isel_xml = st.number_input("IS (%)", min_value=0.0, max_value=100.0, step=0.01, key="isel_xml")

    uploaded_xmls = st.file_uploader("Envie um ou mais arquivos XML de NF-e:", type=["xml"], accept_multiple_files=True, key="xml_uploader")
    data_xml = []

    for uploaded_file in uploaded_xmls:
        tree = ET.parse(uploaded_file)
        root = tree.getroot()
        ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}

        for det in root.findall('.//nfe:det', ns):
            prod = det.find('nfe:prod', ns)
            vProd = float(prod.find('nfe:vProd', ns).text)

            valor_ii_item = vProd * (ii / 100)
            valor_is_item = vProd * (isel_xml / 100)
            base_ibs_cbs_item = vProd + valor_ii_item + valor_is_item
            valor_ibs_item = base_ibs_cbs_item * (ibs / 100)
            valor_cbs_item = base_ibs_cbs_item * (cbs / 100)
            base_icms_item = (vProd + valor_ii_item + valor_is_item + valor_ibs_item + valor_cbs_item) / (1 - icms_xml / 100)
            valor_icms_item = base_icms_item * (icms_xml / 100)

            base_pis_cofins_item = (vProd + vProd * (ipi_xml / 100)) - valor_icms_item
            valor_pis_item = base_pis_cofins_item * (pis_xml / 100)
            valor_cofins_item = base_pis_cofins_item * (cofins_xml / 100)

            valor_icms_old_item = vProd * (icms_xml / 100)
            valor_pis_old_item = vProd * (pis_xml / 100)
            valor_cofins_old_item = vProd * (cofins_xml / 100)
            valor_ipi_item = vProd * (ipi_xml / 100)
            valor_total_item = vProd + valor_ipi_item

            data_xml.append({
                'Valor do Produto': round(vProd, 2),
                'Valor II': round(valor_ii_item, 2),
                'Valor IS': round(valor_is_item, 2),
                'Valor IBS': round(valor_ibs_item, 2),
                'Valor CBS': round(valor_cbs_item, 2),
                'Valor ICMS (Após Reforma)': round(valor_icms_item, 2),
                'Valor ICMS (Antes Reforma)': round(valor_icms_old_item, 2),
                'Valor PIS (Após Reforma)': round(valor_pis_item, 2),
                'Valor PIS (Antes Reforma)': round(valor_pis_old_item, 2),
                'Valor COFINS (Após Reforma)': round(valor_cofins_item, 2),
                'Valor COFINS (Antes Reforma)': round(valor_cofins_old_item, 2),
                'Valor IPI': round(valor_ipi_item, 2),
                'Valor Total do Item': round(valor_total_item, 2)
            })

    if data_xml:
        df_xml = pd.DataFrame(data_xml)
        st.dataframe(df_xml, use_container_width=True)

        df_resumo_xml = pd.DataFrame({
            "Tributo": ["II", "PIS", "COFINS", "IPI", "IS", "IBS", "CBS", "ICMS"],
            "Valor Após Reforma (R$)": [
                df_xml["Valor II"].sum(),
                df_xml["Valor PIS (Após Reforma)"].sum(),
                df_xml["Valor COFINS (Após Reforma)"].sum(),
                df_xml["Valor IPI"].sum(),
                df_xml["Valor IS"].sum(),
                df_xml["Valor IBS"].sum(),
                df_xml["Valor CBS"].sum(),
                df_xml["Valor ICMS (Após Reforma)"].sum()
            ],
            "Valor Antes da Reforma (R$)": [
                df_xml["Valor II"].sum(),
                df_xml["Valor PIS (Antes Reforma)"].sum(),
                df_xml["Valor COFINS (Antes Reforma)"].sum(),
                df_xml["Valor IPI"].sum(),
                0.0,
                0.0,
                0.0,
                df_xml["Valor ICMS (Antes Reforma)"].sum()
            ]
        })
        df_resumo_xml.loc[len(df_resumo_xml)] = [
            "TOTAL",
            df_resumo_xml["Valor Após Reforma (R$)"].sum(),
            df_resumo_xml["Valor Antes da Reforma (R$)"].sum()
        ]

        st.markdown("### **Comparativo XML: Reforma vs Situação Atual**")
        st.dataframe(df_resumo_xml.style.format("R$ {:,.2f}"), use_container_width=True)

        tributos_grafico_xml = df_resumo_xml[df_resumo_xml["Tributo"] != "TOTAL"].melt("Tributo", var_name="Cenário", value_name="Valor")
        st.markdown("### **Gráficos XML (Antes x Depois)**")
        col_x1, col_x2 = st.columns(2)
        with col_x1:
            st.markdown("**Distribuição em Barras**")
            bar_chart_xml = alt.Chart(tributos_grafico_xml).mark_bar().encode(
                x="Tributo:N",
                y="Valor:Q",
                color="Cenário:N",
                tooltip=["Tributo", "Cenário", "Valor"]
            )
            st.altair_chart(bar_chart_xml, use_container_width=True)
        with col_x2:
            st.markdown("**Distribuição em Pizza (Após Reforma)**")
            pie_chart_xml = alt.Chart(df_resumo_xml[df_resumo_xml["Tributo"] != "TOTAL"]).mark_arc(innerRadius=50).encode(
                theta="Valor Após Reforma (R$):Q",
                color="Tributo:N",
                tooltip=["Tributo", "Valor Após Reforma (R$)"]
            )
            st.altair_chart(pie_chart_xml, use_container_width=True)

# ===================== Aba 3: Exportações =====================
with aba_export:
    st.subheader("📥 Exportação de Resultados")
    st.markdown("Baixe os comparativos em **Excel** ou **PDF**.")
    if st.button("Baixar Excel Consolidado", key="btn_excel"):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            if comparativo_simulacao is not None:
                comparativo_simulacao.to_excel(writer, sheet_name="Simulação", index=False)
            if df_xml is not None:
                df_xml.to_excel(writer, sheet_name="XML Detalhes", index=False)
            if df_resumo_xml is not None:
                df_resumo_xml.to_excel(writer, sheet_name="Resumo XML", index=False)
        st.download_button(
            label="Clique para baixar Excel",
            data=output.getvalue(),
            file_name="relatorio_tributos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    if st.button("Baixar PDF Consolidado", key="btn_pdf"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(200, 10, txt="Relatório Comparativo de Tributos", ln=True, align="C")

        if comparativo_simulacao is not None:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(200, 10, txt="Simulação Manual", ln=True)
            pdf.set_font("Arial", "", 10)
            for _, row in comparativo_simulacao.iterrows():
                pdf.cell(0, 10, txt=f"{row['Tributo']}: Após R$ {row['Valor Após Reforma (R$)']:.2f} | Antes R$ {row['Valor Antes da Reforma (R$)']:.2f}", ln=True)

        if df_resumo_xml is not None:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(200, 10, txt="Resumo XML", ln=True)
            pdf.set_font("Arial", "", 10)
            for _, row in df_resumo_xml.iterrows():
                pdf.cell(0, 10, txt=f"{row['Tributo']}: Após R$ {row['Valor Após Reforma (R$)']:.2f} | Antes R$ {row['Valor Antes da Reforma (R$)']:.2f}", ln=True)

        pdf_output = BytesIO()
        pdf.output(pdf_output)
        pdf_output.seek(0)

        b64_pdf = base64.b64encode(pdf_output.read()).decode('utf-8')
        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="relatorio_tributos.pdf">Clique aqui para baixar PDF</a>'
        st.markdown(href, unsafe_allow_html=True)
