# Calibração com vendas reais

Rodar: `python3 ../scripts/avaliar.py <caso>.json --vendido <preço>`

## Vendas registradas

| Caso | Data | Vendido | Observações |
|---|---|---|---|
| `cassino_gramado_2284.json` — R. Gramado 2284, Cassino (ABC-IX), matr. 61.459 | 09/04/2026 | R$ 465.000 à vista | 60 m² averbados + ampliação; lote 300 m² (marinha); piscina envidraçada, gourmet coberta; mobiliada |
| `cidadenova_padrefeijo_608.json` — R. Padre Feijó 608, Cidade Nova, matr. 59.688 | 06/04/2025 | R$ 429.000 (150 mil + financ.) | Reformada, excelente acabamento; piscina aquecida; planejados e eletros incluídos. Anunciada por R$ 530.000 (Loft) → fator oferta real 0,81 |

Comparáveis e terrenos: anúncios coletados em nov/2026 (deflacionados para a data da venda).
Premissas estimadas (a confirmar): área gourmet, área construída real, valor dos móveis.

## Resultados

| Versão | Cassino (465 mil) | Cidade Nova (429 mil) |
|---|---|---|
| v1 — só R$/m² construído, oferta 0,90 | 263 mil (−43%) | 307 mil (−28%) |
| v2 a priori — terreno + lazer em R$ + evolutivo, FC 1,00, peso 70% evolutivo se amostra fraca | 467 mil (+0,5%; comp. −14%, evol. +15%) | 634 mil (+48%; comp. +9%, evol. +64%) |
| v2 ajustada — FC 0,90, conciliação 50/50 com grau de confiança | 440 mil (−5%; confiança MÉDIA) | 551 mil (+28%; confiança BAIXA, faixa 468–635 mil) |

Sensibilidade Cidade Nova (v2 ajustada) — as duas entradas mais incertas:

| Área construída | Padrão | Resultado | Erro |
|---|---|---|---|
| 105 m² | alto (R1-A) | 551 mil | +28% |
| 105 m² | normal-alto | 503 mil | +17% |
| 70 m² | alto (R1-A) | 431 mil | +0,5% |
| 70 m² | normal-alto | 398 mil | −7% |

## Lições
1. Casa pequena em lote grande (Cassino) e lazer (piscina, gourmet) exigem separar terreno e lazer — R$/m² construído sozinho subavalia muito.
2. O evolutivo superestimou nos dois casos (custo de reposição > preço de mercado) → fator de comercialização < 1 em Rio Grande, sobretudo com superadequação (acabamento acima do padrão do bairro).
3. Padrão CUB deve seguir o tipo de projeto (R1-A é casa grande de alto padrão), não só a qualidade do acabamento.
4. A área construída real é a entrada mais sensível — sempre confirmar (matrícula pode estar desatualizada; anúncio pode trazer área do lote).
5. **Atenção:** FC 0,90 e a regra de conciliação foram ajustados depois de ver estas 2 vendas. Não é validação: testar em vendas novas antes de confiar nos parâmetros.
