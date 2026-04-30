import customtkinter as ctk
import banco
from tkinter import messagebox

# --- Configurações Iniciais ---
ctk.set_appearance_mode("System") 
ctk.set_default_color_theme("blue") 

app = ctk.CTk()
app.geometry("1100x750") # Um pouco mais largo para caber todas as colunas financeiras
app.title("SisStock - Gestão de Estoque")

# Tenta carregar o ícone (se o arquivo existir na pasta)
try:
    app.iconbitmap("icone.ico")
except:
    pass # Se não achar o ícone, roda normal sem travar

# --- Função para Limpar a Tela Central ---
def limpar_conteudo():
    for widget in frame_conteudo.winfo_children():
        widget.destroy()
        
    app.unbind('<Escape>')
    app.unbind('<Return>')
    app.unbind('<KP_Enter>')

# --- TELA: DASHBOARD ---
def mostrar_dashboard():
    limpar_conteudo()
    produtos = banco.listar_todos_produtos()
    total_vendido = banco.obter_total_vendido()
    
    # Índices do PEPS: p[0]=EAN, p[1]=Nome, p[2]=QtdTotal, p[3]=CustoTotal, p[4]=PrecoVendaAtual
    metricas = {
        "Total": len(produtos),
        "Zerados": len([p for p in produtos if p[2] <= 0]),
        "Estoque": sum(p[3] for p in produtos), # O banco já mandou o custo total somado dos lotes
        "Vendido": total_vendido 
    }

    frame_cards = ctk.CTkFrame(frame_conteudo, fg_color="transparent")
    frame_cards.pack(pady=20, fill="x")
    frame_cards.columnconfigure((0,1,2,3), weight=1)

    def criar_card(col, titulo, valor, cor):
        f = ctk.CTkFrame(frame_cards, height=120, corner_radius=15)
        f.grid(row=0, column=col, padx=10, sticky="nsew")
        ctk.CTkLabel(f, text=titulo, font=("Arial", 14)).pack(pady=10)
        ctk.CTkLabel(f, text=valor, font=("Arial", 28, "bold"), text_color=cor).pack()

    criar_card(0, "Produtos Ativos", str(metricas["Total"]), "#3b8ed0")
    criar_card(1, "Estoque Zerado", str(metricas["Zerados"]), "#e74c3c")
    criar_card(2, "Custo em Estoque", f"R$ {metricas['Estoque']:.2f}", "#f39c12")
    criar_card(3, "Receita (Vendas)", f"R$ {metricas['Vendido']:.2f}", "#2ecc71")

