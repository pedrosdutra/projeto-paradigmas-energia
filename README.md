# Projeto Paradigmas · Tarifas de energia no Brasil

Compare as tarifas residenciais de energia dos 26 estados e do Distrito Federal, escolha uma data e clique no mapa para ver as distribuidoras de cada estado. [Abrir o painel](https://pedrosdutra.github.io/projeto-paradigmas-energia/)

Em **Comparar estados**, marque as UFs para ver as tarifas em R$/kWh e a diferença entre a maior e a menor média da seleção.

| Pasta | O que você encontra |
| --- | --- |
| [projeto](projeto/) | Código em Python, dados da ANEEL, mapa do IBGE e tela do painel. |
| [docs](docs/) | Página pronta que o GitHub publica e que o aplicativo abre no computador. |

## Abrir no Windows

Para usar a cópia do computador, baixe o projeto em **Code → Download ZIP**, extraia os arquivos e abra o PowerShell na pasta que contém `app.py`. Com o Python 3.12 ou superior instalado, execute uma linha de cada vez.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Abra o endereço que aparecer no terminal. Nas próximas vezes, use apenas o último comando. Pressione Ctrl+C para encerrar.

## Atualizar o painel

Se você alterar os cálculos em Python, gere os resultados novamente. Se alterar apenas a tela, comece pela segunda linha. Para essa etapa, use Node.js 20 ou superior.

```powershell
.\.venv\Scripts\python.exe projeto/exportar_frontend.py
cd projeto/interface
npm ci
npm run build
cd ../..
```

A página pronta fica em `docs/index.html`. Para repetir a coleta da ANEEL, execute `projeto/baixar_dados.py --anos 2024 2025` com o Python antes dos comandos acima. A coleta substitui os dados locais pelos que a fonte devolver.

Os dados de tarifas e atendimento são da ANEEL, sob a licença Open Database License (ODbL). O desenho dos estados é do IBGE. Os endereços das fontes e a data da coleta estão no [registro da coleta](projeto/dados/fontes.json).
