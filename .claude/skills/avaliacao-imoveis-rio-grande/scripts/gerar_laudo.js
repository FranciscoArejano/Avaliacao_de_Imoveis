#!/usr/bin/env node
/*
 * Gera o laudo de avaliação em .docx no modelo da Arejano Corretora de Imóveis.
 *
 * Uso:  node gerar_laudo.js laudo.json [saida.docx]
 *       (depois: soffice --headless --convert-to pdf saida.docx)
 *
 * O JSON segue ../referencias/laudo_exemplo.json. Texto aceita **negrito**, *itálico* e [link](url).
 * Blocos de seção: {"p": "..."} | {"bullets": [...]} | {"num": [...]} | {"nota": "..."} |
 *                  {"tabela": {"colunas": [...], "linhas": [[...]], "pesos": [...], "direita": [i...], "destaqueUltima": true}}
 */
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Header, Footer, Table, TableRow, TableCell,
  AlignmentType, WidthType, ShadingType, BorderStyle, PageNumber, TabStopType, LevelFormat,
  ExternalHyperlink, TableLayoutType,
} = require('docx');

// ---------- Identidade visual (modelo da imobiliária) ----------
const ID = {
  azul: '0037AA',                 // azul escuro do logo
  azulClaro: 'E8EFFC',
  borda: 'B7C4DE',
  fonte: 'Times New Roman',
  logo: path.join(__dirname, '..', 'assets', 'logo_arejano.png'),
  rodape: 'Rua Gen. Vitorino nº 93-B - CEP 96.200-310 - Fone (53) 3233.1720 / 98401.6006 – E-mail: arejanoimoveis@vetorial.net',
  assinatura: ['HONORINA MADUREIRA AREJANO', 'Corretora de Imóveis – CRECI 48.455', 'Arejano Corretora de Imóveis'],
  pagina: { width: 11907, height: 16840 },                       // A4
  margem: { top: 2100, right: 851, bottom: 1247, left: 2155, header: 0, footer: 851 },
};
const LARG = ID.pagina.width - ID.margem.left - ID.margem.right;

// ---------- Texto com marcação simples ----------
function runs(texto, o = {}) {
  const size = o.size || 24;
  const out = [];
  const re = /\*\*(.+?)\*\*|\*(.+?)\*|\[(.+?)\]\((https?:\/\/[^)]+)\)/g;
  let i = 0, m;
  const plain = (s) => s && out.push(new TextRun({ text: s, font: ID.fonte, size, bold: o.bold, italics: o.italics, color: o.color }));
  while ((m = re.exec(texto))) {
    plain(texto.slice(i, m.index));
    if (m[1]) out.push(new TextRun({ text: m[1], font: ID.fonte, size, bold: true, italics: o.italics, color: o.color }));
    else if (m[2]) out.push(new TextRun({ text: m[2], font: ID.fonte, size, italics: true, bold: o.bold, color: o.color }));
    else out.push(new ExternalHyperlink({ link: m[4], children: [new TextRun({ text: m[3], font: ID.fonte, size, color: ID.azul, underline: {} })] }));
    i = re.lastIndex;
  }
  plain(texto.slice(i));
  return out;
}
const par = (texto, o = {}) => new Paragraph({
  children: runs(texto, o), alignment: o.align || AlignmentType.JUSTIFIED,
  spacing: { before: o.before ?? 0, after: o.after ?? 120, line: 300 }, keepNext: o.keepNext,
});
const titulo = (texto) => new Paragraph({
  children: runs(texto.toUpperCase(), { bold: true, color: ID.azul }),
  spacing: { before: 280, after: 120 }, keepNext: true,
  border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: ID.azul, space: 2 } },
});
const item = (texto, ref) => new Paragraph({
  children: runs(texto), numbering: { reference: ref, level: 0 },
  alignment: AlignmentType.JUSTIFIED, spacing: { after: 80, line: 300 },
});

