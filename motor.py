# motor.py
import cv2
import numpy as np
import os
import random
import pyphen
import config

memoria_letras = {}

def carregar_banco_de_letras(pasta_dataset):
    """Matemática original do ultimate.py: Preserva o branco puro (255) para não derreter a folha"""
    banco = {}
    for letra in os.listdir(pasta_dataset):
        caminho = os.path.join(pasta_dataset, letra)
        if os.path.isdir(caminho):
            imagens_letra = []
            altura_alvo, _ = config.obter_parametros_letra(letra)
            
            for arquivo in os.listdir(caminho):
                if arquivo.endswith(('.jpg', '.png')):
                    img = cv2.imread(os.path.join(caminho, arquivo), cv2.IMREAD_GRAYSCALE)
                    if img is not None:
                        img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)
                        
                        min_pixel = np.min(img)
                        if min_pixel < 240:
                            img_float = img.astype(np.float32)
                            img_calculada = ((img_float - min_pixel) / (255 - min_pixel)) * (255 - config.TOM_ALVO) + config.TOM_ALVO
                            img = np.clip(img_calculada, 0, 255).astype(np.uint8)
                        
                        img[img > 210] = 255
                        
                        h_orig, w_orig = img.shape
                        if h_orig > 0:
                            escala = altura_alvo / h_orig
                            nova_largura = max(1, int(w_orig * escala))
                            img = cv2.resize(img, (nova_largura, altura_alvo), interpolation=cv2.INTER_AREA)
                            
                            imagens_letra.append((img, arquivo))
            
            if imagens_letra:
                banco[letra] = imagens_letra
    return banco

def desenhar_ligacao(canvas, p0, p3, char_out, char_in):
    """Traça uma curva de Bézier camuflada para não destoar da caneta"""
    x0, y0 = p0
    x3, y3 = p3
    if x3 <= x0: return
    
    dist_x = x3 - x0
    dist_y = y3 - y0
    dist_total = (dist_x**2 + dist_y**2)**0.5
    barriga = min(int(config.ALTURA_BASE * 0.35), int(dist_total * 0.3))
    
    cx1 = x0 + dist_x * 0.45 + random.uniform(-1, 1)
    cy1 = y0 + random.uniform(-1, 1) if char_out in config.SAIDA_ALTA else y0 + barriga + random.uniform(-1, 1)
    
    cx2 = x3 - dist_x * 0.35 + random.uniform(-1, 1)
    cy2 = y3 - barriga + random.uniform(-1, 1) if char_in in config.ENTRADA_ALTA else y3 + barriga + random.uniform(-1, 1)
    
    pts = []
    for t in np.linspace(0, 1, num=15):
        x = (1-t)**3 * x0 + 3*(1-t)**2 * t * cx1 + 3*(1-t)*t**2 * cx2 + t**3 * x3
        y = (1-t)**3 * y0 + 3*(1-t)**2 * t * cy1 + 3*(1-t)*t**2 * cy2 + t**3 * y3
        pts.append([int(x), int(y)])
        
    pts = np.array(pts, np.int32).reshape((-1, 1, 2))
    
    tom_conexao = min(200, config.TOM_ALVO + 40)
    intensidade_tinta = random.randint(tom_conexao - config.VARIA_TINTA, tom_conexao + config.VARIA_TINTA)
    
    cv2.polylines(canvas, [pts], isClosed=False, color=intensidade_tinta, thickness=config.ESPESSURA_CONEXAO, lineType=cv2.LINE_AA)

