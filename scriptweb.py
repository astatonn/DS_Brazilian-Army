import csv # Lib para trabalhar com arquivos csv
import requests # Lib para fazer requisições HTTP
from bs4 import BeautifulSoup # Lib para analisar e tratar o html retornado da requisição

"""
Desenvolvido por Lucas Lima @astatonn
Função: Realizar a coleta de dados do portal portalweb.dgp.eb.mil.br
        Que contém as informações sobre licenciamento de militares

Processo:   Foi feito um laço de iteração com requisições POST entre
            os anos das turmas de 2024 até 1994 e salvando os dados 
            em um arquivo .csv para análise futura.
"""

""" 
O ACESSO AO SITE É RESTRITO, PRIMEIRAMENTE, O ACESSO FOI FEITO VIA
VPN E APÓS O LOGIN, FOI VERIFICADO NO CONSOLE DE DESENVOLVEDOR QUE
UMA VARIÁVEL DE SESSÃO COM O NOME 'PHPSESSID' FOI GERADA PERMITINDO
O ACESSO AO SITE, DESSA MANEIRA, A MESMA FOI ARMAZENADA EM UMA VA-
RIÁVEL PARA USO DURANTE A REQUSIÇÃO AO SITE
"""
# Armazendo informação do cookie da sessão.
cookies = {
    # 'PHPSESSID': '*****************************',
    'PHPSESSID': 'ku37hbfm4e31ok4mnqm3eputcv',
}


"""
AO LOGAR NO SITE E ACESSAR A ABA 'TURMA' PELO NAVEGADOR, A MESMA APRE-
SENTAVA UM FORMULÁRIO COM TRÊS CAMPOS: 'curso', 'ano' e 'cidade', SEN-
DO O ÚLTIMO, OPCIONAL. O FORMULÁRIO ENVIAVA AS INFORMAÇÕES PARA A MES-
MA ROTA 
https://portalweb.dgp.eb.mil.br/informacoespessoal/pesquisacidadecurso
ENTÃO, AO VERIFICAR O CAMPO SELECT DOS CURSOS, FOI OBSERVADO QUE O VA-
LUE DOS CAMPOS ERA ESPECÍFICO, DESSA MANEIRA, UM DICIONÁRIO FOI CRIADO.
"""

# Definir os cursos
cursos = {
    '007': 'AMAN - Infantaria',
    '002': 'AMAN - Cavalaria',
    '006': 'AMAN - Artilharia',
    '005': 'AMAN - Engenharia',
    '010': 'AMAN - Intendência',
    '011': 'AMAN - Comunicações',
    '009': 'AMAN - Material Bélico',
    '0014': 'IME - Engenheiro Militar',
    '018': 'EsSEx - Médico',
    '017': 'EsSEx - Farmacêutico',
    '016': 'EsSEx - Dentista',
    '019': 'EsVEx - Veterinário',
    '015': 'EsAEx - QCO',
    '566': 'Sgt - Infantaria',
    '567': 'Sgt - Cavalaria',
    '568': 'Sgt - Artilharia',
    '569': 'Sgt - Engenharia',
    '570': 'Sgt - Comunicações',
    '571': 'Sgt - Saúde - Apoio',
    '579': 'Sgt - Saúde - Aux Enfermagem',
    'ADA01': 'Sgt - Saúde - Téc Enfermagem',
    '572': 'Sgt - Mat Bel - Mnt Armt',
    '573': 'Sgt - Mat Bel - Mnt Vtr Auto',
    '574': 'Sgt - Mat Bel - Mec Op',
    '575': 'Sgt - Intendência',
    '577': 'Sgt - topografia',
    '576': 'Sgt - Mnt Com',
    '578': 'Sgt - Corneteiro/Clarim',
    'W01': 'Sgt - Adm Dep',
    'W03': 'Sgt - Form não Ident',
    'W04': 'Sgt - Enfermeiro Vet (Em extinção)',
    '58A': 'Sgt - Aviação do Exército - Mnt',
    '58B': 'Sgt - Aviação do Exército - Apoio',
    'W51': 'Sgt - Músico',
}

