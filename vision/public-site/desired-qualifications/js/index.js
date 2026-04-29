    const fmt = new Intl.NumberFormat("th-TH");
    const visionOrder = ["บริบท", "บทบาท", "เป้าหมาย", "กลยุทธ์", "แผนสี่ปี"];
    let categoryReports = [];
    let sankeySelection = null;
    let sankeySelectionInitialized = false;

    function metric(label, value) {
      const rendered = typeof value === "number" ? fmt.format(value) : value;
      return `<div class="metric"><div class="label">${label}</div><div class="value">${rendered}</div></div>`;
    }

    function renderBars(target, rows, limit = 10) {
      const top = rows.slice(0, limit);
      const max = Math.max(...top.map(row => row.count), 1);
      target.innerHTML = top.map(row => `
        <div class="bar-row" title="${row.name}">
          <div class="bar-label">${row.name}</div>
          <div class="track"><div class="fill" style="width:${(row.count / max) * 100}%"></div></div>
          <div class="num">${fmt.format(row.count)}</div>
        </div>
      `).join("");
    }

    function miniChart(rows, limit = 4) {
      const top = rows.slice(0, limit);
      const max = Math.max(...top.map(row => row.count), 1);
      return `<div class="mini-chart">${top.map(row => `
        <div class="mini-row" title="${row.name}">
          <div class="bar-label">${row.name}</div>
          <div class="track"><div class="fill" style="width:${(row.count / max) * 100}%"></div></div>
          <div class="num">${fmt.format(row.count)}</div>
        </div>
      `).join("")}</div>`;
    }

    function renderSections(indexReports) {
      const bySlug = new Map(categoryReports.map(report => [report.slug, report]));
      document.querySelector("#sections").innerHTML = indexReports.map(row => {
        const report = bySlug.get(row.slug);
        return `
          <article class="section-card">
            <div class="section-head">
              <div class="section-title"><a href="${row.href}">${row.number}. ${row.title}</a></div>
              <div class="badge">${fmt.format(row.weighted_items)} อ้างอิง</div>
            </div>
            <div class="label">ลักษณะพึงประสงค์เด่น</div>
            ${miniChart(report.desired_characteristics, 4)}
            <div class="label">tag/topic เด่น</div>
            ${miniChart(report.frequency_profile, 4)}
            <a class="section-link" href="${row.href}">ดูรายละเอียดหมวด ${row.number}</a>
          </article>
        `;
      }).join("");
    }

    function addLink(map, source, target, value) {
      if (!source || !target || !value) return;
      const key = `${source}|||${target}`;
      const current = map.get(key) || { source, target, value: 0 };
      current.value += value;
      map.set(key, current);
    }

    function groupTop(values, limit, otherLabel) {
      const totals = new Map();
      values.forEach(({ name, value }) => totals.set(name, (totals.get(name) || 0) + value));
      const ordered = [...totals.entries()].sort((a, b) => b[1] - a[1]);
      return {
        keep: new Set(ordered.slice(0, limit).map(([name]) => name)),
        otherLabel
      };
    }

    function sankeyName(name, grouping) {
      return grouping.keep.has(name) ? name : grouping.otherLabel;
    }

    function shortCategory(report) {
      return `หมวด ${report.number}: ${report.title.replace(/\s*\(.+?\)\s*/g, "")}`;
    }

    function buildSankeyData() {
      const topicValues = [];
      const desiredValues = [];
      const visionValues = [];
      const desiredEvidence = [];

      categoryReports.forEach(report => {
        report.evidence
          .filter(item => item.desired_tags.length && item.vision_alignment.length)
          .forEach(item => {
            desiredEvidence.push({ report, item });
            item.desired_tags.forEach(name => desiredValues.push({ name, value: item.weight }));
            item.topic_tags.forEach(name => topicValues.push({ name, value: item.weight }));
            item.vision_alignment.forEach(row => visionValues.push({ name: `${row.dimension}: ${row.title}`, value: item.weight }));
          });
      });

      const desiredGrouping = groupTop(desiredValues, 12, "ลักษณะพึงประสงค์: อื่น ๆ");
      const topicGrouping = groupTop(topicValues, 12, "tag/topic: อื่น ๆ");
      const visionGrouping = groupTop(visionValues, 17, "วิสัยทัศน์: อื่น ๆ");
      const linkMap = new Map();

      desiredEvidence.forEach(({ report, item }) => {
        const category = shortCategory(report);
        const desiredTags = [...new Set(item.desired_tags.map(name => sankeyName(name, desiredGrouping)))];
        const topics = [...new Set(item.topic_tags.length ? item.topic_tags.map(name => sankeyName(name, topicGrouping)) : ["ไม่มี tag/topic"])];
        const visions = [...new Set(item.vision_alignment.map(row => sankeyName(`${row.dimension}: ${row.title}`, visionGrouping)))];

        const topicShare = item.weight / topics.length;
        topics.forEach(topic => {
          addLink(linkMap, category, topic, topicShare);
          desiredTags.forEach(desired => addLink(linkMap, topic, desired, topicShare / desiredTags.length));
        });
        desiredTags.forEach(desired => {
          visions.forEach(vision => addLink(linkMap, desired, vision, item.weight / desiredTags.length / visions.length));
        });
      });

      const links = [...linkMap.values()];
      const nodes = new Map();
      links.forEach(link => {
        nodes.set(link.source, { name: link.source });
        nodes.set(link.target, { name: link.target });
      });
      return { nodes: [...nodes.values()], links };
    }

    function nodeLayer(name) {
      if (name.startsWith("หมวด ")) return 0;
      if (name.includes("tag/topic") || name === "ไม่มี tag/topic" || categoryReports.some(report => report.frequency_profile.some(row => row.name === name))) return 1;
      if (categoryReports.some(report => report.desired_characteristics.some(row => row.name === name)) || name.startsWith("ลักษณะพึงประสงค์:")) return 2;
      return 3;
    }

    function visionRank(name) {
      const index = visionOrder.findIndex(group => name.startsWith(`${group}:`));
      return index < 0 ? 99 : index;
    }

    function renderSankeyFallback() {
      const svg = document.querySelector("#overviewSankey");
      const { nodes, links } = buildSankeyData();
      const width = 1240;
      const height = 760;
      const nodeWidth = 210;
      const layerX = [24, 330, 650, 960];
      const layerLabels = ["หมวด", "tag/topic", "ลักษณะพึงประสงค์", "วิสัยทัศน์"];
      const incoming = new Map();
      const outgoing = new Map();
      links.forEach(link => {
        incoming.set(link.target, (incoming.get(link.target) || 0) + link.value);
        outgoing.set(link.source, (outgoing.get(link.source) || 0) + link.value);
      });
      categoryReports.forEach(report => {
        const category = shortCategory(report);
        incoming.set(category, outgoing.get(category) || report.summary.weighted_items);
      });

      const layers = [0, 1, 2, 3].map(layer => nodes
        .map(node => node.name)
        .filter(name => nodeLayer(name) === layer)
        .sort((a, b) => {
          if (layer === 0) return Number(a.match(/หมวด (\d+)/)?.[1] || 0) - Number(b.match(/หมวด (\d+)/)?.[1] || 0);
          if (layer === 3) return visionRank(a) - visionRank(b) || (incoming.get(b) || 0) - (incoming.get(a) || 0);
          return (incoming.get(b) || 0) - (incoming.get(a) || 0);
        }));

      const nodePos = new Map();
      layers.forEach((layer, layerIndex) => {
        const values = layer.map(name => Math.max(incoming.get(name) || outgoing.get(name) || 1, 1));
        const minHeight = layerIndex === 0 ? 18 : 12;
        const available = height - 76;
        const rawTotal = values.reduce((sum, value) => sum + value, 0);
        const scale = Math.max(0.02, (available - Math.max(0, layer.length - 1) * 8) / rawTotal);
        const heights = values.map(value => Math.max(minHeight, value * scale));
        const used = heights.reduce((sum, value) => sum + value, 0);
        const gap = layer.length > 1 ? Math.max(8, (available - used) / (layer.length - 1)) : 0;
        let cursor = 58;
        layer.forEach((name, index) => {
          const nodeHeight = heights[index];
          const y = layer.length === 1 ? height / 2 - nodeHeight / 2 : cursor;
          nodePos.set(name, { x: layerX[layerIndex], y, width: nodeWidth, height: nodeHeight, value: incoming.get(name) || outgoing.get(name) || 0 });
          cursor += nodeHeight + gap;
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
        const text = name.length > 34 ? `${name.slice(0, 33)}…` : name;
        return `
          <g class="sankey-node" transform="translate(${pos.x},${pos.y})">
            <rect width="${pos.width}" height="${pos.height}" fill="#14b8a6"></rect>
            <text x="10" y="${pos.height / 2 - 4}">${text}</text>
            <text class="node-value" x="10" y="${pos.height / 2 + 10}">จำนวนอ้างอิง ${fmt.format(pos.value)}</text>
            <title>${name}: ${fmt.format(pos.value)}</title>
          </g>
        `;
      }).join("");

      const headerSvg = layerLabels.map((label, index) => {
        const x = layerX[index] + nodeWidth / 2;
        const w = Math.max(86, label.length * 12 + 30);
        return `
          <g class="sankey-layer-header" transform="translate(${x},24)">
            <rect x="${-w / 2}" y="-14" width="${w}" height="28"></rect>
            <text y="5">${label}</text>
          </g>
        `;
      }).join("");

      svg.innerHTML = `<g>${headerSvg}</g><g>${linkSvg}</g><g>${nodeSvg}</g>`;
    }

    function drawSankeyLayerHeaders(svg, graph, labels) {
      const columns = [...d3.group(graph.nodes, node => Math.round(node.x0)).entries()]
        .sort((a, b) => a[0] - b[0])
        .map(([, nodes]) => d3.mean(nodes, node => (node.x0 + node.x1) / 2));

      const header = svg.append("g")
        .attr("class", "sankey-layer-headers")
        .selectAll("g")
        .data(labels.map((label, index) => ({ label, x: columns[index] })).filter(row => Number.isFinite(row.x)))
        .join("g")
        .attr("class", "sankey-layer-header")
        .attr("transform", row => `translate(${row.x},24)`);

      header.append("rect")
        .attr("x", row => -Math.max(86, row.label.length * 12 + 30) / 2)
        .attr("y", -14)
        .attr("width", row => Math.max(86, row.label.length * 12 + 30))
        .attr("height", 28);

      header.append("text")
        .attr("y", 5)
        .text(row => row.label);
    }

    function renderSankey() {
      if (!window.d3 || !d3.sankey) {
        renderSankeyFallback();
        return;
      }

      const svg = d3.select("#overviewSankey");
      svg.selectAll("*").remove();
      const { nodes, links } = buildSankeyData();
      const width = 1240;
      const height = 760;
      const layerLabels = ["หมวด", "tag/topic", "ลักษณะพึงประสงค์", "วิสัยทัศน์"];
      const palette = [
        "#14b8a6", "#f97316", "#8b5cf6", "#06b6d4", "#ef4444",
        "#22c55e", "#eab308", "#ec4899", "#3b82f6", "#a855f7",
        "#10b981", "#f43f5e", "#84cc16", "#0ea5e9", "#f59e0b"
      ];
      const color = d3.scaleOrdinal().domain(nodes.map(node => node.name)).range(palette);

      function sankeyNodeSort(a, b) {
        const layerDiff = nodeLayer(a.name) - nodeLayer(b.name);
        if (layerDiff) return layerDiff;
        if (nodeLayer(a.name) === 0) {
          return Number(a.name.match(/หมวด (\d+)/)?.[1] || 0) - Number(b.name.match(/หมวด (\d+)/)?.[1] || 0);
        }
        if (nodeLayer(a.name) === 3) {
          const rankDiff = visionRank(a.name) - visionRank(b.name);
          if (rankDiff) return rankDiff;
        }
        return d3.descending(a.value, b.value) || d3.ascending(a.name, b.name);
      }

      const graph = {
        nodes: nodes.map(node => ({ ...node })),
        links: links.map(link => ({ ...link }))
      };

      d3.sankey()
        .nodeId(node => node.name)
        .nodeWidth(18)
        .nodePadding(12)
        .extent([[20, 54], [width - 24, height - 16]])
        .nodeSort(sankeyNodeSort)(graph);

      drawSankeyLayerHeaders(svg, graph, layerLabels);

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
        .attr("fill-opacity", .96)
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

      setupSankeyInteractions("#overviewSankey");
    }

    function setupSankeyInteractions(selector) {
      if (!window.d3) return;
      const svg = d3.select(selector);
      const status = document.querySelector(".sankey-status");
      const reset = document.querySelector(".sankey-reset");
      const defaultNodeName = "เข้าใจนิสิตและพัฒนาคุณภาพชีวิต";
      const linkKey = link => `${link.source.name}|||${link.target.name}`;

      function selectedPath(name) {
        const links = svg.selectAll(".sankey-link").data();
        const selectedNodes = new Set([name]);
        const selectedLinks = new Set();
        const upstream = new Set([name]);
        const downstream = new Set([name]);
        let changed = true;
        while (changed) {
          changed = false;
          links.forEach(link => {
            if (upstream.has(link.target.name) && !upstream.has(link.source.name)) {
              upstream.add(link.source.name);
              selectedNodes.add(link.source.name);
              selectedLinks.add(linkKey(link));
              changed = true;
            }
            if (downstream.has(link.source.name) && !downstream.has(link.target.name)) {
              downstream.add(link.target.name);
              selectedNodes.add(link.target.name);
              selectedLinks.add(linkKey(link));
              changed = true;
            }
            if (upstream.has(link.target.name) && upstream.has(link.source.name)) selectedLinks.add(linkKey(link));
            if (downstream.has(link.source.name) && downstream.has(link.target.name)) selectedLinks.add(linkKey(link));
          });
        }
        return { selectedNodes, selectedLinks };
      }

      function clearSelection() {
        sankeySelection = null;
        svg.classed("is-filtered", false);
        svg.selectAll(".sankey-link").classed("is-selected", false);
        svg.selectAll(".sankey-node").classed("is-selected", false);
        if (status) status.textContent = "คลิก node หรือเส้นเพื่อเน้นความสัมพันธ์";
      }

      function applyNodeSelection(name, value) {
        const { selectedNodes, selectedLinks } = selectedPath(name);
        svg.selectAll(".sankey-link").classed("is-selected", link => {
          return selectedLinks.has(linkKey(link));
        });
        svg.selectAll(".sankey-node").classed("is-selected", node => selectedNodes.has(node.name));
        svg.classed("is-filtered", true);
        if (status) status.textContent = `${name} · จำนวนอ้างอิง ${fmt.format(Math.round(value))}`;
      }

      function selectNode(name, value) {
        sankeySelection = { type: "node", name };
        sankeySelectionInitialized = true;
        applyNodeSelection(name, value);
      }

      function applyLinkSelection(link) {
        const selectedKey = linkKey(link);
        svg.classed("is-filtered", true);
        svg.selectAll(".sankey-link").classed("is-selected", row => linkKey(row) === selectedKey);
        svg.selectAll(".sankey-node").classed("is-selected", node => {
          return node.name === link.source.name || node.name === link.target.name;
        });
        if (status) status.textContent = `${link.source.name} → ${link.target.name} · จำนวนอ้างอิง ${fmt.format(Math.round(link.value))}`;
      }

      function selectLink(link) {
        sankeySelection = { type: "link", key: linkKey(link) };
        sankeySelectionInitialized = true;
        applyLinkSelection(link);
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

      const nodeData = svg.selectAll(".sankey-node").data();
      const linkData = svg.selectAll(".sankey-link").data();
      if (sankeySelection?.type === "node") {
        const selectedNode = nodeData.find(node => node.name === sankeySelection.name);
        if (selectedNode) {
          applyNodeSelection(selectedNode.name, selectedNode.value);
        } else {
          clearSelection();
        }
      } else if (sankeySelection?.type === "link") {
        const selectedLink = linkData.find(link => linkKey(link) === sankeySelection.key);
        if (selectedLink) {
          applyLinkSelection(selectedLink);
        } else {
          clearSelection();
        }
      } else if (!sankeySelectionInitialized) {
        const defaultNode = nodeData.find(node => node.name === defaultNodeName);
        if (defaultNode) {
          selectNode(defaultNode.name, defaultNode.value);
        }
        sankeySelectionInitialized = true;
      } else {
        clearSelection();
      }

      if (reset) reset.onclick = clearSelection;
    }

    async function main() {
      const data = await fetch("data/analysis.json").then(response => response.json());
      const categoryIndex = await fetch("data/categories/index.json").then(response => response.json());
      categoryReports = await Promise.all(categoryIndex.reports.map(row => fetch(row.data).then(response => response.json())));

      const respondents = data.respondents || {};
      const summary = data.summary || {};
      const academic = respondents.academic || 287;
      const support = respondents.support || 385;
      const total = respondents.respondents || academic + support || 1;
      const sankeyItems = categoryReports.reduce((sum, report) => {
        return sum + report.evidence
          .filter(item => item.desired_tags.length && item.vision_alignment.length)
          .reduce((itemSum, item) => itemSum + item.weight, 0);
      }, 0);
      document.documentElement.style.setProperty("--academic", `${(academic / total) * 360}deg`);
      document.querySelector("#sourceName").textContent = data.source;
      document.querySelector("#pdfMeta").textContent = `${fmt.format(summary.pages)} หน้า, ${fmt.format(summary.sections)} หมวด, ${fmt.format(summary.items)} รายการที่แยกได้`;

      document.querySelector("#metrics").innerHTML = [
        metric("ผู้ตอบทั้งหมด", total),
        metric("จำนวนหมวด", summary.sections || 7),
        metric("หน้าเอกสาร", summary.pages || 199),
        metric("รายการที่แยกได้", summary.items || 0),
        metric("รายการใน Sankey", sankeyItems)
      ].join("");

      document.querySelector("#legend").innerHTML = `
        <div class="legend-row"><span><i class="dot"></i>สายวิชาการ</span><strong>${fmt.format(academic)} คน</strong></div>
        <div class="legend-row"><span><i class="dot gold"></i>สายสนับสนุนฯ</span><strong>${fmt.format(support)} คน</strong></div>
      `;

      renderBars(document.querySelector("#themeBars"), data.themes, 10);
      renderSections(categoryIndex.reports);
      renderSankey();
    }

    main().catch(error => {
      document.body.innerHTML = `<main class="wrap"><section class="panel"><h1>โหลดข้อมูลไม่สำเร็จ</h1><p>${error.message}</p></section></main>`;
    });
