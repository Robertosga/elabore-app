import streamlit as st
from fpdf import FPDF
from datetime import datetime
import os
from PIL import Image

# 1. FUNÇÃO DE FORMATAÇÃO (PRECISA ESTAR AQUI NO TOPO)
def formatar_br(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Configurações da Empresa
EMPRESA = {
    "nome": "ELABORE TOLDOS",
    "email": "elaboreag@hotmail.com",
    "whatsapp": "62 993301650",
    "instagram": "elaboretoldos",
    "cnpj": "21710043/0001-30"
}

SERVICOS_LISTA = [
    "Toldo Policarbonato", "Toldo Cortina", "Toldo Fixo Lona", "Cobertura Policarbonato",
    "Cobertura Lona", "Painel", "Fachada", "Estrutura", "Banner", "Adesivo", "Plotter",
    "Lona", "Troca de Lona", "Placa", "Mão de Obra", "Impressão", "Calha", "Forro Paraline",
    "Pintura", "Cavalete", "Cartão de visita", "Panfleto", "Luminoso", "Logotipo",
    "Identidade Visual", "Manutenção", "Troca de Mola", "Troca de Tubo", "Vetorização"
]

if 'servicos_adicionados' not in st.session_state:
    st.session_state.servicos_adicionados = [{"servico": SERVICOS_LISTA[0], "qtd": 1.0, "valor": 0.0}]

def gerar_pdf(dados, lista_servicos, tipo_documento):
    pdf = FPDF()
    pdf.add_page()
    
    # Logo
    if os.path.exists('logo.png'):
        try:
            # Abre a imagem original
            img = Image.open('logo.png')
            # Converte para RGB (remove transparências e entrelaçamento que travam o PDF)
            img_rgb = img.convert("RGB")
            # Salva uma versão temporária "limpa"
            img_rgb.save("logo_limpa.jpg", "JPEG")
            # Usa a versão limpa no PDF
            pdf.image("logo_limpa.jpg", 10, 8, 33)
        except Exception as e:
            st.error(f"Erro ao processar a logo: {e}")
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"{tipo_documento}: {EMPRESA['nome']}", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 5, f"CNPJ: {EMPRESA['cnpj']} | Email: {EMPRESA['email']}", ln=True, align='C')
    pdf.cell(0, 5, f"WhatsApp: {EMPRESA['whatsapp']} | Insta: @{EMPRESA['instagram']}", ln=True, align='C')
    pdf.ln(15)

    # Cliente
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "DADOS DO CLIENTE", ln=True, fill=True)
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 8, f"Cliente: {dados['cliente']}", ln=True)
    pdf.cell(0, 8, f"Telefone: {dados['tel']} | Endereco: {dados['end']}", ln=True)
    pdf.ln(5)

    # Tabela
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "DETALHES DOS SERVICOS", ln=True, fill=True)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(90, 8, "Servico", 1)
    pdf.cell(30, 8, "Qtd/m2", 1)
    pdf.cell(35, 8, "V. Unit", 1)
    pdf.cell(35, 8, "Subtotal", 1, ln=True)
    
    pdf.set_font("Arial", size=10)
    for s in lista_servicos:
        sub = s['qtd'] * s['valor']
        # Usando a formatação BR aqui
        pdf.cell(90, 8, s['servico'][:40], 1)
        pdf.cell(30, 8, f"{s['qtd']}", 1)
        pdf.cell(35, 8, f"R$ {formatar_br(s['valor'])}", 1)
        pdf.cell(35, 8, f"R$ {formatar_br(sub)}", 1, ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"TOTAL DOS SERVICOS: R$ {formatar_br(dados['total_geral'])}", ln=True, align='R')
    pdf.cell(0, 10, f"DESCONTO: R$ {formatar_br(dados['desconto'])}", ln=True, align='R')
    pdf.set_text_color(255, 0, 0) # Vermelho para o total final
    pdf.cell(0, 10, f"VALOR FINAL: R$ {formatar_br(dados['valor_final'])}", ln=True, align='R')
    pdf.set_text_color(0, 0, 0) # Volta para preto

    # Pagamento
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "CONDICOES DE PAGAMENTO", ln=True, fill=True)
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 8, f"Forma: {dados['pagamento']} | Entrada: R$ {formatar_br(dados['entrada'])}", ln=True)
    pdf.cell(0, 8, f"Restante: R$ {formatar_br(dados['restante'])} | Entrega: {dados['entrega']}", ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, f"Gerado em: {dados['data_hora']}", align='R')
    
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# --- INTERFACE ---
st.title("🚀 Elabore Toldos - Sistema de Vendas")

