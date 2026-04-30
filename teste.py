import banco

print("--- 1. LIGANDO O MOTOR ---")
banco.inicializar_banco()
print("Banco de dados verificado com sucesso!\n")

print("--- 2. CHEGOU MERCADORIA (INSERT) ---")
banco.adicionar_produto("1111111111111", "Camiseta Branca M", 10, 25.00, 50.00)
banco.adicionar_produto("2222222222222", "Calça Jeans 42", 5, 60.00, 120.00)
print("Camiseta e Calça cadastradas no estoque!\n")

print("--- 3. TESTANDO AS BUSCAS INTELIGENTES (SELECT) ---")
print("Bipando EAN da Camiseta:", banco.buscar_produto("1111111111111"))
print("Digitando nome 'Calça':", banco.buscar_produto("Calça"))
print("\n")

print("--- 4. CORRIGINDO PREÇO (UPDATE) ---")
# Vamos mudar o preço de venda da Camiseta (ID 1) de 50.00 para 55.00
banco.atualizar_produto(1, "1111111111111", "Camiseta Branca M", 10, 25.00, 55.00)
print("Preço atualizado! Buscando ID 1 de novo:", banco.buscar_produto("1"))
print("\n")

print("--- 5. LIMPANDO O ESTOQUE (DELETE) ---")
# Vamos deletar a Calça (ID 2)
banco.excluir_produto(2)
print("Calça excluída! Tentando buscar a Calça agora:", banco.buscar_produto("Calça"))
print("\n--- TESTE FINALIZADO COM SUCESSO! ---")