# --- TELA: ENTRADA INTELIGENTE (CONFERÊNCIA ANTES DE SALVAR) ---
def mostrar_entrada():
    limpar_conteudo()
    
    # Lista temporária que funciona como o "carrinho" de entrada
    lote_temporario = []
    
    ctk.CTkLabel(frame_conteudo, text="📥 Entrada de Estoque (Conferência de Lotes)", font=("Arial", 22, "bold")).pack(pady=10)
    
    # --- 1. FORMULÁRIO DE ENTRADA (Linha Única) ---
    frame_form = ctk.CTkFrame(frame_conteudo, fg_color="transparent")
    frame_form.pack(pady=5, fill="x", padx=10)
    
    # Ajustei os tamanhos para caber tudo numa linha reta
    entry_ean = ctk.CTkEntry(frame_form, placeholder_text="EAN (Bipe aqui)", width=200)
    entry_ean.grid(row=0, column=0, padx=5, pady=5)
    
    entry_nome = ctk.CTkEntry(frame_form, placeholder_text="Nome do Produto", width=250)
    entry_nome.grid(row=0, column=1, padx=5, pady=5)
    
    entry_qtd = ctk.CTkEntry(frame_form, placeholder_text="Qtd", width=80)
    entry_qtd.grid(row=0, column=2, padx=5, pady=5)
    
    entry_compra = ctk.CTkEntry(frame_form, placeholder_text="Custo", width=100)
    entry_compra.grid(row=0, column=3, padx=5, pady=5)
    
    entry_venda = ctk.CTkEntry(frame_form, placeholder_text="Venda Atual", width=100)
    entry_venda.grid(row=0, column=4, padx=5, pady=5)
    
    lbl_msg = ctk.CTkLabel(frame_conteudo, text="Bipe o EAN para buscar. Aperte ENTER nos preços para adicionar à lista.", font=("Arial", 14), text_color="gray")
    lbl_msg.pack(pady=5)

    # --- 2. LISTA DE CONFERÊNCIA (UI) ---
    frame_lista = ctk.CTkFrame(frame_conteudo)
    frame_lista.pack(fill="both", expand=True, padx=10, pady=5)
    
    # Cabeçalho da Lista
    header_frame = ctk.CTkFrame(frame_lista, height=30, fg_color=("gray80", "gray20"))
    header_frame.pack(fill="x", padx=5, pady=5)
    ctk.CTkLabel(header_frame, text="EAN", width=120, font=("Arial", 12, "bold")).grid(row=0, column=0, padx=5)
    ctk.CTkLabel(header_frame, text="Nome", width=250, font=("Arial", 12, "bold"), anchor="w").grid(row=0, column=1, padx=5)
    ctk.CTkLabel(header_frame, text="Qtd", width=60, font=("Arial", 12, "bold")).grid(row=0, column=2, padx=5)
    ctk.CTkLabel(header_frame, text="Custo", width=100, font=("Arial", 12, "bold")).grid(row=0, column=3, padx=5)
    ctk.CTkLabel(header_frame, text="Venda", width=100, font=("Arial", 12, "bold")).grid(row=0, column=4, padx=5)
    ctk.CTkLabel(header_frame, text="Remover", width=60, font=("Arial", 12, "bold")).grid(row=0, column=5, padx=5)
    
    scroll_lista = ctk.CTkScrollableFrame(frame_lista, corner_radius=0, fg_color="transparent")
    scroll_lista.pack(fill="both", expand=True, padx=5, pady=(0, 5))

    # --- 3. BOTÃO DE CONFIRMAÇÃO FINAL ---
    btn_salvar_banco = ctk.CTkButton(frame_conteudo, text="💾 Registrar entrada", fg_color="#2ecc71", hover_color="#27ae60", font=("Arial", 16, "bold"), height=40, state="disabled")
    btn_salvar_banco.pack(pady=10)

    # --- LÓGICAS INTERNAS ---
    def verificar_ean(event=None):
        ean = entry_ean.get().strip()
        if not ean.isdigit(): return
            
        nome_existente = banco.buscar_nome_produto(ean)
        
        if nome_existente:
            entry_nome.configure(state="normal")
            entry_nome.delete(0, 'end')
            entry_nome.insert(0, nome_existente)
            entry_nome.configure(state="disabled") 
            lbl_msg.configure(text=f"✅ Produto encontrado! Insira os valores do lote.", text_color="#3b8ed0")
            entry_qtd.focus()
        else:
            entry_nome.configure(state="normal")
            if not entry_nome.get():
                lbl_msg.configure(text="✨ Novo produto. Preencha o nome.", text_color="#f39c12")
            entry_nome.focus()

    def atualizar_ui_lista():
        # Limpa o que estava na tela
        for widget in scroll_lista.winfo_children():
            widget.destroy()
            
        # Se a lista estiver vazia, bloqueia o botão de salvar no banco
        if not lote_temporario:
            btn_salvar_banco.configure(state="disabled")
            return
            
        btn_salvar_banco.configure(state="normal")
            
        # Desenha os itens atualizados
        for i, item in enumerate(lote_temporario):
            row = ctk.CTkFrame(scroll_lista, fg_color=("gray90", "gray15") if i % 2 == 0 else "transparent", corner_radius=0)
            row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row, text=item['ean'], width=120).grid(row=0, column=0, padx=5)
            ctk.CTkLabel(row, text=item['nome'], width=250, anchor="w").grid(row=0, column=1, padx=5)
            ctk.CTkLabel(row, text=str(item['qtd']), width=60).grid(row=0, column=2, padx=5)
            ctk.CTkLabel(row, text=f"R$ {item['compra']:.2f}", width=100).grid(row=0, column=3, padx=5)
            ctk.CTkLabel(row, text=f"R$ {item['venda']:.2f}", width=100).grid(row=0, column=4, padx=5)
            
            # Botão para deletar apenas da lista temporária
            btn_remover = ctk.CTkButton(row, text="❌", width=40, fg_color="#e74c3c", hover_color="#c0392b",
                                        command=lambda idx=i: remover_da_lista(idx))
            btn_remover.grid(row=0, column=5, padx=5)

    def remover_da_lista(index):
        lote_temporario.pop(index)
        atualizar_ui_lista()
        lbl_msg.configure(text="Item removido da lista de conferência.", text_color="#f39c12")
        entry_ean.focus()

    def adicionar_a_lista(event=None):
        ean = entry_ean.get().strip()
        nome = entry_nome.get() if entry_nome.cget("state") == "normal" else banco.buscar_nome_produto(ean)
        qtd_str = entry_qtd.get().strip()
        compra_str = entry_compra.get().strip().replace(',', '.')
        venda_str = entry_venda.get().strip().replace(',', '.')
        
        if not ean.isdigit() or not nome or not qtd_str.isdigit():
            lbl_msg.configure(text="❌ Preencha EAN, Nome e Quantidade corretamente.", text_color="#e74c3c")
            return
            
        try:
            compra = float(compra_str)
            venda = float(venda_str)
            
            # Adiciona o item ao carrinho temporário
            lote_temporario.append({
                'ean': ean,
                'nome': nome,
                'qtd': int(qtd_str),
                'compra': compra,
                'venda': venda
            })
            
            # Limpa os campos para o próximo item
            entry_ean.delete(0, 'end')
            entry_nome.configure(state="normal")
            entry_nome.delete(0, 'end')
            entry_qtd.delete(0, 'end')
            entry_compra.delete(0, 'end')
            entry_venda.delete(0, 'end')
            
            lbl_msg.configure(text="✅ Lote adicionado à conferência! Bipe o próximo.", text_color="#3b8ed0")
            atualizar_ui_lista()
            entry_ean.focus()
            
        except ValueError:
            lbl_msg.configure(text="❌ Erro: Verifique se os preços são números válidos.", text_color="#e74c3c")

    def gravar_no_banco(event=None):
        if not lote_temporario: return
        
        erros = 0
        # Pega a lista temporária e varre salvando cada item no banco definitivo
        for item in lote_temporario:
            sucesso, _ = banco.registrar_entrada(item['ean'], item['nome'], item['qtd'], item['compra'], item['venda'])
            if not sucesso: 
                erros += 1
            
        if erros == 0:
            lbl_msg.configure(text="🎉 Sucesso! Todos os lotes foram gravados no banco de dados.", text_color="#2ecc71")
            lote_temporario.clear() # Esvazia o carrinho
            atualizar_ui_lista()
            entry_ean.focus()
        else:
            lbl_msg.configure(text=f"⚠️ Concluído, mas houve {erros} erro(s). Verifique o estoque.", text_color="#f39c12")
            lote_temporario.clear()
            atualizar_ui_lista()

    # --- CONFIGURAÇÃO DE ATALHOS ---
    btn_salvar_banco.configure(command=gravar_no_banco)
    
    # Enter no EAN apenas busca
    entry_ean.bind('<Return>', verificar_ean)
    entry_ean.bind('<KP_Enter>', verificar_ean)
    
    # Enter em qualquer outro campo joga para a lista temporária
    entry_nome.bind('<Return>', adicionar_a_lista)
    entry_qtd.bind('<Return>', adicionar_a_lista)
    entry_compra.bind('<Return>', adicionar_a_lista)
    entry_venda.bind('<Return>', adicionar_a_lista)
    
    app.bind('<Escape>', lambda e: mostrar_estoque())
    
    entry_ean.focus()

