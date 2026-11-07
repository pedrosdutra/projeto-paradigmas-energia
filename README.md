# Análise e Visualização Interativa das Tarifas de Energia Elétrica por Estado do Brasil

MVP acadêmico com **processamento funcional em Python e interface em React + Tailwind CSS**. O Streamlit serve o painel localmente; a versão original em Streamlit/Plotly também foi preservada para estudo em `app_streamlit.py`. A versão entregue inclui **dados reais da ANEEL**, malha das 27 UFs do IBGE e uma interface com fonte única de tarifas: ANEEL. Os exemplos sintéticos são usados somente nos testes, fora do painel. O mapa e os dados incluídos não dependem de download durante a navegação. A interface React já está compilada no pacote: **não é necessário instalar Node.js para abrir o painel**. A fonte Inter é solicitada ao Google Fonts; sem internet, a interface usa a fonte do sistema.

## 1. Comece por aqui — Windows

Se você obteve o projeto pelo GitHub, use **Code → Download ZIP** e extraia o arquivo, ou clone o repositório. Execute os comandos na pasta que contém `app.py`. O HTML compilado está versionado para que a execução local não exija Node.js.

1. Extraia `projeto_tarifas.zip` para uma pasta, por exemplo `C:\Projetos\projeto_tarifas`.
2. Instale Python 3.12 ou superior pelo [site oficial](https://www.python.org/downloads/windows/), se ainda não tiver. Na instalação, habilite a opção de adicionar Python ao PATH. O projeto foi verificado com Python 3.14.
3. Abra a pasta no VS Code ou no Explorador de Arquivos. Clique na barra de endereço, digite `powershell` e pressione Enter.
4. Execute os comandos abaixo, um de cada vez, na pasta que contém `app.py`:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

5. Abra o endereço indicado no terminal, normalmente `http://localhost:8501`.
6. Escolha o ano, observe o mapa e o ranking e selecione uma UF para detalhar TE, TUSD e distribuidoras.
7. Para encerrar o servidor, pressione `Ctrl+C` no terminal.

Não é necessário ativar o ambiente virtual nem alterar a política de execução do Windows: os comandos chamam diretamente seu Python. Se `python` não for encontrado mas `py` funcionar, use `py -3 -m venv .venv` para criar o ambiente. Nas próximas vezes, basta executar o último comando, dentro da pasta do projeto.

A primeira instalação precisa de internet. Depois disso, os CSVs e o GeoJSON incluídos permitem a demonstração local sem novas consultas às fontes. Atualizações dos dados são explícitas, não automáticas.

## 2. O que está funcionando

- Mapa coroplético de 26 estados e Distrito Federal, incluindo UFs sem dados em cinza.
- Comparação de tarifas vigentes em uma data comum; anos iniciais: 2024 e 2025.
- Ranking por média simples das distribuidoras observadas, com quantidade, mínimo e máximo.
- Detalhamento por UF ao clicar no mapa SVG, usar Enter/Espaço sobre uma UF ou escolher o nome no seletor.
- Busca por nome ou sigla, com ou sem acento. Atalho Ctrl+K (Command+K no Mac), com o painel em foco.
- Exportação do ranking com data, método e identificação da origem.
- Carregamento automático da base ANEEL, com validação, sem upload nem troca de fonte na interface.
- Diagnóstico de linhas inválidas, conflitos e CNPJs sem mapeamento temporal registrado no JSON exportado e documentado em VALIDACAO.md.
- Navegação em **Visão geral** e **Ranking**. Mapa e detalhamento lado a lado no desktop e empilhados no celular. Ranking com busca e nomes completos dos estados.
- Testes automatizados do núcleo Python, exportação de resultados, busca, cores e CSV. Interações React conferidas diretamente no navegador.

## 3. Estrutura e responsabilidade de cada arquivo

```text
projeto_tarifas/
├── app.py                     Servidor Streamlit do painel React compilado
├── app_streamlit.py           Interface original em Streamlit/Plotly (alternativa)
├── exportar_frontend.py       Gera o snapshot a partir do núcleo funcional
├── frontend/
│   ├── src/App.jsx            Navegação, referência e UF selecionada
│   ├── src/components/        Mapa, detalhe, ranking e busca
│   ├── src/lib/format.mjs      Formatação, escala e exportação CSV
│   ├── src/data/painel.json   Resultados oficiais calculados em Python
│   ├── src/styles.css         Tema e regras responsivas com Tailwind
│   ├── dist/painel.html       Interface pronta, incluída no pacote
│   ├── scripts/build.mjs      Compila e incorpora JS/CSS no HTML
│   ├── tests/data.test.mjs    Testes JavaScript
│   ├── package.json          Dependências e comandos de desenvolvimento
│   └── package-lock.json     Versões do ambiente frontend
├── processamento.py           Validação, normalização e objetos imutáveis
├── analise.py                 Fotografia temporal, médias e ranking
├── arquivos.py                Leitura e gravação de arquivos (efeitos)
├── visualizacao.py            Construção do mapa Plotly
├── baixar_dados.py             Coleta reproduzível da ANEEL e do IBGE
├── gerar_exemplo.py            Geração determinística de exemplos fictícios
├── requirements.txt           Dependências em faixas compatíveis
├── requirements-lock.txt      Versões efetivamente verificadas nesta entrega
├── pytest.ini                 Configuração dos testes
├── README.md                  Instalação, fontes e metodologia
├── VALIDACAO.md                Resultados dos testes e limites verificados
├── tests/
│   ├── test_nucleo.py
│   ├── test_exportacao.py
│   └── test_app.py            Testes opcionais da interface original
└── dados/
    ├── tarifas_aneel.csv       Recorte oficial, exportado pela API CKAN
    ├── evidencias_indger.csv   Municípios e UC ativa por distribuidora/mês
    ├── mapeamento_aneel.csv    Vínculos CNPJ–UF derivados dessas evidências
    ├── brasil_ufs.geojson     Malha simplificada oficial do IBGE
    ├── fontes.json            URLs, filtros, data de coleta e hashes SHA-256
    ├── exemplo_sintetico.csv  Valores fictícios para testes
    └── mapeamento_sintetico.csv
```

## 4. Dados oficiais: o que foi realmente verificado

Consulta e coleta realizadas em **6 de novembro de 2026**. O recurso de tarifas da ANEEL estava disponível por CSV e API CKAN. Foi verificado o cabeçalho e o início do CSV real: UTF-8, separador `;`, campos entre aspas, vírgula decimal e ocorrências como `,00`. Para evitar baixar toda a base de modalidades, o arquivo incluído foi exportado pela API com paginação completa do recorte. **Não é o CSV integral** e não foi obtido de um site intermediário.

Fonte: [Tarifas de aplicação das distribuidoras — ANEEL](https://dadosabertos.aneel.gov.br/dataset/tarifas-distribuidoras-energia-eletrica).

[Download do CSV integral oficial](https://dadosabertos.aneel.gov.br/dataset/5a583f3e-1646-4f67-bf0f-69db4203e89e/resource/fcf2906c-7c32-4b9b-a637-054e7a5234f4/download/tarifas-homologadas-distribuidoras-energia-eletrica.csv).

Campos efetivamente encontrados:

| Campos | Uso no projeto |
|---|---|
| `SigAgente`, `NumCNPJDistribuidora` | Nome e identidade da distribuidora; junção por CNPJ |
| `DatInicioVigencia`, `DatFimVigencia` | Intervalo em que a tarifa se aplica |
| `DscBaseTarifaria`, `DscSubGrupo` | Tarifa de aplicação e subgrupo B1 |
| `DscModalidadeTarifaria` | Modalidade convencional |
| `DscClasse`, `DscSubClasse` | Residencial comum, sem baixa renda |
| `DscDetalhe` | Exclui, entre outros, o detalhe SCEE |
| `NomPostoTarifario`, `SigAgenteAcessante` | Exige “Não se aplica” |
| `DscUnidadeTerciaria` | Unidade; observada como MWh no recorte |
| `VlrTE`, `VlrTUSD` | Componentes da tarifa |
| `DscREH`, `DatGeracaoConjuntoDados` | Resolução e rastreabilidade da publicação |

O CSV tarifário **não possui UF**. Não extraímos a UF do nome da empresa nem do endereço da sede.

Para geografia, usamos [INDGER — dados comerciais da ANEEL](https://dadosabertos.aneel.gov.br/dataset/indger-indicadores-gerenciais-da-distribuicao/resource/fd10c9d4-cb76-4020-a322-e79afb13eaf7): `NumCNPJ`, `CodMunicipioIBGE`, `DatReferenciaInformada`, `QtdUCAtiva` e `SigAgente`. Municípios com quantidade de unidades consumidoras ativas maior que zero fornecem evidência observada de atendimento. Os dois primeiros dígitos do código municipal identificam a UF. A malha vem da [API oficial do IBGE](https://servicodados.ibge.gov.br/api/docs/malhas?versao=3).

Esse mapeamento **é derivado de observações de atendimento, não um cadastro completo de contratos de concessão**. Mantemos somente o mês observado: dezembro/2024 e dezembro/2025. Não extrapolamos a presença para meses, anos ou CNPJs diferentes. Distribuidoras em mais de um estado podem entrar uma vez em cada UF. Transferências de concessão e mudanças de CNPJ não são resolvidas por semelhança de nome.

## 5. Metodologia — por que o cálculo é assim

1. Filtrar tarifa de aplicação; subgrupo B1; modalidade convencional; classe e subclasse residencial; detalhe, posto e acessante “Não se aplica”. A função compara os rótulos sem depender de caixa, acento ou espaços extras, mas não aceita categorias desconhecidas por aproximação.
2. Validar datas, componentes numéricos, identificação e unidade. Valores ausentes, negativos, infinitos, datas incoerentes e unidade de demanda `kW` não entram. Zero explícito é diferente de dado ausente.
3. Normalizar: tarifa = TE + TUSD. Se os valores estiverem em R$/MWh, dividir cada componente por 1.000 para obter R$/kWh. Se já forem kWh, não dividir novamente. A conta usa `Decimal`; a conversão para `float` fica apenas na exibição.
4. Selecionar `início ≤ data de referência ≤ fim`. O filtro de ano oferece somente referências com tarifas e vínculos compatíveis. Na base incluída, as datas são 31/12/2024 e 31/12/2025. A data é exibida ao lado do filtro; o calendário livre foi removido. **Não calculamos média anual**; a duração de cada vigência não é usada como peso porque não estamos resumindo o ano inteiro.
5. Agrupar por CNPJ antes de calcular. Repetições com mesmos componentes não ganham peso. Se houver mais de um par TE/TUSD vigente e distinto para o mesmo CNPJ, excluir o CNPJ e relatá-lo como conflito, sem escolher a última linha arbitrariamente.
6. Cruzar CNPJ com os vínculos geográficos válidos na data. Um mesmo CNPJ aparece uma vez por UF. CNPJs sem correspondência não são atribuídos a um estado presumido.
7. Para cada UF, calcular `soma das tarifas das distribuidoras observadas / número dessas distribuidoras`. Ordenar do maior para o menor; empates são ordenados alfabeticamente por UF. Os valores são arredondados somente para apresentação.

### Limitações da análise

- A média simples dá o mesmo peso a uma distribuidora pequena e a uma grande. **Não é gasto médio da população, tarifa oficial da UF nem média ponderada de consumo.**
- Ter dado em 27 UFs não significa cobrir todas as distribuidoras ou consumidores. As quantidades ficam na tela; as exclusões estão no JSON exportado e em VALIDACAO.md.
- Não exibimos “média nacional”, porque média entre estados ou distribuidoras não representa automaticamente o consumo nacional.
- Não estimamos conta final. Não adicionamos impostos, bandeiras, custo de disponibilidade ou iluminação pública. A [ANEEL explica os elementos excluídos de seu ranking](https://www.gov.br/aneel/pt-br/centrais-de-conteudos/relatorios-e-indicadores/tarifas-e-informacoes-economico-financeiras), incluindo ressalva sobre tratamento tributário de permissionárias do RJ. O código não desfaz tratamentos já incorporados nos valores publicados.
- Valores nominais de anos diferentes não foram corrigidos pela inflação. Mudanças de cobertura também podem alterar as médias.
- O perfil é residencial comum; tarifa social, tarifa branca, demanda, SCEE e contratos específicos exigem análises próprias.
- Vigências conflitantes são excluídas; não consultamos automaticamente decisões judiciais ou atos posteriores fora da base.
- O carregador valida estrutura e conteúdo. A fonte é fixa na interface, mas os arquivos locais ainda devem ser mantidos pelo responsável pelo projeto; isso não é uma autenticação criptográfica da origem.

## 6. Atualizar ou importar os dados

Para repetir a coleta do recorte e do mapeamento:

```powershell
.\.venv\Scripts\python.exe baixar_dados.py --anos 2024 2025
```

Isso consulta os dados publicados naquele momento e substitui os arquivos oficiais após concluir as consultas. Guarde uma cópia da pasta `dados` caso queira preservar uma versão anterior. `fontes.json` registra filtros, recursos, data e hashes dos arquivos. O hash ajuda a verificar integridade; não é assinatura digital da ANEEL.

Para outro ano, só execute `--anos 2026` quando existir o levantamento de dezembro/2026. A base de tarifas pode ter vigências mais recentes, mas isso não autoriza reutilizar o mapeamento antigo. O coletor interrompe a atualização se o mês não estiver disponível.

### Manutenção dos arquivos oficiais caso o portal/API esteja indisponível

1. Acesse o conjunto de tarifas no portal oficial e baixe o CSV. Não substitua números por estimativas.
2. Prepare o mapeamento com evidência e período comprovados. Use como modelo `mapeamento_aneel.csv`. Campos obrigatórios: `CNPJ;UF;Inicio;Fim;Fonte`. Datas no padrão `AAAA-MM-DD`; CNPJ como texto para preservar zeros iniciais. Não invente a vigência do vínculo. Não preencha UF a partir da sede.
3. A atualização é tarefa de manutenção do projeto, não uma escolha no painel. Guarde uma cópia dos arquivos atuais e substitua `dados/tarifas_aneel.csv` e `dados/mapeamento_aneel.csv` somente por dados oficiais verificados. Preserve as evidências e atualize o manifesto de fontes. O coletor é o caminho preferido para isso.
4. Execute o exportador e confira o diagnóstico antes de interpretar o ranking. Falhas de integridade interrompem a exportação. Linhas inválidas do recorte e exclusões são registradas no JSON exportado. Se não houver referência utilizável, o React apresenta uma mensagem de base indisponível.

Se a atualização falhar, utilize a última coleta oficial íntegra, mantendo sua data visível. O painel React usa um **snapshot compilado**: editar CSVs não altera a tela automaticamente. Após uma coleta concluída, execute `exportar_frontend.py` e compile a interface conforme a seção 9. Enquanto isso, a tela continua mostrando a versão anterior, com sua data de coleta. Se o HTML compilado estiver ausente, `app.py` mostra instruções de compilação. Os arquivos sintéticos permanecem apenas como material de teste e não podem ser selecionados na interface.

## 7. Testes

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

O comando padrão executa 39 casos: 37 do núcleo/integração e 2 da exportação para React. Verificam unidade, vírgula decimal, zeros, categorias incompatíveis, datas, imutabilidade, duplicatas, conflitos, múltiplas UFs, ausência de dados, 27 geometrias e correspondência do snapshot com as fontes. Não consultam a internet. Os 2 testes da interface original ficam fora da seleção padrão; para executá-los, use `python -m pytest -q -m legacy_ui`.



## 8. Fontes, licença e crédito

Dados tarifários e INDGER: Agência Nacional de Energia Elétrica — ANEEL, licença **Open Data Commons Open Database License (ODbL)** indicada no portal. Preserve os créditos e verifique as obrigações da licença ao redistribuir bases derivadas. Geometria: IBGE, API de malhas simplificadas, com URL registrada em `fontes.json`. Este é um trabalho acadêmico independente, sem vínculo institucional com ANEEL ou IBGE.

Documentação técnica consultada: [Streamlit — gráficos Plotly e seleção](https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart), [Plotly — tipos de mapas](https://plotly.com/python/map-configuration/). O arquivo de versões verificadas pode ser instalado com `pip install -r requirements-lock.txt` no mesmo Python/plataforma; `requirements.txt` mantém faixas mais flexíveis para outras instalações.


## 9. Desenvolver a interface React — Windows

Esta etapa só é necessária para modificar o visual ou atualizar os dados exibidos. Para abrir a versão entregue, siga apenas a seção 1. Use Node.js 20 ou superior (verificado com Node 24.11.1 e npm 11.6.2).

Na pasta principal:

```powershell
.\.venv\Scripts\python.exe exportar_frontend.py
cd frontend
npm install
npm test
npm run build
cd ..
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Se o Streamlit já estiver aberto, recarregue a página depois do build. O exportador verifica os hashes dos arquivos oficiais antes de gerar o JSON. `npm run build` empacota o React, o CSS e os resultados no HTML que o Streamlit exibe. A primeira instalação npm precisa de internet; a compilação subsequente utiliza os pacotes locais.

Para editar com atualização automática, abra outro terminal dentro de `frontend` e execute `npm run dev`. Use o endereço impresso pelo Vite. Ele exibe o mesmo React, mas não executa os cálculos Python: após mudar dados ou regras, regenere `src/data/painel.json` pelo exportador. Para entregar a alteração, rode o build novamente.

A versão original pode ser executada com `python -m streamlit run app_streamlit.py`. Ela mantém o mapa Plotly; a nova interface usa SVG gerado da mesma malha oficial, com as mesmas médias. Não misture as explicações dos dois mecanismos de interação.

## 10. Publicação no GitHub Pages

`npm run build`, dentro de `frontend`, também gera `docs/index.html` e `docs/.nojekyll`. A pasta `docs` contém a versão estática do protótipo, com o mesmo mapa, filtros e ranking. No GitHub, a publicação usa **Settings → Pages → Deploy from a branch → main → /docs**. Consulte a [documentação oficial do GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).

O site online exibe o snapshot calculado em Python; o GitHub Pages não executa Python, Streamlit nem coleta dados automaticamente. Para atualizar, execute a coleta quando necessário, gere o JSON com `exportar_frontend.py`, rode `npm run build` e envie os arquivos atualizados ao repositório. O código Python continua disponível para reproduzir a análise e executar o aplicativo localmente.
