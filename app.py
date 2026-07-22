import streamlit as st
from fpdf import FPDF
from datetime import datetime, timedelta
import os
from PIL import Image
import pytz
import sqlite3
import json

# Definindo fuso horário do Brasil (Brasília)
FUSO_BR = pytz.timezone('America/Sao_Paulo')

# --- CONFIGURAÇÃO DO BANCO DE DADOS SQLITE ---
BANCO_DADOS = "historico_orcamentos.db"

def iniciar_banco():
    conn = sqlite3.connect(BANCO_DADOS)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orcamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT,
            telefone TEXT,
            endereco TEXT,
            servicos_json TEXT,
            total_geral REAL,
            desconto REAL,
            valor_final REAL,
            pagamento TEXT,
            entrada REAL,
            restante REAL,
            entrega TEXT,
            data_hora DATETIME
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servicos_catalogo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE
        )
    ''')
    
    cursor.execute("SELECT COUNT(*) FROM servicos_catalogo")
    if cursor.fetchone()[0] == 0:
        servicos_iniciais = [
            "Toldo Policarbonato","Troca policarbonato 6mm 1ª linha","Perfil U","Borracha fina perfil", "Toldo Cortina", "Toldo Fixo Lona",
            "Toldo Retratil Braço, tubo e sarrafo aluminio","Cobertura Policarbonato",
            "Cobertura Lona", "Painel","Painel Paraline","Fachada", "Estrutura", "Banner", "Adesivo", "Plotter","Plottagem de adesivo em Painel",
            "Lona", "Troca de Lona", "Placa", "Mão de Obra", "Impressão", "Calha", "Forro Paraline","instalação de refletor",
            "Pintura", "Cavalete", "Cartão de visita", "Panfleto 4x0, 5000 und","Panfleto 4x4 - 5000 und", "Cardápio","Luminoso", "Logotipo",
            "Identidade Visual", "Manutenção", "Troca de Mola", "Troca de Tubo", "Vetorização","Cartaz",
            "Folder","Arte Gráfica","Site","Aplicação Webb"
        ]
        cursor.executemany("INSERT OR IGNORE INTO servicos_catalogo (nome) VALUES (?)", [(s,) for s in servicos_iniciais])
        
    conn.commit()
    conn.close()

def carregar_servicos_banco():
    conn = sqlite3.connect(BANCO_DADOS)
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM servicos_catalogo ORDER BY nome ASC")
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows]

def adicionar_servico_banco(nome):
    conn = sqlite3.connect(BANCO_DADOS)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO servicos_catalogo (nome) VALUES (?)", (nome.strip(),))
        conn.commit()
        sucesso = True
    except sqlite3.IntegrityError:
        sucesso = False
    conn.close()
    return sucesso

def remover_servico_banco(nome):
    conn = sqlite3.connect(BANCO_DADOS)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM servicos_catalogo WHERE nome = ?", (nome,))
    conn.commit()
    conn.close()

def limpar_dados_antigos(dias=60):
    conn = sqlite3.connect(BANCO_DADOS)
    cursor = conn.cursor()
    agora_br = datetime.now(FUSO_BR)
    data_limite = agora_br - timedelta(days=dias)
    cursor.execute("DELETE FROM orcamentos WHERE data_hora < ?", (data_limite.strftime('%Y-%m-%d %H:%M:%S'),))
    conn.commit()
    conn.close()

def deletar_orcamento_banco(orcamento_id):
    conn = sqlite3.connect(BANCO_DADOS)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orcamentos WHERE id = ?", (orcamento_id,))
    conn.commit()
    conn.close()

def salvar_orcamento_banco(dados, lista_servicos):
    conn = sqlite3.connect(BANCO_DADOS)
    cursor = conn.cursor()
    servicos_json = json.dumps(lista_servicos)
    data_hora_br = datetime.now(FUSO_BR).strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
        INSERT INTO orcamentos (cliente, telefone, endereco, servicos_json, total_geral, desconto, valor_final, pagamento, entrada, restante, entrega, data_hora)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        dados['cliente'], dados['tel'], dados['end'], servicos_json,
        dados['total_geral'], dados['desconto'], dados['valor_final'],
        dados['pagamento'], dados['entrada'], dados['restante'],
        dados['entrega'], data_hora_br
    ))
    conn.commit()
    conn.close()

def buscar_orcamentos():
    conn = sqlite3.connect(BANCO_DADOS)
    cursor = conn.cursor()
    cursor.execute("SELECT id, cliente, valor_final, strftime('%d/%m/%Y %H:%M', data_hora) FROM orcamentos ORDER BY id DESC")
    resultados = cursor.fetchall()
    conn.close()
    return resultados

def carregar_orcamento_por_id(orcamento_id):
    conn = sqlite3.connect(BANCO_DADOS)
    cursor = conn.cursor()
    cursor.execute("SELECT id, cliente, telefone, endereco, servicos_json, total_geral, desconto, valor_final, pagamento, entrada, restante, entrega, strftime('%d/%m/%Y %H:%M', data_hora) FROM orcamentos WHERE id = ?", (orcamento_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "cliente": row[1],
            "tel": row[2],
            "end": row[3],
            "servicos": json.loads(row[4]),
            "total_geral": row[5],
            "desconto": row[6],
            "valor_final": row[7],
            "pagamento": row[8],
            "entrada": row[9],
            "restante": row[10],
            "entrega": row[11],
            "data_hora": row[12]
        }
    return None

# Inicializa Banco
iniciar_banco()
limpar_dados_antigos(dias=60)
SERVICOS_LISTA = carregar_servicos_banco()

# --- FUNÇÃO DE SEGURANÇA E SESSÃO ---
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

# --- FUNÇÃO PARA LIMPAR FORMULÁRIO (NOVO ORÇAMENTO) ---
def novo_orcamento():
    # Limpa estados de recuperação de cliente
    st.session_state["cliente_rec"] = ""
    st.session_state["tel_rec"] = ""
    st.session_state["end_rec"] = ""
    
    # Limpa as chaves dos inputs de texto
    for key in ["nome_c_input", "tel_c_input", "end_c_input"]:
        if key in st.session_state:
            del st.session_state[key]
            
    # Reseta a lista de serviços para apenas 1 em branco
    servs = carregar_servicos_banco()
    padrao = servs[0] if servs else ""
    st.session_state.servicos_adicionados = [{"serviço": padrao, "descrição": "", "qtd": 1.0, "valor": 0.0}]
    
    # Remove as chaves dinâmicas dos serviços
    keys_para_remover = [k for k in st.session_state.keys() if k.startswith("ser_") or k.startswith("qtd_") or k.startswith("val_") or k.startswith("desc_")]
    for k in keys_para_remover:
        del st.session_state[k]
        
    st.session_state["exibir_pago_tela"] = False
    st.rerun()

# FUNÇÃO DE FORMATAÇÃO
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

if 'servicos_adicionados' not in st.session_state:
    padrao = SERVICOS_LISTA[0] if SERVICOS_LISTA else ""
    st.session_state.servicos_adicionados = [{"serviço": padrao, "descrição": "", "qtd": 1.0, "valor": 0.0}]

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
    
    is_os = "ORDEM DE SERVIÇO" in tipo_documento.upper() or "O.S." in tipo_documento.upper()
    status_pago_pdf = " (PAGO)" if is_os and dados['entrada'] > 0 else ""
    pdf.cell(0, 8, f"Forma: {dados['pagamento']} | Entrada: R$ {formatar_br(dados['entrada'])}{status_pago_pdf}", ln=True)
    
    pdf.set_text_color(255, 0, 0) if dados['restante'] > 0 else pdf.set_text_color(0, 128, 0)
    pdf.cell(0, 8, f"Restante a Pagar: R$ {formatar_br(dados['restante'])} | Entrega: {dados['entrega']}", ln=True)
    pdf.set_text_color(0, 0, 0)
    
    # --- CARIMBO / ASSINATURA DIGITAL (SÓ NA O.S.) ---
    if is_os:
        pdf.ln(8)
        carimbo_x = 110
        carimbo_y = pdf.get_y()
        
        pdf.set_draw_color(0, 51, 102)
        pdf.set_line_width(0.8)
        pdf.rect(carimbo_x, carimbo_y, 85, 28)
        
        pdf.set_xy(carimbo_x, carimbo_y + 2)
        pdf.set_font("Arial", 'B', 9)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(85, 4, EMPRESA['nome'], align='C', ln=True)
        
        pdf.set_x(carimbo_x)
        pdf.set_font("Arial", '', 8)
        pdf.cell(85, 4, f"CNPJ: {EMPRESA['cnpj']}", align='C', ln=True)
        
        pdf.set_x(carimbo_x)
        pdf.set_font("Arial", 'B', 7)
        pdf.set_text_color(0, 102, 0)
        pdf.cell(85, 5, "[ APROVADO & ASSINADO DIGITALMENTE ]", align='C', ln=True)
        
        pdf.set_x(carimbo_x)
        pdf.set_font("Arial", 'I', 7)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(85, 4, f"Data/Hora: {dados['data_hora']}", align='C', ln=True)
        
        pdf.set_draw_color(0, 0, 0)
        pdf.set_text_color(0, 0, 0)
        pdf.set_line_width(0.2)
        pdf.ln(5)

    pdf.ln(5)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, f"Gerado em: {dados['data_hora']}", align='R')
    
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# --- SIDEBAR: NAVEGAÇÃO DE TELAS ---
st.sidebar.title("📌 Navegação")
pagina = st.sidebar.radio("Ir para:", ["📄 Emissão de Orçamento / O.S.", "⚙️ Gerenciar Lista de Serviços"])

col_sb1, col_sb2 = st.sidebar.columns(2)

# BOTAO NOVO NA SIDEBAR
if col_sb1.button("🆕 Novo", key="btn_novo_sidebar"):
    novo_orcamento()

if col_sb2.button("🚪 Sair", key="btn_sair_sidebar"):
    st.session_state["acesso_liberado"] = False
    st.rerun()

st.sidebar.divider()

# --- TELA 1: EMISSÃO DE ORÇAMENTO / O.S. ---
if pagina == "📄 Emissão de Orçamento / O.S.":
    st.sidebar.title("📚 Histórico (Últimos 60 dias)")
    lista_salvos = buscar_orcamentos()

    if lista_salvos:
        opcoes = {f"#{item[0]} - {item[1]} (R$ {formatar_br(item[2])}) - {item[3]}": item[0] for item in lista_salvos}
        escolha = st.sidebar.selectbox("Restaurar / Excluir:", ["Nenhum"] + list(opcoes.keys()))
        
        if escolha != "Nenhum":
            id_selecionado = opcoes[escolha]
            dados_recuperados = carregar_orcamento_por_id(id_selecionado)
            
            col_side1, col_side2 = st.sidebar.columns(2)
            
            if col_side1.button("📂 Carregar"):
                st.session_state["cliente_rec"] = dados_recuperados["cliente"]
                st.session_state["tel_rec"] = dados_recuperados["tel"]
                st.session_state["end_rec"] = dados_recuperados["end"]
                st.session_state.servicos_adicionados = dados_recuperados["servicos"]
                
                # Atualiza os inputs
                st.session_state["nome_c_input"] = dados_recuperados["cliente"]
                st.session_state["tel_c_input"] = dados_recuperados["tel"]
                st.session_state["end_c_input"] = dados_recuperados["end"]
                st.rerun()
                
            if col_side2.button("🗑️ Excluir"):
                deletar_orcamento_banco(id_selecionado)
                st.sidebar.success("Registro excluído!")
                st.rerun()
            
            pdf_regerado = gerar_pdf(dados_recuperados, dados_recuperados["servicos"], "ORDEM DE SERVIÇO REGERADA")
            st.sidebar.download_button("📥 Baixar PDF Salvo", pdf_regerado, f"OS_{dados_recuperados['cliente']}.pdf")
    else:
        st.sidebar.info("Nenhum orçamento salvo nos últimos 60 dias.")

    st.title("Elabore Toldos")

    with st.expander("👤 Dados do Cliente", expanded=True):
        c1, c2 = st.columns(2)
        nome_c = c1.text_input("Nome do Cliente", value=st.session_state.get("cliente_rec", ""), key="nome_c_input")
        tel_c = c2.text_input("Telefone", value=st.session_state.get("tel_rec", ""), key="tel_c_input")
        end_c = st.text_input("Endereço Completo", value=st.session_state.get("end_rec", ""), key="end_c_input")

    st.write("### 🛠 Serviços")

    SERVICOS_LISTA = carregar_servicos_banco()

    for i, item in enumerate(st.session_state.servicos_adicionados):
        with st.container():
            cols = st.columns([2, 1, 1, 0.5])
            
            servico_atual = item['serviço'] if item['serviço'] in SERVICOS_LISTA else (SERVICOS_LISTA[0] if SERVICOS_LISTA else "")
            st.session_state.servicos_adicionados[i]['serviço'] = cols[0].selectbox(
                f"Serviço {i+1}", 
                SERVICOS_LISTA, 
                index=SERVICOS_LISTA.index(servico_atual) if servico_atual in SERVICOS_LISTA else 0, 
                key=f"ser_{i}"
            )
            st.session_state.servicos_adicionados[i]['qtd'] = cols[1].number_input("Qtd/m²", min_value=0.0, step=1.0, value=float(item['qtd']), key=f"qtd_{i}")
            st.session_state.servicos_adicionados[i]['valor'] = cols[2].number_input("V. Unit", min_value=0.0, step=10.0, value=float(item['valor']), key=f"val_{i}")
            
            if cols[3].button("❌", key=f"del_{i}"):
                st.session_state.servicos_adicionados.pop(i)
                st.rerun()
                
            st.session_state.servicos_adicionados[i]['descrição'] = st.text_input(f"Descrição/Observação do Serviço {i+1}", value=item.get('descrição', ''), key=f"desc_{i}", placeholder="Ex: Lona cor azul, estrutura reforçada, etc.")
            st.divider()

    if st.button("➕ Adicionar mais um serviço"):
        padrao = SERVICOS_LISTA[0] if SERVICOS_LISTA else ""
        st.session_state.servicos_adicionados.append({"serviço": padrao, "descrição": "", "qtd": 1.0, "valor": 0.0})
        st.rerun()

    total_servicos = sum(s['qtd'] * s['valor'] for s in st.session_state.servicos_adicionados)
    desconto = st.number_input("Desconto Total (R$)", min_value=0.0)
    valor_final = max(0.0, total_servicos - desconto)

    st.markdown(f"### **Valor Total: R$ {formatar_br(valor_final)}**")

    with st.expander("💰 Pagamento e Entrega", expanded=True):
        c1, c2, c3 = st.columns(3)
        forma_pag = c1.selectbox("Forma de Pagamento", ["Dinheiro", "Pix", "Cartão de Crédito", "Cartão de Débito"])
        entrada = c2.number_input("Valor da Entrada (R$)", min_value=0.0, max_value=float(valor_final), step=50.0)
        data_ent = c3.date_input("Previsão de Entrega")
        
        if st.session_state.get("exibir_pago_tela", False) and entrada > 0:
            c2.markdown("🟢 **(PAGO)**")
        
        restante = valor_final - entrada

    agora_br = datetime.now(FUSO_BR)

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

    st.subheader(f"💵 **Restante a Pagar:** R$ {formatar_br(restante)}")

    col_a, col_b = st.columns(2)

    if col_a.button("📄 Gerar Orçamento"):
        st.session_state["exibir_pago_tela"] = False
        if nome_c.strip():
            salvar_orcamento_banco(dados_doc, st.session_state.servicos_adicionados)
            st.success("Dados salvos no banco com sucesso!")
        pdf_out = gerar_pdf(dados_doc, st.session_state.servicos_adicionados, "ORÇAMENTO")
        st.download_button("Clique aqui para baixar Orçamento", pdf_out, f"Orcamento_{nome_c}.pdf")

    if col_b.button("✅ Aprovar (Gerar O.S.)"):
        st.session_state["exibir_pago_tela"] = True
        if nome_c.strip():
            salvar_orcamento_banco(dados_doc, st.session_state.servicos_adicionados)
            st.success("Dados salvos no banco com sucesso!")
        pdf_out = gerar_pdf(dados_doc, st.session_state.servicos_adicionados, "ORDEM DE SERVIÇO")
        st.download_button("Clique aqui para baixar O.S.", pdf_out, f"OS_{nome_c}.pdf")

    st.divider()
    if st.button("🔄 Iniciar Novo Orçamento / Limpar Tudo", key="btn_novo_principal"):
        novo_orcamento()

# --- TELA 2: GERENCIAR LISTA DE SERVIÇOS ---
elif pagina == "⚙️ Gerenciar Lista de Serviços":
    st.title("⚙️ Gerenciar Catálogo de Serviços")
    st.write("Adicione novos serviços ou exclua os que não utiliza mais.")
    
    st.subheader("➕ Adicionar Novo Serviço")
    novo_servico_nome = st.text_input("Nome do Novo Serviço:")
    if st.button("Salvar Novo Serviço"):
        if novo_servico_nome.strip():
            if adicionar_servico_banco(novo_servico_nome):
                st.success(f"Serviço '{novo_servico_nome}' adicionado com sucesso!")
                st.rerun()
            else:
                st.warning("Este serviço já existe na lista.")
        else:
            st.error("Digite o nome do serviço.")
            
    st.divider()
    st.subheader("📋 Serviços Cadastrados")
    servicos_atuais = carregar_servicos_banco()
    
    for serv in servicos_atuais:
        col_s1, col_s2 = st.columns([3, 1])
        col_s1.write(f"• **{serv}**")
        if col_s2.button("🗑️ Excluir", key=f"del_cat_{serv}"):
            remover_servico_banco(serv)
            st.success(f"Serviço '{serv}' removido!")
            st.rerun()