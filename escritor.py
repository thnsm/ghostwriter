# main.py
import os
import cv2
import json
import numpy as np
from PIL import Image

import config
import motor

def carregar_texto(caminho_arquivo="entrada.txt"):
    if not os.path.exists(caminho_arquivo):
        texto_padrao = (
            "A análise de circuitos elétricos em regime senoidal requer o uso "
            "extensivo de equações matemáticas e matrizes complexas. Durante "
            "os testes laboratoriais na UFMA, verificamos que a impedância "
            "equivalente do sistema trifásico afeta diretamente a defasagem "
            "angular entre a tensão e a corrente. O projeto final que envolve "
            "a programação de microcontroladores Arduino em C e a modelagem "
            "estrutural exige foco absoluto. A largura da banda de rede local "
            "WLAN saltou de 100Mbps para mais de 650Mbps operando "
            "na frequência de 160MHz. Foi necessário recalcular a resistência de "
            "Thevenin, ajustando os parâmetros na placa de circuito impresso PCB."
        )
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            f.write(texto_padrao)
        return texto_padrao
    
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        return f.read()

def aplicar_filtro_scanner(imagem_colorida):
    """
    Simula o efeito "Magic Color" de aplicativos de scanner.
    Usa ajuste de níveis (Black Point e White Point) para padronizar 
    a tinta em preto sólido sem destruir o anti-aliasing das bordas.
    """
    cinza = cv2.cvtColor(imagem_colorida, cv2.COLOR_BGR2GRAY)
    
    # Parâmetros do "Photoshop"
    PONTO_PRETO = 199  # Tudo abaixo disso vira preto absoluto
    PONTO_BRANCO = 200 # Tudo acima disso vira papel branco absoluto
    
    # Aplica o estiramento (Ajuste de Níveis)
    img_float = cinza.astype(np.float32)
    scan_calculado = ((img_float - PONTO_PRETO) / (PONTO_BRANCO - PONTO_PRETO)) * 255.0
    
    # Corta os excessos que passaram de 0 ou 255
    scan_final = np.clip(scan_calculado, 0, 255).astype(np.uint8)
    
    return scan_final
    
    return scan_pb

def main():
    print("=" * 55)
    print("ESCRITOR CALIGRÁFICO - GERADOR DE PDF SIGAA")
    print("=" * 55)

    pasta_dataset = "dataset_refinado"
    foto_papel_real = "Folha.jpeg"
    arquivo_ancoras = "ancoras.json"
    
    ancoras = None
    if os.path.exists(arquivo_ancoras):
        with open(arquivo_ancoras, 'r', encoding='utf-8') as f:
            ancoras = json.load(f)
        print("[+] Mapa de âncoras cursivas carregado.")

    print("[*] Carregando banco de letras e processando matrizes...")
    banco = motor.carregar_banco_de_letras(pasta_dataset)
    
    if not banco:
        print("[!] ERRO: Nenhuma letra encontrada.")
        return

    texto = carregar_texto("entrada.txt")
    print(f"[+] Texto carregado com sucesso ({len(texto)} caracteres).")

    print(f"[*] Renderizando caligrafia na folha '{foto_papel_real}'...")
    paginas = motor.escrever_texto_longo(texto, banco, ancoras, foto_papel_real)

    if not paginas:
        print("[!] Erro durante a renderização.")
        return

    imagens_pil_pb = []
    print("\n[*] Salvando arquivos gerados:")
    
    for i, pagina in enumerate(paginas):
        # 1. Salva a versão normal (Colorida, textura de papel real)
        nome_normal = f"saida_pagina_{i+1}_NORMAL.jpg"
        cv2.imwrite(nome_normal, pagina, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
        print(f"   -> Imagem Normal salva: {nome_normal}")
        
        # 2. Aplica o filtro de Scanner
        pagina_pb = aplicar_filtro_scanner(pagina)
        
        # 3. Salva a versão P&B (Estilo Xerox/Scanner)
        nome_pb = f"saida_pagina_{i+1}_SIGAA.jpg"
        cv2.imwrite(nome_pb, pagina_pb, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
        print(f"   -> Imagem Escaneada salva: {nome_pb}")
        
        # Converte a imagem P&B para o PDF
        rgb_img_pb = cv2.cvtColor(pagina_pb, cv2.COLOR_GRAY2RGB)
        imagens_pil_pb.append(Image.fromarray(rgb_img_pb))

    if config.GERAR_PDF and imagens_pil_pb:
        imagens_pil_pb[0].save(
            config.NOME_ARQUIVO_PDF,
            save_all=True,
            append_images=imagens_pil_pb[1:]
        )
        print(f"   -> PDF em Preto e Branco finalizado: {config.NOME_ARQUIVO_PDF}")
        
    print("\n" + "=" * 55)
    print("GRAÇAS A DEUS TERMINEI! '_SIGAA.jpg'.")
    print("=" * 55)

if __name__ == "__main__":
    main()