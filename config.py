# config.py
"""
Painel de Controle Geral do Escritor.
Ajuste essas variáveis para mudar a caligrafia, o caos humano e o layout da folha.
"""

# ========================================================
# 1. LAYOUT DA FOLHA E ESPAÇAMENTOS
# ========================================================
ALTURA_BASE = 20             # Tamanho padrão das vogais pequenas (a, e, i, o, u)
ALTURA_LINHA = 70            # Distância vertical entre uma linha e outra
ESPACO_BASE = 12             # Espaço padrão em branco entre as palavras
SOBREPOSICAO_LETRAS = 5     # Quantos pixels uma letra entra na outra para conectar

MARGEM_TOPO = 60
MARGEM_BAIXO = 60
MARGEM_ESQ = 40
MARGEM_DIR = 5

# ========================================================
# 2. VARIÁVEIS DE CAOS (O TOQUE HUMANO)
# ========================================================
VARIA_ESPACO = 4             # Varia o espaço entre palavras (ex: 12 ± 4)
VARIA_MARGEM_ESQ = 5         # Desalinhamento da margem esquerda a cada nova linha
VARIA_ALTURA_LINHA = 10      # O quanto a linha inteira sobe ou desce torta
VARIA_Y_LETRA = 1            # Micro-tremor vertical da letra dentro da mesma palavra

# ========================================================
# 3. ESTILO DA CANETA (TINTA E CORPO)
# ========================================================
TOM_ALVO = 45                # Tom de cinza da tinta (0 = preto puro, 255 = branco)
VARIA_TINTA = 0              # Simula a pressão variada da esferográfica
CORPO_EXTRA_LETRAS = 2       # Dilatação (1 ou 2) para engrossar a letra. 0 desativa.
ESPESSURA_CONEXAO = 1        # Grossura da curva de Bézier que liga as letras

# ========================================================
# 4. REGRAS DE LIGAÇÃO CURSIVA (CURVAS DE BÉZIER)
# ========================================================
NAO_LIGAM_PRA_FRENTE = ['o', 'v', 'w', 'r']
NAO_RECEBEM_LIGACAO_DE_TRAS = ['x']
ENTRADA_ALTA = ['a', 'c', 'd', 'g', 'm', 'o', 'q', 'v', 'w', 'x', 'y', 'b']
SAIDA_ALTA = ['o', 'v', 'b', 'w', 's', 'r', 'x']

# ========================================================
# 5. MAPEAMENTO LINGUÍSTICO (ACENTOS E SINAIS)
# ========================================================
MAPA_ACENTOS = {
    'á': ('a', 'agudo'), 'à': ('a', 'agudo'), 'ã': ('a', 'til'), 'â': ('a', 'circunflexo'),
    'é': ('e', 'agudo'), 'ê': ('e', 'circunflexo'),
    'í': ('i', 'agudo'),
    'ó': ('o', 'agudo'), 'õ': ('o', 'til'), 'ô': ('o', 'circunflexo'),
    'ú': ('u', 'agudo'),
    'Á': ('A_MAI', 'agudo'), 'À': ('A_MAI', 'agudo'), 'Ã': ('A_MAI', 'til'), 'Â': ('A_MAI', 'circunflexo'),
    'É': ('E_MAI', 'agudo'), 'Ê': ('E_MAI', 'circunflexo'),
    'Í': ('I_MAI', 'agudo'),
    'Ó': ('O_MAI', 'agudo'), 'Õ': ('O_MAI', 'til'), 'Ô': ('O_MAI', 'circunflexo'),
    'Ú': ('U_MAI', 'agudo'),
}

MAPA_SINAIS = {
    '.': 'ponto', ',': 'virgula', '(': 'parenteses_abre', ')': 'parenteses_fecha',
    '?': 'interrogacao', '!': 'exclamacao', ':': 'dois_pontos', ';': 'ponto_virgula',
    '+': 'mais', '=': 'igual', '≠': 'diferente',
    '±': 'mais_menos', '≈': 'aproximado', '>': 'maior', '<': 'menor',
    '%': 'porcentagem', 'Ω': 'omega', 'μ': 'micro', 'π': 'pi',
    'θ': 'theta', 'φ': 'phi', 'ω': 'omega_minusculo', 'β': 'beta',
    '∫': 'integral', 'Σ': 'somatorio', '∞': 'infinito', '∠': 'angulo',
    'Δ': 'delta', '&': 'e_comercial', '_': 'underline', '$': 'cifrao', 
    '*': 'multiplica', '^': 'circunflexo'
}

