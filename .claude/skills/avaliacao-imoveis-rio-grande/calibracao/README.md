# Calibração com vendas reais

Rodar: `python3 ../scripts/avaliar.py <caso>.json --vendido <preço>`

## Vendas registradas

| Caso | Data | Vendido | Observações |
|---|---|---|---|
| `cassino_gramado_2284.json` — R. Gramado 2284, Cassino (ABC-IX), matr. 61.459 | 09/04/2026 | R$ 465.000 à vista | 60 m² averbados + ampliação; lote 300 m² (marinha); piscina envidraçada, gourmet coberta; mobiliada |
| `cidadenova_padrefeijo_608.json` — R. Padre Feijó 608, Cidade Nova, matr. 59.688 | 06/04/2025 | R$ 429.000 (150 mil + financ.) | Reformada, excelente acabamento; piscina aquecida; planejados e eletros incluídos. Anunciada por R$ 530.000 (Loft) → fator oferta real 0,81 |
| `apto_braganca_bl06_204.json` — Apto 204 Bl 06 + box, Cond. Bragança (Carreiros), matr. 71.435/72.790 | 10/09/2024 | R$ 165.000 | 47,71 m² priv.; móveis sob medida incluídos |
| `apto_villagecenter_j1_103.json` — Apto 103 Bl J1, Res. Village Center (Pq. Cidade Nova), matr. 63.927 | 24/02/2022 | R$ 160.000 | 54,08 m² priv.; vendido locado, financ. Banrisul |
| `casa_joqueiclub_102_c2.json` — Casa 2, R. Jóquei Club 102, matr. 26.802 | ~12/2020 | R$ 150.000 | 86 m² priv. (1984); avaliação do banco R$ 192.000. **Sem resultado**: só 1 comparável |

Vendas recebidas e **não testadas**:
- R. Victor Canuso 1.181, Cassino (Pq. Guanabara, lote 10x22, matr. 21.417), R$ 180.000 (~2021): falta área construída e descrição da casa.
- Apto 202 Bl 3, R. Alm. Barroso 189 (37,31 m², matr. 23.187), R$ 63.000 (out/2020): venda com dívidas de condomínio quitadas no preço — não é valor de mercado típico; sem comparáveis.
- Posse de 2 lotes + 2 casas de 32,4 m², R. Frederico Albuquerque 840, Ilha do Marinheiro, R$ 60.000 (mar/2026): direitos possessórios sem matrícula — fora do escopo do método.

Comparáveis e terrenos: anúncios coletados em nov/2026 (deflacionados para a data da venda).
Premissas estimadas (a confirmar): área gourmet, área construída real, valor dos móveis.

## Resultados

| Versão | Cassino (465 mil) | Cidade Nova (429 mil) |
|---|---|---|
| v1 — só R$/m² construído, oferta 0,90 | 263 mil (−43%) | 307 mil (−28%) |
| v2 a priori — terreno + lazer em R$ + evolutivo, FC 1,00, peso 70% evolutivo se amostra fraca | 467 mil (+0,5%; comp. −14%, evol. +15%) | 634 mil (+48%; comp. +9%, evol. +64%) |
| v2 ajustada — FC 0,90, conciliação 50/50 com grau de confiança | 440 mil (−5%; confiança MÉDIA) | 551 mil (+28%; confiança BAIXA, faixa 468–635 mil) |

### Validação fora da amostra (parâmetros congelados, nenhum ajuste após ver o resultado)
Áreas gourmet atualizadas com as medidas informadas (Cassino 3x6 = 18 m²; Padre Feijó 2x4 = 8 m²).

| Caso | Vendido | Skill v2 | Erro | Observação |
|---|---|---|---|---|
| Apto Bragança (2024) | 165 mil | 150 mil | −9% | 4 comparáveis do mesmo condomínio (leilões excluídos), CV 8% |
| Apto Village Center (2022) | 160 mil | 145 mil | −10% | 3 comparáveis do mesmo condomínio, CV 3% |
| Casa Jóquei Club (2020) | 150 mil | — | — | amostra insuficiente (1 comparável) |
| Cassino (recalculado c/ gourmet 18 m²) | 465 mil | 426 mil | −8% | confiança MÉDIA |
| Padre Feijó (gourmet 8 m², área 105 m² do anúncio) | 429 mil | 542 mil | +26% | confiança BAIXA; 105 m² era a área do lote |
| **Padre Feijó (área real ~70 m², padrão normal-alto)** | 429 mil | **389 mil** | **−9%** | confiança MÉDIA; comp. −19%, evol. +1%. Com padrão "alto": 422 mil (−2%) |

**Resumo dos 4 casos com resultado (parâmetros atuais):** −8%, −9%, −9%, −10%. Viés sistemático para baixo, vindo do comparativo (−9% a −19%); o evolutivo ficou entre +1% e +3% nas casas. Hipótese: fator oferta 0,85 baixo demais — com 0,90 o erro dos apartamentos cai para −4%. Decidir com mais vendas.

Sensibilidade ao fator oferta (só informativa, **não aplicada**): com 0,90 os apartamentos vão a −4% e o Cassino a −6%, mas a Padre Feijó piora para +30%. Os dois apartamentos sugerem que 0,85 está baixo para unidades padronizadas em condomínio, mas 2 casos não bastam para mudar.

Sensibilidade Cidade Nova (v2 ajustada, gourmet 12 m²) — as duas entradas mais incertas:

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
4. A área construída real é a entrada mais sensível (Padre Feijó: 105 m² do anúncio era o lote; com os ~70 m² reais o erro foi de +26% para −9%) — sempre confirmar (matrícula pode estar desatualizada; anúncio pode trazer área do lote).
5. Apartamento com comparáveis do mesmo condomínio é o caso em que a skill funciona melhor (erro ~−9%, viés para baixo consistente).
6. Excluir leilões e licitações da Caixa da amostra (preço 40% abaixo do mercado no Bragança).
7. **Atenção:** FC 0,90 e a regra de conciliação foram ajustados depois de ver estas 2 vendas. Não é validação: testar em vendas novas antes de confiar nos parâmetros.
