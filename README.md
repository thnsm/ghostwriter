# Ghostwriter — Sintetizador de Caligrafia Humana Realista

O **Ghostwriter** é um motor de síntese tipográfica e caligráfica em Python projetado para converter texto digital estruturado em documentos manuscritos realistas. O algoritmo replica as nuances físicas da escrita manual com caneta esferográfica sobre papel real, gerando saídas de alta fidelidade visual tanto em cor (textura de folha física) quanto em formato digitalizado (filtro de scanner P&B de alto contraste, ideal para documentos digitalizados e impressos).

O sistema foi concebido para permitir a substituição de conjuntos de dados caligráficos com facilidade, adaptando-se à caligrafia de qualquer usuário por meio de recortes de caracteres e calibração de parâmetros de dispersão orgânica.

---

## Demonstração

<!-- Substitua o placeholder abaixo pelo caminho ou link da sua imagem de demonstração -->
![Demonstração da Caligrafia Gerada](link_da_imagem_aqui)

*Exemplo de renderização com simulação de pressão de tinta, conexões por curvas de Bézier e alinhamento dinâmico sobre textura de folha real.*

---

## Estrutura do Repositório

```text
├── assets/
│   └── Folha.jpeg              # Textura base de papel A4 digitalizado
├── inputs/
│   └── entrada.txt             # Arquivo de texto a ser processado pelo escritor
├── dataset_refinado/           # Recortes isolados de caracteres (letras, acentos e símbolos)
├── src/
│   ├── config.py               # Painel de parâmetros, layout, estilo de tinta e variáveis de caos
│   ├── motor.py                # Núcleo de computação gráfica, ligaduras, hifenização e layout
│   └── escritor.py             # Pipeline principal de orquestração, filtros e geração de PDF
├── ancoras.json                # Coordenadas vetoriais normalizadas de entrada/saída das letras
├── requirements.txt            # Dependências externas do projeto
└── README.md                   # Documentação técnica do sistema
```

---

## Arquitetura do Software

O pipeline é modularizado em três componentes centrais dentro do diretório `/src`:

