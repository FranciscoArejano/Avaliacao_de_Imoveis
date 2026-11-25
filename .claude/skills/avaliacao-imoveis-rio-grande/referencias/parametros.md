# Parâmetros de referência

## CUB/m² Sinduscon-RS (NBR 12.721, versão 2006) — residência unifamiliar (R$/m²)
Fonte: Série Histórica — Valor, Sinduscon-RS (https://sinduscon-rs.com.br/cub-rs/), extraída em nov/2026.

| Mês | R1-B (baixo) | R1-N (normal) | R1-A (alto) |
|---|---|---|---|
| abr/2024 | 2.199,83 | 2.840,45 | 3.807,74 |
| abr/2025 | 2.344,88 | 3.073,13 | 4.128,23 |
| out/2025 | 2.425,32 | 3.190,64 | 4.261,42 |
| abr/2026 | 2.467,46 | 3.307,64 | 4.475,05 |
| out/2026 | 2.593,86 | 3.476,31 | 4.689,49 |

O CUB não inclui fundações, projetos, BDI, taxas e itens especiais — por isso o fator 1,20.
Atualize a tabela em `scripts/avaliar.py` (dicionário `CUB`) a cada nova avaliação.

## Ross-Heidecke
Depreciação Ross: `0,5 × (x + x²)`, com x = idade / vida útil.
Heidecke (estado de conservação): novo 0; ótimo 0,32%; bom 2,52%; regular 8,09%;
reparos simples 18,10%; reparos médios 33,20%; reparos importantes 52,60%.
Total: `D = Dross + (1 − Dross) × Heidecke`; fator = `1 − D × (1 − residual)`.

## Área equivalente (NBR 12.721, coeficientes adotados)
- Área coberta aberta (gourmet, varanda): 0,6
- Área descoberta trabalhada (deck, pátio pavimentado): 0,3

## Piscina — custo de reposição (premissa, base abr/2026, corrigida pelo CUB)
Pequena (≤ 15 m²) R$ 35.000 · Média (15–30 m²) R$ 55.000 · Grande R$ 80.000
Aquecimento +R$ 12.000 · Envidraçamento/cobertura +R$ 20.000
Confirmar com orçamentos de piscineiros locais.

## Fatores homogeneização
- Oferta: 0,85 (ver calibração)
- Área: (Acomp/Asub)^0,125 dentro de ±30%; ^0,25 fora
- Padrão: razão entre CUBs do padrão do avaliando e do comparável
- Conservação: razão entre fatores Ross-Heidecke
- Tempo: (1 + 5%)^(anos entre o dado e a data de referência)
