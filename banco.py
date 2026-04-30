import sqlite3
import os

def conectar_banco():
    # Encontra a pasta 'Documentos' do usuário atual no Windows
    caminho_documentos = os.path.expanduser('~/Documents')
    
    # Cria uma pasta chamada 'SisStock' lá dentro (se ela não existir)
    pasta_sistema = os.path.join(caminho_documentos, 'SisStock')
    os.makedirs(pasta_sistema, exist_ok=True)
    
    # O arquivo de banco de dados ficará fixo lá para sempre
    caminho_banco = os.path.join(pasta_sistema, 'estoque_peps.db')
    
    conexao = sqlite3.connect(caminho_banco)
    return conexao, conexao.cursor()

def inicializar_banco():
    conexao, cursor = conectar_banco()
    try:
        # Catálogo Mestre de Produtos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produtos (
                ean TEXT PRIMARY KEY,
                nome TEXT NOT NULL
            )
        ''')
        # Histórico de Entradas (Lotes)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ean TEXT,
                quantidade INTEGER NOT NULL,
                preco_compra REAL NOT NULL,
                preco_venda REAL NOT NULL,
                data_entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(ean) REFERENCES produtos(ean)
            )
        ''')
        # Histórico de Vendas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vendas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ean TEXT,
                quantidade INTEGER,
                valor_total REAL,
                data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conexao.commit()
    except Exception as e:
        print(f"Erro banco: {e}")
    finally:
        conexao.close()

def buscar_nome_produto(ean):
    conexao, cursor = conectar_banco()
    cursor.execute('SELECT nome FROM produtos WHERE ean = ?', (ean,))
    resultado = cursor.fetchone()
    conexao.close()
    return resultado[0] if resultado else None

def registrar_entrada(ean, nome, qtd, compra, venda):
    conexao, cursor = conectar_banco()
    try:
        # 1. Tenta inserir o produto no catálogo (se já existir, ele ignora)
        cursor.execute('INSERT OR IGNORE INTO produtos (ean, nome) VALUES (?, ?)', (ean, nome))
        # 2. Insere o lote com os valores específicos dessa entrada
        cursor.execute('INSERT INTO lotes (ean, quantidade, preco_compra, preco_venda) VALUES (?, ?, ?, ?)', (ean, qtd, compra, venda))
        conexao.commit()
        return True, "Lote registrado com sucesso!"
    except Exception as e:
        return False, f"Erro: {str(e)}"
    finally:
        conexao.close()

def listar_todos_produtos():
    conexao, cursor = conectar_banco()
    # SQL Avançado: Agrupa os lotes por EAN para mostrar o total na tela de estoque
    cursor.execute('''
        SELECT p.ean, p.nome, 
               IFNULL(SUM(l.quantidade), 0) as qtd_total,
               IFNULL(SUM(l.quantidade * l.preco_compra), 0) as custo_total,
               (SELECT preco_venda FROM lotes WHERE ean = p.ean ORDER BY id DESC LIMIT 1) as venda_atual
        FROM produtos p
        LEFT JOIN lotes l ON p.ean = l.ean AND l.quantidade > 0
        GROUP BY p.ean
    ''')
    produtos = cursor.fetchall()
    conexao.close()
    return produtos

def buscar_produto(termo):
    termo = f"%{termo}%"
    conexao, cursor = conectar_banco()
    cursor.execute('''
        SELECT p.ean, p.nome, 
               IFNULL(SUM(l.quantidade), 0) as qtd_total,
               IFNULL(SUM(l.quantidade * l.preco_compra), 0) as custo_total,
               (SELECT preco_venda FROM lotes WHERE ean = p.ean ORDER BY id DESC LIMIT 1) as venda_atual
        FROM produtos p
        LEFT JOIN lotes l ON p.ean = l.ean AND l.quantidade > 0
        WHERE p.nome LIKE ? OR p.ean LIKE ?
        GROUP BY p.ean
    ''', (termo, termo))
    produtos = cursor.fetchall()
    conexao.close()
    return produtos

def registrar_venda(ean, quantidade_vendida, preco_venda_personalizado=None):
    conexao, cursor = conectar_banco()
    try:
        # Verifica estoque total
        cursor.execute('SELECT SUM(quantidade) FROM lotes WHERE ean = ?', (ean,))
        total_estoque = cursor.fetchone()[0] or 0
        
        if total_estoque < quantidade_vendida:
            return False, f"Estoque insuficiente. Disponível: {total_estoque}"

        # Busca lotes para aplicar PEPS
        cursor.execute('SELECT id, quantidade, preco_venda FROM lotes WHERE ean = ? AND quantidade > 0 ORDER BY id ASC', (ean,))
        lotes = cursor.fetchall()
        
        qtd_restante_venda = quantidade_vendida
        valor_total_venda = 0
        
        # Se houver preço manual (com descontos/taxas), calculamos o faturamento por ele
        if preco_venda_personalizado is not None:
            valor_total_venda = quantidade_vendida * preco_venda_personalizado
        
        for lote in lotes:
            id_lote, qtd_lote, preco_venda_padrao = lote
            if qtd_restante_venda == 0: break
                
            if qtd_lote <= qtd_restante_venda:
                cursor.execute('UPDATE lotes SET quantidade = 0 WHERE id = ?', (id_lote,))
                # Se não houver preço manual, usa o valor padrão do lote
                if preco_venda_personalizado is None:
                    valor_total_venda += (qtd_lote * preco_venda_padrao)
                qtd_restante_venda -= qtd_lote
            else:
                nova_qtd = qtd_lote - qtd_restante_venda
                cursor.execute('UPDATE lotes SET quantidade = ? WHERE id = ?', (nova_qtd, id_lote))
                if preco_venda_personalizado is None:
                    valor_total_venda += (qtd_restante_venda * preco_venda_padrao)
                qtd_restante_venda = 0
                
        cursor.execute('INSERT INTO vendas (ean, quantidade, valor_total) VALUES (?, ?, ?)', (ean, quantidade_vendida, valor_total_venda))
        conexao.commit()
        return True, "Venda realizada!"
    except Exception as e:
        conexao.rollback()
        return False, f"Erro: {str(e)}"
    finally:
        conexao.close()

def obter_total_vendido():
    conexao, cursor = conectar_banco()
    cursor.execute('SELECT SUM(valor_total) FROM vendas')
    resultado = cursor.fetchone()[0]
    conexao.close()
    return resultado if resultado else 0.0

def excluir_produto(ean):
    conexao, cursor = conectar_banco()
    cursor.execute('DELETE FROM lotes WHERE ean = ?', (ean,))
    cursor.execute('DELETE FROM produtos WHERE ean = ?', (ean,))
    conexao.commit()
    conexao.close()

def atualizar_produto(ean, novo_nome, novo_preco_venda):
    conexao, cursor = conectar_banco()
    try:
        # 1. Atualiza o nome oficial do produto no catálogo
        cursor.execute('UPDATE produtos SET nome = ? WHERE ean = ?', (novo_nome, ean))
        
        # 2. Atualiza o preço de venda de todos os lotes que ainda tem estoque
        cursor.execute('UPDATE lotes SET preco_venda = ? WHERE ean = ? AND quantidade > 0', (novo_preco_venda, ean))
        
        conexao.commit()
        return True, "Produto atualizado com sucesso!"
    except Exception as e:
        conexao.rollback()
        return False, f"Erro ao atualizar: {str(e)}"
    finally:
        conexao.close()