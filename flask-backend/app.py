from flask import Flask, request
from flask_cors import CORS # type: ignore

import uuid
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import arvoreDriver
import gera_id


# Instanciar o gerador de ID
ids = gera_id.GeraId()
# Instanciar o primeiro nó
arvore = arvoreDriver.ArvDriver(id = ids.geraId())

def login(e: str, s: str, id: int):
    driver: webdriver.Chrome = arvore.encontra(id).obtemDriver() # driver, do tipo webdriver.Chrome, recebe...
    wait = WebDriverWait(driver, 20)
    try:    
        # Espera o botão/formulário e clica
        botao = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "uc_flex-r")))
        botao.click()
        print('Botão clicado')

        # Espera o campo de e-mail
        campo_email = wait.until(EC.presence_of_element_located((By.NAME, "loginfmt")))
        campo_email.send_keys(e)
        campo_email.send_keys(Keys.ENTER)

        # Espera o campo de senha
        campo_senha = wait.until(EC.presence_of_element_located((By.NAME, "passwd")))
        print('Digitando senha...')
        campo_senha.send_keys(s)
        botao_entrar = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
        botao_entrar.click()

        # Espera o botão de confirmação (div do perfil)
        campo_texto = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table-row")))
        nome = campo_texto.find_element(By.TAG_NAME, 'div')
        # nome = nome.find_element(By.TAG_NAME, 'div').text
        print(f'Campo encontrado: {nome}')
        campo_texto.click()

        print("Aguardando autenticação por dois fatores (digite o código)...")
     

    except TimeoutException as e:
        print("Erro de tempo ao carregar um elemento da página:", str(e))
        return {'bool': False}
    
    resposta = {'bool': True, 'id': id}
    resposta = json.dumps(resposta, ensure_ascii=False, indent=4)
    print("Login realizado com sucesso!")
    return resposta

def confirmacao(c: str, id: int):
    driver: webdriver.Chrome = arvore.encontra(id).obtemDriver()
    wait = WebDriverWait(driver, 8)
    resposta = {'bool': False} # Padrão da resposta


    try:
        campo_codigo = wait.until(EC.presence_of_element_located((By.ID, "idTxtBx_SAOTCC_OTC")))
        print('Digitando código...')
        campo_codigo.send_keys(c)
        campo_codigo.send_keys(Keys.ENTER)

        try:
            span = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "uc_appuser-name")))
            nome = 'vazio'
            nome = str(span.text.strip().lower()).split(' ')[1] 
            print(nome)
            if nome != 'vazio':
                resposta = {'bool': True, 'nome': nome} # Resposta sucesso
                resposta = json.dumps(resposta, ensure_ascii=False, indent=4)
            else:
                print("Não foi encontrado o nome:", nome)
        except Exception as e:
            print(e)
    except Exception as e:
        print("Um problema foi encontrado:", e)
    print('Terminando requisição confirmação. ID:', id)
    return resposta

def notas_parciais(id: int):
    driver: webdriver.Chrome = arvore.encontra(id).obtemDriver()
    # print(f'Pegando notas parciais do driver ID: {arvore.encontra(id).obtemId()}, Driver: {driver}') # Adicionar em caso de testes
    # Clicar no aba Notas Parciais
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.ID, "ygtvlabelel10Span"))
        )
        driver.find_element(By.ID, "ygtvlabelel10Span").click()
    except:
        print("Botão não encontrado")

    # Pegar notas parciais
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "ReadonlyAttribute"))
        )
        
        notas_ele = driver.find_elements(By.XPATH, "//*[starts-with(@id, 'span_vACD_ALUNOHISTORICOITEMMEDIAFINAL_00')]")
        notas = [nota.text for nota in notas_ele]
        mates_ele = driver.find_elements(By.XPATH, "//*[starts-with(@id, 'span_vACD_DISCIPLINANOME_00')]")
        mates = []
        
        for i in range(len(mates_ele)):
            if mates_ele[i].text.startswith("Projeto Integrador"):
                notas.pop(i)
            else:
                mates.append(mates_ele[i].text)

        # print("Notas parciais obtidas") # Adicionar em caso de testes

        parcial = [{ "tipo": '', "nome": materia, "nota": nota, 'abc': 'D'} for materia, nota in zip(mates, notas)]
        return parcial
    except:
        print("Os elementos com as notas parciais não foram encontrados.")
        return 'Falha parciais' # Em caso desse return, pode haver erros. Arrumar depois (1/2)

