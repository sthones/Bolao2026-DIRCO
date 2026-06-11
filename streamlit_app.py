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
    .stApp, .main { background-color: #FFDF00 !important; }
    /* Textos gerais em Azul Escuro */
    .stApp, p, span, div, label, h1, h2, h3, h4, h5, h6, li { color: #003882 !important; }
    /* ABAS DE NAVEGAÇÃO (TABS) */
    button[data-baseweb="tab"] { background-color: transparent !important; }
    button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p { color: #003882 !important; font-weight: 800 !important; font-size: 18px !important; }
    button[data-baseweb="tab"][aria-selected="true"] { border-bottom: 4px solid #003882 !important; }
    /* BOTÕES */
    .stButton>button, .stButton>button p { background-color: #003882 !important; color: #FFDF00 !important; font-weight: 900 !important; border: none !important; border-radius: 6px; transition: all 0.3s ease; }
    .stButton>button:hover, .stButton>button:hover p { background-color: #FFFFFF !important; color: #003882 !important; border: 2px solid #003882 !important; }
    /* Expander (Sanfona dos Grupos) */
    .streamlit-expanderHeader { background-color: #F8CB00 !important; color: #003882 !important; font-weight: bold; border-radius: 5px; }
    /* Caixas de input com fundo branco para contraste */
    .stTextInput>div>div>input, .stNumberInput>div>div>input { background-color: #FFFFFF !important; color: #003882 !important; border: 1px solid #003882 !important; }
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
    cidades = {1: "Atlanta", 2: "Boston", 3: "Dallas", 4: "Houston", 5: "Kansas City", 6: "Los Angeles", 7: "Miami", 8: "Nova York/Nova Jersey", 9: "Filadélfia", 10: "São Francisco", 11: "Seattle", 12: "Toronto", 13: "Vancouver", 14: "Guadalajara", 15: "Cidade do México", 16: "Monterrey"}
    jogos_csv = """1,1,2,15,2026-06-11,A\n2,3,4,14,2026-06-11,A\n3,5,6,12,2026-06-12,B\n4,13,14,6,2026-06-12,D\n5,7,8,10,2026-06-13,B\n6,9,10,8,2026-06-13,C\n7,11,12,2,2026-06-13,C\n8,15,16,13,2026-06-14,D\n9,17,18,4,2026-06-14,E\n10,21,22,3,2026-06-14,F\n11,19,20,9,2026-06-14,E\n12,23,24,16,2026-06-14,F\n13,29,30,1,2026-06-15,H\n14,25,26,11,2026-06-15,G\n15,31,32,7,2026-06-15,H\n16,27,28,6,2026-06-15,G\n17,33,34,8,2026-06-16,I\n18,35,36,2,2026-06-16,I\n19,37,38,5,2026-06-16,J\n20,39,40,10,2026-06-17,J\n21,41,42,4,2026-06-17,K\n22,45,46,3,2026-06-17,L\n23,47,48,12,2026-06-17,L\n24,43,44,15,2026-06-17,K\n25,4,2,1,2026-06-18,A\n26,8,6,6,2026-06-18,B\n27,5,7,13,2026-06-18,B\n28,1,3,14,2026-06-18,A\n29,13,15,11,2026-06-19,D\n30,12,10,2,2026-06-19,C\n31,9,11,9,2026-06-19,C\n32,16,14,10,2026-06-20,D\n33,21,23,4,2026-06-20,F\n34,17,19,12,2026-06-20,E\n35,20,18,5,2026-06-20,E\n36,24,22,16,2026-06-21,F\n37,29,31,1,2026-06-21,H\n38,25,27,6,2026-06-21,G\n39,32,30,7,2026-06-21,H\n40,28,26,13,2026-06-21,G\n41,37,39,3,2026-06-22,J\n42,33,35,9,2026-06-22,I\n43,36,34,8,2026-06-22,I\n44,40,38,10,2026-06-22,J\n45,41,43,4,2026-06-23,K\n46,45,47,2,2026-06-23,L\n47,48,46,12,2026-06-23,L\n48,44,42,14,2026-06-23,K\n49,8,5,13,2026-06-24,B\n50,6,7,11,2026-06-24,B\n51,12,9,7,2026-06-24,C\n52,10,11,1,2026-06-24,C\n53,4,1,15,2026-06-24,A\n54,2,3,16,2026-06-24,A\n55,18,19,9,2026-06-25,E\n56,20,17,8,2026-06-25,E\n57,22,23,3,2026-06-25,F\n58,24,21,5,2026-06-25,F\n59,16,13,6,2026-06-25,D\n60,14,15,10,2026-06-25,D\n61,36,33,2,2026-06-26,I\n62,34,35,12,2026-06-26,I\n63,30,31,4,2026-06-26,H\n64,32,29,14,2026-06-26,H\n65,26,27,11,2026-06-26,G\n66,28,25,13,2026-06-26,G\n67,48,45,8,2026-06-27,L\n68,46,47,9,2026-06-27,L\n69,44,41,7,2026-06-27,K\n70,42,43,1,2026-06-27,K\n71,38,39,5,2026-06-27,J\n72,40,37,3,2026-06-27,J"""

    world_cup_games = []
    for linha in jogos_csv.split('\n'):
        if not linha.strip(): continue
        g_id, t_a, t_b, c_id, data, grupo = linha.split(',')
        ano, mes, dia = data.split('-')
        data_formatada = f"{dia}/{mes}/{ano}"
        world_cup_games.append({"game_id": f"WC26_G{int(g_id):03d}", "data": data_formatada, "local": cidades[int(c_id)], "grupo": grupo, "team_a": times[int(t_a)], "team_b": times[int(t_b)], "real_a": np.nan, "real_b": np.nan})
    return pd.DataFrame(world_cup_games)

# ==========================================
# 2. CONEXÃO COM GOOGLE SHEETS E CACHE
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
    "México": "mx", "África do Sul": "za", "Coreia do Sul": "kr", "República Tcheca": "cz", "Canadá": "ca", "Bósnia e Herzegovina": "ba", "Catar": "qa", "Suíça": "ch", "Brasil": "br", "Marrocos": "ma", "Haiti": "ht", "Escócia": "gb-sct", "Estados Unidos": "us", "Paraguai": "py", "Austrália": "au", "Turquia": "tr", "Alemanha": "de", "Curaçao": "cw", "Costa do Marfim": "ci", "Equador": "ec", "Holanda": "nl", "Japão": "jp", "Suécia": "se", "Tunísia": "tn", "Bélgica": "be", "Egito": "eg", "Irã": "ir", "Nova Zelândia": "nz", "Espanha": "es", "Cabo Verde": "cv", "Arábia Saudita": "sa", "Uruguai": "uy", "França": "fr", "Senegal": "sn", "Iraque": "iq", "Noruega": "no", "Argentina": "ar", "Argélia": "dz", "Áustria": "at", "Jordânia": "jo", "Portugal": "pt", "República Democrática do Congo": "cd", "Uzbequistão": "uz", "Colômbia": "co", "Inglaterra": "gb-eng", "Croácia": "hr", "Gana": "gh", "Panamá": "pa"
}

# ==========================================
# 3. SISTEMA DE PONTUAÇÃO E CLASSIFICAÇÃO
# ==========================================
def calculate_score(row):
    pred_a, pred_b = row['pred_a'], row['pred_b']
    real_a, real_b = row['real_a'], row['real_b']
    if pd.isna(real_a) or pd.isna(real_b) or real_a == "" or real_b == "": return 0
    real_win, real_draw, real_loss = real_a > real_b, real_a == real_b, real_a < real_b
    pred_win, pred_draw, pred_loss = pred_a > pred_b, pred_a == pred_b, pred_a < pred_b
    if pred_a == real_a and pred_b == real_b: return 10
    if real_draw and pred_draw: return 5
    if (real_win and pred_win) or (real_loss and pred_loss):
        if (real_win and pred_a == real_a) or (real_loss and pred_b == real_b): return 6
        if (real_win and pred_b == real_b) or (real_loss and pred_a == real_a): return 5
        return 4
    return 0

def acerto_gols_vencedor(row):
    pred_a, pred_b = row['pred_a'], row['pred_b']
    real_a, real_b = row['real_a'], row['real_b']
    if pd.isna(real_a) or pd.isna(real_b) or real_a == real_b: return 0
    if real_a > real_b: return int(pred_a == real_a)
    return int(pred_b == real_b)

def calcular_classificacao_grupo(df_grupo):
    tabela = {}
    for time in pd.concat([df_grupo['team_a'], df_grupo['team_b']]).unique():
        tabela[time] = {'Pts': 0, 'J': 0, 'V': 0, 'E': 0, 'D': 0, 'GP': 0, 'GC': 0, 'SG': 0}
    for _, row in df_grupo.iterrows():
        ta, tb = row['team_a'], row['team_b']
        ra, rb = row['real_a'], row['real_b']
        if pd.notna(ra) and pd.notna(rb) and str(ra).strip() != "" and str(rb).strip() != "":
            ra, rb = int(ra), int(rb)
            tabela[ta]['J'] += 1
            tabela[tb]['J'] += 1
            tabela[ta]['GP'] += ra
            tabela[tb]['GP'] += rb
            tabela[ta]['GC'] += rb
            tabela[tb]['GC'] += ra
            if ra > rb:
                tabela[ta]['Pts'] += 3
                tabela[ta]['V'] += 1
                tabela[tb]['D'] += 1
            elif ra < rb:
                tabela[tb]['Pts'] += 3
                tabela[tb]['V'] += 1
                tabela[ta]['D'] += 1
            else:
                tabela[ta]['Pts'] += 1
                tabela[tb]['Pts'] += 1
                tabela[ta]['E'] += 1
                tabela[tb]['E'] += 1
    for time in tabela:
        tabela[time]['SG'] = tabela[time]['GP'] - tabela[time]['GC']
    df_tab = pd.DataFrame.from_dict(tabela, orient='index').reset_index()
    df_tab = df_tab.rename(columns={'index': 'Seleção'})
    df_tab = df_tab.sort_values(by=['Pts', 'SG', 'GP'], ascending=[False, False, False]).reset_index(drop=True)
    df_tab.index = df_tab.index + 1
    return df_tab

# ==========================================
# 4. INTERFACE DO STREAMLIT
# ==========================================
st.title("🏆 Bolão DIRCO - Copa do Mundo 2026")

aba1, aba2, aba3, aba4, aba5, aba6 = st.tabs(
    ["📝 Fazer Palpites", "📊 Ranking", "📜 Regras", "⚙️ Admin", "🔎 Consultar Meus Palpites", "🔮 Simulador"]
)

# --- ABA 1: FORMULÁRIO DE PALPITES ---
with aba1:
    agora = pd.Timestamp.now(tz="America/Sao_Paulo")
    
    if agora >= PRAZO_FINAL:
        st.error("⛔ **PALPITES ENCERRADOS!**")
        st.warning("O prazo expirou. Acompanhe o seu desempenho na aba **Ranking**!")
    else:
        st.info(f"⏳ O formulário ficará aberto para novos envios e alterações até o dia **{PRAZO_FINAL.strftime('%d/%m/%Y às %H:%M')}** (Horário de Brasília). Seus palpites anteriores serão substituídos ao usar o mesmo e-mail.")
        st.header("Envie ou Altere seus Palpites")
        
        email_input_raw = st.text_input("Digite seu E-mail e aperte 'Enter' para iniciar ou carregar seus palpites:", key="email_inicio")
        email_input = email_input_raw.strip().lower()  
        
        if email_input:
            df_atual = conn.read(worksheet="Palpites", ttl=15)
            df_atual = df_atual.dropna(subset=['email'])
            df_atual = df_atual[df_atual['email'].astype(str).str.strip() != ""]
            
            palpites_existentes = {}
            nome_existente = ""
            email_encontrado = False
            
            if not df_atual.empty:
                df_atual['email_norm'] = df_atual['email'].astype(str).str.strip().str.lower()
                df_atual = df_atual.drop_duplicates(subset=['email_norm', 'game_id'], keep='last')
                
                if email_input in df_atual['email_norm'].values:
                    email_encontrado = True
                    df_usuario = df_atual[df_atual['email_norm'] == email_input]
                    nome_existente = df_usuario.iloc[-1]['nome']
                    for _, r in df_usuario.iterrows():
                        palpites_existentes[r['game_id']] = {'pred_a': int(r['pred_a']), 'pred_b': int(r['pred_b'])}
            
            if email_encontrado:
                st.success("✅ Bem-vindo de volta! Carregamos seus palpites anteriores. Modifique os placares que desejar e clique em Salvar.")
            else:
                st.info("👋 E-mail novo! Preencha seus dados abaixo. Os jogos estão inicialmente com o placar de 0 x 0.")

            with st.form("form_palpites", clear_on_submit=False):
                nome_participante = st.text_input("Seu Nome Completo:", value=nome_existente, max_chars=50)
                st.subheader("Fase de Grupos")
                novos_palpites = []
                
                grupos_unicos = sorted(df_oficiais['grupo'].dropna().unique())
                for grupo in grupos_unicos:
                    with st.expander(f"Jogos do Grupo {grupo}", expanded=False):
                        jogos_do_grupo = df_oficiais[df_oficiais['grupo'] == grupo]
                        col_palpites, col_info = st.columns([1.5, 1], gap="large")
                        
                        with col_palpites:
                            for index, row in jogos_do_grupo.iterrows():
                                g_id = row['game_id']
                                t_a, t_b = row['team_a'], row['team_b']
                                data_jogo, local_jogo = row.get('data', 'Data Indefinida'), row.get('local', 'Sede Indefinida')
                                
                                img_a = f"<img src='https://flagcdn.com/32x24/{flags_iso.get(t_a, 'un')}.png' width='28' style='vertical-align: middle; margin-left: 10px; border-radius: 3px; box-shadow: 1px 1px 3px rgba(0,0,0,0.3);'>"
                                img_b = f"<img src='https://flagcdn.com/32x24/{flags_iso.get(t_b, 'un')}.png' width='28' style='vertical-align: middle; margin-right: 10px; border-radius: 3px; box-shadow: 1px 1px 3px rgba(0,0,0,0.3);'>"
                                st.markdown(f"<div style='text-align: center; color: #003882; font-size: 13px; font-weight: bold; margin-bottom: 5px; opacity: 0.8;'>📅 {data_jogo} &nbsp;|&nbsp; 📍 {local_jogo}</div>", unsafe_allow_html=True)
                                
                                val_a = palpites_existentes.get(g_id, {}).get('pred_a', 0)
                                val_b = palpites_existentes.get(g_id, {}).get('pred_b', 0)
                                
                                c1, c2, c3, c4, c5 = st.columns([2.5, 1, 0.5, 1, 2.5])
                                with c1: st.markdown(f"<h5 style='text-align: right; color:#003882; margin-top:3px;'>{t_a} {img_a}</h5>", unsafe_allow_html=True)
                                with c2: gols_a = st.number_input("", key=f"a_{g_id}", step=1, min_value=0, value=val_a, label_visibility="collapsed")
                                with c3: st.markdown("<h5 style='text-align: center; color:#003882; margin-top:3px;'>X</h5>", unsafe_allow_html=True)
                                with c4: gols_b = st.number_input("", key=f"b_{g_id}", step=1, min_value=0, value=val_b, label_visibility="collapsed")
                                with c5: st.markdown(f"<h5 style='text-align: left; color:#003882; margin-top:3px;'>{img_b} {t_b}</h5>", unsafe_allow_html=True)

                                novos_palpites.append({"participant_id": "", "nome": nome_participante, "email": email_input, "game_id": g_id, "pred_a": gols_a, "pred_b": gols_b})
                                st.write("")
                                st.divider()
                                
                        with col_info:
                            st.markdown(f"<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)
                            st.markdown(f"<h6 style='text-align: center; color:#003882;'>📊 Classificação Oficial - Grupo {grupo}</h6>", unsafe_allow_html=True)
                            st.dataframe(calcular_classificacao_grupo(jogos_do_grupo)[['Seleção', 'Pts', 'J', 'SG']], use_container_width=True, hide_index=True)
                            st.markdown("<h6 style='text-align: center; color:#003882; margin-top: 15px;'>⚽ Resultados Oficiais</h6>", unsafe_allow_html=True)
                            for _, row in jogos_do_grupo.iterrows():
                                ra, rb = row['real_a'], row['real_b']
                                if pd.notna(ra) and pd.notna(rb) and str(ra).strip() != "": st.markdown(f"<div style='text-align: center; font-size: 14px;'>{row['team_a']} <b>{int(ra)} x {int(rb)}</b> {row['team_b']}</div>", unsafe_allow_html=True)
                                else: st.markdown(f"<div style='text-align: center; font-size: 14px; color: gray;'>{row['team_a']} - x - {row['team_b']}</div>", unsafe_allow_html=True)

                submit = st.form_submit_button("⚽ Salvar Palpites")
                if submit:
                    if nome_participante.strip() == "":
                        st.error("Por favor, preencha o seu nome antes de salvar.")
                    else:
                        df_atualizacao = conn.read(worksheet="Palpites", ttl=15)
                        tamanho_planilha_original = len(df_atualizacao)
                        
                        if not df_atualizacao.empty and 'email' in df_atualizacao.columns:
                            df_atualizacao = df_atualizacao.dropna(subset=['email', 'game_id'])
                            df_atualizacao = df_atualizacao[df_atualizacao['email'].astype(str).str.strip() != ""]
                            df_atualizacao['email_norm'] = df_atualizacao['email'].astype(str).str.strip().str.lower()
                            
                            if email_input in df_atualizacao['email_norm'].values:
                                id_part = df_atualizacao[df_atualizacao['email_norm'] == email_input]['participant_id'].iloc[0]
                                df_tabela_limpa = df_atualizacao[df_atualizacao['email_norm'] != email_input].copy()
                            else:
                                num_usuarios = len(df_atualizacao['email_norm'].unique())
                                id_part = f"P{num_usuarios + 1:02d}"
                                df_tabela_limpa = df_atualizacao.copy()
                            df_tabela_limpa = df_tabela_limpa.drop(columns=['email_norm'])
                        else:
                            id_part = "P01"
                            df_tabela_limpa = pd.DataFrame(columns=["participant_id", "nome", "email", "game_id", "pred_a", "pred_b"])
                        
                        for p in novos_palpites:
                            p['participant_id'] = id_part
                            if p['pred_a'] is None: p['pred_a'] = 0
                            if p['pred_b'] is None: p['pred_b'] = 0
                            
                        df_final = pd.concat([df_tabela_limpa, pd.DataFrame(novos_palpites)], ignore_index=True)
                        
                        df_final['email_norm'] = df_final['email'].astype(str).str.strip().str.lower()
                        df_final = df_final.drop_duplicates(subset=['email_norm', 'game_id'], keep='last')
                        df_final = df_final.drop(columns=['email_norm'])
                        
                        tamanho_novo = len(df_final)
                        if tamanho_novo < tamanho_planilha_original:
                            df_vazio = pd.DataFrame("", index=range(tamanho_planilha_original - tamanho_novo), columns=df_final.columns)
                            df_salvar = pd.concat([df_final, df_vazio], ignore_index=True)
                        else:
                            df_salvar = df_final
                            
                        conn.update(worksheet="Palpites", data=df_salvar)
                        st.cache_data.clear()
                        st.success(f"Palpites de {nome_participante} salvos com sucesso! Boa sorte no bolão! 🍀")

# --- ABA 2: RANKING ---
with aba2:
    st.header("Ranking Atualizado")

    df_palpites_rank = conn.read(worksheet="Palpites", ttl=15)
    df_oficiais_rank = conn.read(worksheet="Resultados", ttl=15)

    df_palpites_rank = df_palpites_rank.dropna(subset=['email', 'game_id'])
    df_palpites_rank = df_palpites_rank[df_palpites_rank['email'].astype(str).str.strip() != ""]

    if df_palpites_rank.empty:
        st.info("Nenhum palpite foi registrado no banco de dados ainda.")
    else:
        df_palpites_rank['email'] = df_palpites_rank['email'].astype(str).str.strip().str.lower()
        df_palpites_rank = df_palpites_rank.drop_duplicates(subset=['email', 'game_id'], keep='last')
        
        df_analise = pd.merge(df_palpites_rank, df_oficiais_rank[['game_id', 'real_a', 'real_b']], on='game_id', how='left')
        df_analise['real_a'] = pd.to_numeric(df_analise['real_a'], errors='coerce')
        df_analise['real_b'] = pd.to_numeric(df_analise['real_b'], errors='coerce')
        df_analise['pred_a'] = pd.to_numeric(df_analise['pred_a'], errors='coerce')
        df_analise['pred_b'] = pd.to_numeric(df_analise['pred_b'], errors='coerce')
        
        df_analise['pontos'] = df_analise.apply(calculate_score, axis=1)
        df_analise['acerto_vencedor'] = df_analise.apply(acerto_gols_vencedor, axis=1)

        df_ranking = df_analise.groupby(['email', 'nome']).agg(total_pontos=('pontos', 'sum'), placares_exatos=('pontos', lambda x: (x == 10).sum()), gols_vencedor=('acerto_vencedor', 'sum')).reset_index()
        df_ranking = df_ranking.sort_values(by=['total_pontos', 'placares_exatos', 'gols_vencedor'], ascending=[False, False, False]).reset_index(drop=True)
        df_ranking.index = df_ranking.index + 1
        
        num_participantes = len(df_ranking)
        total_arrecadado = num_participantes * 100
        
        if num_participantes <= 30: distribuicao = [("🥇 1º Lugar", 0.60), ("🥈 2º Lugar", 0.25), ("🥉 3º Lugar", 0.15)]
        elif num_participantes <= 40: distribuicao = [("🥇 1º Lugar", 0.50), ("🥈 2º Lugar", 0.25), ("🥉 3º Lugar", 0.15), ("🏅 4º Lugar", 0.10)]
        elif num_participantes <= 50: distribuicao = [("🥇 1º Lugar", 0.45), ("🥈 2º Lugar", 0.22), ("🥉 3º Lugar", 0.15), ("🏅 4º Lugar", 0.10), ("🏅 5º Lugar", 0.08)]
        else: distribuicao = [("🥇 1º Lugar", 0.40), ("🥈 2º Lugar", 0.20), ("🥉 3º Lugar", 0.15), ("🏅 4º Lugar", 0.10), ("🏅 5º Lugar", 0.08), ("🏅 6º Lugar", 0.07)]

        st.info(f"**💰 Pote Atual Estimado: R$ {total_arrecadado:,.2f}** ({num_participantes} participantes na disputa)".replace(",", "X").replace(".", ",").replace("X", "."))
        
        cols_premio = st.columns(len(distribuicao))
        for i, (posicao, percentual) in enumerate(distribuicao):
            cols_premio[i].metric(posicao, f"R$ {(total_arrecadado * percentual):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            
        st.divider()
        col_m1, col_m2, col_m3 = st.columns(3)
        if len(df_ranking) > 0: col_m1.metric("🥇 1º Colocado", df_ranking.iloc[0]['nome'], f"{int(df_ranking.iloc[0]['total_pontos'])} pts", delta_color="off")
        if len(df_ranking) > 1: col_m2.metric("🥈 2º Colocado", df_ranking.iloc[1]['nome'], f"{int(df_ranking.iloc[1]['total_pontos'])} pts", delta_color="off")
        if len(df_ranking) > 2: col_m3.metric("🥉 3º Colocado", df_ranking.iloc[2]['nome'], f"{int(df_ranking.iloc[2]['total_pontos'])} pts", delta_color="off")

        st.dataframe(df_ranking[['nome', 'total_pontos', 'placares_exatos', 'gols_vencedor']].rename(columns={'nome': 'Participante', 'total_pontos': 'Pontos', 'placares_exatos': 'Placares Exatos', 'gols_vencedor': 'Acertos Gols Vencedor'}), use_container_width=True)
        
        if len(df_ranking) > 0:
            top = df_ranking.iloc[0]
            empatados_primeiro = df_ranking[(df_ranking['total_pontos'] == top['total_pontos']) & (df_ranking['placares_exatos'] == top['placares_exatos']) & (df_ranking['gols_vencedor'] == top['gols_vencedor'])]
            if len(empatados_primeiro) > 1:
                st.warning(f"🏆 Existem {len(empatados_primeiro)} participantes empatados após todos os critérios de desempate. Conforme o regulamento, o prêmio deverá ser dividido.")

        if df_ranking['total_pontos'].sum() > 0:
            st.subheader("Desempenho Visual")
            fig, ax = plt.subplots(figsize=(10, max(4, len(df_ranking) * 0.5)))
            fig.patch.set_alpha(0.0)
            ax.patch.set_alpha(0.0)
            cores_grafico = ['#003882' if i % 2 == 0 else '#FFFFFF' for i in range(len(df_ranking))]
            sns.barplot(data=df_ranking, x='total_pontos', y='nome', palette=cores_grafico, ax=ax, orient='h')
            plt.xlabel("Pontuação Total", fontweight='bold', color='#003882')
            plt.ylabel("Participante", fontweight='bold', color='#003882')
            for p in ax.patches:
                if p.get_width() > 0:
                    ax.annotate(format(p.get_width(), '.0f'), (p.get_width() + 0.5, p.get_y() + p.get_height() / 2.), ha='left', va='center', xytext=(0, 0), textcoords='offset points', fontweight='bold', color='#003882')
            sns.despine()
            ax.tick_params(axis='x', colors='#003882')
            ax.tick_params(axis='y', colors='#003882')
            st.pyplot(fig)

# --- ABA 3: REGRAS ---
with aba3:
    st.header("📜 Regras do Bolão DIRCO 2026")
    st.markdown("""### 1. Valor da Inscrição\n**R$ 100,00**\n\n### 2. PIX para Pagamento\n**glaucorisperi@bb.com.br** (Banco do Brasil)\n\n### 3. Prazo para Envio dos Palpites\nTodos os **72 jogos da fase de grupos** deverão estar preenchidos até:\n\n**11/06/2026 às 14h00 (Horário de Brasília)**\n\n---\n\n## 4. Sistema de Pontuação\n\n### Exemplo 1\n**Resultado Oficial:** Brasil **2 x 1** Marrocos\n\n| Palpite | Pontos | Critério |\n|----------|---------|----------|\n| Brasil 0 x 1 Marrocos | 0 | Errou resultado |\n| Brasil 0 x 0 Marrocos | 0 | Errou resultado |\n| Brasil 1 x 0 Marrocos | 4 | Acerto somente do vencedor |\n| Brasil 3 x 1 Marrocos | 5 | Acerto do vencedor + gols do perdedor |\n| Brasil 2 x 0 Marrocos | 6 | Acerto do vencedor + gols do vencedor |\n| Brasil 2 x 1 Marrocos | 10 | Acerto do placar exato |\n\n### Exemplo 2\n**Resultado Oficial:** Brasil **2 x 2** Marrocos\n\n| Palpite | Pontos | Critério |\n|----------|---------|----------|\n| Brasil 1 x 0 Marrocos | 0 | Errou resultado |\n| Brasil 1 x 2 Marrocos | 0 | Errou resultado |\n| Brasil 0 x 0 Marrocos | 5 | Acerto somente do empate |\n| Brasil 2 x 2 Marrocos | 10 | Acerto do placar exato |\n\n---\n\n## 5. Premiação Dinâmica\n\nA distribuição do prêmio total será definida de acordo com o número final de participantes inscritos:\n\n**Até 30 Participantes:**\n* 1º lugar: 60%\n* 2º lugar: 25%\n* 3º lugar: 15%\n\n**De 31 a 40 Participantes:**\n* 1º lugar: 50%\n* 2º lugar: 25%\n* 3º lugar: 15%\n* 4º lugar: 10%\n\n**De 41 a 50 Participantes:**\n* 1º lugar: 45%\n* 2º lugar: 22%\n* 3º lugar: 15%\n* 4º lugar: 10%\n* 5º lugar: 8%\n\n**Acima de 50 Participantes:**\n* 1º lugar: 40%\n* 2º lugar: 20%\n* 3º lugar: 15%\n* 4º lugar: 10%\n* 5º lugar: 8%\n* 6º lugar: 7%\n\n---\n\n## 6. Critérios de Desempate\n\n### 6.1\nMaior quantidade de **placares exatos**.\n\n### 6.2\nMaior quantidade de **acertos dos gols do vencedor do jogo**.\n\n### 6.3\nPersistindo o empate, o prêmio será dividido entre os participantes empatados.\n\n**Exemplo:** Empate entre dois participantes em 2º lugar.\nSoma-se o valor destinado ao **2º e ao 3º colocado** e divide-se igualmente entre os dois participantes.""")

# --- ABA 4: PAINEL ADMIN ---
with aba4:
    st.header("⚙️ Controle do Administrador")
    senha_input = st.text_input("Digite a Senha de Acesso:", type="password")
    
    if senha_input == SENHA_ADMIN:
        st.success("Acesso Liberado! Sincronizado com o Google Sheets.")
        
        st.subheader("Atualizar Resultados dos Jogos")
        df_admin = conn.read(worksheet="Resultados", ttl=15)
        df_atualizado = st.data_editor(df_admin, column_config={"game_id": st.column_config.TextColumn("ID", disabled=True), "data": st.column_config.TextColumn("Data", disabled=True), "local": st.column_config.TextColumn("Sede", disabled=True), "grupo": st.column_config.TextColumn("Grupo", disabled=True), "team_a": st.column_config.TextColumn("Seleção A", disabled=True), "team_b": st.column_config.TextColumn("Seleção B", disabled=True), "real_a": st.column_config.NumberColumn("Gols A", min_value=0, step=1), "real_b": st.column_config.NumberColumn("Gols B", min_value=0, step=1)}, hide_index=True, use_container_width=True)
        
        if st.button("💾 Salvar Resultados na Planilha"):
            conn.update(worksheet="Resultados", data=df_atualizado)
            st.cache_data.clear()
            st.success("Tabela Oficial updated! Recarregando...")
            st.rerun() 
            
        st.write("") 
        if st.button("🔄 Atualizar App e Ranking (Forçar Leitura)"):
            st.cache_data.clear()
            st.rerun()
            
        st.divider()
        st.subheader("🗑️ Excluir Palpites de um Usuário")
        
        df_palpites_admin = conn.read(worksheet="Palpites", ttl=15)
        df_palpites_admin = df_palpites_admin.dropna(subset=['email'])
        df_palpites_admin = df_palpites_admin[df_palpites_admin['email'].astype(str).str.strip() != ""]
        
        if not df_palpites_admin.empty:
            usuarios_cadastrados = df_palpites_admin['email'].unique()
            if len(usuarios_cadastrados) > 0:
                usuario_para_excluir = st.selectbox("Selecione o e-mail do participante que deseja remover:", usuarios_cadastrados)
                
                if st.button("❌ Apagar Palpites Deste Usuário"):
                    tamanho_original = len(df_palpites_admin)
                    df_palpites_limpo = df_palpites_admin[df_palpites_admin['email'] != usuario_para_excluir]
                    
                    tamanho_novo = len(df_palpites_limpo)
                    if tamanho_novo < tamanho_original:
                        df_vazio = pd.DataFrame("", index=range(tamanho_original - tamanho_novo), columns=df_palpites_limpo.columns)
                        df_salvar_admin = pd.concat([df_palpites_limpo, df_vazio], ignore_index=True)
                    else:
                        df_salvar_admin = df_palpites_limpo
                        
                    conn.update(worksheet="Palpites", data=df_salvar_admin)
                    st.cache_data.clear()
                    st.success(f"Todos os palpites de {usuario_para_excluir} deletados!")
                    st.rerun()
            else: st.info("Nenhum participante registrado ainda.")
        else: st.info("Nenhum participante registrado ainda.")
            
        st.divider()
        st.subheader("⚠️ Área de Perigo Total")
        
        if st.button("🚨 ZERAR O BOLÃO INTEIRO PARA ENTRAR EM PRODUÇÃO"):
            tamanho_original = len(conn.read(worksheet="Palpites", ttl=15))
            df_zerado_palpites = pd.DataFrame(columns=["participant_id", "nome", "email", "game_id", "pred_a", "pred_b"])
            if tamanho_original > 0:
                df_vazio = pd.DataFrame("", index=range(tamanho_original), columns=df_zerado_palpites.columns)
                df_salvar_reset = pd.concat([df_zerado_palpites, df_vazio], ignore_index=True)
            else: df_salvar_reset = df_zerado_palpites
                
            conn.update(worksheet="Palpites", data=df_salvar_reset)
            df_zerado_resultados = df_admin.copy()
            df_zerado_resultados['real_a'] = np.nan
            df_zerado_resultados['real_b'] = np.nan
            conn.update(worksheet="Resultados", data=df_zerado_resultados)
            st.cache_data.clear()
            st.success("SISTEMA RESETADO COM SUCESSO!")
            st.rerun()
            
    elif senha_input != "": st.error("Senha incorreta.")
        
# ==========================================
# ABA 5 - CONSULTAR MEUS PALPITES
# ==========================================
with aba5:
    st.header("🔎 Consultar Meus Palpites")
    st.info("Digite o e-mail utilizado no cadastro para visualizar os palpites registrados.")

    email_consulta_raw = st.text_input("E-mail utilizado no cadastro", key="consulta_email_aba5")
    email_consulta = email_consulta_raw.strip().lower()

    if st.button("Buscar Meus Palpites"):
        if not email_consulta: st.warning("Informe um e-mail.")
        else:
            df_palpites_consulta = conn.read(worksheet="Palpites", ttl=15)
            df_palpites_consulta = df_palpites_consulta.dropna(subset=['email', 'game_id'])
            df_palpites_consulta = df_palpites_consulta[df_palpites_consulta['email'].astype(str).str.strip() != ""]

            if df_palpites_consulta.empty: st.error("Nenhum palpite cadastrado.")
            else:
                df_palpites_consulta['email_norm'] = df_palpites_consulta['email'].astype(str).str.strip().str.lower()
                df_palpites_consulta = df_palpites_consulta.drop_duplicates(subset=['email_norm', 'game_id'], keep='last')
                df_usuario = df_palpites_consulta[df_palpites_consulta['email_norm'] == email_consulta]

                if len(df_usuario) == 0: st.error("Nenhum palpite encontrado para este e-mail.")
                else:
                    nome_usuario = df_usuario.iloc[0]["nome"]
                    st.success(f"Palpites encontrados para {nome_usuario}")

                    df_exibicao = pd.merge(df_usuario, df_oficiais[["game_id", "data", "grupo", "local", "team_a", "team_b"]], on="game_id", how="left")
                    grupos = sorted(df_exibicao["grupo"].dropna().unique())

                    for grupo in grupos:
                        with st.expander(f"Grupo {grupo}", expanded=False):
                            col_meus, col_reais = st.columns([1.5, 1], gap="large")
                            jogos_grupo = df_exibicao[df_exibicao["grupo"] == grupo]
                            
                            with col_meus:
                                st.markdown("<h6 style='text-align: center; color:#003882;'>O Que Eu Apostei</h6>", unsafe_allow_html=True)
                                for _, jogo in jogos_grupo.iterrows():
                                    st.markdown(f"**📅 {jogo['data']}**<br><b>{jogo['team_a']} {int(jogo['pred_a'])} x {int(jogo['pred_b'])} {jogo['team_b']}</b><br>📍 {jogo['local']}", unsafe_allow_html=True)
                                    st.divider()
                                    
                            with col_reais:
                                df_ofc_grupo = df_oficiais[df_oficiais['grupo'] == grupo]
                                st.markdown(f"<h6 style='text-align: center; color:#003882;'>📊 Classificação Oficial - Grupo {grupo}</h6>", unsafe_allow_html=True)
                                st.dataframe(calcular_classificacao_grupo(df_ofc_grupo)[['Seleção', 'Pts', 'J', 'SG']], use_container_width=True, hide_index=True)
                                st.markdown("<h6 style='text-align: center; color:#003882; margin-top: 15px;'>⚽ Resultados Oficiais</h6>", unsafe_allow_html=True)
                                for _, row in df_ofc_grupo.iterrows():
                                    ra, rb = row['real_a'], row['real_b']
                                    if pd.notna(ra) and pd.notna(rb) and str(ra).strip() != "": st.markdown(f"<div style='text-align: center; font-size: 14px;'>{row['team_a']} <b>{int(ra)} x {int(rb)}</b> {row['team_b']}</div>", unsafe_allow_html=True)
                                    else: st.markdown(f"<div style='text-align: center; font-size: 14px; color: gray;'>{row['team_a']} - x - {row['team_b']}</div>", unsafe_allow_html=True)

                    st.divider()
                    st.subheader("📋 Resumo Completo")
                    tabela = df_exibicao[["data", "grupo", "team_a", "pred_a", "pred_b", "team_b"]].copy()
                    tabela.columns = ["Data", "Grupo", "Seleção A", "Gols A", "Gols B", "Seleção B"]
                    st.dataframe(tabela, use_container_width=True, hide_index=True)
                    st.download_button("📥 Baixar Meus Palpites", tabela.to_csv(index=False).encode("utf-8-sig"), file_name=f"palpites_{nome_usuario}.csv", mime="text/csv")

# ==========================================
# ABA 6 - SIMULADOR DE RESULTADOS
# ==========================================
with aba6:
    st.header("🔮 Simulador de Resultados")
    st.info("Brinque com os placares dos jogos para ver como ficaria a classificação geral! **As alterações feitas aqui não afetam o ranking oficial.**")

    df_palpites_sim = conn.read(worksheet="Palpites", ttl=15)
    df_oficiais_sim = conn.read(worksheet="Resultados", ttl=15)
    df_palpites_sim = df_palpites_sim.dropna(subset=['email', 'game_id'])
    df_palpites_sim = df_palpites_sim[df_palpites_sim['email'].astype(str).str.strip() != ""]

    if df_palpites_sim.empty: st.warning("Nenhum palpite registrado ainda para fazer simulações.")
    else:
        df_palpites_sim['email'] = df_palpites_sim['email'].astype(str).str.strip().str.lower()
        df_palpites_sim = df_palpites_sim.drop_duplicates(subset=['email', 'game_id'], keep='last')
        
        st.subheader("1. Digite seus resultados hipotéticos")
        df_simulacao = df_oficiais_sim.copy()
        df_editado = st.data_editor(df_simulacao, column_config={"game_id": st.column_config.TextColumn("ID", disabled=True), "data": st.column_config.TextColumn("Data", disabled=True), "local": st.column_config.TextColumn("Sede", disabled=True), "grupo": st.column_config.TextColumn("Grupo", disabled=True), "team_a": st.column_config.TextColumn("Seleção A", disabled=True), "team_b": st.column_config.TextColumn("Seleção B", disabled=True), "real_a": st.column_config.NumberColumn("Gols A (Simulação)", min_value=0, step=1), "real_b": st.column_config.NumberColumn("Gols B (Simulação)", min_value=0, step=1)}, hide_index=True, use_container_width=True, key="simulador_editor")

        st.subheader("2. Veja como ficaria a tabela")
        if st.button("🚀 Calcular Ranking Simulado"):
            df_analise_sim = pd.merge(df_palpites_sim, df_editado[['game_id', 'real_a', 'real_b']], on='game_id', how='left')
            df_analise_sim['real_a'] = pd.to_numeric(df_analise_sim['real_a'], errors='coerce')
            df_analise_sim['real_b'] = pd.to_numeric(df_analise_sim['real_b'], errors='coerce')
            df_analise_sim['pred_a'] = pd.to_numeric(df_analise_sim['pred_a'], errors='coerce')
            df_analise_sim['pred_b'] = pd.to_numeric(df_analise_sim['pred_b'], errors='coerce')
            
            df_analise_sim['pontos'] = df_analise_sim.apply(calculate_score, axis=1)
            df_analise_sim['acerto_vencedor'] = df_analise_sim.apply(acerto_gols_vencedor, axis=1)

            df_ranking_sim = df_analise_sim.groupby(['email', 'nome']).agg(total_pontos=('pontos', 'sum'), placares_exatos=('pontos', lambda x: (x == 10).sum()), gols_vencedor=('acerto_vencedor', 'sum')).reset_index()
            df_ranking_sim = df_ranking_sim.sort_values(by=['total_pontos', 'placares_exatos', 'gols_vencedor'], ascending=[False, False, False]).reset_index(drop=True)
            df_ranking_sim.index = df_ranking_sim.index + 1

            st.dataframe(df_ranking_sim[['nome', 'total_pontos', 'placares_exatos', 'gols_vencedor']].rename(columns={'nome': 'Participante', 'total_pontos': 'Pontos Simulação', 'placares_exatos': 'Placares Exatos', 'gols_vencedor': 'Acertos Vencedor'}), use_container_width=True)
            st.success("Cálculo realizado!")
