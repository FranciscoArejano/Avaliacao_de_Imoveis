#!/usr/bin/env python3
"""Avaliação de casas (Rio Grande/RS) - comparativo direto + evolutivo + conciliação.

Uso:  python3 avaliar.py caso.json [--vendido 465000]

O JSON de entrada tem: imovel, parametros (opcional), comparaveis, terrenos.
Veja os exemplos em ../calibracao/*.json. Todas as premissas usadas são impressas.
"""
import json, sys, statistics as st
from datetime import date

# ---------------- Tabelas de referência (ver referencias/parametros.md) ----------------
# CUB/m² Sinduscon-RS (NBR 12.721, versão 2006), R$/m². Fonte: Série Histórica Sinduscon-RS.
CUB = {
    "2024-04": {"baixo": 2199.83, "normal": 2840.45, "alto": 3807.74},
    "2025-04": {"baixo": 2344.88, "normal": 3073.13, "alto": 4128.23},
    "2025-10": {"baixo": 2425.32, "normal": 3190.64, "alto": 4261.42},
    "2026-04": {"baixo": 2467.46, "normal": 3307.64, "alto": 4475.05},
    "2026-10": {"baixo": 2593.86, "normal": 3476.31, "alto": 4689.49},
}
# Heidecke: depreciação pelo estado de conservação
HEIDECKE = {"novo": 0.0, "otimo": 0.0032, "bom": 0.0252, "regular": 0.0809,
            "reparos_simples": 0.1810, "reparos_medios": 0.3320, "reparos_importantes": 0.5260}
# Piscina: custo de reposição (R$, ref. 2026) - premissa a confirmar com orçamentos locais
PISCINA_BASE = {"pequena": 35000, "media": 55000, "grande": 80000}
PISCINA_EXTRA = {"aquecida": 12000, "envidracada": 20000}

DEFAULTS = {
    "fator_oferta": 0.85,          # anúncio -> fechamento (calibrar com vendas da corretora)
    "valorizacao_anual": 0.05,     # ajuste temporal de anúncios/vendas antigas
    "bdi": 1.20,                   # itens fora do CUB: fundações, projetos, BDI, taxas
    "fator_comercializacao": 0.90, # evolutivo: provisório, calibrado em 2 vendas (ver calibracao/)
    "valor_residual": 0.20,        # parcela não depreciável da benfeitoria
    "vida_util": 70,               # casa de alvenaria
    "coef_area_coberta_aberta": 0.6,   # gourmet/varanda coberta (NBR 12.721)
    "coef_area_descoberta": 0.3,
    "saneamento": 0.30,
}

def ym(s):
    y, m = map(int, s[:7].split("-")); return y + (m - 1) / 12

def cub(data, padrao):
    k = min(CUB, key=lambda k: abs(ym(k) - ym(data)))
    if padrao == "normal-alto":
        return (CUB[k]["normal"] + CUB[k]["alto"]) / 2, k
    return CUB[k][padrao], k

def fator_conserv(idade, estado, P):
    x = min(idade / P["vida_util"], 1.0)
    d_ross = 0.5 * (x + x * x)
    d = d_ross + (1 - d_ross) * HEIDECKE[estado]
    return 1 - d * (1 - P["valor_residual"])

def valor_piscina(p, data_ref):
    if not p:
        return 0.0
    v = PISCINA_BASE[p.get("tamanho", "media")]
    for k in ("aquecida", "envidracada"):
        if p.get(k):
            v += PISCINA_EXTRA[k]
    # tabela em base 2026-04; corrige pelo CUB normal
    return v * cub(data_ref, "normal")[0] / CUB["2026-04"]["normal"]

def f_area(a_comp, a_sub, faixa=0.3):
    r = a_comp / a_sub
    return r ** (0.125 if 1 - faixa <= r <= 1 + faixa else 0.25)

def f_tempo(data_dado, data_ref, P):
    return (1 + P["valorizacao_anual"]) ** (ym(data_ref) - ym(data_dado))