# ========================================================
# 6. ANATOMIA DAS LETRAS (Redimensionamento)
# ========================================================
def obter_parametros_letra(letra):
    """
    Retorna a proporção de altura e o deslocamento no eixo Y para cada letra.
    Retorno: (altura_redimensionamento, offset_y)
    """
    pequenas = ['a', 'c', 'e', 'i', 'm', 'n', 'o', 'r', 's', 'u', 'v', 'w', 'x']
    altas = ['b', 'd', 'k', 'l'] + [str(n) for n in range(10)]
    baixas_curtas = ['p', 'q']
    baixas_longas = ['g', 'y', 'j']
    
    maiusculas_padrao = [
        'A_MAI', 'B_MAI', 'C_MAI', 'D_MAI', 'E_MAI', 'F_MAI', 'H_MAI',
        'I_MAI', 'K_MAI', 'L_MAI', 'M_MAI', 'N_MAI', 'O_MAI', 'P_MAI',
        'R_MAI', 'S_MAI', 'T_MAI', 'U_MAI', 'V_MAI', 'W_MAI','Y_MAI', 'X_MAI', 'Z_MAI'
    ]
    maiusculas_descendentes = ['G_MAI', 'J_MAI']

    if letra in pequenas: return (ALTURA_BASE, ALTURA_BASE)
    elif letra in altas: return (int(ALTURA_BASE * 1.8), int(ALTURA_BASE * 1.8))
    elif letra in baixas_curtas: return (int(ALTURA_BASE * 1.6), ALTURA_BASE)
    elif letra in baixas_longas: return (int(ALTURA_BASE * 2.2), int(ALTURA_BASE * 1.1))
    
    elif letra == 't': return (int(ALTURA_BASE * 1.4), int(ALTURA_BASE * 1.4))
    elif letra == 'f': return (int(ALTURA_BASE * 2.2), int(ALTURA_BASE * 1.6))
    elif letra == 'z': return (int(ALTURA_BASE * 1.3), int(ALTURA_BASE * 0.7))
    elif letra == 'h': return (int(ALTURA_BASE * 1.5), int(ALTURA_BASE * 1.3))
    elif letra == 'sedilha': return (int(ALTURA_BASE * 1.4), ALTURA_BASE)

    elif letra in maiusculas_padrao: return (int(ALTURA_BASE * 1.8), int(ALTURA_BASE * 1.8))
    elif letra in maiusculas_descendentes: return (int(ALTURA_BASE * 2.4), int(ALTURA_BASE * 1.6))
    elif letra == 'Q_MAI': return (int(ALTURA_BASE * 2.0), int(ALTURA_BASE * 1.6))

    # Matemática e Operadores
    elif letra in ['pi', 'omega_minusculo', 'theta', 'angulo']: return (ALTURA_BASE, ALTURA_BASE)
    elif letra == 'infinito': return (int(ALTURA_BASE * 1.2), int(ALTURA_BASE * 1.0))
    elif letra in ['delta', 'omega', 'somatorio']: return (int(ALTURA_BASE * 1.8), int(ALTURA_BASE * 1.6))
    elif letra in ['micro', 'beta', 'phi']: return (int(ALTURA_BASE * 2.2), int(ALTURA_BASE * 1.7))
    elif letra in ['igual', 'diferente', 'mais', 'menos', 'mais_menos', 'aproximado', 'maior', 'menor']: return (int(ALTURA_BASE * 1.3), int(ALTURA_BASE * 1.3))
    elif letra == 'multiplica': return (int(ALTURA_BASE * 0.6), int(ALTURA_BASE * 1.3))
    elif letra in ['parenteses_abre', 'parenteses_fecha', 'chave_abre', 'chave_fecha', 'colchete_abre', 'colchete_fecha']: return (int(ALTURA_BASE * 2.2), int(ALTURA_BASE * 1.7))
    elif letra in ['barra', 'barra_invertida']: return (int(ALTURA_BASE * 1.8), int(ALTURA_BASE * 1.2))
    elif letra == 'integral': return (int(ALTURA_BASE * 2.8), int(ALTURA_BASE * 1.9))
    elif letra == 'porcentagem': return (int(ALTURA_BASE * 1.9), int(ALTURA_BASE * 1.3))
    elif letra == 'cifrao': return (int(ALTURA_BASE * 2.0), int(ALTURA_BASE * 1.4))
    elif letra == 'e_comercial': return (int(ALTURA_BASE * 1.8), int(ALTURA_BASE * 1.2))
    elif letra == 'underline': return (max(4, int(ALTURA_BASE * 0.8)), int(ALTURA_BASE * 0.6))

    elif letra == '-': return (max(3, int(ALTURA_BASE * 0.20)), int(ALTURA_BASE * 0.9))
    # Pontuação Básica
    elif letra in ['interrogacao', 'exclamacao']: return (int(ALTURA_BASE * 1.8), int(ALTURA_BASE * 1.8))
    elif letra == 'dois_pontos': return (int(ALTURA_BASE * 1.2), int(ALTURA_BASE * 1.5))
    elif letra == 'ponto_virgula': return (int(ALTURA_BASE * 1.5), int(ALTURA_BASE * 1.0))
    elif letra == 'ponto': return (int(ALTURA_BASE * 0.6), int(ALTURA_BASE * 0.6))
    elif letra == 'pingo': return (int(ALTURA_BASE * 0.5), int(ALTURA_BASE * 0.5))
    elif letra == 'virgula': return (int(ALTURA_BASE * 0.9), int(ALTURA_BASE * 0.2))
    elif letra in ['aspas_abre', 'aspas_fecha']: return (int(ALTURA_BASE * 0.6), int(ALTURA_BASE * 1.8))
    elif letra in ['agudo', 'circunflexo']: return (int(ALTURA_BASE * 0.8), int(ALTURA_BASE * -0.45))
    elif letra in ['til']: return (int(ALTURA_BASE * 0.9), int(ALTURA_BASE * -0.45))
    
    
    

    return (ALTURA_BASE, ALTURA_BASE)


# ========================================================
# SAÍDA DO ALGORITMO
# ========================================================
GERAR_PDF = True
NOME_ARQUIVO_PDF = "trabalho_ufma_final.pdf"

# ========================================================
# 7. DIRETÓRIOS
# ========================================================
PASTA_DATASET = "dataset_refinado"