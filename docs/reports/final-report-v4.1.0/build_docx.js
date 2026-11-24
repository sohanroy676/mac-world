// MAC-WORLD final report: markdown subset -> .docx (docx-js).
// Usage: node build_docx.js sections/ordered-list.txt out/report.docx
// Markdown subset: # ## ### headings, paragraphs, "- " bullets, "1. " numbers, pipe tables (optional "Table: caption" line before),
// ![caption](path){w=NNN} images, "> " callouts, **bold** *italic* `code`, \pagebreak, {{include:file}}, {{results:N}}.
const fs = require("fs");
const path = require("path");
const D = require("docx");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType, AlignmentType, HeadingLevel,
  BorderStyle, LevelFormat, ImageRun, PageBreak, Footer, Header, PageNumber, TableOfContents, VerticalAlign,
} = D;

const ROOT = __dirname;
const ACCENT = "1F4E79", GREY = "F2F2F2", HEAD = "DCE6F1";
const CONTENT_W = 9026; // A4 with 1" margins, DXA
let figN = 0, tabN = 0;
const children = [];
let pendingCaption = null;

function readMd(rel) { return fs.readFileSync(path.join(ROOT, rel), "utf8"); }

function runs(text, base = {}) {
  // **bold**, *italic*, `code`
  const out = [];
  const re = /(\*\*[^*]+\*\*|\*[^*\s][^*]*\*|`[^`]+`)/g;
  let last = 0, m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), ...base }));
    const tok = m[0];
    if (tok.startsWith("**")) out.push(new TextRun({ text: tok.slice(2, -2), bold: true, ...base }));
    else if (tok.startsWith("`")) out.push(new TextRun({ text: tok.slice(1, -1), font: "Consolas", size: (base.size || 22) - 2, ...base, font: "Consolas" }));
    else out.push(new TextRun({ text: tok.slice(1, -1), italics: true, ...base }));
    last = m.index + tok.length;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), ...base }));
  return out.length ? out : [new TextRun({ text: "", ...base })];
}

function para(text, opts = {}) {
  return new Paragraph({ children: runs(text, opts.run || {}), spacing: { after: 120, line: 276 }, ...(opts.p || {}) });
}

function caption(kind, text) {
  const n = kind === "Figure" ? ++figN : ++tabN;
  return new Paragraph({
    children: [new TextRun({ text: `${kind} ${n}. `, bold: true, size: 19, color: ACCENT }), ...runs(text, { size: 19, italics: true })],
    spacing: { before: kind === "Table" ? 160 : 60, after: kind === "Table" ? 80 : 200 }, keepNext: kind === "Table",
    alignment: AlignmentType.LEFT,
  });
}

function splitRow(line) {
  let t = line.trim();
  if (t.startsWith("|")) t = t.slice(1);
  if (t.endsWith("|")) t = t.slice(0, -1);
  return t.split("|").map((c) => c.trim());
}

