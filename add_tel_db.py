# Flake8: noqa
import sqlite3


def adicionar_contato(nome, telefone):
    conn = sqlite3.connect('telefones.db')
    cursor = conn.cursor()

    # Verifica se o contato já existe
    cursor.execute('SELECT * FROM contatos WHERE nome = ?', (nome,))
    if cursor.fetchone():
        print("Um contato com esse nome já existe.")
    else:
        cursor.execute('INSERT INTO contatos (nome, telefone) VALUES (?, ?)', (nome, telefone))
        conn.commit()
        print(f"Contato '{nome}' adicionado com sucesso.")

    conn.close()


def main():
    nome = input("Digite o nome do contato: ")
    telefone = input("Digite o telefone do contato: ")
    adicionar_contato(nome, telefone)


if __name__ == "__main__":
    main()
