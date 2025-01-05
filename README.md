# PlayerData

# Comparação de Estatísticas de League of Legends
Este é um projeto em Python utilizando a API da Riot Games e a interface do Streamlit para permitir que você compare estatísticas de jogadores de League of Legends. Ele busca as informações sobre o histórico de partidas, desempenho do jogador, como KDA, CS/min, Damage/min, entre outros, e gera uma comparação entre os jogadores.

Funcionalidades
Busca de PUUID: Através do GameName e TagLine do jogador, é possível obter o PUUID necessário para consultar as estatísticas.
Histórico de Partidas: Recupera o histórico de partidas rankeadas do jogador.
Detalhamento de Partidas: Coleta os detalhes das partidas, como kills, deaths, assists, e outras métricas importantes.
Cálculo de Estatísticas: Calcula o KDA médio, CS/min, Damage/min, Gold/min, e muito mais para cada jogador.
Comparação Entre Jogadores: Exibe as estatísticas de vários jogadores em uma tabela comparativa.
Requisitos
Para rodar o projeto, é necessário ter as seguintes bibliotecas instaladas:

requests
pandas
streamlit
concurrent.futures
Você pode instalar as dependências com o seguinte comando:

pip install requests pandas streamlit


Configuração
Obtenção da API Key da Riot: Para utilizar a API da Riot Games, você precisará de uma chave de API (API Key). Se ainda não tem uma, siga as instruções no site da Riot para obter sua chave: Riot Developer Portal.

Como Usar
Execute o Streamlit: Após configurar o ambiente e as dependências, execute o aplicativo Streamlit com o comando:

bash
Copiar código
streamlit run app.py
Interação com a Interface: Na interface, você pode:

Inserir o número de jogadores que deseja comparar (até 5 jogadores).
Para cada jogador, insira o GameName e TagLine.
Clique no botão "Comparar Jogadores" para ver a tabela comparativa com as estatísticas de todos os jogadores inseridos.
Estrutura do Código
Função request_with_retry: Faz requisições à API com tentativas automáticas em caso de falha temporária (erro 429).
Função get_puuid: Obtém o PUUID do jogador a partir do GameName e TagLine.
Função get_match_history: Retorna o histórico de partidas do jogador.
Função get_match_details: Obtém os detalhes de uma partida específica.
Função generate_stats: Processa os dados das partidas e calcula as estatísticas para cada jogador.
Interface Streamlit: Permite que o usuário insira dados de múltiplos jogadores e visualize a tabela comparativa.
