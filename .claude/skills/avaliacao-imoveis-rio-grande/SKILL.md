---
name: avaliacao-imoveis-rio-grande
description: Avaliar valor de venda ou aluguel de imóveis no Brasil, especialmente em Rio Grande-RS, por método comparativo e evolutivo (NBR 14653) com laudo em português.
---

# Avaliação de imóveis — Rio Grande/RS (Arejano Corretora de Imóveis)

Use quando o usuário pedir para avaliar, precificar, estimar valor de venda/aluguel ou analisar investimento em um imóvel (ex.: "/avaliar Rua X, 123, Cassino").

> Versão 2 (nov/2026). Mudanças em relação à v1 vieram de um teste com 2 vendas reais
> (ver `calibracao/README.md`): a v1 usava só R$/m² construído e subavaliou em 28–43%.

## 1. Coletar dados do imóvel avaliando
Pergunte só o que faltar (uma vez, em lista curta). Se houver matrícula/contrato, extraia deles primeiro.
- Endereço/bairro, tipo (apto, casa, terreno, sala comercial), finalidade (venda, aluguel, garantia, partilha, investimento)
- **Área construída real** e **área averbada** na matrícula (ampliações não averbadas são comuns — perguntar)
- **Terreno**: dimensões e área (m²); se é terreno de marinha/aforamento (laudêmio 5%)
- **Áreas externas cobertas** (gourmet, varanda, garagem) em m² — contam como área equivalente
- **Piscina**: tamanho (pequena até ~15 m² de espelho d'água, média 15–30, grande), aquecida, envidraçada/coberta
- Quartos, suítes, banheiros, vagas
- **Padrão pelo projeto, não só pelo acabamento** (NBR 12.721): baixo (R1-B), normal (R1-N), alto (R1-A = casa grande de alto luxo). Casa pequena com acabamento excelente → `normal-alto`, não `alto`
- Idade (ou **idade aparente** se reformada) e estado de conservação (novo, ótimo, bom, regular, reparos simples/médios/importantes)
- **Móveis/equipamentos incluídos** e valor de mercado usado estimado (planejados, eletros, ar-condicionado)
- Andar, elevador, condomínio, IPTU, diferenciais; se a rua foi atingida pela cheia de 2024
- Preço anunciado e tempo de anúncio, se houver
Se o usuário tiver dados próprios de vendas/anúncios da corretora (planilha), priorize-os.

## 2. Pesquisar dados de mercado
Três amostras separadas:
1. **Casas/aptos comparáveis** (mín. 5, ideal 8–15) no bairro e vizinhos. Registrar fonte (link), data, preço, área construída, **terreno**, quartos, padrão, estado, **piscina/gourmet**.
2. **Terrenos** no mesmo bairro/loteamento (mín. 3), com área e preço — necessários para o evolutivo e para separar o terreno no comparativo.
3. **CUB/m² Sinduscon-RS** (R1-B/N/A) do mês da avaliação — tabela em `referencias/parametros.md`; atualizar pela Série Histórica em https://sinduscon-rs.com.br/cub-rs/ (PDF; extrair com `pdftotext`).

Fontes: sites de imobiliárias locais (Marcos Otero, Reis, Latitude32, Lindalvo, G3, Maurício Saraiva etc.) costumam abrir; ZAP, VivaReal, Imovelweb, Wimóveis, Casa Mineira e Attria **bloqueiam acesso automatizado (403)** — não tentar contornar o bloqueio; usar trechos da busca web (marcando como "fonte secundária") ou pedir ao usuário que cole os anúncios/planilha.
- Não inventar comparáveis nem preços. Se houver poucos dados, dizer isso e ampliar a área de busca (bairros vizinhos, Pelotas como referência secundária, sinalizando).
- **Excluir leilões, licitações da Caixa e vendas com dívidas** — não são preço de mercado (no Bragança ficaram ~40% abaixo).
- **Apartamentos**: priorizar unidades do mesmo condomínio/bloco; é o cenário mais confiável (sem evolutivo; só comparativo).
- **Excluir da amostra o próprio imóvel** (anúncios antigos dele) — mas registrar o preço pedido: serve para calibrar o fator oferta.

## 3. Particularidades de Rio Grande
Considerar e mencionar quando relevante (confirmar com o usuário ou com pesquisa, não presumir):
- Diferença de mercado entre Centro, Cassino (praia, sazonalidade, segunda residência, temporada) e demais bairros.
- No Cassino o **terreno pesa muito** (lote 10x30 ≈ R$ 110–250 mil anunciado em 2026); casa pequena em lote grande não pode ser avaliada só por R$/m² construído.
- Terrenos de marinha (aforamento SPU): laudêmio de 5% na transferência, foro anual.
- Proximidade do Porto, polo naval, FURG (aluguel estudantil) e acessos (BR-392).
- Risco de alagamento/cheia (2024, Lagoa dos Patos) — fator de ajuste se a rua foi atingida.
- **Superadequação**: imóvel com padrão muito acima do típico do bairro não recupera todo o custo na venda (fator de comercialização < 1).

## 4. Cálculo — usar `scripts/avaliar.py` (nunca de cabeça)
Montar um JSON no formato de `calibracao/*.json` e rodar `python3 scripts/avaliar.py caso.json`. O script faz:

**A. Terreno (comparativo de terrenos):** R$/m² × fator oferta × tempo × fator área ((Acomp/Asub)^0,25 fora de ±30%), saneamento ±30%. Só lotes com área entre 0,5× e 2× a do avaliando (lotes grandes/comerciais distorcem); amostra dispersa → mediana, com aviso.

**B. Comparativo direto (NBR 14653-2), com terreno e lazer separados:**
1. Preço do comparável × fator oferta × fator tempo
2. **Menos** o valor do lazer dele (piscina/gourmet em R$) e **menos** o terreno dele (área × R$/m² de terreno; se o terreno for desconhecido, assume igual ao do avaliando)
3. Divide pela área construída → R$/m² da construção
4. Homogeneiza: área ((Acomp/Asub)^n, n=0,125 dentro de ±30%, senão 0,25), **padrão** (razão de CUB avaliando/comparável), **conservação** (razão de Ross-Heidecke)
5. Saneamento ±30% da média
6. Valor = R$/m² × área construída + lazer do avaliando + terreno + móveis

**C. Evolutivo (NBR 14653-2):** terreno + (área equivalente × CUB do padrão × BDI 1,20 × fator Ross-Heidecke) + piscina (reposição depreciada) + móveis, × fator de comercialização.
- Área equivalente = construída + 0,6 × cobertas abertas (gourmet/varanda) + 0,3 × descobertas trabalhadas.

Sem terrenos (apartamentos) só roda o comparativo. Com menos de 2 comparáveis após saneamento o script não dá valor — buscar mais dados em vez de forçar.

**Salvaguardas (caso Vila Junção, nov/2026):**
- Se o terreno estimado deixar resíduo negativo em algum comparável (preço − terreno < 0), a separação de terreno é inválida → o script usa o **comparativo pelo preço total** (terreno embutido no R$/m², válido quando os lotes dos comparáveis são parecidos).
- Se o evolutivo passar de **1,5× o comparativo**, é superadequação/bairro abaixo do custo de reprodução → evolutivo descartado, valor pelo comparativo.

**D. Conciliação:** média simples dos dois métodos. Confiança: ALTA se divergência ≤ 15% e n ≥ 5; MÉDIA ≤ 25%; BAIXA acima — nesse caso reportar a faixa entre os métodos como resultado principal e pedir mais dados (área real, comparáveis melhores).

**Parâmetros padrão** (em `scripts/avaliar.py`, sobrescrevíveis em `"parametros"` no JSON):
| Parâmetro | Valor | Origem |
|---|---|---|
| Fator oferta | 0,90 | Literatura 0,90. Com 0,85 as 4 vendas de calibração ficaram todas 8–10% abaixo; 0,81 observado numa venda isolada (Padre Feijó) |
| Valorização anual | 5% | CUB R1-N subiu ~7,6% abr/25→abr/26; imóveis em geral menos |
| BDI / itens fora do CUB | 1,20 | Fundações, projetos, BDI, taxas |
| Fator comercialização | 0,90 | **Provisório**: evolutivo superestimou nas 2 vendas de calibração |
| Vida útil / residual | 70 anos / 20% | Casa de alvenaria |
| Piscina (reposição 2026) | P 35k / M 55k / G 80k; +12k aquecida; +20k envidraçada | Premissa — confirmar com orçamentos locais |

Com ≥ 12 dados e variáveis suficientes, oferecer também regressão hedônica (ln preço ~ ln área + ln terreno + quartos + vagas + piscina + padrão), reportando R², coeficientes e intervalo de confiança.

Resultado: valor provável, campo de arbítrio (±15%), faixa entre métodos e grau de confiança, arredondados. Para aluguel, também rentabilidade (aluguel anual / valor de venda).

## 5. Análise de investimento (se pedido)
- Rentabilidade bruta e líquida de aluguel (descontando IPTU, condomínio vago, taxa de administração, vacância).
- Comparar com CDI/Tesouro IPCA+ atuais (pesquisar taxa vigente).
- Custos de transação: ITBI de Rio Grande (pesquisar alíquota vigente), escritura e registro, laudêmio (terreno de marinha), corretagem.

## 6. Calibração contínua
- Toda venda real da corretora com dados completos vira um caso em `calibracao/` (JSON + preço vendido). Rodar com `--vendido` e registrar o erro em `calibracao/README.md`.
- Recalibrar fator oferta e fator de comercialização quando houver ≥ 5 vendas; validar em vendas que **não** foram usadas no ajuste.

## 7. Entrega
- Planilha (Sheets) com comparáveis, terrenos, fatores e cálculo dos dois métodos.
- Parecer/laudo em documento (Docs), em português, com: identificação do imóvel, metodologia (comparativo + evolutivo), amostras com fontes, tratamento, resultado, grau de confiança, ressalvas, data.
- Assinatura: "Arejano Corretora de Imóveis".
- Ressalva obrigatória: trata-se de opinião de valor/parecer mercadológico baseado em ofertas públicas; laudo técnico formal (NBR 14653) exige profissional habilitado (CRECI com CNAI, engenheiro ou arquiteto) e vistoria.

## 8. Resposta no chat
Resumo curto: valor provável, faixa, confiança, nº de comparáveis e terrenos, principais fatores que pesaram, premissas estimadas (a confirmar) e links para os arquivos.
