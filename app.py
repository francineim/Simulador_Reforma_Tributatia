import streamlit as st
import pandas as pd
import io
import xml.etree.ElementTree as ET
from fpdf import FPDF
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="Entendendo a Reforma Tributária", layout="wide")

st.title("Entendendo a Reforma Tributária")
st.markdown("""
**Disclaimer:** O objetivo da ferramenta é promover uma discussão sobre a reforma tributária, procurar entender os impactos nas empresas, fazer a simulação de cenários e entender como a reforma vai alterar o ambiente de negócios. Orientamos que envolva o seu departamento jurídico e fiscal/tributário nas discussões relacionadas ao tema, lembrando que trata-se de um assunto multidisciplinar, e outras áreas devem ser envolvidas como contabilidade, finanças, comercial e alta gestão.
""")

st.subheader("Informações Gerais")
st.markdown("""
Acompanhe pelos links abaixo os principais marcos regulatórios da Reforma Tributária do Consumo.

**Portaria RFB nº 549, de 13 de junho de 2025**  
Institui o Piloto da Reforma Tributária do Consumo referente à Contribuição sobre Bens e Serviços - Piloto RTC - CBS.

**Lei Complementar nº 214, de 16 de janeiro de 2025**  
Institui o Imposto sobre Bens e Serviços (IBS), a Contribuição Social sobre Bens e Serviços (CBS) e o Imposto Seletivo (IS); cria o Comitê Gestor do IBS e altera a legislação tributária.

**Portaria RFB nº 501, de 20 de dezembro de 2024**  
Institui o Programa de Reforma Tributária do Consumo - Programa RTC para implantação da reforma tributária de que trata a Emenda Constitucional nº 132, de 20 de dezembro de 2023.

**Projeto de Lei Complementar n°108, de 2024 (em tramitação)**  
O projeto propõe criar o Comitê Gestor do Imposto sobre Bens e Serviços (CG-IBS) e estabelece normas gerenciar e administrar esse novo imposto.

**Emenda Constitucional nº 132, de 20 de dezembro de 2023**  
Altera o Sistema Tributário Nacional e ficou conhecido como Reforma Tributária do Consumo.
""")

with st.expander("Leia sobre a Base de Cálculo do IBS/CBS e do Imposto Seletivo (IS)"):
    try:
        with open("base_calculo_completa.txt", "r", encoding="utf-8") as f:
            st.markdown(f.read())
    except FileNotFoundError:
        st.warning("Arquivo 'base_calculo_completa.txt' não encontrado. Por favor, inclua-o no repositório.")

st.subheader("O que muda")
st.markdown("""
#### Tributos que passarão a existir:
- **CBS**: Contribuição sobre Bens e Serviços (Federal)
- **IBS**: Imposto sobre Bens e Serviços (Estadual e Municipal)
- **IS**: Imposto Seletivo (Federal)

#### Tributos que deixarão de existir:
- **PIS/PASEP**: Contribuição para o Programa de Integração Social e Programa de Formação do Patrimônio do Servidor Público (Federal)
- **Cofins**: Contribuição para Financiamento da Seguridade Social (Federal)
- **ICMS**: Imposto sobre Circulação de Mercadorias e Serviços (Estadual)
- **ISSQN**: Imposto sobre Serviços de Qualquer Natureza (Municipal)

#### Imposto Seletivo:
- Criado para desestimular o consumo de bens e serviços prejudiciais à saúde ou ao meio ambiente.
- Incide sobre produção, extração, comercialização ou importação de itens definidos por lei.
- A partir de 2027, entrará em vigor.

#### Imposto sobre Produtos Industrializados (IPI):
- A partir de 2027, terá alíquota reduzida a zero para quase todos os produtos.
- Será mantido apenas para preservar a competitividade da Zona Franca de Manaus.
""")

st.subheader("Simulador Reforma Tributária")
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

    st.markdown("### Comparativo: Reforma Tributária vs Situação Atual")

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

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    st.download_button("Baixar Relatório em PDF", data=pdf_bytes, file_name="simulacao_tributaria.pdf")
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

    st.subheader("Definir Alíquotas para Cálculo de Tributos")
    col1, col2, col3 = st.columns(3)
    with col1:
        aliq_ibs = st.number_input("Alíquota IBS para XML (%)", min_value=0.0, step=0.01)
    with col2:
        aliq_cbs = st.number_input("Alíquota CBS para XML (%)", min_value=0.0, step=0.01)
    with col3:
        aliq_is = st.number_input("Alíquota IS para XML (%)", min_value=0.0, step=0.01)

    df_xml['IBS'] = df_xml['Valor do Produto'] * (aliq_ibs / 100)
    df_xml['CBS'] = df_xml['Valor do Produto'] * (aliq_cbs / 100)
    df_xml['IS'] = df_xml['Valor do Produto'] * (aliq_is / 100)

    st.subheader("Informações Extraídas dos XMLs")
    st.dataframe(df_xml, use_container_width=True)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_xml.to_excel(writer, sheet_name='NF-e XML', index=False)
    st.download_button("Baixar XML em Excel", data=output.getvalue(), file_name="nfe_xml_extraido.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