function table(lines) {
  const rows = lines.filter((l, i) => !(i === 1 && /^\s*\|?[\s:\-|]+\|?\s*$/.test(l))).map(splitRow);
  const ncol = Math.max(...rows.map((r) => r.length));
  const plain = (s) => s.replace(/[*`]/g, "");
  // widths proportional to sqrt-ish of the longest cell, bounded
  let w = [];
  for (let c = 0; c < ncol; c++) {
    const L = Math.max(...rows.map((r) => plain(r[c] || "").length), 3);
    w.push(Math.min(Math.max(L, 4), 38));
  }
  const tot = w.reduce((a, b) => a + b, 0);
  let cols = w.map((x) => Math.max(520, Math.floor((x / tot) * CONTENT_W)));
  const diff = CONTENT_W - cols.reduce((a, b) => a + b, 0);
  cols[cols.length - 1] += diff;
  const fs_ = ncol >= 11 ? 14 : ncol >= 8 ? 15 : ncol >= 6 ? 17 : 19;
  const border = { style: BorderStyle.SINGLE, size: 4, color: "BFBFBF" };
  const borders = { top: border, bottom: border, left: border, right: border };
  const trs = rows.map((r, ri) => new TableRow({
    tableHeader: ri === 0, cantSplit: true,
    children: Array.from({ length: ncol }, (_, c) => new TableCell({
      width: { size: cols[c], type: WidthType.DXA }, borders, verticalAlign: VerticalAlign.CENTER,
      shading: ri === 0 ? { fill: HEAD, type: ShadingType.CLEAR, color: "auto" } : undefined,
      margins: { top: 40, bottom: 40, left: 70, right: 70 },
      children: [new Paragraph({ children: runs(r[c] || "", { size: fs_, bold: ri === 0 }), spacing: { after: 0 }, alignment: c > 0 && /^[-+\d.\s%()/±x–−]+$/.test(plain(r[c] || "")) ? AlignmentType.CENTER : AlignmentType.LEFT })],
    })),
  }));
  return new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: cols, rows: trs });
}

function image(cap, rel, wpx) {
  const p = path.join(ROOT, rel);
  if (!fs.existsSync(p)) { children.push(para(`[missing figure: ${rel}]`, { run: { color: "C00000" } })); return; }
  const buf = fs.readFileSync(p);
  // PNG size from header
  const pw = buf.readUInt32BE(16), ph = buf.readUInt32BE(20);
  const width = Math.min(wpx || 600, 600), height = Math.round(width * ph / pw);
  children.push(new Paragraph({ children: [new ImageRun({ type: "png", data: buf, transformation: { width, height }, altText: { title: cap, description: cap, name: rel } })], alignment: AlignmentType.CENTER, spacing: { before: 120, after: 40 }, keepNext: true }));
  children.push(caption("Figure", cap));
}

function render(md) {
  const lines = md.split("\n");
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    const t = line.trim();
    if (t === "") { i++; continue; }
    let m;
    if ((m = t.match(/^\{\{include:(.+)\}\}$/))) {
      if (fs.existsSync(path.join(ROOT, m[1]))) render(readMd(m[1])); else console.warn("missing include (skipped): " + m[1]);
      i++; continue;
    }
    if ((m = t.match(/^\{\{results:(\w+)\}\}$/))) {
      const f = `generated/results_${m[1]}.md`;
      render(fs.existsSync(path.join(ROOT, f)) ? readMd(f) : "> Results for this scenario are not available in this build.");
      i++; continue;
    }
    if (t === "\\pagebreak") { children.push(new Paragraph({ children: [new PageBreak()] })); i++; continue; }
    if ((m = t.match(/^(#{1,4})\s+(.*)$/))) {
      const lvl = m[1].length;
      const H = [HeadingLevel.HEADING_1, HeadingLevel.HEADING_2, HeadingLevel.HEADING_3, HeadingLevel.HEADING_4][lvl - 1];
      children.push(new Paragraph({ heading: H, children: [new TextRun(m[2])], pageBreakBefore: lvl === 1 && children.length > 8 }));
      i++; continue;
    }
    if ((m = t.match(/^!\[(.*)\]\((.+?)\)(\{w=(\d+)\})?$/))) { image(m[1], m[2], m[4] ? +m[4] : 560); i++; continue; }
    if ((m = t.match(/^Table:\s*(.*)$/))) { children.push(caption("Table", m[1])); i++; continue; }
    if (t.startsWith("|")) {
      const blk = [];
      while (i < lines.length && lines[i].trim().startsWith("|")) { blk.push(lines[i]); i++; }
      children.push(table(blk));
      children.push(new Paragraph({ children: [], spacing: { after: 120 } }));
      continue;
    }
    if (/^[-*]\s+/.test(t) && !/^\*\*/.test(t)) {
      while (i < lines.length && /^\s*[-*]\s+/.test(lines[i]) && !/^\s*\*\*/.test(lines[i])) {
        const lead = lines[i].match(/^(\s*)/)[1].length;
        children.push(new Paragraph({ numbering: { reference: "bul", level: lead >= 2 ? 1 : 0 }, children: runs(lines[i].replace(/^\s*[-*]\s+/, "")), spacing: { after: 60, line: 276 } }));
        i++;
        while (i < lines.length && lines[i].trim() === "" && i + 1 < lines.length && /^\s*[-*]\s+/.test(lines[i + 1])) i++;
      }
      continue;
    }
    if (/^\d+\.\s+/.test(t)) {
      numRef++;
      while (i < lines.length && /^\s*\d+\.\s+/.test(lines[i])) {
        children.push(new Paragraph({ numbering: { reference: "num" + numRef, level: 0 }, children: runs(lines[i].replace(/^\s*\d+\.\s+/, "")), spacing: { after: 60, line: 276 } }));
        i++;
        while (i < lines.length && lines[i].trim() === "" && i + 1 < lines.length && /^\s*\d+\.\s+/.test(lines[i + 1])) i++;
      }
      continue;
    }
    if (t.startsWith(">")) {
      const buf = [];
      while (i < lines.length && lines[i].trim().startsWith(">")) { buf.push(lines[i].trim().replace(/^>\s?/, "")); i++; }
      children.push(new Paragraph({
        children: runs(buf.join(" "), { size: 21 }), spacing: { before: 80, after: 160, line: 276 },
        shading: { type: ShadingType.CLEAR, fill: GREY, color: "auto" },
        border: { left: { style: BorderStyle.SINGLE, size: 18, color: ACCENT, space: 8 } }, indent: { left: 200, right: 100 },
      }));
      continue;
    }
    // paragraph: join following non-empty plain lines
    const buf = [t]; i++;
    while (i < lines.length && lines[i].trim() !== "" && !/^(#{1,4}\s|\||>|!\[|[-*]\s|\d+\.\s|\{\{|Table:|\\pagebreak)/.test(lines[i].trim())) { buf.push(lines[i].trim()); i++; }
    children.push(para(buf.join(" ")));
  }
}

let numRef = 0;
const order = fs.readFileSync(path.join(ROOT, process.argv[2]), "utf8").split("\n").map((s) => s.trim()).filter((s) => s && !s.startsWith("#"));
const front = JSON.parse(fs.readFileSync(path.join(ROOT, "sections/front.json"), "utf8"));

// front block
children.push(new Paragraph({ children: [new TextRun({ text: front.title, bold: true, size: 44, color: ACCENT, font: "Calibri" })], spacing: { before: 200, after: 120 } }));
children.push(new Paragraph({ children: [new TextRun({ text: front.subtitle, size: 26, color: "404040" })], spacing: { after: 240 } }));
children.push(new Paragraph({ children: [new TextRun({ text: front.authors, bold: true, size: 24 })], spacing: { after: 40 } }));
children.push(new Paragraph({ children: [new TextRun({ text: front.college, size: 22 })], spacing: { after: 40 } }));
children.push(new Paragraph({ children: [new TextRun({ text: front.version_line, size: 20, color: "595959" })], spacing: { after: 240 }, border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: ACCENT, space: 6 } } }));
children.push(new Paragraph({ children: [new TextRun({ text: "Contents", bold: true, size: 28, color: ACCENT })], spacing: { before: 120, after: 80 } }));
children.push(new TableOfContents("Contents", { hyperlink: true, headingStyleRange: "1-2" }));

for (const f of order) render(readMd(f));

// numbering configs for numbered lists (one per list)
const numbering = [{ reference: "bul", levels: [
  { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } },
  { level: 1, format: LevelFormat.BULLET, text: "–", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 1080, hanging: 270 } } } }] }];
for (let k = 1; k <= numRef; k++) numbering.push({ reference: "num" + k, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 300 } } } }] });

const doc = new Document({
  creator: front.authors, title: front.title, description: front.subtitle,
  features: { updateFields: true },
  styles: {
    default: { document: { run: { font: "Calibri", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: "Calibri", size: 36, bold: true, color: ACCENT }, paragraph: { spacing: { before: 360, after: 160 }, keepNext: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: "Calibri", size: 29, bold: true, color: ACCENT }, paragraph: { spacing: { before: 300, after: 120 }, keepNext: true, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: "Calibri", size: 25, bold: true, color: "2E5A88" }, paragraph: { spacing: { before: 220, after: 90 }, keepNext: true, outlineLevel: 2 } },
      { id: "Heading4", name: "Heading 4", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: "Calibri", size: 22, bold: true, italics: true, color: "404040" }, paragraph: { spacing: { before: 160, after: 60 }, keepNext: true, outlineLevel: 3 } },
    ],
  },
  numbering: { config: numbering },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1300, bottom: 1200, left: 1440, right: 1440 } } },
    headers: { default: new Header({ children: [new Paragraph({ children: [new TextRun({ text: front.header, size: 17, color: "7F7F7F" })], alignment: AlignmentType.RIGHT })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: front.footer + "  |  Page ", size: 17, color: "7F7F7F" }), new TextRun({ children: [PageNumber.CURRENT], size: 17, color: "7F7F7F" })] })] }) },
    children,
  }],
});
Packer.toBuffer(doc).then((b) => { fs.mkdirSync(path.dirname(path.join(ROOT, process.argv[3])), { recursive: true }); fs.writeFileSync(path.join(ROOT, process.argv[3]), b); console.log("wrote", process.argv[3], b.length, "bytes;", figN, "figures,", tabN, "captioned tables"); });
