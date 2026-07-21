import streamlit as st
from fpdf import FPDF
from datetime import datetime
import os
from PIL import Image
import pytz

# --- FUNÇÃO DE SEGURANÇA ---
def verificar_acesso():
    if "acesso_liberado" not in st.session_state:
        st.session_state["acesso_liberado"] = False

    if st.session_state["acesso_liberado"]:
        return True

    st.title("🔐 Acesso Restrito - Elabore Toldos")
    senha_digitada = st.text_input("Digite a senha para continuar:", type="password")
    
    if st.button("Entrar"):
        if senha_digitada == st.secrets["credentials"]["password"]:
            st.session_state["acesso_liberado"] = True
            st.rerun()
        else:
            st.error("Senha incorreta! Tente novamente.")
    
    return False

if not verificar_acesso():
    st.stop()

# 1. FUNÇÃO DE FORMATAÇÃO
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
   "Toldo Policarbonato","Troca policarbonato 6mm 1ª linha","Perfil U","Borracha fina perfil", "Toldo Cortina", "Toldo Fixo Lona",
    "Toldo Retratil Braço, tubo e sarrafo aluminio","Cobertura Policarbonato",
    "Cobertura Lona", "Painel","Painel Paraline","Fachada", "Estrutura", "Banner", "Adesivo", "Plotter","Plottagem de adesivo em Painel",
    "Lona", "Troca de Lona", "Placa", "Mão de Obra", "Impressão", "Calha", "Forro Paraline", "Forro Pvc", "instalação de refletor",
    "Pintura", "Cavalete", "Cartão de visita", "Panfleto 4x0, 5000 und","Panfleto 4x4 - 5000 und", "Cardápio","Luminoso", "Logotipo",
    "Identidade Visual", "Manutenção", "Troca de Mola", "Troca de Tubo", "Vetorização","Cartaz",
    "Folder","Arte Gráfica","Site","Aplicação Webb"
]
]

# Inicialização do estado com o campo 'descrição'
if 'servicos_adicionados' not in st.session_state:
    st.session_state.servicos_adicionados = [{"serviço": SERVICOS_LISTA[0], "descrição": "", "qtd": 1.0, "valor": 0.0}]

def gerar_pdf(dados, lista_servicos, tipo_documento):
    pdf = FPDF()
    pdf.add_page()
    
    # Logo
    if os.path.exists('logo.png'):
        try:
            img = Image.open('logo.png')
            img_rgb = img.convert("RGB")
            img_rgb.save("logo_limpa.jpg", "JPEG")
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
    pdf.cell(0, 8, "DETALHES DOS SERVIÇOS", ln=True, fill=True)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(90, 8, "Serviço / Descrição", 1)
    pdf.cell(30, 8, "Qtd/m2", 1)
    pdf.cell(35, 8, "V. Unit", 1)
    pdf.cell(35, 8, "Subtotal", 1, ln=True)
    
    pdf.set_font("Arial", size=9)
    for s in lista_servicos:
        sub = s['qtd'] * s['valor']
        
        x = pdf.get_x()
        y = pdf.get_y()
        
        texto_servico = f"{s['serviço']}"
        if s['descrição']:
            texto_servico += f"\nObs: {s['descrição']}"
            
        pdf.multi_cell(90, 5, texto_servico, 1)
        novo_y = pdf.get_y()
        altura_celula = novo_y - y
        
        pdf.set_xy(x + 90, y)
        pdf.cell(30, altura_celula, f"{s['qtd']}", 1)
        pdf.cell(35, altura_celula, f"R$ {formatar_br(s['valor'])}", 1)
        pdf.cell(35, altura_celula, f"R$ {formatar_br(sub)}", 1, ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"TOTAL DOS SERVICOS: R$ {formatar_br(dados['total_geral'])}", ln=True, align='R')
    pdf.cell(0, 10, f"DESCONTO: R$ {formatar_br(dados['desconto'])}", ln=True, align='R')
    pdf.set_text_color(0, 128, 0)
    pdf.cell(0, 10, f"VALOR TOTAL COM DESCONTO: R$ {formatar_br(dados['valor_final'])}", ln=True, align='R')
    pdf.set_text_color(0, 0, 0)

    # Pagamento
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "CONDIÇÕES DE PAGAMENTO", ln=True, fill=True)
    pdf.set_font("Arial", size=11)
    
    # Texto para a entrada no PDF indicando se já foi pago
    status_pago_pdf = " (PAGO)" if dados['entrada'] > 0 else ""
    pdf.cell(0, 8, f"Forma: {dados['pagamento']} | Entrada: R$ {formatar_br(dados['entrada'])}{status_pago_pdf}", ln=True)
    
    pdf.set_text_color(255, 0, 0) if dados['restante'] > 0 else pdf.set_text_color(0, 128, 0)
    pdf.cell(0, 8, f"Restante a Pagar: R$ {formatar_br(dados['restante'])} | Entrega: {dados['entrega']}", ln=True)
    pdf.set_text_color(0, 0, 0)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, f"Gerado em: {dados['data_hora']}", align='R')
    
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# --- INTERFACE ---
st.title("Elabore Toldos")

