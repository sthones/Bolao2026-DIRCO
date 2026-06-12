import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import requests
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ==========================================
# CONFIGURAÇÃO INICIAL E ESTÉTICA
# ==========================================
st.set_page_config(page_title="Bolão DIRCO - Copa do Mundo 2026", page_icon="🏆", layout="wide")

SENHA_ADMIN = "dirco2026" 
API_KEY = "08c35382bdaf4a812b2025b1e6266551"

st.markdown("""
    <style>
    .stApp, .main { background-color: #FFDF00 !important; }
    .stApp, p, span, div, label, h1, h2, h3, h4, h5, h6, li { color: #003882 !important; }
    button[data-baseweb="tab"] { background-color: transparent !important; }
    button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p { color: #003882 !important; font-weight: 800 !important; font-size: 18px !important; }
    button[data-baseweb="tab"][aria-selected="true"] { border-bottom: 4px solid #003882 !important; }
    .stButton>button, .stButton>button p { background-color: #003882 !important; color: #FFDF00 !important; font-weight: 900 !important; border: none !important; border-radius: 6px; transition: all 0.3s ease; }
    .stButton>button:hover, .stButton>button:hover p { background-color: #FFFFFF !important; color: #003882 !important; border: 2px solid #003882 !important; }
    .streamlit-expanderHeader { background-color: #F8CB00 !important; color: #003882 !important; font-weight: bold; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. CARGA DE DADOS E DICIONÁRIOS
# ==========================================
tradutor_api = {
    "México": "Mexico", "África do Sul": "South Africa", "Coreia do Sul": "South Korea", "República Tcheca": "Czech Republic",
    "Canadá": "Canada", "Bósnia e Herzegovina": "Bosnia", "Catar": "Qatar", "Suíça": "Switzerland",
    "Brasil": "Brazil", "Marrocos": "Morocco", "Haiti": "Haiti", "Escócia": "Scotland",
    "Estados Unidos": "USA", "Paraguai": "Paraguay", "Austrália": "Australia", "Turquia": "Turkey",
    "Alemanha": "Germany", "Curaçao": "Curacao", "Costa do Marfim": "Ivory Coast", "Equador": "Ecuador",
    "Holanda": "Netherlands", "Japão": "Japan", "Suécia": "Sweden", "Tunísia": "Tunisia",
    "Bélgica": "Belgium", "Egito": "Egypt", "Irã": "Iran", "Nova Zelândia": "New Zealand",
    "Espanha": "Spain", "Cabo Verde": "Cape Verde", "Arábia Saudita": "Saudi Arabia", "Uruguai": "Uruguay",
    "França": "France", "Senegal": "Senegal", "Iraque": "Iraq", "Noruega": "Norway",
    "Argentina": "Argentina", "Argélia": "Algeria", "Áustria": "Austria", "Jordânia": "Jordan",
    "Portugal": "Portugal", "República Democrática do Congo": "DR Congo", "Uzbequistão": "Uzbekistan", "Colômbia": "Colombia",
    "Inglaterra": "England", "Croácia": "Croatia", "Gana": "Ghana", "Panamá": "Panama"
}
reverso_api = {v: k for k, v in tradutor_api.items()}

def carregar_jogos_iniciais():
    times_list = list(tradutor_api.keys())
    cidades = {1: "Atlanta", 2: "Boston", 3: "Dallas", 4: "Houston", 5: "Kansas City", 6: "Los Angeles", 7: "Miami", 8: "Nova York/Nova Jersey", 9: "Filadélfia", 10: "São Francisco", 11: "Seattle", 12: "Toronto", 13: "Vancouver", 14: "Guadalajara", 15: "Cidade do México", 16: "Monterrey"}
    jogos_csv = """1,1,2,15,2026-06-11,A\n2,3,4,14,2026-06-11,A\n3,5,6,12,2026-06-12,B\n4,13,14,6,2026-06-12,D\n5,7,8,10,2026-06-13,B\n6,9,10,8,2026-06-13,C\n7,11,12,2,2026-06-13,C\n8,15,16,13,2026-06-14,D\n9,17,18,4,2026-06-14,E\n10,21,22,3,2026-06-14,F\n11,19,20,9,2026-06-14,E\n12,23,24,16,2026-06-14,F\n13,29,30,1,2026-06-15,H\n14,25,26,11,2026-06-15,G\n15,31,32,7,2026-06-15,H\n16,27,28,6,2026-06-15,G\n17,33,34,8,2026-06-16,I\n18,35,36,2,2026-06-16,I\n19,37,38,5,2026-06-16,J\n20,39,40,10,2026-06-17,J\n21,41,42,4,2026-06-17,K\n22,45,46,3,2026-06-17,L\n23,47,48,12,2026-06-17,L\n24,43,44,15,2026-06-17,K\n25,4,2,1,2026-06-18,A\n26,8,6,6,2026-06-18,B\n27,5,7,13,2026-06-18,B\n28,1,3,14,2026-06-18,A\n29,13,15,11,2026-06-19,D\n30,12,10,2,2026-06-19,C\n31,9,11,9,2026-06-19,C\n32,16,14,10,2026-06-20,D\n33,21,23,4,2026-06-20,F\n34,17,19,12,2026-06-20,E\n35,20,18,5,2026-06-20,E\n36,24,22,16,2026-06-21,F\n37,29,31,1,2026-06-21,H\n38,25,27,6,2026-06-21,G\n39,32,30,7,2026-06-21,H\n40,28,26,13,2026-06-21,G\n41,37,39,3,2026-06-22,J\n42,33,35,9,2026-06-22,I\n43,36,34,8,2026-06-22,I\n44,40,38,10,2026-06-22,J\n45,41,43,4,2026-06-23,K\n46,45,47,2,2026-06-23,L\n47,48,46,12,2026-06-23,L\n48,44,42,14,2026-06-23,K\n49,8,5,13,2026-06-24,B\n50,6,7,11,2026-06-24,B\n51,12,9,7,2026-06-24,C\n52,10,11,1,2026-06-24,C\n53,4,1,15,2026-06-24,A\n54,2,3,16,2026-06-24,A\n55,18,19,9,2026-06-25,E\n56,20,17,8,2026-06-25,E\n57,22,23,3,2026-06-25,F\n58,24,21,5,2026-06-25,F\n59,16,13,6,2026-06-25,D\n60,14,15,10,2026-06-25,D\n61,36,33,2,2026-06-26,I\n62,34,35,12,2026-06-26,I\n63,30,31,4,2026-06-26,H\n64,32,29,14,2026-06-26,H\n65,26,27,11,2026-06-26,G\n66,28,25,13,2026-06-26,G\n67,48,45,8,2026-06-27,L\n68,46,47,9,2026-06-27,L\n69,44,41,7,2026-06-27,K\n70,42,43,1,2026-06-27,K\n71,38,39,5,2026-06-27,J\n72,40,37,3,2026-06-27,J"""

    world_cup_games = []
    for linha in jogos_csv.split('\n'):
        if not linha.strip(): continue
        g_id, t_a, t_b, c_id, data, grupo = linha.split(',')
        ano, mes, dia = data.split('-')
        
        nome_a = times_list[int(t_a)-1]
        nome_b = times_list[int(t_b)-1]
        
        world_cup_games.append({"game_id": f"WC26_G{int(g_id):03d}", "data": f"{dia}/{mes}/{ano}", "local": cidades[int(c_id)], "grupo": grupo, "team_a": nome_a, "team_b": nome_b, "real_a": np.nan, "real_b": np.nan})
    return pd.DataFrame(world_cup_games)

# ==========================================
# MOTOR DA API DE FUTEBOL (Sincronização Ativa)
# ==========================================
@st.cache_data(ttl=60) # Atualiza a cada minuto para bater com o live score
def extrair_dados_api():
    url = "https://v3.football.api-sports.io/fixtures"
    querystring = {"league": "1", "season": "2026"}
    headers = {"x-apisports-key": API_KEY}
    try:
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

# ==========================================
# 2. CONEXÃO COM GOOGLE SHEETS
# ==========================================
conn = st.connection("gsheets", type=GSheetsConnection)

df_oficiais = conn.read(worksheet="Resultados", ttl=15) 
if df_oficiais.empty or 'data' not in df_oficiais.columns:
    df_base_jogos = carregar_jogos_iniciais()
    conn.update(worksheet="Resultados", data=df_base_jogos)
    df_oficiais = df_base_jogos

# AUTOSALVAMENTO E SINCRONIZAÇÃO EM TEMPO REAL
dados_json = extrair_dados_api()
houve_gol = False

if dados_json and dados_json.get("results", 0) > 0:
    for partida in dados_json["response"]:
        time_a_eng = partida["teams"]["home"]["name"]
        time_b_eng = partida["teams"]["away"]["name"]
        gols_a = partida["goals"]["home"]
        gols_b = partida["goals"]["away"]
        status = partida["fixture"]["status"]["short"]
        
        time_a_pt = reverso_api.get(time_a_eng, time_a_eng)
        time_b_pt = reverso_api.get(time_b_eng, time_b_eng)
        
        if status in ["1H", "2H", "HT", "ET", "P", "FT", "AET", "PEN"] and gols_a is not None and gols_b is not None:
            idx = df_oficiais.index[(df_oficiais['team_a'] == time_a_pt) & (df_oficiais['team_b'] == time_b_pt)].tolist()
            if idx:
                i = idx[0]
                real_a_banco = df_oficiais.at[i, 'real_a']
                real_b_banco = df_oficiais.at[i, 'real_b']
                
                # Só escreve no banco se o placar oficial de fato tiver mudado
                if pd.isna(real_a_banco) or pd.isna(real_b_banco) or int(real_a_banco) != int(gols_a) or int(real_b_banco) != int(gols_b):
                    df_oficiais.at[i, 'real_a'] = int(gols_a)
                    df_oficiais.at[i, 'real_b'] = int(gols_b)
                    houve_gol = True

if houve_gol:
    conn.update(worksheet="Resultados", data=df_oficiais)
    st.cache_data.clear()

df_palpites_geral = conn.read(worksheet="Palpites", ttl=15)
if df_palpites_geral.empty or 'email' not in df_palpites_geral.columns:
    df_base_palpites = pd.DataFrame(columns=["participant_id", "nome", "email", "game_id", "pred_a", "pred_b"])
    conn.update(worksheet="Palpites", data=df_base_palpites)
    df_palpites_geral = df_base_palpites

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
    ["🗓️ Jogos do Dia", "📊 Ranking", "📜 Regras", "⚙️ Admin", "🔎 Consultar Meus Palpites", "🔮 Simulador"]
)

# --- ABA 1: JOGOS DO DIA (SUBSTITUI O ENVIO DE PALPITES) ---
with aba1:
    st.header("🗓️ Palpites da Rodada")
    st.info("A fase de envio de palpites foi encerrada! Acompanhe abaixo os jogos do dia e os palpites de todos os participantes de forma transparente.")
    
    # Extrai datas únicas para o seletor
    datas_disponiveis = sorted(df_oficiais['data'].dropna().unique().tolist(), key=lambda x: pd.to_datetime(x, format='%d/%m/%Y'))
    
    # Data de hoje para colocar como padrão no filtro
    hoje_str = pd.Timestamp.now(tz="America/Sao_Paulo").strftime("%d/%m/%Y")
    idx_padrao = datas_disponiveis.index(hoje_str) if hoje_str in datas_disponiveis else 0
    
    data_selecionada = st.selectbox("Selecione a data dos jogos:", datas_disponiveis, index=idx_padrao)
    
    jogos_dia = df_oficiais[df_oficiais['data'] == data_selecionada]
    
    df_palpites_dia = conn.read(worksheet="Palpites", ttl=15)
    df_palpites_dia = df_palpites_dia.dropna(subset=['email', 'game_id'])
    df_palpites_dia['email_norm'] = df_palpites_dia['email'].astype(str).str.strip().str.lower()
    df_palpites_dia = df_palpites_dia.drop_duplicates(subset=['email_norm', 'game_id'], keep='last')
    
    if jogos_dia.empty:
        st.warning("Não há jogos agendados para esta data.")
    else:
        for _, jogo in jogos_dia.iterrows():
            st.subheader(f"⚽ {jogo['team_a']} x {jogo['team_b']}")
            
            ra = jogo['real_a']
            rb = jogo['real_b']
            placar_of = f"{int(ra)} x {int(rb)}" if pd.notna(ra) and pd.notna(rb) else "Aguardando Início..."
            
            st.markdown(f"**Grupo {jogo['grupo']}** &nbsp;|&nbsp; 📍 {jogo['local']} &nbsp;|&nbsp; **Placar Oficial:** `{placar_of}`")
            
            palpites_do_jogo = df_palpites_dia[df_palpites_dia['game_id'] == jogo['game_id']]
            
            if palpites_do_jogo.empty:
                st.write("Nenhum palpite foi registrado para este jogo.")
            else:
                tabela_palpites = palpites_do_jogo[['nome', 'pred_a', 'pred_b']].copy()
                tabela_palpites['pred_a'] = pd.to_numeric(tabela_palpites['pred_a'], downcast='integer')
                tabela_palpites['pred_b'] = pd.to_numeric(tabela_palpites['pred_b'], downcast='integer')
                
                tabela_palpites = tabela_palpites.rename(columns={
                    'nome': 'Participante',
                    'pred_a': f"Palpite {jogo['team_a']}",
                    'pred_b': f"Palpite {jogo['team_b']}"
                }).sort_values(by='Participante')
                
                st.dataframe(tabela_palpites, use_container_width=True, hide_index=True)
            st.divider()

# --- ABA 2: RANKING E DASHBOARD DINÂMICO ---
with aba2:
    st.header("Ranking Atualizado (Sincronizado ao Vivo 📡)")

    df_palpites_rank = conn.read(worksheet="Palpites", ttl=15)
    df_oficiais_rank = df_oficiais

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
    st.markdown("""### 1. Valor da Inscrição\n**R$ 100,00**\n\n### 2. PIX para Pagamento\n**glaucorisperi@bb.com.br** (Banco do Brasil)\n\n### 3. Prazo para Envio dos Palpites\nTodos os **72 jogos da fase de grupos** deverão 