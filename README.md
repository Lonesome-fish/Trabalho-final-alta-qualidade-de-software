# Supermarket Receipt — Modernização de Sistema Legado

Trabalho da disciplina **Alta Qualidade de Software**. Modernização incremental do kata
[Supermarket Receipt](https://github.com/emilybache/SupermarketReceipt-Refactoring-Kata)
(versão `python_pytest`): testes de caracterização, refatoração com padrões de projeto,
combos promocionais e análise de segurança.

## Requisitos

- Python 3.10 ou superior
- Dependências em `python_pytest/requirements.txt` (versões fixadas)

## Como rodar

```bash
cd python_pytest
python -m venv .venv
.venv\Scripts\activate          # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python -m pytest
```

Cobertura:

```bash
python -m coverage run -m pytest
python -m coverage report
```

## Análise de segurança

```bash
pip install bandit pip-audit safety
bandit -r src
pip-audit -r requirements.txt
safety scan          # exige login gratuito na Safety CLI
```

## Estrutura

```
python_pytest/
  src/
    catalog.py               interface do catálogo de produtos
    model_objects.py         Product, Offer, Discount e enums
    shopping_cart.py         carrinho: guarda itens e valida quantidades
    teller.py                caixa: registra ofertas/combos e faz o checkout
    discount_strategies.py   estratégias de desconto, factory e calculadora
    receipt.py               recibo e cálculo do total
  tests/                     testes pytest (legado, ofertas, combos, recibo)
python/                      versão original sem pytest (não modificada)
```

## Decisões de arquitetura

- **Strategy:** cada regra de desconto é uma classe (`ThreeForTwoStrategy`,
  `PercentageDiscountStrategy`, `XForAmountStrategy`, `ComboDiscountStrategy`).
- **Factory:** `DiscountStrategyFactory` escolhe a estratégia pelo tipo da oferta.
- **DiscountCalculator:** concentra o cálculo; o carrinho só guarda itens e o Teller orquestra.
- **Combos:** 10% sobre os conjuntos completos. Nenhuma unidade recebe dois descontos, e o
  sistema escolhe a combinação mais barata para o cliente.
- **Mudanças intencionais de comportamento:** "2 por X" com quantidade ímpar, fração em
  produtos por kg nas ofertas de pacote e validação de quantidades no carrinho.

## Licença

Baseado no kata de Emily Bache. Ver `license.txt`.
