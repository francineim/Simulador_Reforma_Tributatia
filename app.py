import streamlit as st
import pandas as pd
import altair as alt
import xml.etree.ElementTree as ET
from fpdf import FPDF
from datetime import datetime
from io import BytesIO

# ==========================================
# Funções Auxiliares
# ==========================================
def calcular_tributos(valor_aduaneiro, ii, pis, cofins, ipi, isel, ibs, cbs, icms):
    """
    Calcula os tributos da operação e o custo total da importação,
    excluindo IS, IBS e CBS do custo_total_importacao.
    """
    valores = {
        "II": valor_aduaneiro * (ii / 100),
        "PIS": valor_aduaneiro * (pis / 100),
        "COFINS": valor_aduaneiro * (cofins / 100),
        "IPI": valor_aduaneiro * (ipi / 100),
        "IS": valor_aduaneiro * (isel / 100),
        "IBS": valor_aduaneiro * (ibs / 100),
        "CBS": valor_aduaneiro * (cbs / 100),
        "ICMS": valor_aduaneiro * (icms / 100),
    }
    total_tributos = valores["II"] + valores["PIS"] + valores["COFINS"] + valores["IPI"] + valores["ICMS"]
    custo_total_importacao = valor_aduaneiro + total_tributos
    return valores, custo_total_importacao

def criar_comparativo(valores, valores_old):
    """
    Cria dataframe comparativo entre situação atual e pós-reforma, com totalizador.
    """
    df = pd.DataFrame({
        "Tributo": ["II", "PIS", "COFINS", "IPI", "IS", "IBS", "CBS", "ICMS"],
        "Valor Após Reforma (R$)": [
            valores["II"], valores["PIS"], valores["COFINS"], valores["IPI"],
            valores["IS"], valores["IBS"], valores["CBS"], valores["ICMS"]
        ],
        "Valor Antes da Reforma (R$)": [
            valores_old["II"], valores_old["PIS"], valores_old["COFINS"], valores_old["IPI"],
            0.0, 0.0, 0.0, valores_old["ICMS"]
        ]
    })
    # Adiciona totalizador
    df.loc[len(df)] = [
        "TOTAL",
        df["Valor Após Reforma (R$)"].sum(),
        df["Valor Antes da Reforma (R$)"].sum()
    ]
    return df

def gerar_grafico_comparativo(df):
    """
    Gera gráfico de barras comparando os tributos antes e depois da reforma.
    """
    chart_data = df[df["Tributo"] != "TOTAL"]
    chart = alt.Chart(chart_data).transform_fold(
        ["Valor Antes da Reforma (R$)", "Valor Após Reforma (R$)"],
        as_=["Cenário", "Valor"]
    ).mark_bar().encode(
        x=alt.X("Tributo:N", title="Tributo"),
        y=alt.Y("Valor:Q", title="Valor (R$)"),
        color="Cenário:N"
    )
    return chart

# ==========================================
# Layout da Página
# ==========================================
st.set_page_config(page_title="Simulador Reforma Tributária", layout="wide")
st.title("💼 Simulador de Importação – Reforma Tributária")

tabs = st.tabs(["Simulação", "Importar XML de NF-e"])

# ==========================================
# Aba de Simulação
# ==========================================
with tabs[0]:
    st.subheader("Informe os Dados da Operação de Importação")

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
        valores, custo_total_importacao = calcular_tributos(valor_aduaneiro, ii, pis, cofins, ipi, isel, ibs, cbs, icms)

        # Antes da reforma (sem IS, IBS, CBS)
        valores_old = {
            "II": valores["II"],
            "PIS": valores["PIS"],
            "COFINS": valores["COFINS"],
            "IPI": valores["IPI"],
            "ICMS": valores["ICMS"]
        }

        df_comparativo = criar_comparativo(valores, valores_old)

        st.success(f"**Valor Aduaneiro:** R$ {valor_aduaneiro:,.2f}")
        st.info(f"**Custo Total da Importação (com tributos):** R$ {custo_total_importacao:,.2f}")

        st.markdown("### Comparativo: Reforma Tributária vs Situação Atual")
        st.dataframe(df_comparativo.style.format({
            "Valor Após Reforma (R$)": "R$ {:,.2f}",
            "Valor Antes da Reforma (R$)": "R$ {:,.2f}"
        }), use_container_width=True)

        st.markdown("### Gráfico Comparativo")
        st.altair_chart(gerar_grafico_comparativo(df_comparativo), use_container_width=True)

# ==========================================
# Aba de XML de NF-e
# ==========================================
with tabs[1]:
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

            icms = imposto.find('nfe:ICMS/*', ns)
            CST_ICMS = icms.find('nfe:CST', ns).text if icms.find('nfe:CST', ns) is not None else ''
            vBC_ICMS = float(icms.find('nfe:vBC', ns).text) if icms.find('nfe:vBC', ns) is not None else 0
            pICMS = float(icms.find('nfe:pICMS', ns).text) if icms.find('nfe:pICMS', ns) is not None else 0
            vICMS = float(icms.find('nfe:vICMS', ns).text) if icms.find('nfe:vICMS', ns) is not None else 0

            ipi = imposto.find('nfe:IPI/nfe:IPITrib', ns)
            CST_IPI = ipi.find('nfe:CST', ns).text if ipi is not None and ipi.find('nfe:CST', ns) is not None else ''
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
                'CST ICMS': CST_ICMS,
                'Base ICMS': round(vBC_ICMS, 2),
                'Alíquota ICMS': round(pICMS, 2),
                'Valor ICMS': round(vICMS, 2),
                'CST IPI': CST_IPI,
                'Valor IPI': round(vIPI, 2),
                'Valor Total do Item': valor_total_item
            })

    if data_xml:
        df_xml = pd.DataFrame(data_xml)
        st.dataframe(df_xml, use_container_width=True)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_xml.to_excel(writer, sheet_name='NF-e XML', index=False)
        st.download_button("Baixar XML em Excel", data=output.getvalue(),
                           file_name="nfe_xml_extraido.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
