# Crawler para disciplinas do Jupiter
# - codcg varia de um range: checar se nao é nulo
# - checar primeiro row: pode ter outras paginas ou nao ter disciplinas
#

from bs4 import BeautifulSoup
import requests
import re

base_jupiter = 'https://uspdigital.usp.br/jupiterweb/'
base_url = base_jupiter + 'jupDisciplinaLista?codcg='
base_disciplina = base_jupiter + 'obterDisciplina?'
tipo_ending = '&tipo=T'
codcg_null = 'Não existe nenhuma disciplina oferecida esta Unidade ou Entidade.'
codcg_range = range(1, 103)

biblio = 'Bibliografia'
met = 'Método'
pr = 'Programa Resumido'
docs = 'Docente(s) Responsável(eis)'
objs = 'Objetivos'
ca = 'Créditos Aula:'

for codcg in codcg_range:
    url = base_url + str(codcg) + tipo_ending
    r = requests.get(url)
    html_doc = r.text
    soup = BeautifulSoup(html_doc, 'html.parser')
    tables = soup.find_all('table')
    if len(tables):
        print("Achei a tabela com as disciplinas!")
        table = tables[1]
        tr = table.tr
        if len(tr): #and table.tr.td.font.span.text.strip() != codcg_null:
            tds = tr.find_all('td')
            a_s = []
            for td in tds:
                a_s.append(td.find_all('a'))
            onepage = False
            for a in a_s:
                print("Verificando as referências...")
                print(f"Olhando a referência: {a}")
                hrefs_for_other_pages = []
                hrefs_disciplinas = []
                if a:
                    # outras paginas para ler
                    print("Página não é única! Temos que verificar a outra também")
                    hrefs_for_other_pages.append(a[0].href)
                elif not onepage:
                    # soh uma pagina para ler
                    print("Página única! Coletando disciplinas...")
                    trs = table.find_all('tr')
                    trs_without_sigla_nome = trs[1:]
                    for tr_dis in trs_without_sigla_nome:
                        a_s_in_tr = tr_dis.find_all('a')
                        for a_s_ in a_s_in_tr:
                            hrefs_disciplinas.append(a_s_.attrs['href'])
                    print("Disciplinas coletadas {}".format(len(hrefs_disciplinas)))
                    
                if len(hrefs_for_other_pages) > 0: # caso tenham outras paginas para ler, verificalas
                    hrefs_disciplinas_todas_paginas = []
                    for pagina in hrefs_for_other_pages:
                        pass
                elif not onepage:
                    onepage = True
                    for href in hrefs_disciplinas:
                        print(href)
                        sgldis = re.findall(r'(?<=\?)[^"]*&', href)[0][:-1] # elemento 0, removendo & no final
                        print(sgldis)
                        url_disciplina = base_disciplina + sgldis
                        print("----------> Vendo a url: {}".format(url_disciplina))
                        r_dis = requests.get(url_disciplina)
                        html_doc_dis = r_dis.text
                        soup_dis = BeautifulSoup(html_doc_dis, 'html.parser')
                        tables_in_page = soup_dis.find_all('table')
                        span_in_page = []
                        for tb in tables_in_page:
                            spans = tb.find_all('span')
                            if spans and spans not in span_in_page:
                                span_in_page.append(tb.find_all('span'))
                        
                        nome_unidade = ''
                        curso = ''
                        dis_nome = ''
                        cred_aula = 0
                        cred_trab = 0
                        ativ = ''
                        horas = 0
                        dis_objs = ''
                        for i in range(len(span_in_page)):
                            span = span_in_page[i]
                            if i == 0:
                                nome_unidade = span[0].text
                                curso = span[1].text
                                dis_nome = span[2].text
                                print(nome_unidade, curso, dis_nome)
                            elif i == 1:
                                cred_aula = int(span[1].text.strip())
                                cred_trab = int(span[3].text.strip())
                                ativ = span[-2:-1][0].text.strip()
                                horas = int(re.sub('\D', '', span[5].text))
                                print(cred_aula, cred_trab, ativ, horas)
                            elif i == 2:
                                dis_objs = span[1].text.strip()
                                print(dis_objs)
                            elif i == 3:
                                docs_resp = list(filter(None,[docs.text.strip() for docs in span[1:]]))
                                print(docs_resp)
                            print('\n\n')
                        # print(span_in_page)
    break