with st.expander("👤 Dados do Cliente", expanded=True):
    c1, c2 = st.columns(2)
    nome_c = c1.text_input("Nome do Cliente")
    tel_c = c2.text_input("Telefone")
    end_c = st.text_input("Endereço Completo")

st.write("### 🛠 Serviços")

for i, item in enumerate(st.session_state.servicos_adicionados):
    with st.container():
        cols = st.columns([2, 1, 1, 0.5])
        st.session_state.servicos_adicionados[i]['serviço'] = cols[0].selectbox(f"Serviço {i+1}", SERVICOS_LISTA, key=f"ser_{i}")
        st.session_state.servicos_adicionados[i]['qtd'] = cols[1].number_input("Qtd/m²", min_value=0.0, step=1.0, key=f"qtd_{i}")
        st.session_state.servicos_adicionados[i]['valor'] = cols[2].number_input("V. Unit", min_value=0.0, step=10.0, key=f"val_{i}")
        
        # Botão de excluir
        if cols[3].button("❌", key=f"del_{i}"):
            st.session_state.servicos_adicionados.pop(i)
            st.rerun()
            
        st.session_state.servicos_adicionados[i]['descrição'] = st.text_input(f"Descrição/Observação do Serviço {i+1}", key=f"desc_{i}", placeholder="Ex: Lona cor azul, estrutura reforçada, etc.")
        st.divider()

if st.button("➕ Adicionar mais um serviço"):
    st.session_state.servicos_adicionados.append({"serviço": SERVICOS_LISTA[0], "descrição": "", "qtd": 1.0, "valor": 0.0})
    st.rerun()

total_servicos = sum(s['qtd'] * s['valor'] for s in st.session_state.servicos_adicionados)
desconto = st.number_input("Desconto Total (R$)", min_value=0.0)
valor_final = max(0.0, total_servicos - desconto)

st.markdown(f"### **Valor Total: R$ {formatar_br(valor_final)}**")

with st.expander("💰 Pagamento e Entrega", expanded=True):
    c1, c2, c3 = st.columns(3)
    forma_pag = c1.selectbox("Forma de Pagamento", ["Dinheiro", "Pix", "Cartão de Crédito", "Cartão de Débito"])
    
    # Campo para valor da entrada
    entrada = c2.number_input("Valor da Entrada (R$)", min_value=0.0, max_value=float(valor_final), step=50.0)
    data_ent = c3.date_input("Previsão de Entrega")
    
    # Exibe a indicação de pago e atualiza o restante a pagar
    if entrada > 0:
        c2.markdown("🟢 **(PAGO)**")
    
    restante = valor_final - entrada

fuso_br = pytz.timezone('America/Sao_Paulo')
agora_br = datetime.now(fuso_br)

dados_doc = {
    "cliente": nome_c, 
    "tel": tel_c, 
    "end": end_c,
    "total_geral": total_servicos, 
    "desconto": desconto, 
    "valor_final": valor_final,
    "pagamento": forma_pag, 
    "entrada": entrada, 
    "restante": restante,
    "entrega": data_ent.strftime('%d/%m/%Y'),
    "data_hora": agora_br.strftime('%d/%m/%Y %H:%M')
}

# Destaque para o valor que falta pagar
st.subheader(f"💵 **Restante a Pagar:** R$ {formatar_br(restante)}")

col_a, col_b = st.columns(2)
if col_a.button("📄 Gerar Orçamento"):
    pdf_out = gerar_pdf(dados_doc, st.session_state.servicos_adicionados, "ORÇAMENTO")
    st.download_button("Clique aqui para baixar Orçamento", pdf_out, f"Orcamento_{nome_c}.pdf")

if col_b.button("✅ Aprovar (Gerar O.S.)"):
    pdf_out = gerar_pdf(dados_doc, st.session_state.servicos_adicionados, "ORDEM DE SERVIÇO")
    st.download_button("Clique aqui para baixar O.S.", pdf_out, f"OS_{nome_c}.pdf")