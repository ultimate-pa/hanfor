require("bootstrap")
require("d3-selection")
require("./lib_ts_editor.css")

const d3 = require("d3")

const svg = d3.select("#graphArea")

const nodes = [
  {
    id: 0,
    label: "Node 0",
    x: 100,
    y: 100,
    r: 30,
    initial: false,
  },
  {
    id: 1,
    label: "Node 1",
    x: 300,
    y: 100,
    r: 30,
    initial: false,
  },
]
const transitions = [
  {
    source: 0,
    target: 1,
    label: "true",
  },
]
let nodeId = 2
let contextNode = null
let contextNodeElement = null
let selectedStart = null
let selectedEnd = null
let newNodeX = 0
let newNodeY = 0

const g = svg.append("g").attr("id", "zoom-group") // für Zoom später
const zoomGroup = d3.select("#zoom-group")
const zoom = d3
  .zoom()
  .scaleExtent([0.1, 4]) // Min und Max Zoom
  .on("zoom", (event) => {
    zoomGroup.attr("transform", event.transform) // Transformation anwenden
  })
svg.call(zoom)

d3.select("#reset-zoom").on("click", () => {
  svg.transition().duration(500).call(zoom.transform, d3.zoomIdentity)
})

const drag = d3
  .drag()
  .on("start", (event, d) => {
    d3.select(event.sourceEvent.target.closest("g")).raise()
  })
  .on("drag", (event, d) => {
    d.x = event.x
    d.y = event.y
    update()
  })

d3.select("#graphArea").on("contextmenu", (event) => {
  event.preventDefault()

  const svgRect = d3.select("#graphArea").node().getBoundingClientRect()

  const transform = d3.zoomTransform(svg.node())
  ;[newNodeX, newNodeY] = transform.invert([event.pageX - svgRect.left, event.pageY - svgRect.top])
  openSvgContextMenu(event.pageX, event.pageY)
})

function openSvgContextMenu(x, y) {
  d3.select("#context-menu-svg").style("left", `${x}px`).style("top", `${y}px`).style("display", "block")
}

d3.select("#edit-node-label").on("click", () => {
  d3.select(contextNodeElement).dispatch("dblclick")
  closeContextMenu()
})

d3.select("#select-transition-source").on("click", () => {
  selectedStart = contextNode

  if (selectedEnd === contextNode) {
    selectedEnd = null
  }

  addTransition()

  update()
  closeContextMenu()
})

d3.select("#select-transition-target").on("click", () => {
  selectedEnd = contextNode

  if (selectedStart === contextNode) {
    selectedStart = null
  }

  addTransition()

  update()
  closeContextMenu()
})

function addTransition() {
  if (selectedStart && selectedEnd && selectedStart.id !== selectedEnd.id) {
    transitions.push({
      source: selectedStart.id,
      target: selectedEnd.id,
      label: "true",
    })

    selectedStart = null
    selectedEnd = null
  }
}

d3.select("#cancel-transition").on("click", () => {
  selectedStart = null
  selectedEnd = null
  update()
  closeContextMenu()
})

d3.select("#add-node").on("click", () => {
  addNode(newNodeX, newNodeY)
  closeContextMenu()
})
d3.select("#cancel-transition-selection").on("click", () => {
  selectedStart = null
  selectedEnd = null
  update()
  closeContextMenu()
})

d3.select("#mark-initial").on("click", () => {
  contextNode.initial = !contextNode.initial
  update()
  closeContextMenu()
})

d3.select("#remove-node").on("click", () => {
  const nodeIndex = nodes.findIndex((n) => n.id === contextNode.id)
  if (nodeIndex > -1) {
    nodes.splice(nodeIndex, 1)
  }

  for (let i = transitions.length - 1; i >= 0; i--) {
    if (transitions[i].source === contextNode.id || transitions[i].target === contextNode.id) {
      transitions.splice(i, 1)
    }
  }
  update()
  closeContextMenu()
})

d3.select("body").on("click", () => {
  closeContextMenu()
})

function closeContextMenu() {
  d3.select("#context-menu-nodes").style("display", "none")
  d3.select("#context-menu-svg").style("display", "none")
}

function getNodeById(id) {
  return nodes.find((n) => n.id === id)
}

function calculateEdgeEndpoints(edge) {
  let target = getNodeById(edge.target)
  let source = getNodeById(edge.source)
  let dx = target.x - source.x
  let dy = target.y - source.y
  let distance = Math.sqrt(dx * dx + dy * dy)
  dx /= distance
  dy /= distance

  return {
    x1: source.x + source.r * dx,
    y1: source.y + source.r * dy,
    x2: target.x - (target.r + 9) * dx,
    y2: target.y - (target.r + 9) * dy,
  }
}

const tmp = 1 / Math.sqrt(2)

function curvedPathQ(d) {
  let target = getNodeById(d.target)
  let source = getNodeById(d.source)
  const sx = source.x
  const sy = source.y
  const tx = target.x
  const ty = target.y

  // Richtung Vektor
  const dx = tx - sx
  const dy = ty - sy

  // Länge
  const len = Math.sqrt(dx * dx + dy * dy)

  let sox = tmp * ((dx + dy) / len) * (source.r + 1)
  let soy = tmp * ((dx - dy) / len) * (source.r + 1)

  let tox = tmp * ((dx - dy) / len) * (target.r + 6)
  let toy = tmp * ((-dx - dy) / len) * (target.r + 6)

  // Mittelpunkt
  const mx = (sx + sox + tx - tox) / 2
  const my = (sy - soy + ty + toy) / 2

  // Normierter Vektor orthogonal zur Verbindung
  const perpX = -dy / len
  const perpY = dx / len

  // Offset für die Krümmung (z. B. 40px)
  const curveOffset = -40

  // Kontrollpunkt = Mitte + Offset
  const cx = mx + perpX * curveOffset
  const cy = my + perpY * curveOffset

  return `M${sx + sox},${sy - soy} Q${cx},${cy} ${tx - tox},${ty + toy}`
}

