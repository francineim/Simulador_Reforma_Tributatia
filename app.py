import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime
from io import BytesIO
import altair as alt

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
with st.expander("📚 Informações Gerais"):
    st.markdown("""
    **Marcos regulatórios da Reforma Tributária do Consumo:**

    - **Portaria RFB nº 549, de 13/06/2025** – Institui o Piloto da Reforma Tributária do Consumo referente à Contribuição sobre Bens e Serviços (CBS).  
    - **Lei Complementar nº 214, de 16/01/2025** – Cria o Imposto sobre Bens e Serviços (IBS), CBS e Imposto Seletivo (IS).  
    - **Portaria RFB nº 501, de 20/12/2024** – Programa de Reforma Tributária do Consumo (RTC).  
    - **Projeto de Lei Complementar nº 108, de 2024 (em tramitação)** – Normas para o Comitê Gestor do IBS.  
    - **Emenda Constitucional nº 132, de 20/12/2023** – Reforma Tributária do Consumo.
    """)

with st.expander("🔎 Leia sobre a Base de Cálculo do IBS/CBS e do Imposto Seletivo (IS)"):
    try:
        with open("base_calculo_completa.txt", "r", encoding="utf-8") as f:
            st.markdown(f.read())
    except FileNotFoundError:
        st.warning("Arquivo 'base_calculo_completa.txt' não encontrado. Inclua-o no repositório.")
st.divider()

# ===================== Abas =====================
aba_simulacao, aba_xml = st.tabs(["🧮 Simulação Reforma Tributária", "📂 Importar XML de NF-e"])

# ===================== Aba 1: Simulação =====================
with aba_simulacao:
    st.subheader("Simulação de Importação")
    st.markdown("### **Alíquotas dos Impostos e Contribuições**")

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

    st.markdown("### **Dados da Operação de Importação**")
    valor_fob = st.number_input("Valor FOB da mercadoria (R$)", min_value=0.0, step=0.01)
    frete = st.number_input("Valor do frete internacional (R$)", min_value=0.0, step=0.01)
    seguro = st.number_input("Valor do seguro internacional (R$)", min_value=0.0, step=0.01)
    outros = st.number_input("Outros custos aduaneiros (AFRMM, Cide, etc) (R$)", min_value=0.0, step=0.01)

    if st.button("Calcular Tributos", key="btn_simulacao"):
        valor_aduaneiro = valor_fob + frete + seguro + outros
        valor_ii = valor_aduaneiro * (ii / 100)
        valor_is = valor_aduaneiro * (isel / 100)

        # NOVAS BASES
        base_ibs_cbs = valor_aduaneiro + valor_ii + valor_is + outros
        valor_ibs = base_ibs_cbs * (ibs / 100)
        valor_cbs = base_ibs_cbs * (cbs / 100)
        valor_ipi = valor_aduaneiro * (ipi / 100)

        base_icms = (valor_aduaneiro + valor_ii + valor_is + valor_ibs + valor_cbs + outros) / (1 - icms / 100)
        valor_icms = base_icms * (icms / 100)

        valor_pis = valor_aduaneiro * (pis / 100)
        valor_cofins = valor_aduaneiro * (cofins / 100)

        total_tributos = valor_ii + valor_pis + valor_cofins + valor_ipi + valor_icms
        custo_total_importacao = valor_aduaneiro + total_tributos

        st.success(f"**Valor Aduaneiro:** R$ {valor_aduaneiro:,.2f}")
        st.info(f"**Custo Total da Importação (com tributos):** R$ {custo_total_importacao:,.2f}")

        st.markdown("### **Comparativo: Reforma Tributária vs Situação Atual**")
        comparativo = pd.DataFrame({
            "Tributo": ["II", "PIS", "COFINS", "IPI", "IS", "IBS", "CBS", "ICMS"],
            "Valor Após Reforma (R$)": [valor_ii, valor_pis, valor_cofins, valor_ipi, valor_is, valor_ibs, valor_cbs, valor_icms],
            "Valor Antes da Reforma (R$)": [valor_ii, valor_pis, valor_cofins, valor_ipi, 0.0, 0.0, 0.0, valor_aduaneiro * (icms / 100)]
        })
        comparativo.loc[len(comparativo)] = ["TOTAL",
                                             comparativo["Valor Após Reforma (R$)"].sum(),
                                             comparativo["Valor Antes da Reforma (R$)"].sum()]

        st.dataframe(comparativo.style.format({
            "Valor Após Reforma (R$)": "R$ {:,.2f}",
            "Valor Antes da Reforma (R$)": "R$ {:,.2f}"
        }), use_container_width=True)