def gerar_palavra(texto, banco_letras, ancoras=None, escala=1.0):
    imagens_sorteadas = []
    aspas_abertas = False
    global memoria_letras
    
    # Blindagem de acentos embutida no núcleo (Ignora o config se ele falhar)
    mapa_acentos_fixo = {
        'á': ('a', 'agudo'), 'é': ('e', 'agudo'), 'í': ('i', 'agudo'), 'ó': ('o', 'agudo'), 'ú': ('u', 'agudo'),
        'ã': ('a', 'til'), 'õ': ('o', 'til'),
        'â': ('a', 'circunflexo'), 'ê': ('e', 'circunflexo'), 'ô': ('o', 'circunflexo'),
        'à': ('a', 'crase'),
        'Á': ('A_MAI', 'agudo'), 'É': ('E_MAI', 'agudo'), 'Í': ('I_MAI', 'agudo'), 'Ó': ('O_MAI', 'agudo'), 'Ú': ('U_MAI', 'agudo'),
        'Ã': ('A_MAI', 'til'), 'Õ': ('O_MAI', 'til'),
        'Â': ('A_MAI', 'circunflexo'), 'Ê': ('E_MAI', 'circunflexo'), 'Ô': ('O_MAI', 'circunflexo'),
        'À': ('A_MAI', 'crase')
    }
    
    for char in texto:
        letra_base, nome_acento = None, None
        
        if char in mapa_acentos_fixo:
            letra_base, nome_acento = mapa_acentos_fixo[char]
        elif char == 'i': letra_base, nome_acento = 'i', 'ponto'
        elif char == 'j': letra_base, nome_acento = 'j', 'ponto'
        elif char in config.MAPA_SINAIS: letra_base = config.MAPA_SINAIS[char]
        elif char == '"':
            letra_base = 'aspas_abre' if not aspas_abertas else 'aspas_fecha'
            aspas_abertas = not aspas_abertas
        elif char.isupper(): letra_base = f"{char}_MAI"
        else: letra_base = char
        
        if letra_base not in banco_letras: continue
        
        opcoes = banco_letras[letra_base]
        if len(opcoes) > 1:
            ultimo_idx = memoria_letras.get(letra_base, -1)
            indices_validos = [i for i in range(len(opcoes)) if i != ultimo_idx]
            idx_sorteado = random.choice(indices_validos)
            memoria_letras[letra_base] = idx_sorteado
            img, arquivo_letra = opcoes[idx_sorteado]
        else:
            img, arquivo_letra = opcoes[0]
            
        _, offset_y = config.obter_parametros_letra(letra_base)
        
        acento_img = None
        if nome_acento and nome_acento in banco_letras:
            acento_img, _ = random.choice(banco_letras[nome_acento])
            
        imagens_sorteadas.append((img, offset_y, char, acento_img, arquivo_letra, letra_base))
        
    if not imagens_sorteadas: return None
    
    largura_minima = sum([img.shape[1] for img, _, _, _, _, _ in imagens_sorteadas])
    altura_canvas = int(config.ALTURA_BASE * 6)
    canvas = np.ones((altura_canvas, largura_minima + 50), dtype=np.uint8) * 255
    linha_base = altura_canvas // 2 + (config.ALTURA_BASE // 2)
    
    pos_x = 10
    limite_direito = 0
    info_anterior = None
    
    for i, (img_letra, offset_y, char, img_acento, arquivo_letra, letra_base) in enumerate(imagens_sorteadas):
        h, w = img_letra.shape
        pos_y = linha_base - offset_y + random.randint(-config.VARIA_Y_LETRA, config.VARIA_Y_LETRA)
        
        regiao_alvo = canvas[pos_y:pos_y+h, pos_x:pos_x+w]
        canvas[pos_y:pos_y+h, pos_x:pos_x+w] = np.minimum(regiao_alvo, img_letra)
        
        if info_anterior is not None and ancoras is not None:
            if letra_base not in config.NAO_RECEBEM_LIGACAO_DE_TRAS:
                letra_ant, arq_ant, px_ant, py_ant, w_ant, h_ant = info_anterior
                if letra_ant not in config.NAO_LIGAM_PRA_FRENTE:
                    if letra_ant in ancoras and arq_ant in ancoras[letra_ant]:
                        if letra_base in ancoras and arquivo_letra in ancoras[letra_base]:
                            s_rel = ancoras[letra_ant][arq_ant]["saida"]
                            e_rel = ancoras[letra_base][arquivo_letra]["entrada"]
                            
                            P_out = (px_ant + int(s_rel[0] * w_ant), py_ant + int(s_rel[1] * h_ant))
                            P_in = (pos_x + int(e_rel[0] * w), pos_y + int(e_rel[1] * h))
                            desenhar_ligacao(canvas, P_out, P_in, letra_ant, letra_base)
                            
        info_anterior = (letra_base, arquivo_letra, pos_x, pos_y, w, h) if (ancoras and letra_base in ancoras) else None
        
        # Posicionamento por Centróide e Blindagem de Corte
        if img_acento is not None:
            h_a, w_a = img_acento.shape
            tinta_coords = np.where(img_letra < 240)
            if len(tinta_coords[0]) > 0:
                centro_x_tinta = int(np.mean(tinta_coords[1]))
                topo_y_tinta = int(np.min(tinta_coords[0]))
            else:
                centro_x_tinta = w // 2
                topo_y_tinta = 0
                
            pos_x_a = pos_x + centro_x_tinta - (w_a // 2)
            pos_y_a = pos_y + topo_y_tinta - h_a - random.randint(1, 3)
            
            y1_a = max(0, pos_y_a)
            y2_a = min(canvas.shape[0], pos_y_a + h_a)
            x1_a = max(0, pos_x_a)
            x2_a = min(canvas.shape[1], pos_x_a + w_a)
            
            h_efetivo = y2_a - y1_a
            w_efetivo = x2_a - x1_a
            
            if h_efetivo > 0 and w_efetivo > 0:
                ay1 = h_a - h_efetivo if pos_y_a < 0 else 0
                ax1 = w_a - w_efetivo if pos_x_a < 0 else 0
                
                regiao_a = canvas[y1_a:y2_a, x1_a:x2_a]
                recorte_acento = img_acento[ay1:ay1+h_efetivo, ax1:ax1+w_efetivo]
                canvas[y1_a:y2_a, x1_a:x2_a] = np.minimum(regiao_a, recorte_acento)
                
        if pos_x + w > limite_direito: limite_direito = pos_x + w
        
        proximo_char = imagens_sorteadas[i+1][2] if i + 1 < len(imagens_sorteadas) else ''
        if proximo_char == '-' or char in ['-', 'r', '.', ',', '(', ')', '+', '"']:
            sobrep = 0
        else:
            sobrep = config.SOBREPOSICAO_LETRAS
            
        pos_x += (w - sobrep)
        
    y_min = max(0, linha_base - int(config.ALTURA_BASE * 3.5))
    y_max = min(altura_canvas, linha_base + int(config.ALTURA_BASE * 2.5))
    canvas_final = canvas[y_min:y_max, 0:limite_direito + 5]
    
    if escala != 1.0:
        novo_w = int(canvas_final.shape[1] * escala)
        novo_h = int(canvas_final.shape[0] * escala)
        canvas_final = cv2.resize(canvas_final, (novo_w, novo_h), interpolation=cv2.INTER_AREA)
        
    canvas_final = cv2.GaussianBlur(canvas_final, (3, 3), 0)
    return canvas_final
def separar_silaba_dinamica(palavra, max_letras):
    if len(palavra) < 5 or max_letras < 3: return None
    corte = min(max_letras - 1, len(palavra) - 2)
    if corte < 2: return None
    
    vogais = "aeiouAEIOUáàãâéêíóõôúÁÀÃÂÉÊÍÓÕÔÚ"
    for i in range(corte, 1, -1):
        if palavra[i-1] in vogais:
            prox = palavra[i:i+2].lower()
            if prox not in ['nh', 'lh', 'ch', 'rr', 'ss']:
                return palavra[:i], palavra[i:]
    return palavra[:corte], palavra[corte:]

def carregar_fundo(caminho):
    A4_LARGURA, A4_ALTURA = 1240, 1754
    fundo = cv2.imread(caminho)
    if fundo is None:
        fundo = np.ones((A4_ALTURA, A4_LARGURA, 3), dtype=np.uint8) * 255
    else:
        fundo = cv2.resize(fundo, (A4_LARGURA, A4_ALTURA), interpolation=cv2.INTER_AREA)
    return fundo, A4_LARGURA, A4_ALTURA

def desenhar_colchete_tremido(canvas, x, y_topo, y_baixo, cor, espessura, lado='esq'):
    direcao = 1 if lado == 'esq' else -1
    tamanho_haste = 9
    altura_total = y_baixo - y_topo
    
    desvio_base = random.randint(-3, 3)
    
    pontos_topo = []
    x_atual, y_atual = x, y_topo
    for _ in range(4):
        pontos_topo.append((x_atual, y_atual))
        x_atual += (tamanho_haste // 4) * direcao
        y_atual += random.randint(0, 1)
    pontos_topo.append((x + tamanho_haste * direcao, y_topo + random.randint(0, 1)))
    
    for i in range(len(pontos_topo) - 1):
        cv2.line(canvas, pontos_topo[i], pontos_topo[i+1], cor, espessura, cv2.LINE_AA)
        
    passos = max(6, int(altura_total / 6))
    pontos_vertical = []
    
    for step in range(passos + 1):
        progress = step / passos
        y_pos = int(y_topo + altura_total * progress)
        x_base_interpolado = x + int(desvio_base * progress)
        arco = int(2.5 * 4 * progress * (1 - progress)) * (-direcao)
        x_pos = x_base_interpolado + arco + random.randint(0, 1)
        pontos_vertical.append((x_pos, y_pos))
        
    for i in range(len(pontos_vertical) - 1):
        cv2.line(canvas, pontos_vertical[i], pontos_vertical[i+1], cor, espessura, cv2.LINE_AA)
        
    x_fim_haste = pontos_vertical[-1][0]
    pontos_base = []
    x_atual, y_atual = x_fim_haste, y_baixo
    for _ in range(4):
        pontos_base.append((x_atual, y_atual))
        x_atual += (tamanho_haste // 4) * direcao
        y_atual += random.randint(0, 1)
    pontos_base.append((x_fim_haste + tamanho_haste * direcao, y_baixo + random.randint(0, 1)))
    
    for i in range(len(pontos_base) - 1):
        cv2.line(canvas, pontos_base[i], pontos_base[i+1], cor, espessura, cv2.LINE_AA)

def desenhar_linha_tremida(canvas, pt1, pt2, cor, espessura):
    x1, y1 = pt1
    x2, y2 = pt2
    
    p_inicio = (x1 + random.randint(-1, 1), y1 + random.randint(-1, 1))
    p_fim = (x2 + random.randint(-2, 2), y2 + random.randint(-2, 2))
    
    dx = p_fim[0] - p_inicio[0]
    dy = p_fim[1] - p_inicio[1]
    comprimento = (dx**2 + dy**2)**0.5
    
    if comprimento < 5:
        cv2.line(canvas, p_inicio, p_fim, cor, espessura, cv2.LINE_AA)
        return

    passos = max(8, int(comprimento / 8))
    pontos = []
    
    nx = -dy / comprimento
    ny = dx / comprimento
    desvio_macro = random.randint(-3, 3)
    
    for i in range(passos + 1):
        t = i / passos
        bx = p_inicio[0] + (p_fim[0] - p_inicio[0]) * t
        by = p_inicio[1] + (p_fim[1] - p_inicio[1]) * t
        
        fator_arco = 4 * t * (1 - t) 
        curvatura_x = nx * desvio_macro * fator_arco
        curvatura_y = ny * desvio_macro * fator_arco
        
        micro_x = random.randint(-1, 1) if 0 < i < passos else 0
        micro_y = random.randint(-1, 1) if 0 < i < passos else 0
        
        px = int(bx + curvatura_x + micro_x)
        py = int(by + curvatura_y + micro_y)
        pontos.append((px, py))
        
    for i in range(len(pontos) - 1):
        cv2.line(canvas, pontos[i], pontos[i+1], cor, espessura, cv2.LINE_AA)

def desenhar_matriz(matriz_dados, banco_letras, ancoras=None):
    celulas_imgs = []
    col_larguras = [0] * len(matriz_dados[0])
    row_alturas = [0] * len(matriz_dados)
    pixels_tinta = []
    
    for r_idx, linha in enumerate(matriz_dados):
        linha_imgs = []
        for c_idx, val in enumerate(linha):
            img_cel = gerar_palavra(str(val), banco_letras, ancoras, escala=1.0)
            if img_cel is None:
                img_cel = np.ones((config.ALTURA_BASE, 15), dtype=np.uint8) * 255
            else:
                tinta = img_cel[img_cel < 240]
                if tinta.size > 0: pixels_tinta.extend(tinta)
            
            h, w = img_cel.shape
            linha_imgs.append(img_cel)
            if w > col_larguras[c_idx]: col_larguras[c_idx] = w
            if h > row_alturas[r_idx]: row_alturas[r_idx] = h
        celulas_imgs.append(linha_imgs)
        
    tom_medio_tinta = int(np.mean(pixels_tinta)) if pixels_tinta else config.TOM_ALVO
    esp_coluna, esp_linha = 22, 14
    
    matriz_w = sum(col_larguras) + (esp_coluna * (len(col_larguras) - 1)) + 50
    matriz_h = sum(row_alturas) + (esp_linha * (len(row_alturas) - 1)) + 40
    
    canvas_matriz = np.ones((matriz_h, matriz_w + 80), dtype=np.uint8) * 255
    canvas_h, canvas_w = canvas_matriz.shape
    start_x, start_y = 40, 20
    
    curr_y = start_y
    for r_idx, linha_imgs in enumerate(celulas_imgs):
        curr_x = start_x
        r_h = row_alturas[r_idx]
        for c_idx, img_cel in enumerate(linha_imgs):
            c_w = col_larguras[c_idx]
            h_cel, w_cel = img_cel.shape
            
            centro_base_x = curr_x + (c_w - w_cel) // 2
            centro_base_y = curr_y + (r_h - h_cel) // 2
            slot_x = centro_base_x + random.randint(-1, 2)
            slot_y = centro_base_y + random.randint(-1, 1)
            
            x_fim = min(slot_x + w_cel, canvas_w)
            y_fim = min(slot_y + h_cel, canvas_h)
            w_efetivo = x_fim - slot_x
            h_efetivo = y_fim - slot_y
            
            if w_efetivo > 0 and h_efetivo > 0:
                regiao = canvas_matriz[slot_y:y_fim, slot_x:x_fim]
                parte_celula = img_cel[:h_efetivo, :w_efetivo]
                canvas_matriz[slot_y:y_fim, slot_x:x_fim] = np.minimum(regiao, parte_celula)
            
            curr_x += c_w + esp_coluna
        curr_y += r_h + esp_linha
        
    espessura_linha = max(2, config.ESPESSURA_CONEXAO + 1)
    x_esq = start_x - 14
    y_topo = start_y - 6
    y_baixo = curr_y - esp_linha + 6
    
    desenhar_colchete_tremido(canvas_matriz, x_esq, y_topo, y_baixo, tom_medio_tinta, espessura_linha, lado='esq')
    fim_x = start_x + sum(col_larguras) + (esp_coluna * (len(col_larguras) - 1)) + 14
    desenhar_colchete_tremido(canvas_matriz, fim_x, y_topo, y_baixo, tom_medio_tinta, espessura_linha, lado='dir')
    
    return cv2.GaussianBlur(canvas_matriz, (3, 3), 0)

def desenhar_tabela(tabela_dados, banco_letras, ancoras=None):
    celulas_imgs = []
    col_larguras = [0] * len(tabela_dados[0])
    row_alturas = [0] * len(tabela_dados)
    pixels_tinta = []
    padding_x, padding_y = 10, 8
    
    for r_idx, linha in enumerate(tabela_dados):
        linha_imgs = []
        for c_idx, val in enumerate(linha):
            img_cel = gerar_palavra(str(val), banco_letras, ancoras, escala=1.0)
            if img_cel is None:
                img_cel = np.ones((config.ALTURA_BASE, 15), dtype=np.uint8) * 255
            else:
                tinta = img_cel[img_cel < 240]
                if tinta.size > 0: pixels_tinta.extend(tinta)
            
            h, w = img_cel.shape
            linha_imgs.append(img_cel)
            w_com_padding = w + (padding_x * 2)
            h_com_padding = h + (padding_y * 2)
            if w_com_padding > col_larguras[c_idx]: col_larguras[c_idx] = w_com_padding
            if h_com_padding > row_alturas[r_idx]: row_alturas[r_idx] = h_com_padding
        celulas_imgs.append(linha_imgs)
        
    tom_medio_tinta = int(np.mean(pixels_tinta)) if pixels_tinta else config.TOM_ALVO
    tabela_w, tabela_h = sum(col_larguras), sum(row_alturas)
    
    canvas_tabela = np.ones((tabela_h + 80, tabela_w + 80), dtype=np.uint8) * 255
    canvas_h, canvas_w = canvas_tabela.shape
    start_x, start_y = 40, 40
    
    curr_y = start_y
    coords_linhas_y = [curr_y]
    
    for r_idx, linha_imgs in enumerate(celulas_imgs):
        curr_x = start_x
        r_h = row_alturas[r_idx]
        if r_idx == 0: coords_linhas_x = [curr_x]
            
        for c_idx, img_cel in enumerate(linha_imgs):
            c_w = col_larguras[c_idx]
            h_cel, w_cel = img_cel.shape
            
            centro_base_x = curr_x + (c_w - w_cel) // 2
            centro_base_y = curr_y + (r_h - h_cel) // 2
            slot_x = centro_base_x + random.randint(-1, 1)
            slot_y = centro_base_y + random.randint(-1, 1)
            
            x_fim = min(slot_x + w_cel, canvas_w)
            y_fim = min(slot_y + h_cel, canvas_h)
            w_efetivo = x_fim - slot_x
            h_efetivo = y_fim - slot_y
            
            if w_efetivo > 0 and h_efetivo > 0:
                regiao = canvas_tabela[slot_y:y_fim, slot_x:x_fim]
                parte_celula = img_cel[:h_efetivo, :w_efetivo]
                canvas_tabela[slot_y:y_fim, slot_x:x_fim] = np.minimum(regiao, parte_celula)
            
            if r_idx == 0: coords_linhas_x.append(curr_x + c_w)
            curr_x += c_w
            
        curr_y += r_h
        coords_linhas_y.append(curr_y)
        
    espessura_linha = max(2, config.ESPESSURA_CONEXAO + 1)
    x_inicio, x_fim_tabela = coords_linhas_x[0], coords_linhas_x[-1]
    y_inicio, y_fim_tabela = coords_linhas_y[0], coords_linhas_y[-1]
    
    for y_coord in coords_linhas_y:
        desenhar_linha_tremida(canvas_tabela, (x_inicio, y_coord), (x_fim_tabela, y_coord), tom_medio_tinta, espessura_linha)
    for x_coord in coords_linhas_x:
        desenhar_linha_tremida(canvas_tabela, (x_coord, y_inicio), (x_coord, y_fim_tabela), tom_medio_tinta, espessura_linha)
        
    return cv2.GaussianBlur(canvas_tabela, (3, 3), 0)

def escrever_texto_longo(texto, banco_letras, ancoras, caminho_fundo):
    fundo, A4_LARGURA, A4_ALTURA = carregar_fundo(caminho_fundo)
    paginas_geradas = []
    
    pos_x = config.MARGEM_ESQ
    pos_y = config.MARGEM_TOPO
    
    linhas_texto = texto.splitlines()
    i = 0
    area_util = A4_LARGURA - config.MARGEM_ESQ - config.MARGEM_DIR
    
    while i < len(linhas_texto):
        linha = linhas_texto[i]
        linha_limpa = linha.strip()
        
        if linha_limpa.startswith('[pular'):
            qtd = 1
            if ':' in linha_limpa:
                try: qtd = int(linha_limpa.split(':')[1].replace(']', '').strip())
                except: qtd = 1
            pos_y += int(config.ALTURA_LINHA * 1.0) * qtd
            pos_x = config.MARGEM_ESQ
            i += 1
            continue
        
        # Bloco Matriz (Com Auto-Scaler)
        if '[matriz]' in linha_limpa:
            is_centralizado = '[centro]' in linha_limpa
            i += 1
            linhas_matriz = []
            while i < len(linhas_texto) and '[/matriz]' not in linhas_texto[i]:
                if linhas_texto[i].strip(): linhas_matriz.append(linhas_texto[i].strip())
                i += 1
            i += 1
            
            matriz_dados = [[cel.strip() for cel in l.split(',')] for l in linhas_matriz]
            if not matriz_dados: continue
            
            img_m = desenhar_matriz(matriz_dados, banco_letras, ancoras)
            if img_m is not None:
                h_m, w_m = img_m.shape
                # Reduz a matriz inteira se ela for mais larga que a página
                if w_m > area_util:
                    fator = area_util / w_m
                    img_m = cv2.resize(img_m, (int(w_m * fator), int(h_m * fator)), interpolation=cv2.INTER_AREA)
                    h_m, w_m = img_m.shape
                    
                if pos_y + h_m > (A4_ALTURA - config.MARGEM_BAIXO):
                    paginas_geradas.append(fundo.copy())
                    fundo, _, _ = carregar_fundo(caminho_fundo)
                    pos_y = config.MARGEM_TOPO
                
                pos_x = config.MARGEM_ESQ + max(0, (area_util - w_m) // 2) if is_centralizado else config.MARGEM_ESQ
                    
                x_fim = min(pos_x + w_m, A4_LARGURA)
                y_fim = min(pos_y + h_m, A4_ALTURA)
                w_ef, h_ef = x_fim - pos_x, y_fim - pos_y
                
                if w_ef > 0 and h_ef > 0:
                    img_col = cv2.cvtColor(img_m[:h_ef, :w_ef], cv2.COLOR_GRAY2BGR)
                    regiao = fundo[pos_y:y_fim, pos_x:x_fim]
                    fundo[pos_y:y_fim, pos_x:x_fim] = np.minimum(regiao, img_col)
                pos_y += h_m + int(config.ALTURA_LINHA * 0.8)
            continue
            
        # Bloco Tabela (Com Auto-Scaler)
        if '[tabela]' in linha_limpa:
            is_centralizado = '[centro]' in linha_limpa
            i += 1
            linhas_tabela = []
            while i < len(linhas_texto) and '[/tabela]' not in linhas_texto[i]:
                if linhas_texto[i].strip(): linhas_tabela.append(linhas_texto[i].strip())
                i += 1
            i += 1
            
            tabela_dados = [[cel.strip() for cel in l.split('|')] for l in linhas_tabela]
            if not tabela_dados: continue
            
            img_t = desenhar_tabela(tabela_dados, banco_letras, ancoras)
            if img_t is not None:
                h_t, w_t = img_t.shape
                if w_t > area_util:
                    fator = area_util / w_t
                    img_t = cv2.resize(img_t, (int(w_t * fator), int(h_t * fator)), interpolation=cv2.INTER_AREA)
                    h_t, w_t = img_t.shape
                    
                if pos_y + h_t > (A4_ALTURA - config.MARGEM_BAIXO):
                    paginas_geradas.append(fundo.copy())
                    fundo, _, _ = carregar_fundo(caminho_fundo)
                    pos_y = config.MARGEM_TOPO
                
                pos_x = config.MARGEM_ESQ + max(0, (area_util - w_t) // 2) if is_centralizado else config.MARGEM_ESQ
                    
                x_fim = min(pos_x + w_t, A4_LARGURA)
                y_fim = min(pos_y + h_t, A4_ALTURA)
                w_ef, h_ef = x_fim - pos_x, y_fim - pos_y
                
                if w_ef > 0 and h_ef > 0:
                    img_col = cv2.cvtColor(img_t[:h_ef, :w_ef], cv2.COLOR_GRAY2BGR)
                    regiao = fundo[pos_y:y_fim, pos_x:x_fim]
                    fundo[pos_y:y_fim, pos_x:x_fim] = np.minimum(regiao, img_col)
                pos_y += h_t + int(config.ALTURA_LINHA * 0.8)
            continue

        if not linha_limpa:
            pos_y += int(config.ALTURA_LINHA * 0.8)
            pos_x = config.MARGEM_ESQ
            i += 1
            continue
            
        is_titulo = linha_limpa.startswith('#')
        if is_titulo:
            linha_limpa = linha_limpa[1:].strip()
            escala_atual = 1.45
            altura_linha_atual = int(config.ALTURA_LINHA * 1.5)
        else:
            escala_atual = 1.0
            altura_linha_atual = config.ALTURA_LINHA
            
        is_centralizado = '[centro]' in linha_limpa
        if is_centralizado:
            linha_limpa = linha_limpa.replace('[centro]', '').strip()
            
        palavras_originais = linha_limpa.split()
        if not palavras_originais:
            i += 1
            continue
            
        limite_linha = A4_LARGURA - config.MARGEM_DIR
        
        # Titulo e Centralizados (Com Auto-Scaler para caber na folha!)
        if is_centralizado or is_titulo:
            imgs_linha = []
            largura_total_linha = 0
            
            for p in palavras_originais:
                img_p = gerar_palavra(p, banco_letras, ancoras, escala=escala_atual)
                if img_p is not None:
                    imgs_linha.append(img_p)
                    largura_total_linha += img_p.shape[1] + config.ESPACO_BASE
                    
            if imgs_linha:
                # Se o titulo for maior que a folha, ele encolhe automaticamente a escala
                if largura_total_linha > area_util:
                    fator_reducao = (area_util - 30) / largura_total_linha
                    escala_atual *= fator_reducao
                    
                    # Refaz o calculo com a nova escala
                    imgs_linha = []
                    largura_total_linha = 0
                    for p in palavras_originais:
                        img_p = gerar_palavra(p, banco_letras, ancoras, escala=escala_atual)
                        if img_p is not None:
                            imgs_linha.append(img_p)
                            largura_total_linha += img_p.shape[1] + config.ESPACO_BASE
                
                if is_centralizado:
                    pos_x = config.MARGEM_ESQ + max(0, (area_util - largura_total_linha) // 2)
                else:
                    pos_x = config.MARGEM_ESQ + random.randint(-config.VARIA_MARGEM_ESQ, config.VARIA_MARGEM_ESQ)
                    
                if pos_y + altura_linha_atual > (A4_ALTURA - config.MARGEM_BAIXO):
                    paginas_geradas.append(fundo.copy())
                    fundo, _, _ = carregar_fundo(caminho_fundo)
                    pos_y = config.MARGEM_TOPO
                    
                for img_palavra in imgs_linha:
                    h, w = img_palavra.shape
                    y_alinhado = pos_y + ((altura_linha_atual - h) // 2)
                    x_fim = min(pos_x + w, A4_LARGURA)
                    y_fim = min(y_alinhado + h, A4_ALTURA)
                    w_ef, h_ef = x_fim - pos_x, y_fim - y_alinhado
                    
                    if w_ef > 0 and h_ef > 0:
                        img_colorida = cv2.cvtColor(img_palavra[:h_ef, :w_ef], cv2.COLOR_GRAY2BGR)
                        regiao = fundo[y_alinhado:y_fim, pos_x:x_fim]
                        fundo[y_alinhado:y_fim, pos_x:x_fim] = np.minimum(regiao, img_colorida)
                        
                    pos_x += w + config.ESPACO_BASE + random.randint(-config.VARIA_ESPACO, config.VARIA_ESPACO)
                    
            pos_y += altura_linha_atual + random.randint(-config.VARIA_ALTURA_LINHA, config.VARIA_ALTURA_LINHA)
            pos_x = config.MARGEM_ESQ
            i += 1
            continue

        # Texto normal (restante igual, hifenizacao mantida...)
        pos_x = config.MARGEM_ESQ + random.randint(-config.VARIA_MARGEM_ESQ, config.VARIA_MARGEM_ESQ)
        fola_palavras = list(palavras_originais)
        
        while fola_palavras:
            if pos_y + altura_linha_atual > (A4_ALTURA - config.MARGEM_BAIXO):
                paginas_geradas.append(fundo.copy())
                fundo, _, _ = carregar_fundo(caminho_fundo)
                pos_x = config.MARGEM_ESQ + random.randint(-config.VARIA_MARGEM_ESQ, config.VARIA_MARGEM_ESQ)
                pos_y = config.MARGEM_TOPO
                
            p = fola_palavras.pop(0)
            img_palavra = gerar_palavra(p, banco_letras, ancoras, escala=escala_atual)
            if img_palavra is None: continue
            
            h, w = img_palavra.shape
            
            if pos_x + w > limite_linha:
                espaco_restante = limite_linha - pos_x
                w_media_letra = w / max(1, len(p))
                letras_que_cabem = int(espaco_restante / w_media_letra)
                
                partes = separar_silaba_dinamica(p, letras_que_cabem) if '-' in banco_letras else None
                
                if partes:
                    p1, p2 = partes
                    img_p1 = gerar_palavra(p1 + '-', banco_letras, ancoras, escala=escala_atual)
                    
                    if img_p1 is not None and (pos_x + img_p1.shape[1] < limite_linha + 15):
                        h1, w1 = img_p1.shape
                        y_alinhado1 = pos_y + ((altura_linha_atual - h1) // 2)
                        
                        x_fim = min(pos_x + w1, A4_LARGURA)
                        y_fim = min(y_alinhado1 + h1, A4_ALTURA)
                        w_ef, h_ef = x_fim - pos_x, y_fim - y_alinhado1
                        
                        if w_ef > 0 and h_ef > 0:
                            img_c1 = cv2.cvtColor(img_p1[:h_ef, :w_ef], cv2.COLOR_GRAY2BGR)
                            regiao1 = fundo[y_alinhado1:y_fim, pos_x:x_fim]
                            fundo[y_alinhado1:y_fim, pos_x:x_fim] = np.minimum(regiao1, img_c1)
                            
                        fola_palavras.insert(0, p2)
                        pos_y += altura_linha_atual + random.randint(-config.VARIA_ALTURA_LINHA, config.VARIA_ALTURA_LINHA)
                        pos_x = config.MARGEM_ESQ + random.randint(-config.VARIA_MARGEM_ESQ, config.VARIA_MARGEM_ESQ)
                        continue
                
                pos_y += altura_linha_atual + random.randint(-config.VARIA_ALTURA_LINHA, config.VARIA_ALTURA_LINHA)
                pos_x = config.MARGEM_ESQ + random.randint(-config.VARIA_MARGEM_ESQ, config.VARIA_MARGEM_ESQ)
                
                if pos_y + altura_linha_atual > (A4_ALTURA - config.MARGEM_BAIXO):
                    paginas_geradas.append(fundo.copy())
                    fundo, _, _ = carregar_fundo(caminho_fundo)
                    pos_x = config.MARGEM_ESQ + random.randint(-config.VARIA_MARGEM_ESQ, config.VARIA_MARGEM_ESQ)
                    pos_y = config.MARGEM_TOPO
                
                img_palavra = gerar_palavra(p, banco_letras, ancoras, escala=escala_atual)
                if img_palavra is None: continue
                h, w = img_palavra.shape

            y_alinhado = pos_y + ((altura_linha_atual - h) // 2)
            x_fim = min(pos_x + w, A4_LARGURA)
            y_fim = min(y_alinhado + h, A4_ALTURA)
            w_ef, h_ef = x_fim - pos_x, y_fim - y_alinhado
            
            if w_ef > 0 and h_ef > 0:
                img_colorida = cv2.cvtColor(img_palavra[:h_ef, :w_ef], cv2.COLOR_GRAY2BGR)
                regiao = fundo[y_alinhado:y_fim, pos_x:x_fim]
                fundo[y_alinhado:y_fim, pos_x:x_fim] = np.minimum(regiao, img_colorida)
                
            pos_x += w + config.ESPACO_BASE + random.randint(-config.VARIA_ESPACO, config.VARIA_ESPACO)
            
        pos_y += altura_linha_atual + random.randint(-config.VARIA_ALTURA_LINHA, config.VARIA_ALTURA_LINHA)
        pos_x = config.MARGEM_ESQ
        i += 1
        
    paginas_geradas.append(fundo)
    return paginas_geradas