# --- TELA: EDIÇÃO DE PRODUTO ---
def mostrar_edicao(ean, nome_atual, preco_venda_atual):
    limpar_conteudo()
    
    ctk.CTkLabel(frame_conteudo, text=f"✏️ Editar Produto (EAN: {ean})", font=("Arial", 22, "bold"), text_color="#f39c12").pack(pady=20)
    
    frame_form = ctk.CTkFrame(frame_conteudo, fg_color="transparent")
    frame_form.pack(pady=10)
    
    ctk.CTkLabel(frame_form, text="Nome do Produto:", font=("Arial", 12)).grid(row=0, column=0, padx=10, sticky="w")
    entry_nome = ctk.CTkEntry(frame_form, width=400, font=("Arial पिन", 16))
    entry_nome.grid(row=1, column=0, padx=10, pady=(0, 15))
    entry_nome.insert(0, nome_atual) # Preenche com o nome atual
    
    ctk.CTkLabel(frame_form, text="Preço de Venda Padrão Atualizado:", font=("Arial", 12)).grid(row=2, column=0, padx=10, sticky="w")
    entry_venda = ctk.CTkEntry(frame_form, width=400, font=("Arial", 16))
    entry_venda.grid(row=3, column=0, padx=10, pady=(0, 15))
    entry_venda.insert(0, f"{preco_venda_atual:.2f}") # Preenche com o preço atual
    
    lbl_msg = ctk.CTkLabel(frame_conteudo, text="", font=("Arial", 14))
    lbl_msg.pack(pady=10)
    
    def salvar_edicao(event=None):
        novo_nome = entry_nome.get().strip()
        preco_str = entry_venda.get().strip().replace(',', '.')
        
        if not novo_nome:
            lbl_msg.configure(text="❌ O nome não pode ficar vazio.", text_color="red")
            return
            
        try:
            novo_preco = float(preco_str)
            sucesso, msg = banco.atualizar_produto(ean, novo_nome, novo_preco)
            
            if sucesso:
                mostrar_estoque() # Se deu certo, volta pra lista automaticamente
            else:
                lbl_msg.configure(text=msg, text_color="red")
        except ValueError:
            lbl_msg.configure(text="❌ Preço inválido. Use apenas números.", text_color="red")
            
    ctk.CTkButton(frame_conteudo, text="Salvar Alterações (Enter)", command=salvar_edicao, fg_color="#3b8ed0", hover_color="#2980b9").pack(pady=10)
    ctk.CTkButton(frame_conteudo, text="Cancelar (Esc)", command=mostrar_estoque, fg_color="gray").pack()
    
    app.bind('<Return>', salvar_edicao)
    app.bind('<KP_Enter>', salvar_edicao)
    app.bind('<Escape>', lambda e: mostrar_estoque())
    
    entry_nome.focus()

