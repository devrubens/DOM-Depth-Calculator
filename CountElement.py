from bs4 import BeautifulSoup
import uuid
from datetime import datetime
import json
import re


class ElementAnalyzer:
    def __init__(self, html):
        self.soup = BeautifulSoup(html, 'html.parser')
        self.analysis_id = str(uuid.uuid4())
        self.now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def analyze(self, css_selector):
        try:
            safe_selector = self._sanitize_selector(css_selector)
            element = self.soup.select_one(safe_selector)

            if not element:
                return self._error_response(f"Elemento não encontrado com: '{css_selector}'")

            analysis = self._element_analysis(element)
            selector_analysis = self._selector_analysis(css_selector, element)

            return {
                'analysis_id': self.analysis_id,
                'element_info': analysis,
                'selector_info': selector_analysis
            }

        except Exception as e:
            return self._error_response(str(e), css_selector)

    def _sanitize_selector(self, selector):
        # Adiciona # se for um ID puro
        if not selector.startswith(('#', '.', '[', '(')) and '=' not in selector:
            selector = f'#{selector}'

        # Escape avançado para caracteres especiais
        selector = re.sub(r'(?<!\\)(:)', r'\\\1', selector)
        selector = re.sub(r'(?<!\\)(\[)', r'\\\1', selector)
        selector = re.sub(r'\s+', ' ', selector).strip()
        return selector

    def _element_analysis(self, element):
        return {
            'html_id': element.get('id', 'Nenhum'),
            'tag': element.name,
            'attributes': self._get_attributes(element),
            'depth': self._dom_depth(element),
            'text': self._clean_text(element),
            'classes': len(self._get_classes(element)),
            'attributes_count': len(element.attrs),
        }

    def _get_attributes(self, element):
        attrs = {
            'static': {},
            'dynamic': {},
            'metadata': {}
        }

        for attr, value in element.attrs.items():
            if attr in ['id', 'name']:
                attrs['static'][attr] = value
            elif attr.startswith(('data-', 'aria-')):
                attrs['dynamic'][attr] = value
            else:
                attrs['metadata'][attr] = value

        return json.dumps(attrs, ensure_ascii=False, indent=2)

    def _dom_depth(self, element):
        depth = 0
        current = element.parent
        while current and current.name != 'html':
            depth += 1
            current = current.parent
        return depth

    def _clean_text(self, element):
        return re.sub(r'\s+', ' ', element.get_text(strip=True))

    def _get_classes(self, element):
        return element.get('class', [])

    def _selector_analysis(self, selector, element):
        return {
            'selector': selector,
            'is_dynamic': self._is_dynamic(selector),
            'dynamic_patterns': self._find_dynamic_patterns(selector),
            'recommended': self._recommend_alternatives(element),
            'warnings': self._detect_warnings(selector, element)
        }

    def _is_dynamic(self, selector):
        patterns = [
            r'\\?:[\w-]+',
            r'\[\d+\]',
            r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{12}',
            r'\d{10,}',
            r'[A-Z0-9]{16}'
        ]
        return any(re.search(p, selector) for p in patterns)

    def _find_dynamic_patterns(self, selector):
        patterns = {
            'headlessui_id': r'\\?:[\w-]+',
            'uuid': r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{12}',
            'timestamp': r'\d{10,}',
            'index': r'\[\d+\]'
        }
        return [name for name, p in patterns.items() if re.search(p, selector)]

    def _recommend_alternatives(self, element):
        stable_attrs = ['data-testid', 'data-qa', 'data-cy', 'data-test', 'aria-label']
        return {
            'attributes': [attr for attr in stable_attrs if attr in element.attrs],
            'selectors': self._generate_stable_selectors(element)
        }

    def _generate_stable_selectors(self, element):
        selectors = []
        if 'data-testid' in element.attrs:
            selectors.append(f"[data-testid='{element['data-testid']}']")
        if 'aria-label' in element.attrs:
            selectors.append(f"[aria-label='{element['aria-label']}']")
        if element.get('role'):
            selectors.append(f"[role='{element['role']}']")
        return selectors

    def _detect_warnings(self, selector, element):
        warnings = []
        if 'id' in selector and 'data-testid' in element.attrs:
            warnings.append("ID dinâmico detectado - Prefira usar data-testid")
        if '::' in selector:
            warnings.append("Sintaxe de pseudo-elemento inválida - Use ':' para pseudo-classes")
        return warnings

    def _error_response(self, message, selector=None):
        response = {
            'error': message,
            'severity': 'critical' if 'não encontrado' in message else 'warning',
            'timestamp': self.now
        }
        if selector:
            response['selector'] = selector
            response['suggestions'] = self._general_suggestions(selector)
        return response

    def _general_suggestions(self, selector):
        suggestions = []
        if not selector.startswith(('#', '.', '[')):
            suggestions.append("Seletor parece ser um ID - Tente adicionar # no início")
        if '::' in selector:
            suggestions.append("Para pseudo-elementos use '::', para pseudo-classes use ':'")
        return suggestions