function calculateTransitionLabel(d) {
  let target = getNodeById(d.target)
  let source = getNodeById(d.source)
  const sx = source.x
  const sy = source.y
  const tx = target.x
  const ty = target.y

  // Richtung Vektor
  const dx = tx - sx
  const dy = ty - sy

  // Länge
  const len = Math.sqrt(dx * dx + dy * dy)

  let sox = tmp * ((dx + dy) / len) * (source.r + 1)
  let soy = tmp * ((dx - dy) / len) * (source.r + 1)

  let tox = tmp * ((dx - dy) / len) * (target.r + 6)
  let toy = tmp * ((-dx - dy) / len) * (target.r + 6)

  // Mittelpunkt
  const mx = (sx + sox + tx - tox) / 2
  const my = (sy - soy + ty + toy) / 2

  // Normierter Vektor orthogonal zur Verbindung
  const perpX = -dy / len
  const perpY = dx / len

  // Offset für die Krümmung (z. B. 40px)
  const curveOffset = -30

  // Kontrollpunkt = Mitte + Offset
  const cx = mx + perpX * curveOffset
  const cy = my + perpY * curveOffset

  return { x: cx, y: cy }
}

function update() {
  const transitionGroup = g.selectAll(".transition").data(transitions, (d) => `${d.source}-${d.target}`)

  const transitionEnterGroup = transitionGroup.enter().append("g").attr("class", "transition")

  //transitionEnterGroup.append("line").attr("stroke", "#999").attr("stroke-width", 2).attr("marker-end", "url(#arrow)")
  transitionEnterGroup.append("path")

  transitionEnterGroup.append("text").attr("text-anchor", "middle") // TODO make this direction dependent

  const transitionMergedGroup = transitionEnterGroup.merge(transitionGroup)
  transitionMergedGroup.select("path").attr("d", (d) => curvedPathQ(d))

  transitionMergedGroup
    .select("text")
    .attr("x", (d) => calculateTransitionLabel(d).x)
    .attr("y", (d) => calculateTransitionLabel(d).y)
    //.attr("dy", -5)
    .text((d) => d.label)

  transitionGroup.exit().remove()

  const nodeGroup = g.selectAll(".node").data(nodes, (d) => d.id)

  // ENTER
  const enterGroup = nodeGroup.enter().append("g").attr("class", "node").call(drag)

  enterGroup.append("circle").attr("r", (d) => d.r)

  enterGroup.append("text").attr("dy", "0.35em").attr("text-anchor", "middle")

  enterGroup
    .append("line")
    .attr("y1", (d) => d.r + 49)
    .attr("y2", (d) => d.r + 9)

  enterGroup.on("contextmenu", (event, d) => {
    event.preventDefault()
    event.stopPropagation()
    closeContextMenu()
    contextNodeElement = event.currentTarget
    contextNode = d

    // Position & Anzeigen
    const menu = d3.select("#context-menu-nodes")
    menu.style("left", `${event.pageX}px`).style("top", `${event.pageY}px`).style("display", "block")
    d3.select("#mark-initial").text(d.initial ? "Mark as non initial" : "Mark as initial")
  })

  enterGroup.on("dblclick", (event, d) => {
    event.stopPropagation()
    const svgRect = svg.node().getBoundingClientRect()
    const pageX = svgRect.left + d.x
    const pageY = svgRect.top + d.y

    // Input-Feld erstellen
    const input = d3
      .select("body")
      .append("input")
      .attr("type", "text")
      .attr("value", d.label)
      .style("position", "absolute")
      .style("left", `${pageX - 40}px`) // leicht nach links verschoben
      .style("top", `${pageY - 10}px`) // leicht nach oben verschoben
      .style("width", "80px")
      .style("font-size", "14px")
      .node()

    input.focus()
    input.select()

    function applyChange() {
      d.label = input.value
      d3.select(input).remove()
      update()
    }

    input.addEventListener("blur", () => {
      d3.select(input).remove()
    })
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") applyChange()
    })
  })

  // UPDATE
  const mergedGroup = enterGroup.merge(nodeGroup)
  mergedGroup
    .attr("transform", (d) => `translate(${d.x},${d.y})`)
    .classed("selected-start", (d) => selectedStart !== null && d.id === selectedStart.id)
    .classed("selected-end", (d) => selectedEnd !== null && d.id === selectedEnd.id)
    .select("text")
    .text((d) => d.label)

  mergedGroup
    .select("line")
    .classed("initial", (d) => d.initial)
    .attr("y1", (d) => -(d.r + 49))
    .attr("y2", (d) => -(d.r + 9))

  // EXIT
  nodeGroup.exit().remove()
}

d3.select("#addNodeBtn").on("click", () => {
  addNode(100, 100)
})
d3.select("#printBtn").on("click", () => {
  console.log(nodes)
  console.log(transitions)
})

function addNode(posX, posY) {
  nodes.push({
    id: nodeId,
    label: "Node " + nodeId,
    x: posX,
    y: posY,
    r: 30,
    initial: false,
  })
  nodeId++
  update()
}

update()