def amenidades(x, data_ref, P, cub_n):
    """R$ de piscina + área gourmet/coberta aberta, já depreciados de forma simplificada."""
    v = valor_piscina(x.get("piscina"), data_ref)
    ac = x.get("area_coberta_aberta", 0) or (15 if x.get("gourmet") else 0)
    v += ac * P["coef_area_coberta_aberta"] * cub_n * P["bdi"]
    return v * fator_conserv(x.get("idade", 20), x.get("estado", "regular"), P)

def sanear(vals, lim):
    m = st.mean(v for _, v in vals)
    keep = [(i, v) for i, v in vals if (1 - lim) * m <= v <= (1 + lim) * m]
    return keep, [i for i, v in vals if (i, v) not in keep], m

# ---------------- Terreno (comparativo de terrenos) ----------------
def valor_terreno(S, terrenos, P, log):
    ref = S["data_ref"]; a = S["terreno_m2"]
    vals = []
    for t in terrenos:
        u = t["preco"] / t["area"] * P["fator_oferta"] * f_tempo(t.get("data", ref), ref, P) * f_area(t["area"], a)
        vals.append((t["id"], u))
    keep, out, m = sanear(vals, P["saneamento"])
    vu = st.mean(v for _, v in keep)
    log.append(f"Terreno: {len(terrenos)} dados, excluídos {out}; R$ {vu:,.0f}/m² x {a} m² = R$ {vu*a:,.0f}")
    return vu, vu * a

# ---------------- Método comparativo direto (com terreno e lazer em R$) ----------------
def comparativo(S, comps, vu_terreno, P, log):
    ref = S["data_ref"]
    cub_n_ref = cub(ref, "normal")[0]
    a_sub = S["area_construida"]
    pad_sub = cub(ref, S.get("padrao", "normal"))[0]
    fc_sub = fator_conserv(S.get("idade", 20), S.get("estado", "regular"), P)
    rows = []
    for c in comps:
        p = c["preco"] * P["fator_oferta"] * f_tempo(c.get("data", ref), ref, P)
        amen_c = amenidades(c, ref, P, cub_n_ref)
        terr_c = (c.get("terreno_m2") or S["terreno_m2"]) * vu_terreno if vu_terreno else 0
        base = p - amen_c - terr_c
        unit = base / c["area"]
        fa = f_area(c["area"], a_sub)
        fp = pad_sub / cub(ref, c.get("padrao", "normal"))[0]
        fcv = fc_sub / fator_conserv(c.get("idade", 20), c.get("estado", "regular"), P)
        h = unit * fa * fp * fcv
        rows.append((c["id"], h))
        log.append(f"  {c['id']:<28} R$ {c['preco']:>9,.0f} {c['area']:>4} m² | -lazer {amen_c:>7,.0f} -terreno {terr_c:>8,.0f} "
                   f"| área {fa:.2f} padrão {fp:.2f} conserv {fcv:.2f} => R$ {h:,.0f}/m² constr.")
    keep, out, m = sanear(rows, P["saneamento"])
    if len(keep) < 2:
        log.append(f"Comparativo: amostra insuficiente após saneamento (n={len(keep)})"); return None, None, 0
    mu = st.mean(v for _, v in keep); cv = st.stdev(v for _, v in keep) / mu
    amen_s = amenidades(S, ref, P, cub_n_ref)
    terr_s = S["terreno_m2"] * vu_terreno if vu_terreno else 0
    v = mu * a_sub + amen_s + terr_s + S.get("moveis_valor", 0)
    log.append(f"Comparativo: excluídos {out}; média R$ {mu:,.0f}/m² (n={len(keep)}, CV {cv:.0%})")
    log.append(f"  = {mu:,.0f} x {a_sub} m² + lazer {amen_s:,.0f} + terreno {terr_s:,.0f} + móveis {S.get('moveis_valor',0):,.0f} = R$ {v:,.0f}")
    return v, cv, len(keep)

