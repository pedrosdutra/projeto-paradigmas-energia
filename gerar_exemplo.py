"""Gera dados explicitamente fictícios para demonstrações e testes offline."""
from pathlib import Path
from arquivos import salvar_csv
from processamento import UFS

def gerar():
    pasta=Path(__file__).resolve().parent/'dados'
    linhas=[]
    vinculos=[]
    for ano in (2024,2025):
        for indice,uf in enumerate(UFS):
            cnpj=f'{indice+1:014d}'
            linhas.append({'DatGeracaoConjuntoDados':'2026-11-06','DscREH':'EXEMPLO SINTÉTICO, SEM VALIDADE',
              'SigAgente':f'FICTÍCIA {uf}','NumCNPJDistribuidora':cnpj,
              'DatInicioVigencia':f'{ano}-01-01','DatFimVigencia':f'{ano}-12-31',
              'DscBaseTarifaria':'Tarifa de Aplicação','DscSubGrupo':'B1',
              'DscModalidadeTarifaria':'Convencional','DscClasse':'Residencial',
              'DscSubClasse':'Residencial','DscDetalhe':'Não se aplica','NomPostoTarifario':'Não se aplica',
              'DscUnidadeTerciaria':'MWh','SigAgenteAcessante':'Não se aplica',
              'VlrTE':str(200+indice*3+(ano-2024)*10)+',00','VlrTUSD':str(300+indice*4)+',00'})
            vinculos.append({'CNPJ':cnpj,'UF':uf,'Inicio':f'{ano}-01-01','Fim':f'{ano}-12-31',
                            'Fonte':'SINTÉTICO: empresa e valores inventados para teste'})
    salvar_csv(pasta/'exemplo_sintetico.csv',linhas)
    salvar_csv(pasta/'mapeamento_sintetico.csv',vinculos)

if __name__=='__main__':
    gerar()
    print('Exemplos SINTÉTICOS gerados. Não representam tarifas reais.')
