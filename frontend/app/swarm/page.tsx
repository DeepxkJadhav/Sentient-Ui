"use client";
import { useEffect, useRef, useState } from "react";
import { Network } from "lucide-react";
import * as d3 from "d3";
import { useAgentStore, useSwarmStore } from "@/store";
import { swarmApi, type SwarmTopology, type SwarmMetrics } from "@/lib/api";

/* Node status → neutral tones, no neon */
const STATUS_STROKE: Record<string, string> = {
  executing: "#6366f1",
  thinking:  "#60a5fa",
  idle:      "#46464f",
  error:     "#f87171",
};

export default function SwarmPage() {
  const svgRef       = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const topology     = useSwarmStore((s) => s.topology);
  const agents       = useAgentStore((s) => s.agents);
  const [metrics, setMetrics]             = useState<SwarmMetrics | null>(null);
  const [localTopology, setLocalTopology] = useState<SwarmTopology | null>(null);
  const simRef = useRef<d3.Simulation<d3.SimulationNodeDatum, undefined> | null>(null);

  useEffect(() => {
    swarmApi.topology().then(setLocalTopology).catch(() => {});
    swarmApi.metrics().then(setMetrics).catch(() => {});
  }, []);

  const data = topology || localTopology;

  useEffect(() => {
    if (!data) return;
    const container = containerRef.current;
    if (!container) return;
    const { width, height } = container.getBoundingClientRect();
    drawGraph(data, Math.max(width || 800, 400), Math.max(height || 500, 300));
  }, [data]);

  const drawGraph = (topo: SwarmTopology, width: number, height: number) => {
    const svg = d3.select(svgRef.current!);
    svg.selectAll("*").remove();
    svg.attr("width", width).attr("height", height);

    const g = svg.append("g");

    svg.call(
      d3.zoom<SVGSVGElement, unknown>()
        .scaleExtent([0.3, 3])
        .on("zoom", (e) => g.attr("transform", e.transform)) as never
    );

    const nodes = topo.nodes.map((n) => ({ ...n, x: width / 2, y: height / 2 })) as (typeof topo.nodes[0] & d3.SimulationNodeDatum)[];
    const nodeMap = new Map(nodes.map((n) => [n.id, n]));
    const links = topo.edges
      .map((e) => ({ source: nodeMap.get(e.source)!, target: nodeMap.get(e.target)!, strength: e.strength, messages: e.messages }))
      .filter((l) => l.source && l.target);

    simRef.current = d3.forceSimulation(nodes)
      .force("link",      d3.forceLink(links).id((d: any) => d.id).distance(120).strength(0.5))
      .force("charge",    d3.forceManyBody().strength(-200))
      .force("center",    d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide(40));

    /* Links — quiet grey with variable opacity */
    const link = g.append("g").selectAll("line")
      .data(links).join("line")
      .attr("stroke", "var(--border-mid)")
      .attr("stroke-width", (d) => d.strength * 1.5)
      .attr("stroke-opacity", 0.5)
      .attr("class", "link");

    /* Nodes */
    const node = g.append("g").selectAll("g")
      .data(nodes).join("g")
      .attr("class", "node")
      .call(d3.drag<SVGGElement, typeof nodes[0]>()
        .on("start", (e, d) => { if (!e.active) simRef.current?.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
        .on("drag",  (e, d) => { d.fx = e.x; d.fy = e.y; })
        .on("end",   (e, d) => { if (!e.active) simRef.current?.alphaTarget(0); d.fx = null; d.fy = null; }) as never);

    node.append("circle")
      .attr("r", (d: any) => d.status === "executing" ? 20 : d.status === "thinking" ? 16 : 12)
      .attr("fill", "var(--bg-elevated)")
      .attr("stroke", (d: any) => STATUS_STROKE[d.status] || "var(--border-mid)")
      .attr("stroke-width", 1.5);

    node.append("text")
      .attr("dy", 28)
      .attr("text-anchor", "middle")
      .attr("font-size", "10px")
      .attr("fill", "var(--text-muted)")
      .attr("font-family", "var(--font-mono)")
      .text((d: any) => d.name);

    simRef.current.on("tick", () => {
      link
        .attr("x1", (d: any) => d.source.x)
        .attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x)
        .attr("y2", (d: any) => d.target.y);
      node.attr("transform", (d: any) => `translate(${d.x},${d.y})`);
    });
  };

  return (
    <div className="page-container" style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
            <Network size={16} strokeWidth={1.75} style={{ color: "var(--text-muted)" }} />
            <h1 style={{ fontSize: 18, fontWeight: 600 }}>Swarm</h1>
          </div>
          <p style={{ fontSize: 13, color: "var(--text-secondary)" }}>
            {data?.mode || "hybrid-mesh"} · {data?.nodes.length || 0} nodes · {data?.edges.length || 0} channels
          </p>
        </div>

        {metrics && (
          <div style={{ display: "flex", gap: 10 }}>
            <StatChip label="Msg/s"     value={metrics.messages_per_sec} />
            <StatChip label="Avg lat"   value={`${metrics.avg_latency_ms}ms`} />
            <StatChip label="Channels"  value={metrics.total_channels} />
          </div>
        )}
      </div>

      {/* Graph */}
      <div
        ref={containerRef}
        className="swarm-container"
        style={{ flex: 1, minHeight: "calc(100vh - 260px)" }}
      >
        <svg ref={svgRef} width="100%" height="100%" style={{ background: "transparent" }} />
        {!data && (
          <div
            style={{
              position: "absolute",
              inset: 0,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 13,
              color: "var(--text-muted)",
            }}
          >
            Loading topology…
          </div>
        )}
      </div>

      {/* Legend */}
      <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
        {[
          { label: "Executing", status: "executing" },
          { label: "Thinking",  status: "thinking" },
          { label: "Idle",      status: "idle" },
          { label: "Error",     status: "error" },
        ].map((s) => (
          <div key={s.status} style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <span className={`status-dot status-${s.status}`} />
            <span style={{ fontSize: 12, color: "var(--text-muted)" }}>{s.label}</span>
          </div>
        ))}
        <span style={{ fontSize: 12, color: "var(--text-muted)", marginLeft: 8 }}>
          Drag nodes · scroll to zoom
        </span>
      </div>
    </div>
  );
}

function StatChip({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="metric-card" style={{ padding: "8px 14px", textAlign: "center" }}>
      <div style={{ fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 4 }}>
        {label}
      </div>
      <div style={{ fontSize: 15, fontWeight: 700, fontFamily: "var(--font-mono)" }}>
        {value}
      </div>
    </div>
  );
}
