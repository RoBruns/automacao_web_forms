import json
import sqlite3

# Carregar o JSON
with open('telefones.json', 'r') as file:
    dados = json.load(file)

# Extrair os dados dos telefones
phones = dados['phones'][0]

# Conectar ao banco de dados SQLite (se o banco de dados não existir, ele será criado)
conn = sqlite3.connect('telefones.db')
c = conn.cursor()

# Criar uma tabela para armazenar os dados
c.execute('''CREATE TABLE IF NOT EXISTS telefones
             (nome text, numero text)''')

# Inserir os dados na tabela
for nome, numero in phones.items():
    c.execute("INSERT INTO telefones (nome, numero) VALUES (?, ?)", (nome, numero))

# Commit (salvar) as alterações no banco de dados
conn.commit()

# Fechar a conexão com o banco de dados
conn.close()