# --- TELA: LISTA DE ESTOQUE E BUSCA ---
def mostrar_estoque():
    limpar_conteudo()
    
    barra_acoes = ctk.CTkFrame(frame_conteudo, fg_color="transparent")
    barra_acoes.pack(fill="x", padx=10, pady=10)
    
    entry_busca = ctk.CTkEntry(barra_acoes, placeholder_text="Buscar por Nome ou EAN...", width=400)
    entry_busca.pack(side="left", padx=10)
    entry_busca.focus()
    
    def realizar_busca(event=None):
        termo = entry_busca.get()
        produtos = banco.buscar_produto(termo) if termo else banco.listar_todos_produtos()
        atualizar_tabela(produtos)

    def resetar_busca(event=None):
        entry_busca.delete(0, 'end')
        realizar_busca()

    ctk.CTkButton(barra_acoes, text="🔍 Buscar (Enter)", width=100, command=realizar_busca).pack(side="left")
    ctk.CTkButton(barra_acoes, text="+ Entrada / Novo", fg_color="#2ecc71", hover_color="#27ae60", command=mostrar_entrada).pack(side="right", padx=10)

    # Ajustei a largura da última coluna para caber os dois botões
    header_frame = ctk.CTkFrame(frame_conteudo, height=30, fg_color=("gray80", "gray20"))
    header_frame.pack(fill="x", padx=10, pady=(10, 0))
    
    ctk.CTkLabel(header_frame, text="EAN", width=120, font=("Arial", 12, "bold")).grid(row=0, column=0, padx=5)
    ctk.CTkLabel(header_frame, text="Nome", width=220, font=("Arial", 12, "bold"), anchor="w").grid(row=0, column=1, padx=5) 
    ctk.CTkLabel(header_frame, text="Qtd", width=60, font=("Arial", 12, "bold")).grid(row=0, column=2, padx=5)
    ctk.CTkLabel(header_frame, text="Pr. Venda", width=90, font=("Arial", 12, "bold")).grid(row=0, column=3, padx=5)
    ctk.CTkLabel(header_frame, text="Total Custo", width=100, font=("Arial", 12, "bold")).grid(row=0, column=4, padx=5)
    ctk.CTkLabel(header_frame, text="Total Venda", width=100, font=("Arial", 12, "bold")).grid(row=0, column=5, padx=5)
    ctk.CTkLabel(header_frame, text="Ações", width=80, font=("Arial", 12, "bold")).grid(row=0, column=6, padx=5)

    lista_scroll = ctk.CTkScrollableFrame(frame_conteudo, corner_radius=0, fg_color="transparent")
    lista_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def deletar_item(ean_produto, nome_produto):
        confirmacao = messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir TODOS os lotes do produto:\n'{nome_produto}'?")
        if confirmacao:
            banco.excluir_produto(ean_produto)
            realizar_busca() 

    def atualizar_tabela(lista_produtos):
        for widget in lista_scroll.winfo_children():
            widget.destroy()
            
        for i, p in enumerate(lista_produtos):
            cor_fundo = ("gray90", "gray15") if i % 2 == 0 else "transparent"
            row = ctk.CTkFrame(lista_scroll, fg_color=cor_fundo, corner_radius=0)
            row.pack(fill="x")
            
            ean = p[0]
            nome = p[1]
            qtd = p[2]
            total_custo = p[3]
            preco_venda = p[4] if p[4] is not None else 0.0
            total_venda = qtd * preco_venda
            
            ctk.CTkLabel(row, text=ean, width=120).grid(row=0, column=0, padx=5) 
            ctk.CTkLabel(row, text=nome, width=220, anchor="w").grid(row=0, column=1, padx=5) 
            ctk.CTkLabel(row, text=str(qtd), width=60).grid(row=0, column=2, padx=5) 
            ctk.CTkLabel(row, text=f"R$ {preco_venda:.2f}", width=90).grid(row=0, column=3, padx=5) 
            ctk.CTkLabel(row, text=f"R$ {total_custo:.2f}", width=100, text_color="#e74c3c", font=("Arial", 12, "bold")).grid(row=0, column=4, padx=5) 
            ctk.CTkLabel(row, text=f"R$ {total_venda:.2f}", width=100, text_color="#2ecc71", font=("Arial", 12, "bold")).grid(row=0, column=5, padx=5) 

            # Frame para agrupar os dois botões de ação lado a lado
            frame_acoes = ctk.CTkFrame(row, fg_color="transparent")
            frame_acoes.grid(row=0, column=6, padx=5, pady=2)
            
            # Botão de Editar (Laranja)
            btn_editar = ctk.CTkButton(frame_acoes, text="✏️", width=35, fg_color="#f39c12", hover_color="#d35400", 
                                       command=lambda e=ean, n=nome, pv=preco_venda: mostrar_edicao(e, n, pv))
            btn_editar.pack(side="left", padx=(0, 5))

            # Botão de Excluir (Vermelho)
            btn_excluir = ctk.CTkButton(frame_acoes, text="🗑️", width=35, fg_color="#e74c3c", hover_color="#c0392b", 
                                        command=lambda e_prod=ean, n_prod=nome: deletar_item(e_prod, n_prod))
            btn_excluir.pack(side="left")

    app.bind('<Return>', realizar_busca)
    app.bind('<KP_Enter>', realizar_busca)
    app.bind('<Escape>', resetar_busca) 

    atualizar_tabela(banco.listar_todos_produtos())

