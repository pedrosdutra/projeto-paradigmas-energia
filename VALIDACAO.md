# Registro de validação

## Retoques — apresentação enxuta

Removidos a aba Metodologia, seu componente e o link “Entenda o cálculo”. A identificação lateral passou a “Projeto Paradigmas”. Foram retirados o subtítulo de apresentação, a lista de tecnologias e os parágrafos didáticos do mapa, detalhe e ranking. Rótulos, unidades, referência, fonte e legenda permanecem na interface; método e exclusões continuam documentados nos arquivos do projeto.

Build concluído com 37 módulos. Esta alteração é de navegação e conteúdo visual; não altera os dados nem as funções de cálculo.

## Ajuste visual — modo escuro e mapa azul

A interface atual utiliza fundo grafite, textos claros e destaque azul, conforme a preferência do usuário. A escala do mapa passou para cinco tons de azul; ausência continua cinza, e a seleção recebe contorno branco. O tema foi aplicado também à busca, tabelas, filtros e à configuração local do Streamlit.

O build foi concluído e os 4 testes JavaScript passaram após a alteração. Foram conferidos visualmente o painel e o diálogo de busca no navegador. Nenhuma fórmula, arquivo de tarifas ou referência temporal foi alterado. A captura desta revisão é `painel_escuro.jpg`. O registro abaixo descreve a validação funcional realizada na entrega React anterior.

## Versão atual — React + Tailwind com núcleo Python

Revisão concluída em 6 de novembro de 2026. A interface principal agora é React + Tailwind, exibida pelo Streamlit. A alternativa anterior está em `app_streamlit.py`. Os CSVs oficiais e as funções de cálculo não foram alterados nesta revisão.

Validação automatizada:

```text
Python: 39 passed, 2 deselected in 1.09s
JavaScript: 4 tests, 4 pass, 0 fail
Vite: 38 modules transformed; build concluído
```

Os 39 testes Python são os 37 casos anteriores de núcleo/integração mais 2 casos da exportação. Esses novos casos conferem os hashes das fontes, a igualdade entre o snapshot React e o processamento Python, as 27 geometrias e o HTML autocontido. O hash do JSON incorporado ao HTML detecta uma compilação com dados desatualizados.

Os 4 testes JavaScript conferem UFs e referências, busca sem acentos, conteúdo do CSV e tratamento de ausência/zero na escala. Os 2 testes marcados `legacy_ui` pertencem à interface Streamlit original e não foram reexecutados nesta revisão. A exclusão é explícita no `pytest.ini`; podem ser executados com `python -m pytest -q -m legacy_ui`.

Conferência no navegador integrado:

- Abertura da nova interface com fonte fixa ANEEL, mapa e detalhes.
- Clique na Bahia atualizando o detalhe para BA e suas duas distribuidoras.
- Troca para 31/12/2024, com 102 distribuidoras observadas; seleção de DF mostrando Neoenergia Brasília.
- Busca por `sao paulo` encontrando São Paulo, seleção do resultado e fechamento do diálogo.
- Abertura por clique e atalho Ctrl+K; fechamento por Escape.
- Navegação para ranking, busca sem resultado e acesso à metodologia.
- Seleção geográfica com Enter em tela de 390 × 844.
- Layouts de celular (390 × 844) e notebook (1280 × 900), sem rolagem horizontal da página. O tamanho original do navegador foi restaurado.

O botão de exportação foi acionado sem erro de JavaScript capturado, mas a ferramenta do navegador integrado não confirmou o evento de download. Portanto, não registramos o salvamento do arquivo pelo navegador como aprovado. O conteúdo exportado passou pelos testes; cópias dos mesmos CSVs estão incluídas em `frontend/dist/rankings` para abertura direta.

A interface é um snapshot local, não uma consulta ao vivo. Os testes não certificam todos os navegadores, leitores de tela ou a cobertura integral da fonte. A fonte tipográfica Inter depende de Google Fonts; sem conexão, há alternativa do sistema. Captura desta revisão: `painel_react.jpg`, entregue fora da pasta do projeto.

Ambiente frontend verificado: React 18.3.1, Tailwind CSS 4.1.18, Vite 5.4.21, Node.js 24.11.1 e npm 11.6.2. A interface compilada está incluída, e `node_modules` não faz parte do ZIP.

## Histórico: atualização da interface Streamlit — fonte única ANEEL

Em 6 de novembro de 2026, o painel passou a carregar exclusivamente os arquivos da ANEEL. Foram removidos o seletor de fonte, o upload, o modo sintético da tela e o calendário livre. O mapa e os detalhes agora ficam lado a lado, com abas para ranking e metodologia.

