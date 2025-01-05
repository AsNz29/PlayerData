import os
import time
import requests
import json
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import streamlit as st

# Configurações iniciais
API_KEY = os.getenv("RIOT_API_KEY", "RGAPI-1251abc8-b6d9-4050-a9f2-5933844400f6")
BASE_URL = "https://americas.api.riotgames.com/lol/match/v5/matches"

# Função para lidar com requisições com retries
def request_with_retry(url, headers, params=None, retries=3):
    for attempt in range(retries):
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            time.sleep(2)
        else:
            break
    raise Exception(f"Falha após {retries} tentativas: {response.status_code} - {response.text}")

# Função para buscar PUUID a partir de GameName e TagLine
def get_puuid(game_name, tag_line):
    url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    headers = {"X-Riot-Token": API_KEY}
    data = request_with_retry(url, headers)
    return data["puuid"]

# Função para buscar o histórico de partidas
def get_match_history(puuid, start=0, count=20):
    url = f"{BASE_URL}/by-puuid/{puuid}/ids"
    params = {"type": "ranked", "start": start, "count": count}
    headers = {"X-Riot-Token": API_KEY}
    return request_with_retry(url, headers, params)

# Função para buscar os detalhes de uma partida
def get_match_details(match_id):
    url = f"{BASE_URL}/{match_id}"
    headers = {"X-Riot-Token": API_KEY}
    return request_with_retry(url, headers)

# Função para processar os dados e gerar tabelas
def generate_stats(puuids, player_names):
    all_data = {}
    for player_name, puuid in zip(player_names, puuids):
        st.write(f"Buscando dados para {player_name}...")
        match_history = get_match_history(puuid)
        if not match_history:
            st.write(f"Nenhuma partida encontrada para {player_name}.")
            continue

        data = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            match_details_list = list(executor.map(get_match_details, match_history))

        for match_details in match_details_list:
            participants = match_details["info"]["participants"]
            participant = next((p for p in participants if p["puuid"] == puuid), None)
            if not participant:
                continue

            game_duration = match_details["info"]["gameDuration"] / 60
            if game_duration == 0:
                continue

            kills = participant["kills"]
            deaths = participant["deaths"] if participant["deaths"] > 0 else 1
            assists = participant["assists"]

            data.append({
                "Kills": kills,
                "Deaths": participant["deaths"],
                "Assists": assists,
                "CS/min": (participant["totalMinionsKilled"] + participant["neutralMinionsKilled"]) / game_duration,
                "Damage/min": participant["totalDamageDealtToChampions"] / game_duration,
                "Gold/min": participant["goldEarned"] / game_duration,
                "Tanked/min": participant["totalDamageTaken"] / game_duration,
                "Wards/min": (participant["wardsPlaced"] + participant["wardsKilled"]) / game_duration,
                "Kill Participation": (kills + assists) / max(1, match_details["info"]["teams"][0]["objectives"]["champion"]["kills"]),
                "Win": 1 if participant["win"] else 0
            })

        df = pd.DataFrame(data)
        df["KDA"] = (df["Kills"] + df["Assists"]) / df["Deaths"].replace(0, 1)

        aggregated_data = {
            "Jogador": player_name,
            "Número de Partidas": len(df),
            "KDA Médio": df["KDA"].mean(),
            "CS/min Médio": df["CS/min"].mean(),
            "Damage/min Médio": df["Damage/min"].mean(),
            "Gold/min Médio": df["Gold/min"].mean(),
            "Tanked/min Médio": df["Tanked/min"].mean(),
            "Wards/min Médio": df["Wards/min"].mean(),
            "Win Rate (%)": df["Win"].mean() * 100 if not df["Win"].empty else 0,
            "Kill Participation Médio (%)": df["Kill Participation"].mean() * 100 if not df["Kill Participation"].empty else 0,
            "Média de Mortes": df["Deaths"].mean()
        }

        all_data[player_name] = aggregated_data

    comparison_df = pd.DataFrame.from_dict(all_data, orient="index")
    st.write("--- Comparação Entre Jogadores ---")
    st.dataframe(comparison_df)

# Interface do Streamlit
st.title("Comparação de Estatísticas de League of Legends")
st.write("Insira os GameName e TagLine dos jogadores que deseja comparar.")

num_players = st.number_input("Quantos jogadores deseja comparar?", min_value=1, max_value=5, step=1, value=2)

player_names = []
puuids = []

for i in range(num_players):
    st.subheader(f"Jogador {i + 1}")
    game_name = st.text_input(f"GameName do Jogador {i + 1}").strip()
    tag_line = st.text_input(f"TagLine do Jogador {i + 1}").strip()

    if game_name and tag_line:
        try:
            puuid = get_puuid(game_name, tag_line)
            player_names.append(f"{game_name}#{tag_line}")
            puuids.append(puuid)
        except Exception as e:
            st.error(f"Erro ao buscar dados do jogador {game_name}: {e}")

if st.button("Comparar Jogadores"):
    if len(puuids) == num_players:
        generate_stats(puuids, player_names)
    else:
        st.warning("Por favor, insira os dados de todos os jogadores corretamente.")
