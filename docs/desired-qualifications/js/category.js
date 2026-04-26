    const fmt = new Intl.NumberFormat("th-TH");
    let report;
    const expandedLists = new Set();
    const exampleStates = new Map();
    let examplesInitialized = false;

    function refText(item) {
      return `ข้อ ${item.document_item}, หน้า ${item.page}, ลำดับ ${item.sequence}`;
    }

    function metric(label, value) {
      const rendered = typeof value === "number" ? fmt.format(value) : value;
      return `<div class="metric"><div class="label">${label}</div><div class="value">${rendered}</div></div>`;
    }

    async function renderCategoryNav(currentSlug) {
      const index = await fetch("../data/categories/index.json").then(response => response.json());
      document.querySelector("#categoryNav").innerHTML = index.reports.map(row => `
        <a class="category-link ${row.slug === currentSlug ? "is-active" : ""}" href="${row.slug}.html">
          ${row.number}. ${row.title.replace(/\s*\(.+?\)\s*/g, "")}
        </a>
      `).join("");
    }

    function renderBars(target, rows) {
      const max = Math.max(...rows.map(row => row.count), 1);
      target.innerHTML = rows.slice(0, 10).map(row => `
        <div class="bar-row" title="${row.name}">
          <div class="bar-label">${row.name}</div>
          <div class="track"><div class="fill" style="width:${(row.count / max) * 100}%"></div></div>
          <div class="num">${fmt.format(row.count)}</div>
        </div>
      `).join("");
    }

    function renderSummaryCards(target, rows, limit = 6) {
      const id = target.id;
      const expanded = expandedLists.has(id);
      const visible = expanded ? rows : rows.slice(0, limit);
      target.innerHTML = visible.map(row => `
        <article class="card">
          <div class="card-head">
            <span>${row.name}</span>
            <span class="card-count">
              <span class="num">จำนวนอ้างอิงรวม ${fmt.format(row.count)}</span>
              <span class="subnum">จาก ${fmt.format(row.item_count || row.examples.length)} ข้อ</span>
            </span>
          </div>
          ${renderExampleBlock(`${id}:${row.name}`, row.examples)}
        </article>
      `).join("") + moreButton(id, rows.length, visible.length);
    }

    function renderExampleBlock(id, examples) {
      if (!examples || !examples.length) return "";
      const total = examples.length;
      const visible = exampleStates.get(id) || 0;
      if (!visible) {
        return `
          <div class="example-controls">
            <button class="mini-btn" type="button" data-example-id="${id}" data-example-action="more">ดูรายการอ้างอิง</button>
          </div>
        `;
      }
      return `
        <ol class="examples">
          ${examples.slice(0, visible).map(item => `
            <li><span class="ref">${refText(item)}</span> ${item.short_text}</li>
          `).join("")}
        </ol>
        <div class="example-controls">
          <button class="mini-btn" type="button" data-example-id="${id}" data-example-action="collapse">ยุบทั้งหมด</button>
          <button class="mini-btn" type="button" data-example-id="${id}" data-example-action="less" ${visible <= 3 ? "disabled" : ""}>ดูน้อยลง</button>
          <button class="mini-btn" type="button" data-example-id="${id}" data-example-action="more" ${visible >= total ? "disabled" : ""}>ดูเพิ่ม</button>
          <button class="mini-btn" type="button" data-example-id="${id}" data-example-action="all" ${visible >= total ? "disabled" : ""}>ขยายทั้งหมด</button>
        </div>
      `;
    }

    function handleExampleAction(id, action) {
      const total = countExamples(id);
      const current = exampleStates.get(id) || 0;
      if (action === "collapse") exampleStates.set(id, 0);
      if (action === "less") exampleStates.set(id, Math.max(3, current - 3));
      if (action === "more") exampleStates.set(id, Math.min(total, current ? current + 3 : 3));
      if (action === "all") exampleStates.set(id, total);
      rerenderExampleCards();
    }

    function countExamples(id) {
      const [scope, ...rest] = id.split(":");
      const key = rest.join(":");
      if (scope === "desired") return (report.desired_characteristics.find(row => row.name === key)?.examples || []).length;
      if (scope === "concerns") return (report.concerns.find(row => row.name === key)?.examples || []).length;
      if (scope === "vision") {
        return report.vision_alignment_summary.by_group
          .flatMap(group => group.items)
          .find(item => item.id === key)?.examples.length || 0;
      }
      return 0;
    }

    function rerenderExampleCards() {
      renderSummaryCards(document.querySelector("#desired"), report.desired_characteristics);
      renderSummaryCards(document.querySelector("#concerns"), report.concerns);
      renderVisionAlignment(document.querySelector("#visionAlignment"));
      wireMoreButtons();
    }

    function initializeExpandedExamples() {
      if (examplesInitialized) return;
      report.desired_characteristics.forEach(row => {
        if (row.examples.length) exampleStates.set(`desired:${row.name}`, Math.min(3, row.examples.length));
      });
      report.vision_alignment_summary.by_group
        .flatMap(group => group.items)
        .forEach(item => {
          if (item.examples.length) exampleStates.set(`vision:${item.id}`, Math.min(3, item.examples.length));
        });
      examplesInitialized = true;
    }

    function renderIssueCards(target, items, limit = 8) {
      if (!items.length) {
        target.innerHTML = `<div class="card">ไม่พบรายการตามเกณฑ์นี้ในหมวดนี้</div>`;
        return;
      }
      const id = target.id;
      const expanded = expandedLists.has(id);
      const visible = expanded ? items : items.slice(0, limit);
      target.innerHTML = visible.map(item => `
        <article class="card">
          <div class="card-head"><span>${refText(item)}</span><span class="num">จำนวนอ้างอิง ${fmt.format(item.weight)}</span></div>
          <div>${item.short_text}</div>
          <div class="tags">
            ${[...item.classifications, ...item.topic_tags].map(tag => `<span class="tag">${tag}</span>`).join("")}
          </div>
        </article>
      `).join("") + moreButton(id, items.length, visible.length);
    }

    function moreButton(id, total, visible) {
      if (total <= visible && !expandedLists.has(id)) return "";
      const label = expandedLists.has(id) ? "แสดงน้อยลง" : `ดูเพิ่ม (${fmt.format(total - visible)} รายการ)`;
      return `<button class="more-btn" type="button" data-toggle-list="${id}">${label}</button>`;
    }

    function rerenderList(id) {
      if (id === "desired") renderSummaryCards(document.querySelector("#desired"), report.desired_characteristics);
      if (id === "concerns") renderSummaryCards(document.querySelector("#concerns"), report.concerns);
      if (id === "sensitive") renderIssueCards(document.querySelector("#sensitive"), report.sensitive_issues, 8);
      if (id === "lessRelevant") renderIssueCards(document.querySelector("#lessRelevant"), report.less_relevant_issues, 8);
      wireMoreButtons();
    }

    function wireMoreButtons() {
      document.querySelectorAll("[data-toggle-list]").forEach(button => {
        button.addEventListener("click", () => {
          const id = button.dataset.toggleList;
          if (expandedLists.has(id)) expandedLists.delete(id);
          else expandedLists.add(id);
          rerenderList(id);
        });
      });
    }

    function renderVisionAlignment(target) {
      target.innerHTML = report.vision_alignment_summary.by_group.map(group => `
        <div class="alignment-group">
          <h3 class="alignment-title">${group.dimension}</h3>
          ${group.items.map(item => `
            <article class="alignment-card ${item.count ? "" : "is-empty"}">
              <div class="card-head">
                <span>${item.title}</span>
                <span class="card-count">
                  <span class="num">จำนวนอ้างอิงรวม ${fmt.format(item.count)}</span>
                  <span class="subnum">จาก ${fmt.format(item.item_count || item.examples.length)} ข้อ</span>
                </span>
              </div>
              <div class="alignment-summary">${item.summary}</div>
              ${item.examples.length ? renderExampleBlock(`vision:${item.id}`, item.examples) : `<div class="alignment-summary">ยังไม่พบ evidence ที่ match โดยตรงในหมวดนี้</div>`}
            </article>
          `).join("")}
        </div>
      `).join("");
    }

    function groupTop(values, limit, otherLabel) {
      const totals = new Map();
      values.forEach(({ name, value }) => totals.set(name, (totals.get(name) || 0) + value));
      const ordered = [...totals.entries()].sort((a, b) => b[1] - a[1]);
      const keep = new Set(ordered.slice(0, limit).map(([name]) => name));
      return { keep, otherLabel };
    }

    function sankeyName(name, grouping) {
      return grouping.keep.has(name) ? name : grouping.otherLabel;
    }

    function addLink(map, source, target, value) {
      if (!source || !target || !value) return;
      const key = `${source}|||${target}`;
      const current = map.get(key) || { source, target, value: 0 };
      current.value += value;
      map.set(key, current);
    }

    function buildSankeyData() {
      const category = `หมวด ${report.number}: ${report.title}`;
      const topicValues = [];
      const visionValues = [];
      const desiredEvidence = report.evidence.filter(item => item.desired_tags.length);

      desiredEvidence.forEach(item => {
        item.topic_tags.forEach(name => topicValues.push({ name, value: item.weight }));
        item.vision_alignment.forEach(row => visionValues.push({ name: `${row.dimension}: ${row.title}`, value: item.weight }));
      });
      const topicGrouping = groupTop(topicValues, 10, "tag/topic: อื่น ๆ");
      const visionGrouping = groupTop(visionValues, 17, "วิสัยทัศน์: อื่น ๆ");

      const linkMap = new Map();
      desiredEvidence.forEach(item => {
        const desiredTags = item.desired_tags.length ? item.desired_tags : ["ลักษณะพึงประสงค์: อื่น ๆ"];
        const uniqueDesiredTags = [...new Set(desiredTags)];
        const topics = [...new Set(item.topic_tags.length ? item.topic_tags.map(name => sankeyName(name, topicGrouping)) : ["ไม่มี tag/topic"])];
        const visions = [...new Set(item.vision_alignment.map(row => sankeyName(`${row.dimension}: ${row.title}`, visionGrouping)))];
        const desiredShare = item.weight / uniqueDesiredTags.length;
        const topicShare = item.weight / topics.length;

        uniqueDesiredTags.forEach(desiredTag => addLink(linkMap, category, desiredTag, desiredShare));
        uniqueDesiredTags.forEach(desiredTag => {
          topics.forEach(topic => addLink(linkMap, desiredTag, topic, desiredShare / topics.length));
        });
        topics.forEach(topic => {
          visions.forEach(vision => addLink(linkMap, topic, vision, topicShare / visions.length));
        });
      });

      const links = [...linkMap.values()];
      const nodes = new Map();
      links.forEach(link => {
        nodes.set(link.source, { name: link.source });
        nodes.set(link.target, { name: link.target });
      });
      return { nodes: [...nodes.values()], links, category, desiredEvidence };
    }

    function renderSankeyFallback() {
      const svg = document.querySelector("#sankey");
      const { nodes, links, category } = buildSankeyData();
      const width = 1200;
      const height = 720;
      const nodeWidth = 190;
      const nodeHeight = 28;
      const layerX = [24, 315, 610, 900];
      const layers = [
        [category],
        [...new Set(links.filter(link => link.source === category).map(link => link.target))],
        [...new Set(links.filter(link => layerName(link.source) === 1).map(link => link.target))],
        [...new Set(links.filter(link => layerName(link.source) === 2).map(link => link.target))]
      ];
      const visionOrder = ["บริบท", "บทบาท", "เป้าหมาย", "กลยุทธ์", "แผนสี่ปี"];

      function layerName(name) {
        if (name === category) return 0;
        if (report.evidence.some(item => item.desired_tags.includes(name))) return 1;
        if (name.includes("tag/topic") || name === "ไม่มี tag/topic" || report.evidence.some(item => item.topic_tags.includes(name))) return 2;
        return 3;
      }

      function sortNodes(a, b, layerIndex) {
        if (layerIndex === 3) {
          const ag = visionOrder.findIndex(group => a.startsWith(`${group}:`));
          const bg = visionOrder.findIndex(group => b.startsWith(`${group}:`));
          if (ag !== bg) return (ag < 0 ? 99 : ag) - (bg < 0 ? 99 : bg);
        }
        return (incoming.get(b) || 0) - (incoming.get(a) || 0);
      }

      const incoming = new Map();
      links.forEach(link => incoming.set(link.target, (incoming.get(link.target) || 0) + link.value));
      incoming.set(category, report.summary.weighted_items);

      const nodePos = new Map();
      layers.forEach((layer, layerIndex) => {
        const sorted = [...layer].sort((a, b) => sortNodes(a, b, layerIndex));
        const gap = Math.max(10, (height - 40 - sorted.length * nodeHeight) / Math.max(1, sorted.length - 1));
        sorted.forEach((name, index) => {
          const y = sorted.length === 1 ? height / 2 - nodeHeight / 2 : 20 + index * (nodeHeight + gap);
          nodePos.set(name, { x: layerX[layerIndex], y, width: nodeWidth, height: nodeHeight, value: incoming.get(name) || 0 });
        });
      });

      const maxLink = Math.max(...links.map(link => link.value), 1);
      const linkSvg = links.map(link => {
        const source = nodePos.get(link.source);
        const target = nodePos.get(link.target);
        if (!source || !target) return "";
        const x1 = source.x + source.width;
        const y1 = source.y + source.height / 2;
        const x2 = target.x;
        const y2 = target.y + target.height / 2;
        const mid = (x2 - x1) * .5;
        const stroke = Math.max(1.5, Math.sqrt(link.value / maxLink) * 18);
        return `<path class="sankey-link" d="M${x1},${y1} C${x1 + mid},${y1} ${x2 - mid},${y2} ${x2},${y2}" stroke="#38bdf8" stroke-width="${stroke}"><title>${link.source} → ${link.target}: ${fmt.format(link.value)}</title></path>`;
      }).join("");

      const nodeSvg = [...nodePos.entries()].map(([name, pos]) => {
        const text = name.length > 32 ? `${name.slice(0, 31)}…` : name;
        return `
          <g class="sankey-node" transform="translate(${pos.x},${pos.y})">
            <rect width="${pos.width}" height="${pos.height}" fill="#22c55e"></rect>
            <text x="10" y="${pos.height / 2 - 4}">${text}</text>
            <text class="node-value" x="10" y="${pos.height / 2 + 10}">จำนวนอ้างอิง ${fmt.format(pos.value)}</text>
            <title>${name}: ${fmt.format(pos.value)}</title>
          </g>
        `;
      }).join("");

      svg.innerHTML = `<g>${linkSvg}</g><g>${nodeSvg}</g>`;
    }

    function renderSankey() {
      if (!window.d3 || !d3.sankey) {
        renderSankeyFallback();
        return;
      }

      const svg = d3.select("#sankey");
      svg.selectAll("*").remove();

      const { nodes, links } = buildSankeyData();
      const width = 1200;
      const height = 720;
      const vividPalette = [
        "#14b8a6", "#f97316", "#8b5cf6", "#06b6d4", "#ef4444",
        "#22c55e", "#eab308", "#ec4899", "#3b82f6", "#a855f7",
        "#10b981", "#f43f5e", "#84cc16", "#0ea5e9", "#f59e0b"
      ];
      const color = d3.scaleOrdinal()
        .domain(nodes.map(node => node.name))
        .range(vividPalette);
      const visionOrder = ["บริบท", "บทบาท", "เป้าหมาย", "กลยุทธ์", "แผนสี่ปี"];

      function nodeLayer(node) {
        if (node.name.startsWith("หมวด ")) return 0;
        if (report.evidence.some(item => item.desired_tags.includes(node.name))) return 1;
        if (node.name.includes("tag/topic") || node.name === "ไม่มี tag/topic" || report.evidence.some(item => item.topic_tags.includes(node.name))) return 2;
        return 3;
      }

      function visionRank(name) {
        const index = visionOrder.findIndex(group => name.startsWith(`${group}:`));
        return index < 0 ? 99 : index;
      }

      function sankeyNodeSort(a, b) {
        const layerDiff = nodeLayer(a) - nodeLayer(b);
        if (layerDiff) return layerDiff;
        if (nodeLayer(a) === 3) {
          const groupDiff = visionRank(a.name) - visionRank(b.name);
          if (groupDiff) return groupDiff;
        }
        return d3.descending(a.value, b.value) || d3.ascending(a.name, b.name);
      }

      const graph = {
        nodes: nodes.map(node => ({ ...node })),
        links: links.map(link => ({ ...link }))
      };

      const sankey = d3.sankey()
        .nodeId(node => node.name)
        .nodeWidth(18)
        .nodePadding(13)
        .extent([[20, 16], [width - 24, height - 16]])
        .nodeSort(sankeyNodeSort);

      sankey(graph);

      const linkSelection = svg.append("g")
        .attr("fill", "none")
        .selectAll("path")
        .data(graph.links)
        .join("path")
        .attr("d", d3.sankeyLinkHorizontal())
        .attr("stroke", link => color(link.source.name))
        .attr("stroke-opacity", 0.34)
        .attr("stroke-width", link => Math.max(1, link.width))
        .attr("class", "sankey-link");

      linkSelection.append("title")
        .text(link => `${link.source.name} → ${link.target.name}: ${fmt.format(link.value)}`);

      const node = svg.append("g")
        .selectAll("g")
        .data(graph.nodes)
        .join("g")
        .attr("class", "sankey-node");

      node.append("rect")
        .attr("x", node => node.x0)
        .attr("y", node => node.y0)
        .attr("height", node => Math.max(1, node.y1 - node.y0))
        .attr("width", node => node.x1 - node.x0)
        .attr("fill", node => color(node.name))
        .attr("fill-opacity", 0.96)
        .append("title")
        .text(node => `${node.name}: ${fmt.format(node.value)}`);

      node.append("text")
        .attr("x", node => node.x0 < width / 2 ? node.x1 + 8 : node.x0 - 8)
        .attr("y", node => (node.y0 + node.y1) / 2 - 5)
        .attr("text-anchor", node => node.x0 < width / 2 ? "start" : "end")
        .text(node => node.name.length > 34 ? `${node.name.slice(0, 33)}…` : node.name);

      node.append("text")
        .attr("class", "node-value")
        .attr("x", node => node.x0 < width / 2 ? node.x1 + 8 : node.x0 - 8)
        .attr("y", node => (node.y0 + node.y1) / 2 + 10)
        .attr("text-anchor", node => node.x0 < width / 2 ? "start" : "end")
        .text(node => `จำนวนอ้างอิง ${fmt.format(node.value)}`);

      setupSankeyInteractions("#sankey");
    }

    function setupSankeyInteractions(selector) {
      if (!window.d3) return;
      const svg = d3.select(selector);
      const status = document.querySelector(".sankey-status");
      const reset = document.querySelector(".sankey-reset");

      function clearSelection() {
        svg.classed("is-filtered", false);
        svg.selectAll(".sankey-link").classed("is-selected", false);
        svg.selectAll(".sankey-node").classed("is-selected", false);
        if (status) status.textContent = "คลิก node หรือเส้นเพื่อเน้นความสัมพันธ์";
      }

      function selectNode(name, value) {
        const connected = new Set([name]);
        svg.selectAll(".sankey-link").classed("is-selected", link => {
          const matched = link.source.name === name || link.target.name === name;
          if (matched) {
            connected.add(link.source.name);
            connected.add(link.target.name);
          }
          return matched;
        });
        svg.selectAll(".sankey-node").classed("is-selected", node => connected.has(node.name));
        svg.classed("is-filtered", true);
        if (status) status.textContent = `${name} · จำนวนอ้างอิง ${fmt.format(Math.round(value))}`;
      }

      function selectLink(link) {
        svg.classed("is-filtered", true);
        svg.selectAll(".sankey-link").classed("is-selected", row => row === link);
        svg.selectAll(".sankey-node").classed("is-selected", node => {
          return node.name === link.source.name || node.name === link.target.name;
        });
        if (status) status.textContent = `${link.source.name} → ${link.target.name} · จำนวนอ้างอิง ${fmt.format(Math.round(link.value))}`;
      }

      svg.selectAll(".sankey-node")
        .on("click", (event, node) => {
          event.stopPropagation();
          selectNode(node.name, node.value);
        });

      svg.selectAll(".sankey-link")
        .on("click", (event, link) => {
          event.stopPropagation();
          selectLink(link);
        });

      reset?.addEventListener("click", clearSelection);
    }

    function setupSankeyFullscreen() {
      const wrap = document.querySelector(".sankey-wrap");
      const close = wrap.querySelector(".sankey-close");
      const expand = wrap.querySelector(".sankey-expand");
      function open() {
        wrap.classList.add("is-fullscreen");
        document.body.classList.add("sankey-locked");
      }
      function closeFullscreen() {
        wrap.classList.remove("is-fullscreen");
        document.body.classList.remove("sankey-locked");
      }
      expand?.addEventListener("click", open);
      close.addEventListener("click", event => {
        event.stopPropagation();
        closeFullscreen();
      });
      document.addEventListener("keydown", event => {
        if (event.key === "Escape") closeFullscreen();
      });
    }

    function tagList(tags) {
      return `<div class="tags">${tags.map(tag => `<span class="tag">${tag}</span>`).join("")}</div>`;
    }

    function renderClassificationOptions() {
      const values = [...new Set(report.evidence.flatMap(item => item.classifications))];
      document.querySelector("#classification").innerHTML = `<option value="">ทุกประเภท</option>` + values.map(value => `
        <option value="${value}">${value}</option>
      `).join("");
    }

    function renderEvidence() {
      const query = document.querySelector("#search").value.trim().toLowerCase();
      const classification = document.querySelector("#classification").value;
      const confidence = document.querySelector("#confidence").value;

      const rows = report.evidence.filter(item => {
        const haystack = [
          item.display,
          item.page,
          item.document_item,
          item.sequence,
          ...item.classifications,
          ...item.topic_tags,
          ...item.desired_tags,
          ...item.concern_tags,
          ...item.vision_alignment.map(alignment => alignment.title),
          ...item.vision_alignment.map(alignment => alignment.dimension)
        ].join(" ").toLowerCase();
        return (!query || haystack.includes(query))
          && (!classification || item.classifications.includes(classification))
          && (!confidence || item.confidence === confidence);
      });

      document.querySelector("#evidenceRows").innerHTML = rows.map(item => `
        <tr>
          <td class="small">${refText(item)}</td>
          <td class="small">${fmt.format(item.weight)}</td>
          <td>${item.display}</td>
          <td>${tagList(item.classifications)}</td>
          <td>${tagList([...item.topic_tags, ...item.desired_tags, ...item.concern_tags])}</td>
          <td>${tagList(item.vision_alignment.slice(0, 5).map(alignment => `${alignment.dimension}: ${alignment.title}`))}</td>
          <td class="small">${item.confidence}</td>
        </tr>
      `).join("");
    }

    async function main() {
      const slug = location.pathname.split("/").pop().replace(/\.html$/, "") || "administration";
      await renderCategoryNav(slug);
      report = await fetch(`../data/categories/${slug}.json`).then(response => response.json());
      document.title = `หมวด ${report.number} ${report.title}`;
      document.querySelector("#title").textContent = `หมวด ${report.number}: ${report.title}`;
      document.querySelector("#summary").textContent = report.interpretive_summary;
      document.querySelector("#metrics").innerHTML = [
        metric("รายการที่แยกได้", report.summary.items),
        metric("จำนวนอ้างอิงรวม", report.summary.weighted_items),
        metric("ช่วงหน้า PDF", `${report.summary.pages[0]}-${report.summary.pages.at(-1)}`),
        metric("หมวด", report.number)
      ].join("");

      initializeExpandedExamples();
      renderBars(document.querySelector("#frequency"), report.frequency_profile);
      renderSummaryCards(document.querySelector("#desired"), report.desired_characteristics);
      renderSummaryCards(document.querySelector("#concerns"), report.concerns);
      renderIssueCards(document.querySelector("#sensitive"), report.sensitive_issues, 8);
      renderIssueCards(document.querySelector("#lessRelevant"), report.less_relevant_issues, 8);
      wireMoreButtons();
      renderVisionAlignment(document.querySelector("#visionAlignment"));
      renderSankey();
      setupSankeyFullscreen();
      renderClassificationOptions();
      renderEvidence();

      document.querySelector("#search").addEventListener("input", renderEvidence);
      document.querySelector("#classification").addEventListener("change", renderEvidence);
      document.querySelector("#confidence").addEventListener("change", renderEvidence);
      document.addEventListener("click", event => {
        const button = event.target.closest("[data-example-id]");
        if (!button || button.disabled) return;
        handleExampleAction(button.dataset.exampleId, button.dataset.exampleAction);
      });
    }

    main().catch(error => {
      document.body.innerHTML = `<main class="wrap"><section class="panel"><h1>โหลดข้อมูลไม่สำเร็จ</h1><p>${error.message}</p></section></main>`;
    });