Verificação desta revisão: **37 testes de núcleo/integração passaram em 0,70 s**, e todos os arquivos Python passaram pela compilação de sintaxe. Os dois testes de interface foram atualizados para verificar a fonte única, os períodos válidos e o detalhamento. Sua reexecução ficou bloqueada na criação de um canal local do Windows (`socketpair`/`asyncio`) pelas restrições do ambiente assistido, antes da execução do aplicativo; portanto, o total de 39 aprovações registrado abaixo pertence à versão anterior.

Conferência direta no navegador desta revisão: carregamento do mapa e dos cartões; ausência de troca de fonte e upload; seleção de 2024 com referência 31/12/2024 e 102 distribuidoras; seleção por nome de Distrito Federal e atualização de seu detalhe; abertura da aba de ranking. A base e a metodologia de cálculo não foram alteradas. Os exemplos sintéticos são somente arquivos para testes, sem acesso pela interface.

O comando para executar todos os testes continua sendo `python -m pytest -q`, dentro do ambiente virtual. A captura atualizada da interface é entregue separadamente como `painel_tarifas_atualizado.jpg`.

## Histórico: primeira versão

Verificação realizada em 6 de novembro de 2026, Windows, Python 3.14.0. Versões principais: Streamlit 1.67.0, Plotly 6.9.0, pandas 3.1.1 e pytest 9.2.0. Todas as versões do ambiente constam em `requirements-lock.txt`.

## Resultado automatizado

Comando executado com o Python do ambiente virtual:

```text
python -m pytest -q
....................................... [100%]
39 passed in 5.10s
```

São 37 casos de núcleo/integração e 2 testes de interface. A parametrização permite exercitar várias entradas diferentes. O conjunto de testes não acessa a internet. Os testes de interface precisaram ser executados fora da restrição de execução do ambiente assistido; concluíram normalmente nesse contexto. Isso não requer configuração especial de permissões no computador de apresentação.

Cobertura de comportamento: números brasileiros, valores vazios e inválidos, conversão MWh/kWh, rejeição de kW, perfil residencial comum, datas inválidas, vigência inclusiva, imutabilidade, duplicatas, conflitos com total diferente e com total igual, múltiplas UFs, falta de mapeamento, ausência distinta de zero, CSV malformado, validade mensal do vínculo e 27 geometrias. Na interface: abertura com dados reais, troca de ano, escolha de DF, modo sintético e importação ainda sem arquivos.

## Conferência da base incluída

- 5.450 linhas no recorte recebido da API, mantendo histórico e detalhes para validação local.
- 1.235 linhas fora do perfil final, devido ao detalhe específico; 4.215 linhas históricas comparáveis.
- Nenhuma linha do perfil final apresentou erro de normalização nesta coleta.
- 239 vínculos CNPJ–UF/período derivados das evidências municipais dos dois meses coletados.

| Data | UFs com dados | CNPJs vigentes | CNPJs incluídos | Conflitos | CNPJs sem vínculo utilizável |
|---|---:|---:|---:|---:|---:|
| 31/12/2024 | 27 | 103 | 102 | 0 | 1 |
| 31/12/2025 | 27 | 103 | 101 | 0 | 2 |

Sem vínculo em 2024: `11810343000138`. Sem vínculo em 2025: `11810343000138` e `87462750000163`. Essas ausências não foram preenchidas por inferência. A contagem de distribuidoras é de CNPJs únicos; a soma das quantidades por UF pode ser maior porque uma empresa pode atuar em mais de uma UF.

## Conferência visual

O servidor local foi iniciado e o painel aberto no navegador integrado. Foi verificada a renderização do mapa brasileiro com fronteiras estaduais, cores, legenda e ranking. O clique sobre a Bahia atualizou a seleção para BA; depois, a escolha manual de DF mostrou Neoenergia Brasília e seus componentes TE/TUSD. Essa verificação não garante comportamento idêntico em todos os navegadores. O seletor de UF permanece como alternativa.

Captura de tela entregue separadamente: `painel_tarifas.jpg`.

## Limites da validação

Os testes comprovam os comportamentos exercitados, não a exatidão de todos os registros publicados pela fonte. Não houve auditoria individual de todas as resoluções tarifárias nem comprovação de cobertura integral do INDGER. A geografia deriva de atendimento observado por município; a média continua sendo simples, sem peso de consumo ou clientes. Consulte o README para a metodologia completa.