class AnalysisPresenter:
    @staticmethod
    def present(result):
        if 'error' in result:
            AnalysisPresenter._print_error(result)
        else:
            AnalysisPresenter._print_success(result)

    @staticmethod
    def _print_error(result):
        print(f"\n\033[1;31mERRO: {result['error']}\033[0m")
        print(f"\033[33mSeletor usado: {result.get('selector', 'N/A')}\033[0m")
        print("\n\033[1mSugestões:\033[0m")
        for suggestion in result.get('suggestions', []):
            print(f" • \033[32m{suggestion}\033[0m")

    @staticmethod
    def _print_success(result):
        print(f"\n\033[1;36m=== RESULTADO DA ANÁLISE ===\033[0m")
        print(f"\033[1mID da Análise (UUID):\033[0m {result['analysis_id']}")
        print(f"\033[1mID do Elemento (HTML):\033[0m {result['element_info']['html_id']}")

        print("\n\033[1mINFORMAÇÕES DO ELEMENTO:\033[0m")
        print(f" • Tag: {result['element_info']['tag']}")
        print(f" • Texto: '{result['element_info']['text']}'")
        print(f" • Profundidade DOM: {result['element_info']['depth']} nível(s)")
        print(f" • Classes: {result['element_info']['classes']}")
        print(f" • Total de Atributos: {result['element_info']['attributes_count']}")

        print("\n\033[1mDETALHAMENTO DOS ATRIBUTOS:\033[0m")
        attributes = json.loads(result['element_info']['attributes'])

        print("\n\033[1;34m● Estáticos (ID, Name):\033[0m")
        for attr in ['id', 'name']:
            if attributes['static'].get(attr):
                print(f"  {attr}: {attributes['static'][attr]}")

        print("\n\033[1;35m● Dinâmicos (Data-*, Aria-*):\033[0m")
        for attr, value in attributes['dynamic'].items():
            print(f"  {attr}: {value}")

        print("\n\033[1;36m● Metadados (Type, Value, etc):\033[0m")
        for attr, value in attributes['metadata'].items():
            if attr not in ['class']:  # Classes já são mostradas separadamente
                print(f"  {attr}: {value}")

        print("\n\033[1mANÁLISE DO SELETOR:\033[0m")
        selector_info = result['selector_info']
        status = "\033[32mESTÁTICO\033[0m" if not selector_info['is_dynamic'] else "\033[31mDINÂMICO\033[0m"
        print(f" • Status: {status}")

        if selector_info['dynamic_patterns']:
            print(f" • Padrões dinâmicos: {', '.join(selector_info['dynamic_patterns'])}")

        if selector_info['recommended']['attributes']:
            print("\n\033[1mATRIBUTOS ESTÁVEIS DISPONÍVEIS:\033[0m")
            for attr in selector_info['recommended']['attributes']:
                print(
                    f" • \033[34m{attr}: {json.loads(result['element_info']['attributes'])['dynamic'].get(attr, '')}\033[0m")

        if selector_info['recommended']['selectors']:
            print("\n\033[1mSELETORES RECOMENDADOS:\033[0m")
            for selector in selector_info['recommended']['selectors']:
                print(f" • \033[35m{selector}\033[0m")


def main():
    print("\033[1;34m\nCOLE O HTML (duas linhas vazias para finalizar):\033[0m")
    html = []
    while True:
        line = input()
        if not line and html and html[-1] == "":
            break
        html.append(line)

    selector = input("\n\033[1;34mDIGITE O SELETOR CSS:\033[0m ")

    analyzer = ElementAnalyzer('\n'.join(html))
    result = analyzer.analyze(selector)

    AnalysisPresenter.present(result)


if __name__ == "__main__":
    main()