# ---------------- Método evolutivo ----------------
def evolutivo(S, terreno, P, log):
    ref = S["data_ref"]
    c, k = cub(ref, S.get("padrao", "normal"))
    fcv = fator_conserv(S.get("idade", 20), S.get("estado", "regular"), P)
    a_eq = S["area_construida"] + S.get("area_coberta_aberta", 0) * P["coef_area_coberta_aberta"] \
        + S.get("area_descoberta_trabalhada", 0) * P["coef_area_descoberta"]
    benf = a_eq * c * P["bdi"] * fcv
    pisc = valor_piscina(S.get("piscina"), ref) * fcv
    mov = S.get("moveis_valor", 0)
    total = (terreno + benf + pisc + mov) * P["fator_comercializacao"]
    log.append(f"Evolutivo: CUB {S.get('padrao','normal')} {k} R$ {c:,.2f}; área equiv. {a_eq:.1f} m²; "
               f"BDI {P['bdi']}; fator conservação {fcv:.3f}")
    log.append(f"  terreno {terreno:,.0f} + benfeitoria {benf:,.0f} + piscina {pisc:,.0f} + móveis {mov:,.0f} "
               f"x FC {P['fator_comercializacao']} = R$ {total:,.0f}")
    return total, terreno / total

def main():
    caso = json.load(open(sys.argv[1]))
    vendido = None
    if "--vendido" in sys.argv:
        vendido = float(sys.argv[sys.argv.index("--vendido") + 1])
    P = {**DEFAULTS, **caso.get("parametros", {})}
    S = caso["imovel"]; log = []
    vu_t, terreno = valor_terreno(S, caso["terrenos"], P, log) if caso.get("terrenos") else (0, 0)
    log.append("Comparativo direto (preço - lazer - terreno, homogeneizado por m² construído):")
    vc, cv, n = comparativo(S, caso["comparaveis"], vu_t, P, log) if caso.get("comparaveis") else (None, None, 0)
    ve, share_t = evolutivo(S, terreno, P, log) if terreno else (None, 0)
    # Conciliação
    if vc and ve:
        # Peso igual. Calibração (2 vendas reais) mostrou que o evolutivo superestima
        # quando o padrão do imóvel está acima do bairro (superadequação), então não se
        # privilegia o evolutivo automaticamente.
        final = (vc + ve) / 2
        div = abs(vc - ve) / final
        conf = "ALTA" if div <= 0.15 and n >= 5 else ("MÉDIA" if div <= 0.25 else "BAIXA")
        log.append(f"Conciliação: média simples; divergência entre métodos {div:.0%}; confiança {conf}"
                   f"{' -> reportar a faixa entre os dois métodos e buscar mais dados' if conf == 'BAIXA' else ''}")
        log.append(f"  faixa entre métodos: R$ {round(min(vc,ve),-3):,.0f} – {round(max(vc,ve),-3):,.0f}")
    else:
        final = vc or ve
    if not final:
        log.append("SEM RESULTADO: amostra insuficiente (mín. 2 comparáveis após saneamento, ou terrenos para o evolutivo). Buscar mais dados.")
        print(f"=== {S.get('nome','imóvel')} | data ref. {S['data_ref']} ===")
        print("\n".join(log)); return None
    log.append(f"VALOR PROVÁVEL: R$ {round(final, -3):,.0f}  | campo de arbítrio R$ {round(final*0.85,-3):,.0f} – {round(final*1.15,-3):,.0f}")
    if vendido:
        partes = [f"{n} {(v-vendido)/vendido:+.1%}" for n, v in (("comparativo", vc), ("evolutivo", ve)) if v]
        log.append(f"Vendido R$ {vendido:,.0f}: erro {(final-vendido)/vendido:+.1%} ({', '.join(partes)})")
    print(f"=== {S.get('nome','imóvel')} | data ref. {S['data_ref']} ===")
    print("\n".join(log))
    return final

if __name__ == "__main__":
    main()