def notas_historicas(id: int):
    # Clicar no aba Notas Histórico
    driver: webdriver.Chrome = arvore.encontra(id).obtemDriver()
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.ID, "ygtvlabelel8Span"))
        )
        driver.find_element(By.ID, "ygtvlabelel8Span").click()
    except:
        print("Botão Histórico não encontrado")

    # Pegar notas históricas
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "ReadonlyAttribute"))
        )
        
        notas_ele = driver.find_elements(By.XPATH, "//*[starts-with(@id, 'span_vACD_ALUNOHISTORICOITEMMEDIAFINAL_00')]")
        notas = [nota.text for nota in notas_ele]
        mates_ele = driver.find_elements(By.XPATH, "//*[starts-with(@id, 'span_vACD_DISCIPLINANOME_00')]")
        mates = []
        
        for i in range(len(mates_ele)):
            if mates_ele[i].text.startswith("Projeto Integrador"):
                notas.pop(i)
            else:
                mates.append(mates_ele[i].text)

        # print("Notas históricas obtidas") # Adicionar em caso de testes

        historico = [{ "tipo": 'h', "nome": materia, "nota": nota, 'abc': 'D'} for materia, nota in zip(mates, notas)]
        
        return historico
    except:
        # print("Os elementos com as notas parciais não foram encontrados.") # Adicionar em caso de testes
        return 'Falha historicas' # Em caso desse return, pode haver erros. Arrumar depois (2/2)


app = Flask(__name__)
CORS(app)

@app.route('/api/login', methods=['POST'])
def receber_login():
    print('\n\n\n\ndados recebidos para login')
    dados = request.json 
    e = dados['email']
    s = dados['senha']
    # print(dados)  # Adicionar em caso de testes
    chrome_options = Options()
    chrome_options.add_experimental_option('detach', True)
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--disable-gpu")  
    # chrome_options.add_argument("--no-sandbox")  
    # chrome_options.add_argument("--disable-dev-shm-usage")  


    id = ids.geraId()
    # Inserir primeira árvore que possui Driver
    arvore.insere(id = id, driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), 
                                                options=chrome_options))
    # print('inserido uma nova árvore') # Adicionar em caso de testes
    arvore.encontra(id).obtemDriver().get('https://siga.cps.sp.gov.br/sigaaluno/applogin.aspx')

    # print('Árvore') # Adicionar em caso de testes
    # arvore.mostra_EmOrdem() # Adicionar em caso de testes
    # print('Return') # Adicionar em caso de testes
    return login(e, s, id)

@app.route('/api/login/confirmacao', methods=['POST'])
def confirmacao_login():
    print('\n\n\nConfirmação recebida para login')
    dados = request.json
    c = dados['codigo']
    id = dados['id']

    print('Código de confirmação:', c) # mudar para receber 
    return confirmacao(c, id)

@app.route('/api/notas', methods=['POST'])
def scrape_notas():
    print('\n\n\n\nDados recebidos para pegar notas')
    dados = request.json
    # print(dados)  # Adicionar em caso de testes
    id = dados['id']

    notas_a = notas_parciais(id)
    notas_h = notas_historicas(id)

    notas = {
        "parciais": notas_a,
        "historicas": notas_h
    }

    notas = json.dumps(notas, ensure_ascii=False, indent=4)
    # print(notas) # Adicionar em caso de testes
    return notas

if __name__ == '__main__':
    app.run(debug=True)