function tabela(tb) {
  const pesos = tb.pesos || tb.colunas.map(() => 1);
  const total = pesos.reduce((a, b) => a + b, 0);
  const w = pesos.map((x) => Math.round((x / total) * LARG));
  w[w.length - 1] += LARG - w.reduce((a, b) => a + b, 0);
  const b = { style: BorderStyle.SINGLE, size: 4, color: ID.borda };
  const dir = tb.direita || [];
  const cel = (txt, i, cab, dest) => new TableCell({
    width: { size: w[i], type: WidthType.DXA }, borders: { top: b, bottom: b, left: b, right: b },
    shading: cab ? { type: ShadingType.CLEAR, fill: ID.azul, color: 'auto' }
      : dest ? { type: ShadingType.CLEAR, fill: ID.azulClaro, color: 'auto' } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: [new Paragraph({
      alignment: dir.includes(i) && !cab ? AlignmentType.RIGHT : AlignmentType.LEFT,
      children: runs(String(txt), { size: 20, bold: cab || dest, color: cab ? 'FFFFFF' : undefined }),
    })],
  });
  const linhas = [new TableRow({ tableHeader: true, children: tb.colunas.map((c, i) => cel(c, i, true)) })];
  tb.linhas.forEach((l, k) => linhas.push(new TableRow({
    cantSplit: true, children: l.map((c, i) => cel(c, i, false, tb.destaqueUltima && k === tb.linhas.length - 1)),
  })));
  return [new Table({ width: { size: LARG, type: WidthType.DXA }, columnWidths: w, layout: TableLayoutType.FIXED, rows: linhas }),
    new Paragraph({ children: [], spacing: { after: 120 } })];
}

function bloco(bl, proximoEhTabela) {
  if (bl.p !== undefined) return [par(bl.p, { keepNext: proximoEhTabela })];
  if (bl.nota !== undefined) return [par(bl.nota, { size: 20, italics: true, before: 120, keepNext: proximoEhTabela })];
  if (bl.bullets) return bl.bullets.map((x) => item(x, 'marcadores'));
  if (bl.num) return bl.num.map((x) => item(x, 'numeros'));
  if (bl.tabela) return tabela(bl.tabela);
  throw new Error('bloco desconhecido: ' + JSON.stringify(bl).slice(0, 80));
}

function gerar(L) {
  const c = [];
  c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120, after: 60 },
    children: runs(L.titulo || 'LAUDO DE AVALIAÇÃO DE IMÓVEL', { bold: true, size: 28 }) }));
  c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 },
    children: runs(L.subtitulo || 'Parecer de valor de mercado', { italics: true, size: 22 }) }));
  (L.cabecalho || []).forEach(([rot, val], i, arr) => c.push(new Paragraph({
    spacing: { after: i === arr.length - 1 ? 240 : 40 },
    children: [...runs(rot.toUpperCase() + ': ', { bold: true, size: 22 }), ...runs(val.toUpperCase(), { size: 22 })] })));
  if (L.resumo) c.push(...tabela({ colunas: ['Conclusão', 'Valor (R$)'], linhas: L.resumo, pesos: [3, 2], direita: [1] }));
  for (const s of L.secoes) {
    c.push(titulo(s.titulo));
    s.blocos.forEach((bl, k) => c.push(...bloco(bl, !!(s.blocos[k + 1] && s.blocos[k + 1].tabela))));
  }
  c.push(par(L.local_data, { before: 240, after: 720, align: AlignmentType.LEFT }));
  c.push(new Paragraph({ keepNext: true, children: runs('_________________________________________') }));
  const ass = L.assinatura || ID.assinatura;
  ass.forEach((linha, i) => c.push(new Paragraph({ keepNext: i < ass.length - 1, children: runs(linha, { bold: i === 0 }) })));

  const header = new Header({ children: [new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 360 },
    children: [new ImageRun({ type: 'png', data: fs.readFileSync(ID.logo), transformation: { width: 290, height: 91 } })] })] });
  const footer = new Footer({ children: [new Paragraph({
    border: { top: { style: BorderStyle.SINGLE, size: 18, color: '000000', space: 4 } },
    tabStops: [{ type: TabStopType.RIGHT, position: LARG }],
    children: [new TextRun({ text: ID.rodape, font: ID.fonte, size: 16, bold: true }),
      new TextRun({ children: ['\t', PageNumber.CURRENT], font: ID.fonte, size: 16, bold: true })] })] });

  return new Document({
    creator: 'Arejano Corretora de Imóveis', title: L.titulo_arquivo || 'Laudo de Avaliação',
    styles: { default: { document: { run: { font: ID.fonte, size: 24 } } } },
    numbering: { config: [
      { reference: 'marcadores', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 260 } } } }] },
      { reference: 'numeros', levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 300 } } } }] },
    ] },
    sections: [{ properties: { page: { size: ID.pagina, margin: ID.margem } }, headers: { default: header }, footers: { default: footer }, children: c }],
  });
}

if (require.main === module) {
  const [entrada, saida] = process.argv.slice(2);
  if (!entrada) { console.error('uso: node gerar_laudo.js laudo.json [saida.docx]'); process.exit(1); }
  const L = JSON.parse(fs.readFileSync(entrada, 'utf8'));
  const out = saida || entrada.replace(/\.json$/i, '') + '.docx';
  Packer.toBuffer(gerar(L)).then((b) => { fs.writeFileSync(out, b); console.log(out); });
}
module.exports = { gerar, ID };
