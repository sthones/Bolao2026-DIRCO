import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from streamlit_gsheets import GSheetsConnection

# ==========================================
# CONFIGURAÇÃO INICIAL E ESTÉTICA
# ==========================================
st.set_page_config(page_title="Bolão DIRCO - Copa do Mundo 2026", page_icon="🏆", layout="wide")

SENHA_ADMIN = "dirco2026" 

# TRAVA DE SEGURANÇA: Data e hora máxima para aceitar palpites (Horário de Brasília)
PRAZO_FINAL = pd.Timestamp("2026-06-11 14:00:00", tz="America/Sao_Paulo")

# CSS Blindado contra o "Dark Mode" do Streamlit e cores da DIRCO
st.markdown("""
    <style>
    /* Fundo Amarelo Principal do App */
    .stApp, .main {
        background-color: #FFDF00 !important;
    }
    
    /* Textos gerais em Azul Escuro */
    .stApp, p, span, div, label, h1, h2, h3, h4, h5, h6, li {
        color: #003882 !important;
    }

    /* =========================================
       ABAS DE NAVEGAÇÃO (TABS)
       ========================================= */
    button[data-baseweb="tab"] {
        background-color: transparent !important;
    }
    button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
        color: #003882 !important;
        font-weight: 800 !important;
        font-size: 18px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        border-bottom: 4px solid #003882 !important;
    }

    /* =========================================
       BOTÕES
       ========================================= */
    .stButton>button, .stButton>button p {
        background-color: #003882 !important;
        color: #FFDF00 !important;
        font-weight: 900 !important;
        border: none !important;
        border-radius: 6px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover, .stButton>button:hover p {
        background-color: #FFFFFF !important;
        color: #003882 !important;
        border: 2px solid #003882 !important;
    }

    /* Expander (Sanfona dos Grupos) */
    .streamlit-expanderHeader {
        background-color: #F8CB00 !important;
        color: #003882 !important;
        font-weight: bold;
        border-radius: 5px;
    }

    /* Caixas de input com fundo branco para contraste */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #FFFFFF !important;
        color: #003882 !important;
        border: 1px solid #003882 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. CARGA DE DADOS
# ==========================================
def carregar_jogos_iniciais():
    times = {
        1: "México", 2: "África do Sul", 3: "Coreia do Sul", 4: "República Tcheca",
        5: "Canadá", 6: "Bósnia e Herzegovina", 7: "Catar", 8: "Suíça",
        9: "Brasil", 10: "Marrocos", 11: "Haiti", 12: "Escócia",
        13: "Estados Unidos", 14: "Paraguai", 15: "Austrália", 16: "Turquia",
        17: "Alemanha", 18: "Curaçao", 19: "Costa do Marfim", 20: "Equador",
        21: "Holanda", 22: "Japão", 23: "Suécia", 24: "Tunísia",
        25: "Bélgica", 26: "Egito", 27: "Irã", 28: "Nova Zelândia",
        29: "Espanha", 30: "Cabo Verde", 31: "Arábia Saudita", 32: "Uruguai",
        33: "França", 34: "Senegal", 35: "Iraque", 36: "Noruega",
        37: "Argentina", 38: "Argélia", 39: "Áustria", 40: "Jordânia",
        41: "Portugal", 42: "República Democrática do Congo", 43: "Uzbequistão", 44: "Colômbia",
        45: "Inglaterra", 46: "Croácia", 47: "Gana", 48: "Panamá"
    }
    
    cidades = {
        1: "Atlanta", 2: "Boston", 3: "Dallas", 4: "Houston", 5: "Kansas City",
        6: "Los Angeles", 7: "Miami", 8: "Nova York/Nova Jersey", 9: "Filadélfia",
        10: "São Francisco", 11: "Seattle", 12: "Toronto", 13: "Vancouver",
        14: "Guadalajara", 15: "Cidade do México", 16: "Monterrey"
    }

    jogos_csv = """1,1,2,15,2026-06-11,A\n2,3,4,14,2026-06-11,A\n3,5,6,12,2026-06-12,B\n4,13,14,6,2026-06-12,D\n5,7,8,10,2026-06-13,B\n6,9,10,8,2026-06-13,C\n7,11,12,2,2026-06-13,C\n8,15,16,13,2026-06-14,D\n9,17,18,4,2026-06-14,E\n10,21,22,3,2026-06-14,F\n11,19,20,9,2026-06-14,E\n12,23,24,16,2026-06-14,F\n13,29,30,1,2026-06-15,H\n14,25,26,11,2026-06-15,G\n15,31,32,7,2026-06-15,H\n16,27,28,6,2026-06-15,G\n17,33,34,8,2026-06-16,I\n18,35,36,2,2026-06-16,I\n19,37,38,5,2026-06-16,J\n20,39,40,10,2026-06-17,J\n21,41,42,4,2026-06-17,K\n22,45,46,3,2026-06-17,L\n23,47,48,12,2026-06-17,L\n24,43,44,15,2026-06-17,K\n25,4,2,1,2026-06-18,A\n26,8,6,6,2026-06-18,B\n27,5,7,13,2026-06-18,B\n28,1,3,14,2026-06-18,A\n29,13,15,11,2026-06-19,D\n30,12,10,2,2026-06-19,C\n31,9,11,9,2026-06-19,C\n32,16,14,10,2026-06-20,D\n33,21,23,4,2026-06-20,F\n34,17,19,12,2026-06-20,E\n35,20,18,5,2026-06-20,E\n36,24,22,16,2026-06-21,F\n37,29,31,1,2026-06-21,H\n38,25,27,6,2026-06-21,G\n39,32,30,7,2026-06-21,H\n40,28,26,13,2026-06-21,G\n41,37,39,3,2026-06-22,J\n42,33,35,9,2026-06-22,I\n43,36,34,8,2026-06-22,I\n44,40,38,10,2026-06-22,J\n45,41,43,4,2026-06-23,K\n46,45,47,2,2026-06-23,L\n47,48,46,12,2026-06-23,L\n48,44,42,14,2026-06-23,K\n49,8,5,13,2026-06-24,B\n50,6,7,11,2026-06-24,B\n51,12,9,7,2026-06-24,C\n52,10,11,1,2026-06-24,C\n53,4,1,15,2026-06-24,A\n54,2,3,16,2026-06-24,A\n55,18,19,9,2026-06-25,E\n56,20,17,8,2026-06-25,E\n57,22,23,3,2026-06-25,F\n58,24,21,5,2026-06-25,F\n59,16,13,6,2026-06-25,D\n60,14,15,10,2026-06-25,D\n61,36,33,2,2026-06-26,I\n62,34,35,12,2026-06-26,I\n63,30,31,4,2026-06-26,H\n64,32,29,14,2026-06-26,H\n65,26,27,11,2026-06-26,G\n66,28,25,13,2026-06-26,G\n67,48,45,8,2026-06-27,L\n68,46,47,9,2026-06-27,L\n69,44,41,7,2026-06-27,K\n70,42,43,1,2026-06-27,K\n71,38,39,5,2026-06-27,J\n72,40,37,3,2026-06-27,J"""

    world_cup_games = []
    
    for linha in jogos_csv.split('\n'):
        if not linha.strip(): continue
        g_id, t_a, t_b, c_id, data, grupo = linha.split(',')
        ano, mes, dia = data.split('-')
        data_formatada = f"{dia}/{mes}/{ano}"
        
        world_cup_games.append({
            "game_id": f"WC26_G{int(g_id):03d}",
            "data": data_formatada,
            "local": cidades[int(c_id)],
            "grupo": grupo,
            "team_a": times[int(t_a)],
            "team_b": times[int(t_b)],
            "real_a": np.nan,
            "real_b": np.nan
        })
        
    return pd.DataFrame(world_cup_games)

# ==========================================
# 2. CONEXÃO COM GOOGLE SHEETS
# ==========================================
conn = st.connection("gsheets", type=GSheetsConnection)

df_oficiais = conn.read(worksheet="Resultados", ttl=15) 

precisa_atualizar = False
if df_oficiais.empty or 'data' not in df_oficiais.columns:
    precisa_atualizar = True
elif df_oficiais['team_a'].astype(str).str.contains('Rep\. UEFA|Rep\. FIFA|RD Congo', regex=True).any():
    precisa_atualizar = True

if precisa_atualizar:
    df_base_jogos = carregar_jogos_iniciais()
    conn.update(worksheet="Resultados", data=df_base_jogos)
    df_oficiais = df_base_jogos

df_palpites_geral = conn.read(worksheet="Palpites", ttl=15)
if df_palpites_geral.empty or 'email' not in df_palpites_geral.columns:
    df_base_palpites = pd.DataFrame(columns=["participant_id", "nome", "email", "game_id", "pred_a", "pred_b"])
    conn.update(worksheet="Palpites", data=df_base_palpites)
    df_palpites_geral = df_base_palpites

flags_iso = {
    "México": "mx", "África do Sul": "za", "Coreia do Sul": "kr", "República Tcheca": "cz",
    "Canadá": "ca", "Bósnia e Herzegovina": "ba", "Catar": "qa", "Suíça": "ch",
    "Brasil": "br", "Marrocos": "ma", "Haiti": "ht", "Escócia": "gb-sct",
    "Estados Unidos": "us", "Paraguai": "py", "Austrália": "au", "Turquia": "tr",
    "Alemanha": "de", "Curaçao": "cw", "Costa do Marfim": "ci", "Equador": "ec",
    "Holanda": "nl", "Japão": "jp", "Suécia": "se", "Tunísia": "tn",
    "Bélgica": "be", "Egito": "eg", "Irã": "ir", "Nova Zelândia": "nz",
    "Espanha": "es", "Cabo Verde": "cv", "Arábia Saudita": "sa", "Uruguai": "uy",
    "França": "fr", "Senegal": "sn", "Iraque": "iq", "Noruega": "no",
    "Argentina": "ar", "Argélia": "dz", "Áustria": "at", "Jordânia": "jo",
    "Portugal": "pt", "República Democrática do Congo": "cd", "Uzbequistão": "uz", "Colômbia": "co",
    "Inglaterra": "gb-eng", "Croácia": "hr", "Gana": "gh", "Panamá": "pa"
}

# ==========================================
# 3. SISTEMA DE PONTUAÇÃO
# ==========================================
def calculate_score(row):
    pred_a, pred_b = row['pred_a'], row['pred_b']
    real_a, real_b = row['real_a'], row['real_b']

    if pd.isna(real_a) or pd.isna(real_b) or real_a == "" or real_b == "": 
        return 0

    real_win, real_draw, real_loss = real_a > real_b, real_a == real_b, real_a < real_b
    pred_win, pred_draw, pred_loss = pred_a > pred_b, pred_a == pred_b, pred_a < pred_b

    if pred_a == real_a and pred_b == real_b: return 10
    if real_draw and pred_draw: return 5

    if (real_win and pred_win) or (real_loss and pred_loss):
        if (real_win and pred_a == real_a) or (real_loss and pred_b == real_b): return 6
        if (real_win and pred_b == real_b) or (real_loss and pred_a == real_a): return 5
        return 4

    return 0

# ==========================================
# 4. INTERFACE DO STREAMLIT
# ==========================================
st.title("🏆 Bolão DIRCO - Copa do Mundo 2026")

aba1, aba2, aba3, aba4 = st.tabs(["📝 Fazer Palpites", "📊 Ranking", "📜 Regras", "⚙️ Admin"])

# --- ABA 1: FORMULÁRIO DE PALPITES (COM TRAVA DE TEMPO E ORDENAÇÃO) ---
with aba1:
    agora = pd.Timestamp.now(tz="America/Sao_Paulo")
    
    if agora >= PRAZO_FINAL:
        st.error("⛔ **PALPITES ENCERRADOS!**")
        st.warning("O prazo para enviar os palpites expirou, pois a Copa do Mundo já começou (ou está prestes a começar). Acompanhe o seu desempenho na aba **Ranking**!")
    else:
        st.info(f"⏳ O formulário ficará aberto até o dia **{PRAZO_FINAL.strftime('%d/%m/%Y às %H:%M')}** (Horário de Brasília).")
        
        st.header("Envie seus Palpites")

        with st.form("form_palpites", clear_on_submit=True):
            nome_participante = st.text_input("Seu Nome Completo:", max_chars=50)
            email_participante = st.text_input("Seu E-mail:")
            
            st.subheader("Fase de Grupos")
            novos_palpites = []
            
            # ATUALIZAÇÃO AQUI: Organiza os grupos rigorosamente em ordem alfabética (A, B, C, D...)
            grupos_unicos = sorted(df_oficiais['grupo'].dropna().unique())
            
            for grupo in grupos_unicos:
                with st.expander(f"Jogos do Grupo {grupo}", expanded=False):
                    jogos_do_grupo = df_oficiais[df_oficiais['grupo'] == grupo]
                    
                    for index, row in jogos_do_grupo.iterrows():
                        data_jogo = row.get('data', 'Data Indefinida')
                        local_jogo = row.get('local', 'Sede Indefinida')
                        t_a = row['team_a']
                        t_b = row['team_b']
                        
                        img_a = f"<img src='https://flagcdn.com/32x24/{flags_iso.get(t_a, 'un')}.png' width='28' style='vertical-align: middle; margin-left: 10px; border-radius: 3px; box-shadow: 1px 1px 3px rgba(0,0,0,0.3);'>"
                        img_b = f"<img src='https://flagcdn.com/32x24/{flags_iso.get(t_b, 'un')}.png' width='28' style='vertical-align: middle; margin-right: 10px; border-radius: 3px; box-shadow: 1px 1px 3px rgba(0,0,0,0.3);'>"
                        
                        st.markdown(f"<div style='text-align: center; color: #003882; font-size: 13px; font-weight: bold; margin-bottom: 5px; opacity: 0.8;'>📅 {data_jogo} &nbsp;|&nbsp; 📍 {local_jogo}</div>", unsafe_allow_html=True)
                        
                        col1, col2, col3, col4, col5 = st.columns([2.5, 1, 0.5, 1, 2.5])

                        with col1: st.markdown(f"<h5 style='text-align: right; color:#003882; margin-top:3px;'>{t_a} {img_a}</h5>", unsafe_allow_html=True)
                        with col2: gols_a = st.number_input("", key=f"a_{row['game_id']}", step=1, min_value=0, label_visibility="collapsed")
                        with col3: st.markdown("<h5 style='text-align: center; color:#003882; margin-top:3px;'>X</h5>", unsafe_allow_html=True)
                        with col4: gols_b = st.number_input("", key=f"b_{row['game_id']}", step=1, min_value=0, label_visibility="collapsed")
                        with col5: st.markdown(f"<h5 style='text-align: left; color:#003882; margin-top:3px;'>{img_b} {t_b}</h5>", unsafe_allow_html=True)

                        novos_palpites.append({
                            "participant_id": "",
                            "nome": nome_participante,
                            "email": email_participante,
                            "game_id": row['game_id'],
                            "pred_a": gols_a,
                            "pred_b": gols_b
                        })
                        st.write("") 
                        st.divider()

            submit = st.form_submit_button("⚽ Confirmar Meus Palpites")

            if submit:
                if nome_participante.strip() == "" or email_participante.strip() == "":
                    st.error("Por favor, preencha o seu nome e e-mail antes de enviar.")
                else:
                    df_palpites_verificacao = conn.read(worksheet="Palpites", ttl=15)
                    
                    if not df_palpites_verificacao.empty and email_participante in df_palpites_verificacao['email'].values:
                        st.error("Já existe um palpite registrado com este e-mail!")
                    else:
                        id_part = f"P{len(df_palpites_verificacao['email'].unique()) + 1:02d}"
                        
                        # --- AQUI ESTÁ A MÁGICA DO ZERO AUTOMÁTICO ---
                        for p in novos_palpites:
                            p['participant_id'] = id_part
                            # Se o valor for None ou vazio, vira 0
                            if p['pred_a'] is None: p['pred_a'] = 0
                            if p['pred_b'] is None: p['pred_b'] = 0
                        # ---------------------------------------------
                        
                        df_novos = pd.DataFrame(novos_palpites)
                        df_final = pd.concat([df_palpites_verificacao, df_novos], ignore_index=True)
                        
                        conn.update(worksheet="Palpites", data=df_final)
                        st.cache_data.clear()
                        st.success(f"Palpites de {nome_participante} registrados! Jogos vazios foram preenchidos como 0x0.")
# --- ABA 2: RANKING E DASHBOARD ---
with aba2:
    st.header("Ranking Atualizado")

    df_palpites_rank = conn.read(worksheet="Palpites", ttl=15)
    df_oficiais_rank = conn.read(worksheet="Resultados", ttl=15)

    if df_palpites_rank.empty or len(df_palpites_rank.dropna(subset=['email'])) == 0:
        st.info("Nenhum palpite foi registrado no banco de dados ainda.")
    else:
        df_analise = pd.merge(df_palpites_rank, df_oficiais_rank[['game_id', 'real_a', 'real_b']], on='game_id', how='left')
        
        df_analise['real_a'] = pd.to_numeric(df_analise['real_a'], errors='coerce')
        df_analise['real_b'] = pd.to_numeric(df_analise['real_b'], errors='coerce')
        df_analise['pred_a'] = pd.to_numeric(df_analise['pred_a'], errors='coerce')
        df_analise['pred_b'] = pd.to_numeric(df_analise['pred_b'], errors='coerce')
        
        df_analise['pontos'] = df_analise.apply(calculate_score, axis=1)

        df_ranking = df_analise.groupby(['email', 'nome']).agg(
            total_pontos=('pontos', 'sum'),
            placares_exatos=('pontos', lambda x: (x == 10).sum())
        ).reset_index()

        df_ranking = df_ranking.sort_values(by=['total_pontos', 'placares_exatos'], ascending=[False, False]).reset_index(drop=True)
        df_ranking.index = df_ranking.index + 1

        col_m1, col_m2, col_m3 = st.columns(3)
        
        if len(df_ranking) > 0:
            col_m1.metric("🥇 1º Colocado", df_ranking.iloc[0]['nome'], f"{int(df_ranking.iloc[0]['total_pontos'])} pts", delta_color="off")
        else:
            col_m1.metric("🥇 1º Colocado", "-", "-")
            
        if len(df_ranking) > 1:
            col_m2.metric("🥈 2º Colocado", df_ranking.iloc[1]['nome'], f"{int(df_ranking.iloc[1]['total_pontos'])} pts", delta_color="off")
        else:
            col_m2.metric("🥈 2º Colocado", "-", "-")
            
        if len(df_ranking) > 2:
            col_m3.metric("🥉 3º Colocado", df_ranking.iloc[2]['nome'], f"{int(df_ranking.iloc[2]['total_pontos'])} pts", delta_color="off")
        else:
            col_m3.metric("🥉 3º Colocado", "-", "-")

        st.dataframe(df_ranking[['nome', 'total_pontos', 'placares_exatos']], use_container_width=True)

        if df_ranking['total_pontos'].sum() > 0:
            st.subheader("Desempenho Visual")
            
            altura_grafico = max(4, len(df_ranking) * 0.5)
            fig, ax = plt.subplots(figsize=(10, altura_grafico))
            
            fig.patch.set_alpha(0.0)
            ax.patch.set_alpha(0.0)
            
            cores_grafico = ['#003882' if i % 2 == 0 else '#FFFFFF' for i in range(len(df_ranking))]
            
            sns.barplot(data=df_ranking, x='total_pontos', y='nome', palette=cores_grafico, ax=ax, orient='h')
            plt.xlabel("Pontuação Total", fontweight='bold', color='#003882')
            plt.ylabel("Participante", fontweight='bold', color='#003882')

            for p in ax.patches:
                largura = p.get_width()
                if largura > 0:
                    ax.annotate(format(largura, '.0f'),
                                (largura + 0.5, p.get_y() + p.get_height() / 2.),
                                ha='left', va='center', xytext=(0, 0),
                                textcoords='offset points', fontweight='bold', color='#003882')
            
            sns.despine()
            ax.tick_params(axis='x', colors='#003882')
            ax.tick_params(axis='y', colors='#003882')
            
            st.pyplot(fig)

# --- ABA 3: REGRAS (ATUALIZADA COM A PREMIAÇÃO) ---
with aba3:
    st.header("Regras do Bolão")
    
    st.subheader("💰 Premiação")
    st.markdown("""
    O valor total arrecadado com as inscrições será dividido da seguinte forma:
    * 🥇 **1º Lugar:** 60% da arrecadação
    * 🥈 **2º Lugar:** 30% da arrecadação
    * 🥉 **3º Lugar:** 10% da arrecadação
    """)
    
    st.divider()
    
    st.subheader("⚽ Sistema de Pontuação")
    st.markdown("""
    * **10 pts:** Acerto do Placar Exato.
    * **06 pts:** Acerto do Vencedor + Gols do Vencedor.
    * **05 pts:** Acerto do Empate sem placar exato / Acerto Vencedor + Gols Perdedor.
    * **04 pts:** Acerto somente do Vencedor.
    """)

# --- ABA 4: PAINEL ADMIN ---
with aba4:
    st.header("⚙️ Controle do Administrador")
    senha_input = st.text_input("Digite a Senha de Acesso:", type="password")
    
    if senha_input == SENHA_ADMIN:
        st.success("Acesso Liberado! Sincronizado com o Google Sheets.")
        
        st.subheader("Atualizar Resultados dos Jogos")
        df_admin = conn.read(worksheet="Resultados", ttl=15)
        
        df_atualizado = st.data_editor(
            df_admin,
            column_config={
                "game_id": st.column_config.TextColumn("ID", disabled=True),
                "data": st.column_config.TextColumn("Data", disabled=True),
                "local": st.column_config.TextColumn("Sede", disabled=True),
                "grupo": st.column_config.TextColumn("Grupo", disabled=True),
                "team_a": st.column_config.TextColumn("Seleção A", disabled=True),
                "team_b": st.column_config.TextColumn("Seleção B", disabled=True),
                "real_a": st.column_config.NumberColumn("Gols A", min_value=0, step=1),
                "real_b": st.column_config.NumberColumn("Gols B", min_value=0, step=1)
            },
            hide_index=True,
            use_container_width=True
        )
        
        if st.button("💾 Salvar Resultados na Planilha"):
            conn.update(worksheet="Resultados", data=df_atualizado)
            st.cache_data.clear()
            st.success("Tabela Oficial atualizada! Recarregando o sistema...")
            st.rerun() 
            
        st.write("") # Espaçamento
        if st.button("🔄 Atualizar App e Ranking (Forçar Leitura)"):
            st.cache_data.clear()
            st.rerun()
            
        st.divider()
        st.subheader("🗑️ Excluir Palpites de um Usuário")
        
        df_palpites_admin = conn.read(worksheet="Palpites", ttl=15)
        if not df_palpites_admin.empty and 'email' in df_palpites_admin.columns:
            usuarios_cadastrados = df_palpites_admin['email'].dropna().unique()
            
            if len(usuarios_cadastrados) > 0:
                usuario_para_excluir = st.selectbox("Selecione o e-mail do participante que deseja remover:", usuarios_cadastrados)
                
                if st.button("❌ Apagar Palpites Deste Usuário"):
                    df_palpites_limpo = df_palpites_admin[df_palpites_admin['email'] != usuario_para_excluir]
                    conn.update(worksheet="Palpites", data=df_palpites_limpo)
                    
                    st.cache_data.clear()
                    st.success(f"Todos os palpites de {usuario_para_excluir} foram deletados com sucesso!")
                    st.rerun()
            else:
                st.info("Nenhum participante registrado ainda.")
        else:
            st.info("Nenhum participante registrado ainda.")
            
        st.divider()
        st.subheader("⚠️ Área de Perigo Total")
        
        if st.button("🚨 ZERAR O BOLÃO INTEIRO PARA ENTRAR EM PRODUÇÃO"):
            df_zerado_palpites = pd.DataFrame(columns=["participant_id", "nome", "email", "game_id", "pred_a", "pred_b"])
            conn.update(worksheet="Palpites", data=df_zerado_palpites)
            
            df_zerado_resultados = df_admin.copy()
            df_zerado_resultados['real_a'] = np.nan
            df_zerado_resultados['real_b'] = np.nan
            conn.update(worksheet="Resultados", data=df_zerado_resultados)
            
            st.cache_data.clear()
            st.success("SISTEMA RESETADO! A planilha foi limpa e está pronta para uso.")
            st.rerun()
            
    elif senha_input != "":
        st.error("Senha incorreta.")