with st.expander("👤 Dados do Cliente", expanded=True):
    c1, c2 = st.columns(2)
    nome_c = c1.text_input("Nome do Cliente")
    tel_c = c2.text_input("Telefone")
    end_c = st.text_input("Endereço Completo")

st.write("### 🛠 Serviços")

for i, item in enumerate(st.session_state.servicos_adicionados):
    cols = st.columns([3, 1, 1, 0.5])
    st.session_state.servicos_adicionados[i]['servico'] = cols[0].selectbox(f"Serviço {i+1}", SERVICOS_LISTA, key=f"ser_{i}")
    st.session_state.servicos_adicionados[i]['qtd'] = cols[1].number_input("Qtd/m²", min_value=0.0, step=1.0, key=f"qtd_{i}")
    st.session_state.servicos_adicionados[i]['valor'] = cols[2].number_input("V. Unit", min_value=0.0, step=10.0, key=f"val_{i}")
    if cols[3].button("❌", key=f"del_{i}"):
        st.session_state.servicos_adicionados.pop(i)
        st.rerun()

if st.button("➕ Adicionar mais um serviço"):
    st.session_state.servicos_adicionados.append({"servico": SERVICOS_LISTA[0], "qtd": 1.0, "valor": 0.0})
    st.rerun()

st.divider()

total_servicos = sum(s['qtd'] * s['valor'] for s in st.session_state.servicos_adicionados)
desconto = st.number_input("Desconto Total (R$)", min_value=0.0)
valor_final = total_servicos - desconto

st.markdown(f"### **Total Geral: R$ {formatar_br(valor_final)}**")

with st.expander("💰 Pagamento e Entrega"):
    c1, c2, c3 = st.columns(3)
    forma_pag = c1.selectbox("Forma de Pagamento", ["Dinheiro", "Pix", "Cartão de Crédito", "Cartão de Débito"])
    entrada = c2.number_input("Entrada (R$)", min_value=0.0)
    data_ent = c3.date_input("Previsão de Entrega")
    restante = valor_final - entrada

dados_doc = {
    "cliente": nome_c, "tel": tel_c, "end": end_c,
    "total_geral": total_servicos, "desconto": desconto, "valor_final": valor_final,
    "pagamento": forma_pag, "entrada": entrada, "restante": restante,
    "entrega": data_ent.strftime('%d/%m/%Y'),
    "data_hora": datetime.now().strftime('%d/%m/%Y %H:%M')
}

st.write(f"**Restante: R$ {formatar_br(restante)}**")

col_a, col_b = st.columns(2)
if col_a.button("📄 Gerar Orçamento"):
    pdf_out = gerar_pdf(dados_doc, st.session_state.servicos_adicionados, "ORÇAMENTO")
    st.download_button("Clique aqui para baixar Orçamento", pdf_out, f"Orcamento_{nome_c}.pdf")

if col_b.button("✅ Aprovar (Gerar O.S.)"):
    pdf_out = gerar_pdf(dados_doc, st.session_state.servicos_adicionados, "ORDEM DE SERVIÇO")
    st.download_button("Clique aqui para baixar O.S.", pdf_out, f"OS_{nome_c}.pdf")