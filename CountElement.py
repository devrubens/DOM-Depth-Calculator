from bs4 import BeautifulSoup

def calcular_profundidade(elemento):
    """Calcula quantos níveis hierárquicos existem até o elemento HTML raiz"""
    profundidade = 0
    atual = elemento.parent
    while atual is not None and atual.name != 'html':
        profundidade += 1
        atual = atual.parent
    return profundidade + 1  # Adiciona 1 para contar o próprio elemento html

def contar_classes(elemento):
    """Conta quantas classes estão presentes no elemento"""
    classes = elemento.get('class', [])
    return len(classes) if isinstance(classes, list) else len(classes.split())

def analisar_elemento():
    # Recebe o HTML do usuário
    print("Cole seu HTML abaixo (pressione Enter duas vezes para finalizar):")
    html_lines = []
    while True:
        line = input()
        if line == "":
            break
        html_lines.append(line)
    html = '\n'.join(html_lines)

    # Recebe o seletor CSS do elemento
    seletor = input("\nDigite o seletor CSS do elemento: ")

    # Processa o HTML
    soup = BeautifulSoup(html, 'html.parser')
    elemento = soup.select_one(seletor)

    if elemento:
        # Calcula as métricas
        profundidade = calcular_profundidade(elemento)
        num_classes = contar_classes(elemento)

        # Exibe os resultados
        print("\nResultado da análise:")
        print(f"Tag: {elemento.name}")
        print(f"Profundidade DOM: {profundidade} níveis")
        print(f"Classes encontradas: {num_classes}")
        if 'class' in elemento.attrs:
            print(f"Lista de classes: {', '.join(elemento['class'])}")
    else:
        print("Elemento não encontrado!")

if __name__ == "__main__":
    analisar_elemento()