# Função para enviar a requisição POST
def post_requesition(base_url, ano, curso):
    # Preparando o payload para a requisição POST
    payload = {
        'ano': ano,
        'curso': curso
    }
    
    # Enviar a requisição POST
    """
    AQUI É ONDE SE OBTÉM OS DADOS COM A URL, O PAYLOAD,
    QUE SÃO OS CAMPOS DO FORMULÁRIO, OS COOKIES, QUE 
    CONTÉM OS DADOS DA SESSÃO E O CAMPO 'verify' COM O
    VALOR FALSE, DIZ PARA FAZER UMA REQUISIÇÃO ATRAVÉS
    DO PROTOCOLO HTTP E NÃO HTTPS. 
    """
    response = requests.post(base_url, data=payload, cookies=cookies, verify=False)
    
    # Caso haja sucesso (cód. 200), retorna o conteúdo
    if response.status_code == 200:
        return response.content
    # Caso contrário, retorna que houve erro para acessar o dado
    else:
        print(f"Erro ao acessar {base_url} para o ano {ano} e curso {curso}")
        return None

# Função para processar o conteúdo HTML e extrair as informações da tabela
def processar_resposta(response_content, ano, curso_id, nome_curso, writer):
    # Transforma o response de texto para  um objeto.
    soup = BeautifulSoup(response_content, 'html.parser')
    
    """
    ANALIZANDO A PÁGINA, AS INFORMAÇÕES QUE INTERESSAVAM
    ESTAVAM NA TABELA COM ID 'listTable3', QUE ERA REFE-
    RENTE AOS EXCLUÍDOS DA TURMA.
    """
    # Encontrar a tabela de informações
    table = soup.find('table', {'id': 'listTable4'})
    
    # Caso a tabela exista
    if table:
        # Iterar sobre as linhas da tabela (tr)
        for row in table.find_all('tr')[1:]:  # pular o cabeçalho

            # Itera sobre cada linha analizando cada uma das colunas
            cols = row.find_all('td')
            if len(cols) == 4:  # Certificando que a linha tem 4 colunas

                # Salva as informações em variáveis
                posto_grad = cols[0].get_text(strip=True)
                nome = cols[1].get_text(strip=True)
                data = cols[2].get_text(strip=True)
                motivo_exclusao = cols[3].get_text(strip=True)
                
                # Escrever as informações no arquivo CSV
                writer.writerow([ano, nome_curso, curso_id, posto_grad, nome, data, motivo_exclusao])


# Função principal
def main(csv_file, base_url):
    
    # Abertura do arquivo/criação do arquivo csv
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        # Chama o método de escrita de arquivo.
        writer = csv.writer(file)
        # Criando o cabeçalho no arquivo .csv
        writer.writerow(['Ano', 'Curso', 'Curso ID', 'Posto Graduação', 'Nome', 'Turma', 'Data'])

        """
        PARA O ESTUDO, FOI ESTIPULADO QUE SERIAM ANALISADOS OS DADOS DAS TURMA DE 1994 ATÉ 2024 (30 ANOS)
        """
        # Percorrer os anos de 2024 até 1994
        for ano in range(2024, 1993, -1):

            # Para cada ano, percorrer os cursos
            for curso_id, nome_curso in cursos.items():
                print(f"Enviando requisição para {nome_curso} ({ano})")

                # Chama a função para realizar a requisição
                response_content = post_requesition(base_url, ano, curso_id)
                
                # Após o retorno da informação, a mesma é tratada com o BeautifulSoup4
                if response_content:
                    # Processar a resposta e gravar as informações no CSV
                    processar_resposta(response_content, ano, curso_id, nome_curso, writer)


"""
O CÓDIGO É INICIADO AQUI COM DUAS CONSTANTES A
BASE_URL COM A URL A SER ANALISADA E O NOME DO
ARQUIVO CSV A SER GERADO. APÓS ISSO, A FUNÇÃO
MAIN É CHAMADA.
"""
BASE_URL = 'https://portalweb.dgp.eb.mil.br/informacoespessoal/pesquisacidadecurso'
CSV_FILE = 'dados_cursos_excluidos_turma.csv'

if __name__ == '__main__':
    main(CSV_FILE, BASE_URL)