# --- TELA: SAÍDA / VENDA DE MERCADORIAS (PDV / CARRINHO) ---
def mostrar_venda():
    limpar_conteudo()
    
    # O nosso "carrinho" de compras temporário
    carrinho_venda = []
    
    ctk.CTkLabel(frame_conteudo, text="📤 Frente de Caixa (PDV)", font=("Arial", 22, "bold"), text_color="#e74c3c").pack(pady=10)
    
    # --- 1. FORMULÁRIO DE VENDA ---
    frame_form = ctk.CTkFrame(frame_conteudo, fg_color="transparent")
    frame_form.pack(pady=5, fill="x", padx=10)
    
    ctk.CTkLabel(frame_form, text="1. Código EAN:", font=("Arial", 12)).grid(row=0, column=0, padx=5, sticky="w")
    entry_ean = ctk.CTkEntry(frame_form, width=200, font=("Arial", 16))
    entry_ean.grid(row=1, column=0, padx=5, pady=(0, 5))
    
    lbl_produto = ctk.CTkLabel(frame_form, text="Aguardando bipagem...", font=("Arial", 14, "italic"), text_color="gray")
    lbl_produto.grid(row=1, column=1, padx=10, pady=(0, 5), sticky="w")
    
    ctk.CTkLabel(frame_form, text="2. Quantidade:", font=("Arial", 12)).grid(row=2, column=0, padx=5, sticky="w")
    entry_qtd = ctk.CTkEntry(frame_form, width=200, font=("Arial", 16))
    entry_qtd.grid(row=3, column=0, padx=5, pady=(0, 10))
    entry_qtd.configure(state="disabled")
    
    ctk.CTkLabel(frame_form, text="3. Valor Unitário (C/ Descontos/Taxas):", font=("Arial", 12)).grid(row=2, column=1, padx=10, sticky="w")
    entry_venda_final = ctk.CTkEntry(frame_form, width=200, font=("Arial", 16))
    entry_venda_final.grid(row=3, column=1, padx=10, pady=(0, 10))
    entry_venda_final.configure(state="disabled")

    lbl_msg = ctk.CTkLabel(frame_conteudo, text="Bipe o EAN para buscar. Depois aperte ENTER nos valores para adicionar ao carrinho.", font=("Arial", 14), text_color="gray")
    lbl_msg.pack(pady=5)

    # --- 2. LISTA DO CARRINHO (UI) ---
    frame_lista = ctk.CTkFrame(frame_conteudo)
    frame_lista.pack(fill="both", expand=True, padx=10, pady=5)
    
    header_frame = ctk.CTkFrame(frame_lista, height=30, fg_color=("gray80", "gray20"))
    header_frame.pack(fill="x", padx=5, pady=5)
    ctk.CTkLabel(header_frame, text="EAN", width=120, font=("Arial", 12, "bold")).grid(row=0, column=0, padx=5)
    ctk.CTkLabel(header_frame, text="Nome", width=250, font=("Arial", 12, "bold"), anchor="w").grid(row=0, column=1, padx=5)
    ctk.CTkLabel(header_frame, text="Qtd", width=60, font=("Arial", 12, "bold")).grid(row=0, column=2, padx=5)
    ctk.CTkLabel(header_frame, text="Val. Unitário", width=100, font=("Arial", 12, "bold")).grid(row=0, column=3, padx=5)
    ctk.CTkLabel(header_frame, text="Subtotal", width=100, font=("Arial", 12, "bold")).grid(row=0, column=4, padx=5)
    ctk.CTkLabel(header_frame, text="Remover", width=60, font=("Arial", 12, "bold")).grid(row=0, column=5, padx=5)
    
    scroll_lista = ctk.CTkScrollableFrame(frame_lista, corner_radius=0, fg_color="transparent")
    scroll_lista.pack(fill="both", expand=True, padx=5, pady=(0, 5))

    # --- 3. RODAPÉ (TOTAL E FINALIZAR) ---
    frame_rodape = ctk.CTkFrame(frame_conteudo, fg_color="transparent")
    frame_rodape.pack(fill="x", padx=10, pady=10)
    
    lbl_total_venda = ctk.CTkLabel(frame_rodape, text="Total: R$ 0.00", font=("Arial", 32, "bold"), text_color="#2ecc71")
    lbl_total_venda.pack(side="left", padx=20)
    
    btn_finalizar = ctk.CTkButton(frame_rodape, text="💸 Finalizar Venda", fg_color="#e74c3c", hover_color="#c0392b", font=("Arial", 18, "bold"), height=50, state="disabled")
    btn_finalizar.pack(side="right", padx=20)

    # Dicionário temporário para segurar a informação do bip atual
    produto_info = {"ean": None, "nome": None, "estoque": 0}

    # --- LÓGICAS INTERNAS ---
    def buscar_ean(event=None):
        ean = entry_ean.get().strip()
        if not ean: return
        
        resultados = banco.buscar_produto(ean)
        p = next((item for item in resultados if item[0] == ean), None)
        
        if p:
            produto_info["ean"] = p[0]
            produto_info["nome"] = p[1]
            produto_info["estoque"] = p[2]
            
            lbl_produto.configure(text=f"📦 {p[1]} | Estoque Disp: {p[2]}", text_color="#3b8ed0")
            
            entry_venda_final.configure(state="normal")
            entry_qtd.configure(state="normal")
            
            # Preenche o preço padrão e sugere a quantidade 1 para agilizar
            entry_venda_final.delete(0, 'end')
            entry_venda_final.insert(0, f"{p[4]:.2f}")
            entry_qtd.delete(0, 'end')
            entry_qtd.insert(0, "1") 
            
            lbl_msg.configure(text="")
            entry_qtd.focus()
        else:
            lbl_produto.configure(text="❌ Produto não encontrado ou zerado!", text_color="red")
            entry_venda_final.configure(state="disabled")
            entry_qtd.configure(state="disabled")
            entry_ean.focus()

    def atualizar_ui_carrinho():
        for widget in scroll_lista.winfo_children():
            widget.destroy()
            
        total_geral = 0
            
        if not carrinho_venda:
            btn_finalizar.configure(state="disabled")
            lbl_total_venda.configure(text="Total: R$ 0.00")
            return
            
        btn_finalizar.configure(state="normal")
            
        for i, item in enumerate(carrinho_venda):
            row = ctk.CTkFrame(scroll_lista, fg_color=("gray90", "gray15") if i % 2 == 0 else "transparent", corner_radius=0)
            row.pack(fill="x", pady=2)
            
            subtotal = item['qtd'] * item['preco']
            total_geral += subtotal
            
            ctk.CTkLabel(row, text=item['ean'], width=120).grid(row=0, column=0, padx=5)
            ctk.CTkLabel(row, text=item['nome'], width=250, anchor="w").grid(row=0, column=1, padx=5)
            ctk.CTkLabel(row, text=str(item['qtd']), width=60).grid(row=0, column=2, padx=5)
            ctk.CTkLabel(row, text=f"R$ {item['preco']:.2f}", width=100).grid(row=0, column=3, padx=5)
            ctk.CTkLabel(row, text=f"R$ {subtotal:.2f}", width=100, font=("Arial", 12, "bold")).grid(row=0, column=4, padx=5)
            
            btn_remover = ctk.CTkButton(row, text="❌", width=40, fg_color="#e74c3c", hover_color="#c0392b", command=lambda idx=i: remover_do_carrinho(idx))
            btn_remover.grid(row=0, column=5, padx=5)
            
        lbl_total_venda.configure(text=f"Total: R$ {total_geral:.2f}")

    def remover_do_carrinho(index):
        carrinho_venda.pop(index)
        atualizar_ui_carrinho()
        lbl_msg.configure(text="Item removido do carrinho.", text_color="#f39c12")
        entry_ean.focus()

    def adicionar_ao_carrinho(event=None):
        if not produto_info["ean"]: return
            
        try:
            qtd_pedida = int(entry_qtd.get())
            preco_final = float(entry_venda_final.get().replace(',', '.'))
            
            if qtd_pedida <= 0:
                lbl_msg.configure(text="❌ A quantidade deve ser maior que zero.", text_color="red")
                return
                
            # Verifica se já tem esse produto no carrinho para somar e bater com o estoque real
            qtd_ja_no_carrinho = sum(item['qtd'] for item in carrinho_venda if item['ean'] == produto_info["ean"])
            
            if (qtd_ja_no_carrinho + qtd_pedida) > produto_info["estoque"]:
                lbl_msg.configure(text=f"❌ Estoque insuficiente! Disponível: {produto_info['estoque']} | Já no carrinho: {qtd_ja_no_carrinho}", text_color="red")
                return
            
            # Agrupa os itens iguais que têm o mesmo preço
            item_existente = next((item for item in carrinho_venda if item['ean'] == produto_info["ean"] and item['preco'] == preco_final), None)
            
            if item_existente:
                item_existente['qtd'] += qtd_pedida
            else:
                carrinho_venda.append({'ean': produto_info["ean"], 'nome': produto_info["nome"], 'qtd': qtd_pedida, 'preco': preco_final})
            
            # Reset campos
            entry_ean.delete(0, 'end')
            entry_qtd.delete(0, 'end')
            entry_venda_final.delete(0, 'end')
            entry_qtd.configure(state="disabled")
            entry_venda_final.configure(state="disabled")
            lbl_produto.configure(text="Aguardando bipagem...", text_color="gray")
            produto_info["ean"] = None
            
            lbl_msg.configure(text="✅ Adicionado ao carrinho!", text_color="#3b8ed0")
            atualizar_ui_carrinho()
            entry_ean.focus()
            
        except ValueError:
            lbl_msg.configure(text="❌ Verifique se a quantidade e o preço estão corretos.", text_color="red")

    def registrar_venda_banco(event=None):
        if not carrinho_venda: return
        
        erros = 0
        for item in carrinho_venda:
            sucesso, _ = banco.registrar_venda(item['ean'], item['qtd'], item['preco'])
            if not sucesso: erros += 1
                
        if erros == 0:
            lbl_msg.configure(text="🎉 Venda finalizada e baixada do estoque com sucesso!", text_color="#2ecc71")
            carrinho_venda.clear()
            atualizar_ui_carrinho()
            entry_ean.focus()
        else:
            lbl_msg.configure(text=f"⚠️ Venda finalizada, mas houve erro em {erros} item(ns).", text_color="#f39c12")
            carrinho_venda.clear()
            atualizar_ui_carrinho()

    # Vínculo do Botão Finalizar
    btn_finalizar.configure(command=registrar_venda_banco)

    # Atalhos de Teclado
    entry_ean.bind('<Return>', buscar_ean)
    entry_ean.bind('<KP_Enter>', buscar_ean)
    
    entry_qtd.bind('<Return>', adicionar_ao_carrinho)
    entry_qtd.bind('<KP_Enter>', adicionar_ao_carrinho)
    entry_venda_final.bind('<Return>', adicionar_ao_carrinho)
    entry_venda_final.bind('<KP_Enter>', adicionar_ao_carrinho)
    
    app.bind('<Escape>', lambda e: mostrar_dashboard())
    
    entry_ean.focus()

# --- Interface Principal (Navegação) ---
frame_cabecalho = ctk.CTkFrame(app, height=60, corner_radius=0)
frame_cabecalho.pack(side="top", fill="x")

ctk.CTkButton(frame_cabecalho, text="📊 Resumo", width=120, command=mostrar_dashboard).pack(side="left", padx=10, pady=10)
ctk.CTkButton(frame_cabecalho, text="📦 Estoque", width=120, command=mostrar_estoque).pack(side="left", padx=10, pady=10)
# Note que o botão Entrada agora chama a mesma função unificada!
ctk.CTkButton(frame_cabecalho, text="📥 Entrada", width=120, command=mostrar_entrada).pack(side="left", padx=10, pady=10)
ctk.CTkButton(frame_cabecalho, text="📤 Saída/Venda", width=120, command=mostrar_venda, fg_color="#e74c3c", hover_color="#c0392b").pack(side="left", padx=10, pady=10)

frame_conteudo = ctk.CTkFrame(app, fg_color="transparent")
frame_conteudo.pack(fill="both", expand=True, padx=20, pady=20)

# Inicializa o banco (criará o novo estoque_peps.db) e abre o dashboard
banco.inicializar_banco()
mostrar_dashboard()
app.mainloop()