# ===================== Aba 2: Importação de XML =====================
with aba_xml:
    st.subheader("Importar XML de NF-e")
    uploaded_xmls = st.file_uploader("Envie um ou mais arquivos XML de NF-e:", type=["xml"], accept_multiple_files=True)

    data_xml = []
    for uploaded_file in uploaded_xmls:
        tree = ET.parse(uploaded_file)
        root = tree.getroot()
        ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}

        for det in root.findall('.//nfe:det', ns):
            ide = root.find('.//nfe:ide', ns)
            emit = root.find('.//nfe:emit', ns)
            prod = det.find('nfe:prod', ns)
            imposto = det.find('nfe:imposto', ns)

            nNF = ide.find('nfe:nNF', ns).text
            dhEmi = ide.find('nfe:dhEmi', ns).text
            dhEmi_formatada = datetime.strptime(dhEmi[:19], "%Y-%m-%dT%H:%M:%S").strftime("%d/%m/%Y")
            xNome = emit.find('nfe:xNome', ns).text
            UF = emit.find('nfe:enderEmit/nfe:UF', ns).text
            CNPJ = emit.find('nfe:CNPJ', ns).text

            cProd = prod.find('nfe:cProd', ns).text
            xProd = prod.find('nfe:xProd', ns).text
            NCM = prod.find('nfe:NCM', ns).text
            CFOP = prod.find('nfe:CFOP', ns).text
            uCom = prod.find('nfe:uCom', ns).text
            qCom = float(prod.find('nfe:qCom', ns).text)
            vUnCom = float(prod.find('nfe:vUnCom', ns).text)
            vProd = float(prod.find('nfe:vProd', ns).text)

            # Recalcular tributos
            valor_ii_item = vProd * (ii / 100)
            valor_is_item = vProd * (isel / 100)
            base_ibs_cbs_item = vProd + valor_ii_item + valor_is_item + outros
            valor_ibs_item = base_ibs_cbs_item * (ibs / 100)
            valor_cbs_item = base_ibs_cbs_item * (cbs / 100)
            base_icms_item = (vProd + valor_ii_item + valor_is_item + valor_ibs_item + valor_cbs_item + outros) / (1 - icms / 100)
            valor_icms_item = base_icms_item * (icms / 100)

            ipi = imposto.find('nfe:IPI/nfe:IPITrib', ns)
            vIPI = float(ipi.find('nfe:vIPI', ns).text) if ipi is not None and ipi.find('nfe:vIPI', ns) is not None else 0
            valor_total_item = vProd + vIPI

            data_xml.append({
                'Número NF-e': nNF,
                'Emissão': dhEmi_formatada,
                'Fornecedor': xNome,
                'UF': UF,
                'Filial (CNPJ)': CNPJ,
                'Código Produto': cProd,
                'Descrição do Produto': xProd,
                'NCM': NCM,
                'CFOP': CFOP,
                'Unidade': uCom,
                'Quantidade': qCom,
                'Valor Unitário': vUnCom,
                'Valor do Produto': round(vProd, 2),
                'Valor II': round(valor_ii_item, 2),
                'Valor IS': round(valor_is_item, 2),
                'Valor IBS': round(valor_ibs_item, 2),
                'Valor CBS': round(valor_cbs_item, 2),
                'Valor ICMS': round(valor_icms_item, 2),
                'Valor IPI': round(vIPI, 2),
                'Valor Total do Item': round(valor_total_item, 2)
            })

    if data_xml:
        df_xml = pd.DataFrame(data_xml)
        st.dataframe(df_xml, use_container_width=True)

        # Resumo dos totais
        resumo = pd.DataFrame([{
            "Total Valor Produtos": df_xml["Valor do Produto"].sum(),
            "Total II": df_xml["Valor II"].sum(),
            "Total IS": df_xml["Valor IS"].sum(),
            "Total IBS": df_xml["Valor IBS"].sum(),
            "Total CBS": df_xml["Valor CBS"].sum(),
            "Total ICMS": df_xml["Valor ICMS"].sum(),
            "Total IPI": df_xml["Valor IPI"].sum(),
            "Total Geral Itens": df_xml["Valor Total do Item"].sum()
        }])

        st.markdown("### **Resumo Consolidado dos Tributos (XML)**")
        st.dataframe(resumo.style.format("R$ {:,.2f}"), use_container_width=True)

        # ===================== GRÁFICOS =====================
        st.markdown("### **Gráficos de Distribuição de Tributos**")

        tributos_grafico = pd.DataFrame({
            "Tributo": ["II", "IS", "IBS", "CBS", "ICMS", "IPI"],
            "Valor": [
                resumo["Total II"].iloc[0],
                resumo["Total IS"].iloc[0],
                resumo["Total IBS"].iloc[0],
                resumo["Total CBS"].iloc[0],
                resumo["Total ICMS"].iloc[0],
                resumo["Total IPI"].iloc[0]
            ]
        })

        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("**Distribuição em Barras**")
            bar_chart = alt.Chart(tributos_grafico).mark_bar().encode(
                x=alt.X("Tributo", sort=None),
                y=alt.Y("Valor"),
                color="Tributo"
            )
            st.altair_chart(bar_chart, use_container_width=True)

        with col_g2:
            st.markdown("**Distribuição em Pizza**")
            pie_chart = alt.Chart(tributos_grafico).mark_arc(innerRadius=50).encode(
                theta="Valor",
                color="Tributo",
                tooltip=["Tributo", "Valor"]
            )
            st.altair_chart(pie_chart, use_container_width=True)

        # Download Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_xml.to_excel(writer, sheet_name='NF-e XML', index=False)
            resumo.to_excel(writer, sheet_name='Resumo Tributos', index=False)
        st.download_button("Baixar XML em Excel", data=output.getvalue(),
                           file_name="nfe_xml_extraido.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