* [**`motor.py`**](file:///src/motor.py) **(Core Engine & Computação Gráfica)**:
  Contém o núcleo matemático e gráfico do projeto. É responsável pela leitura e normalização de contraste dos recortes do dataset, posicionamento dinâmico de glifos ao longo da linha de base, interpolação de ligaduras cursivas através de curvas cúbicas de Bézier com micro-variações randômicas nos pontos de controle, quebra de linha com hifenização silábica dinâmica, centralização de acentos a partir do centróide da massa de tinta do caractere e renderização de tabelas e matrizes com colchetes e traços orgânicos.

* [**`escritor.py`**](file:///src/escritor.py) **(Orquestrador do Pipeline)**:
  Atua como ponto de entrada da aplicação. Carrega as configurações de diretório e texto de entrada, coordena a renderização das páginas chamando o motor gráfico, aplica o filtro de digitalização via ajuste de níveis (*Black Point / White Point stretching*) para reproduzir o aspecto de scanner de documentos ("Magic Color") e empacota o conjunto final de páginas em imagens JPEG e no documento compilado PDF.

* [**`config.py`**](file:///src/config.py) **(Camada de Configuração & Resolução de Caminhos)**:
  Centraliza todas as variáveis de calibração em um único painel acessível. Expõe métricas de escala tipográfica (`ALTURA_BASE`, `ALTURA_LINHA`), tolerâncias de sobreposição, coeficientes de caos estocástico (tremor de mão, desvio de linha, flutuação de margem e variação de pressão da tinta) e regras de conexão cursiva. Conta ainda com um resolvedor universal de caminhos relativos (`resolver_caminho`), assegurando execução idempotente tanto a partir da raiz do repositório quanto de dentro da pasta `/src`.

---

## Lógica de Processamento e Desafios de Engenharia

Simular a escrita manual envolve superar desafios que tipografias tradicionais ignoram por completo:

1. **Ligaduras Cursivas Vetoriais (Curvas de Bézier)**:
   Ao contrário de fontes de computador que utilizam espaçamento fixo, a escrita cursiva humana exige que a cauda de uma letra se funda fluidamente com a haste da próxima. O sistema resolve isso mapeando pontos de contato normalizados (0.0 a 1.0) em `ancoras.json`. O algoritmo traça curvas cúbicas cujos pontos de controle são calculados a partir da anatomia das letras adjacentes (entradas/saídas altas ou baixas), adicionando micro-perturbações randômicas para evitar traços perfeitamente geométricos.

2. **Caos Orgânico Estocástico (Imperfeição Humana)**:
   A repetição visual idêntica denuncia automação. O motor mitiga esse problema implementando:
   * **Memória de glifos (`memoria_letras`)**: Garante que o mesmo recorte de letra não seja repetido consecutivamente quando há variações disponíveis no dataset.
   * **Ruído gaussiano na linha de base e margens**: Simula a fadiga muscular e a tendência natural da mão em subir, descer ou flutuar ao longo da folha.
   * **Variação de pressão e tom de tinta**: Pequenas alterações na intensidade do cinza/preto no traço da caneta esferográfica.

3. **Posicionamento de Acentos por Centróide de Massa**:
   Letras com larguras variáveis não recebem acentos no centro geométrico de sua *bounding box*. O algoritmo analisa as coordenadas espaciais dos pixels de tinta da letra base (`np.where(img_letra < 240)`) para posicionar acentos (agudo, til, circunflexo) exatamente acima do centro de massa do caractere, com *clipping* defensivo contra cortes de borda.

4. **Hifenização Dinâmica e Quebra de Linha Proporcional**:
   Ao atingir o limite da margem direita da página A4, o algoritmo calcula o espaço residual restante e decompõe a palavra em sílabas fonéticas válidas (`separar_silaba_dinamica`), inserindo o hífen artesanal na linha atual e transportando o restante da palavra para a linha seguinte.

5. **Estruturas Matemáticas (Matrizes e Tabelas Manuscritas)**:
   O motor interpreta blocos `[matriz]` e `[tabela]` diretamente no texto de entrada, calculando larguras de colunas sob medida, renderizando colchetes com arqueamento progressivo (`desenhar_colchete_tremido`) e linhas de grade com micro-tremores (`desenhar_linha_tremida`), aplicando redimensionamento automático proporcional caso a estrutura exceda a largura útil da folha.

6. **Composição Gráfica e Filtro de Scanner**:
   A mesclagem dos caracteres sobre a imagem de papel real é executada em matrizes NumPy usando a operação de mínimo (`np.minimum`), fundindo a tinta escura sem produzir halos esbranquiçados sobre o papel. Em seguida, a rotina de pós-processamento estica os níveis de luminância (pontos pretos e brancos definidos), produzindo o contraste de documento fotocopiado/escaneado.

---

## Como Executar

### 1. Pré-requisitos
* Python 3.10 ou superior
* Gerenciador de pacotes `pip`

### 2. Configurar o Ambiente Virtual
Clone ou navegue até a pasta do projeto e configure o ambiente virtual:

```bash
# Criar o ambiente virtual
python3 -m venv .venv

# Ativar o ambiente virtual (Linux / macOS)
source .venv/bin/activate

# Ativar no Windows (PowerShell)
# .venv\Scripts\Activate.ps1
```

### 3. Instalar Dependências
Instale as bibliotecas requeridas via `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Executar a Renderização
Edite o arquivo de texto em [`inputs/entrada.txt`](file:///inputs/entrada.txt) com o conteúdo desejado e execute o orquestrador a partir da raiz do projeto:

```bash
python src/escritor.py
```

*(O script também pode ser executado diretamente de dentro da pasta `/src` com `cd src && python escritor.py`, graças ao resolvedor interno de caminhos).*

### 5. Arquivos Gerados
Ao concluir a execução, os seguintes artefatos são gravados na raiz do repositório:
* `saida_pagina_X_NORMAL.jpg`: Imagem colorida renderizada sobre a textura de papel real.
* `saida_pagina_X_SCANNER.jpg`: Imagem com pós-processamento P&B de scanner ("Magic Color").
* `documento_manuscrito_final.pdf`: Documento PDF consolidado com todas as páginas geradas prontas para compartilhamento ou impressão.
