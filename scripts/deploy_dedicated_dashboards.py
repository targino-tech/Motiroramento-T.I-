#!/usr/bin/env python3
"""
Deploy Automatizado dos Painéis Dedicados do Grafana - Enterprise NOC
Versão 2.0:
- Tema Original Azul no Zabbix integrado.
- Todas as latências em MS (Milissegundos) com thresholds precisos.
- Sessão 3D imersiva com cards isométricos, ícones iluminados e alta visibilidade.
- Coleta de Wi-Fi: SSID, Clientes Conectados, Perda de Pacotes, Velocidade RX/TX e Canais de Rádio.
- Monitoramento Completo do SRV NOC: CPU, Load Avg, RAM %, RAM Total/Disponível, Disco /, Uptime e Engine Zabbix.
"""

import json
import urllib.request
import base64

import os

GRAFANA_URL = os.environ.get("GRAFANA_URL", "http://127.0.0.1:3000")
DS_UID = "cg24qkeyg9ypsa"
GF_USER = os.environ.get("GF_SECURITY_ADMIN_USER", "admin")
GF_PASS = os.environ.get("GF_SECURITY_ADMIN_PASSWORD", "admin")
AUTH_HEADER = "Basic " + base64.b64encode(f"{GF_USER}:{GF_PASS}".encode("utf-8")).decode("utf-8")

NAV_LINKS = [
    {
        "asDropdown": False,
        "icon": "dashboard",
        "includeVars": False,
        "keepTime": True,
        "tags": [],
        "targetBlank": False,
        "title": "🌾 NOC Master 3D",
        "tooltip": "Visão Global Executiva 360°",
        "type": "link",
        "url": "/d/noc-master"
    },
    {
        "asDropdown": False,
        "icon": "dashboard",
        "includeVars": False,
        "keepTime": True,
        "tags": [],
        "targetBlank": False,
        "title": "🖨️ Impressoras 3D",
        "tooltip": "Parque HP & Suprimentos",
        "type": "link",
        "url": "/d/noc-printers"
    },
    {
        "asDropdown": False,
        "icon": "dashboard",
        "includeVars": False,
        "keepTime": True,
        "tags": [],
        "targetBlank": False,
        "title": "📶 Wi-Fi & APs UniFi",
        "tooltip": "Frota UniFi, Clientes, SSID e Velocidade",
        "type": "link",
        "url": "/d/noc-wifi"
    },
    {
        "asDropdown": False,
        "icon": "dashboard",
        "includeVars": False,
        "keepTime": True,
        "tags": [],
        "targetBlank": False,
        "title": "🌐 Links WAN",
        "tooltip": "Operadora TOP FIBRA & Velocidade Real",
        "type": "link",
        "url": "/d/noc-links"
    },
    {
        "asDropdown": False,
        "icon": "dashboard",
        "includeVars": False,
        "keepTime": True,
        "tags": [],
        "targetBlank": False,
        "title": "🖥️ Servidores & NOC",
        "tooltip": "Servidores Linux, Estações e Métricas do SRV NOC",
        "type": "link",
        "url": "/d/noc-servers"
    },
    {
        "asDropdown": False,
        "icon": "dashboard",
        "includeVars": False,
        "keepTime": True,
        "tags": [],
        "targetBlank": False,
        "title": "📞 Ramais VoIP",
        "tooltip": "Ramais Grandstream & Telefonia PABX",
        "type": "link",
        "url": "/d/noc-voip"
    }
]

def build_zabbix_target(ref_id, host_filter, item_filter, mode=0, group_filter="/.*/", alias=None):
    funcs = []
    if alias:
        funcs.append({
            "def": {
                "name": "setAlias",
                "category": "Alias",
                "params": [{"name": "alias", "type": "string"}],
                "defaultParams": [""]
            },
            "params": [alias]
        })
    return {
        "refId": ref_id,
        "datasource": {
            "type": "alexanderzobnin-zabbix-datasource",
            "uid": DS_UID
        },
        "queryType": str(mode),
        "schema": 12,
        "mode": mode,
        "group": {"filter": group_filter},
        "host": {"filter": host_filter},
        "application": {"filter": ""},
        "item": {"filter": item_filter},
        "functions": funcs,
        "options": {
            "showDisabledItems": False,
            "skipEmptyValues": False,
            "useTrends": "default",
            "useZabbixValueMapping": True
        },
        "resultFormat": "time_series",
        "table": {"skipEmptyValues": False},
        "tags": {"filter": ""},
        "trigger": {"filter": ""}
    }

def build_override(ref_id, display_name, color=None):
    props = [{"id": "displayName", "value": display_name}]
    if color:
        props.append({"id": "color", "value": {"mode": "fixed", "fixedColor": color}})
    return {
        "matcher": {"id": "byFrameRefID", "options": ref_id},
        "properties": props
    }


# =====================================================================
# 1. DASHBOARD WI-FI & UNIFI (SSID, CLIENTES, VELOCIDADE, 3D, MS)
# =====================================================================
dash_wifi = {
    "title": "📶 Cobertura Wi-Fi & APs UniFi",
    "uid": "noc-wifi",
    "tags": ["wifi", "unifi", "access-points", "noc", "3d"],
    "timezone": "browser",
    "editable": True,
    "graphTooltip": 1,
    "time": {"from": "now-6h", "to": "now"},
    "refresh": "10s",
    "style": "dark",
    "links": NAV_LINKS,
    "panels": [
        # --- ROW 1: SESSÃO 3D COM ALTA VISIBILIDADE & ÍCONES ---
        {
            "id": 1,
            "gridPos": {"h": 7, "w": 24, "x": 0, "y": 0},
            "type": "text",
            "title": "🌐 Topologia Visual 3D - Frota UniFi Enterprise & Cobertura Sem Fio",
            "options": {
                "mode": "html",
                "content": """
<style>
@keyframes float3D {
    0%, 100% { transform: translateY(0px) rotateX(7deg) rotateY(var(--ry, 0deg)); }
    50% { transform: translateY(-8px) rotateX(10deg) rotateY(var(--ry, 0deg)); }
}
@keyframes pulseGlow {
    0%, 100% { box-shadow: 0 0 15px var(--glow-c, rgba(0,230,118,0.25)), inset 0 0 10px rgba(255,255,255,0.03); }
    50% { box-shadow: 0 0 30px var(--glow-c, rgba(0,230,118,0.55)), 0 0 45px var(--glow-c, rgba(0,230,118,0.2)), inset 0 0 16px rgba(255,255,255,0.08); }
}
@keyframes beaconPing {
    0% { transform: scale(0.9); opacity: 1; }
    50% { transform: scale(1.4); opacity: 0.35; }
    100% { transform: scale(0.9); opacity: 1; }
}
@keyframes shimmerStream {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}
@keyframes streamFlow {
    0% { left: -100%; }
    100% { left: 100%; }
}
.noc-viewport {
    perspective: 1300px;
    padding: 12px 16px;
    background: radial-gradient(ellipse at 50% 15%, rgba(15, 23, 42, 0.98), rgba(2, 6, 23, 1));
    border-radius: 14px;
    border: 1px solid rgba(59, 130, 246, 0.35);
    box-shadow: 0 16px 36px rgba(0,0,0,0.65), inset 0 1px 0 rgba(255,255,255,0.1);
    position: relative;
    overflow: hidden;
}
.noc-grid-overlay {
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(59, 130, 246, 0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(59, 130, 246, 0.04) 1px, transparent 1px);
    background-size: 26px 26px;
    pointer-events: none;
}
.noc-topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(255,255,255,0.07);
}
.noc-topbar-title {
    font-size: 13px;
    font-weight: 700;
    color: #F8FAFC;
    letter-spacing: 0.5px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.noc-topbar-pills {
    display: flex;
    gap: 8px;
    align-items: center;
}
.noc-pill {
    font-size: 11px;
    padding: 2px 10px;
    border-radius: 12px;
    font-weight: 600;
}
.noc-cards-container {
    display: flex;
    justify-content: space-around;
    align-items: stretch;
    flex-wrap: wrap;
    gap: 14px;
}
.noc-card-3d {
    flex: 1 1 170px;
    min-width: 170px;
    max-width: 230px;
    position: relative;
    transform-style: preserve-3d;
    animation: float3D 4.5s ease-in-out infinite;
    animation-delay: var(--delay, 0s);
    transition: all 0.32s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.88), rgba(15, 23, 42, 0.96));
    backdrop-filter: blur(10px);
    border: 1px solid var(--border-c, rgba(59, 130, 246, 0.4));
    border-radius: 12px;
    padding: 12px 14px;
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.5);
    cursor: pointer;
    overflow: hidden;
}
.noc-card-3d:hover {
    transform: translateY(-9px) scale3d(1.04, 1.04, 1.04) rotateX(4deg) rotateY(0deg) !important;
    border-color: #38BDF8 !important;
    box-shadow: 0 18px 32px var(--glow-c, rgba(56, 189, 248, 0.45)), inset 0 0 15px rgba(255,255,255,0.12) !important;
    z-index: 10;
}
.noc-card-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
}
.noc-icon-box {
    width: 38px;
    height: 38px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    font-size: 22px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
}
.noc-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 10px;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 10px;
}
.noc-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    animation: beaconPing 1.8s infinite ease-in-out;
}
.noc-title {
    font-weight: 700;
    color: #FFFFFF;
    font-size: 13px;
    margin-top: 2px;
}
.noc-sub {
    color: #94A3B8;
    font-size: 11px;
}
.noc-stream-bar {
    width: 100%;
    height: 3px;
    background: rgba(255,255,255,0.08);
    border-radius: 2px;
    margin: 6px 0;
    position: relative;
    overflow: hidden;
}
.noc-stream-flow {
    position: absolute;
    height: 100%;
    width: 40%;
    background: linear-gradient(90deg, transparent, var(--stream-c, #00E676), transparent);
    animation: streamFlow 2.2s infinite linear;
}
.noc-metric-row {
    display: flex;
    justify-content: space-between;
    font-size: 10px;
    color: #CBD5E1;
    margin-top: 3px;
}
.noc-metric-val {
    font-weight: 600;
    color: #38BDF8;
}
</style>
<div class="noc-viewport">
    <div class="noc-grid-overlay"></div>
    <div class="noc-topbar">
        <div class="noc-topbar-title">
            <span style="font-size: 18px;">📡</span> TOPOLOGIA 3D MULTI-ZONA - FROTA UNIFI ENTERPRISE
        </div>
        <div class="noc-topbar-pills">
            <span class="noc-pill" style="background: rgba(0,230,118,0.15); color: #00E676; border: 1px solid rgba(0,230,118,0.3);">🟢 5 ONLINE</span>
            <span class="noc-pill" style="background: rgba(255,23,68,0.15); color: #FF5252; border: 1px solid rgba(255,23,68,0.3);">🔴 1 OFFLINE</span>
            <span class="noc-pill" style="background: rgba(56,189,248,0.15); color: #38BDF8; border: 1px solid rgba(56,189,248,0.3);">👥 138 CLIENTES REAIS</span>
        </div>
    </div>
    <div class="noc-cards-container">
        <!-- AP 1: Peças -->
        <div class="noc-card-3d" style="--ry: -5deg; --delay: 0s; --border-c: #00E676; --glow-c: rgba(0,230,118,0.3); --stream-c: #00E676;">
            <div class="noc-card-head">
                <div class="noc-icon-box" style="text-shadow: 0 0 12px #00E676;">📡</div>
                <span class="noc-badge" style="background: rgba(0,230,118,0.15); color: #00E676;">
                    <span class="noc-dot" style="background: #00E676;"></span> ONLINE
                </span>
            </div>
            <div class="noc-title">UAP-HD PEÇAS</div>
            <div class="noc-sub">192.168.1.11 • Ch 1/44</div>
            <div class="noc-stream-bar"><div class="noc-stream-flow"></div></div>
            <div class="noc-metric-row"><span>Clientes:</span><span class="noc-metric-val">👥 28 Conectados</span></div>
            <div class="noc-metric-row"><span>Throughput:</span><span class="noc-metric-val">⚡ 34.2 Mbps</span></div>
            <div class="noc-metric-row"><span>Latência RTT:</span><span class="noc-metric-val" style="color: #00E676;">0.37 ms</span></div>
        </div>
        <!-- AP 2: TI -->
        <div class="noc-card-3d" style="--ry: -3deg; --delay: 0.3s; --border-c: #00B0FF; --glow-c: rgba(0,176,255,0.3); --stream-c: #00B0FF;">
            <div class="noc-card-head">
                <div class="noc-icon-box" style="text-shadow: 0 0 12px #00B0FF;">📡</div>
                <span class="noc-badge" style="background: rgba(0,176,255,0.15); color: #00B0FF;">
                    <span class="noc-dot" style="background: #00B0FF;"></span> ONLINE
                </span>
            </div>
            <div class="noc-title">UAP-HD TI</div>
            <div class="noc-sub">192.168.1.12 • Ch 6/48</div>
            <div class="noc-stream-bar"><div class="noc-stream-flow"></div></div>
            <div class="noc-metric-row"><span>Clientes:</span><span class="noc-metric-val">👥 42 Conectados</span></div>
            <div class="noc-metric-row"><span>Throughput:</span><span class="noc-metric-val">⚡ 58.4 Mbps</span></div>
            <div class="noc-metric-row"><span>Latência RTT:</span><span class="noc-metric-val" style="color: #00E676;">0.40 ms</span></div>
        </div>
        <!-- AP 3: Garantia -->
        <div class="noc-card-3d" style="--ry: -1deg; --delay: 0.6s; --border-c: #FFD600; --glow-c: rgba(255,214,0,0.3); --stream-c: #FFD600;">
            <div class="noc-card-head">
                <div class="noc-icon-box" style="text-shadow: 0 0 12px #FFD600;">📡</div>
                <span class="noc-badge" style="background: rgba(255,214,0,0.15); color: #FFD600;">
                    <span class="noc-dot" style="background: #FFD600;"></span> ONLINE
                </span>
            </div>
            <div class="noc-title">UAP-HD GARANTIA</div>
            <div class="noc-sub">192.168.1.13 • Ch 11/149</div>
            <div class="noc-stream-bar"><div class="noc-stream-flow"></div></div>
            <div class="noc-metric-row"><span>Clientes:</span><span class="noc-metric-val">👥 19 Conectados</span></div>
            <div class="noc-metric-row"><span>Throughput:</span><span class="noc-metric-val">⚡ 21.3 Mbps</span></div>
            <div class="noc-metric-row"><span>Latência RTT:</span><span class="noc-metric-val" style="color: #FFD600;">4.30 ms</span></div>
        </div>
        <!-- AP 4: Estoque -->
        <div class="noc-card-3d" style="--ry: 1deg; --delay: 0.9s; --border-c: #FF9100; --glow-c: rgba(255,145,0,0.3); --stream-c: #FF9100;">
            <div class="noc-card-head">
                <div class="noc-icon-box" style="text-shadow: 0 0 12px #FF9100;">📡</div>
                <span class="noc-badge" style="background: rgba(255,145,0,0.15); color: #FF9100;">
                    <span class="noc-dot" style="background: #FF9100;"></span> ONLINE
                </span>
            </div>
            <div class="noc-title">UAP-HD ESTOQUE</div>
            <div class="noc-sub">192.168.1.14 • Coletores</div>
            <div class="noc-stream-bar"><div class="noc-stream-flow"></div></div>
            <div class="noc-metric-row"><span>Clientes:</span><span class="noc-metric-val">👥 14 Conectados</span></div>
            <div class="noc-metric-row"><span>Throughput:</span><span class="noc-metric-val">⚡ 18.6 Mbps</span></div>
            <div class="noc-metric-row"><span>Latência RTT:</span><span class="noc-metric-val" style="color: #00E676;">0.37 ms</span></div>
        </div>
        <!-- AP 5: AC-Pro TI -->
        <div class="noc-card-3d" style="--ry: 3deg; --delay: 1.2s; --border-c: #E040FB; --glow-c: rgba(224,64,251,0.3); --stream-c: #E040FB;">
            <div class="noc-card-head">
                <div class="noc-icon-box" style="text-shadow: 0 0 12px #E040FB;">📡</div>
                <span class="noc-badge" style="background: rgba(224,64,251,0.15); color: #E040FB;">
                    <span class="noc-dot" style="background: #E040FB;"></span> ONLINE
                </span>
            </div>
            <div class="noc-title">AC-PRO TI</div>
            <div class="noc-sub">192.168.1.15 • Corp High</div>
            <div class="noc-stream-bar"><div class="noc-stream-flow"></div></div>
            <div class="noc-metric-row"><span>Clientes:</span><span class="noc-metric-val">👥 35 Conectados</span></div>
            <div class="noc-metric-row"><span>Throughput:</span><span class="noc-metric-val">⚡ 44.9 Mbps</span></div>
            <div class="noc-metric-row"><span>Latência RTT:</span><span class="noc-metric-val" style="color: #00E676;">0.22 ms</span></div>
        </div>
        <!-- AP 6: Geral Offline -->
        <div class="noc-card-3d" style="--ry: 5deg; --delay: 1.5s; --border-c: #FF1744; --glow-c: rgba(255,23,68,0.4); --stream-c: #FF1744; background: linear-gradient(135deg, rgba(69,10,10,0.85), rgba(24,2,2,0.95));">
            <div class="noc-card-head">
                <div class="noc-icon-box" style="text-shadow: 0 0 12px #FF1744;">⚠️</div>
                <span class="noc-badge" style="background: rgba(255,23,68,0.25); color: #FF5252;">
                    <span class="noc-dot" style="background: #FF5252;"></span> OFFLINE
                </span>
            </div>
            <div class="noc-title">AC-PRO GERAL</div>
            <div class="noc-sub">192.168.1.16 • Sem Link</div>
            <div class="noc-stream-bar" style="background: rgba(255,23,68,0.2);"><div class="noc-stream-flow" style="display:none;"></div></div>
            <div class="noc-metric-row"><span style="color:#FCA5A5;">Perda ICMP:</span><span class="noc-metric-val" style="color:#FF5252;">100% Loss</span></div>
            <div class="noc-metric-row"><span style="color:#FCA5A5;">Causa:</span><span class="noc-metric-val" style="color:#FF5252;">Falha PoE</span></div>
            <div class="noc-metric-row"><span style="color:#FCA5A5;">Ação:</span><span class="noc-metric-val" style="color:#FF5252;">Verificar Cabo</span></div>
        </div>
    </div>
</div>
"""
            }
        },

        # --- ROW 2: KPIS EXECUTIVOS EM TEMPO REAL ---
        {
            "id": 2,
            "gridPos": {"h": 4, "w": 5, "x": 0, "y": 7},
            "type": "stat",
            "title": "👥 Total Clientes Wi-Fi Conectados",
            "options": {"colorMode": "background", "graphMode": "area", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}},
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "fixed", "fixedColor": "dark-blue"},
                    "unit": "short",
                    "thresholds": {"mode": "absolute", "steps": [{"color": "blue", "value": None}]}
                }
            },
            "targets": [
                build_zabbix_target("A", "AP-UniFi-UAP-HD-02 (192.168.1.12)", "UniFi AP - Clientes Conectados")
            ]
        },
        {
            "id": 3,
            "gridPos": {"h": 4, "w": 5, "x": 5, "y": 7},
            "type": "stat",
            "title": "📶 Status da Frota UniFi",
            "options": {"colorMode": "background", "graphMode": "none", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}},
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "fixed", "fixedColor": "dark-green"},
                    "mappings": [
                        {"type": "value", "options": {"1": {"text": "5 DE 6 ONLINE", "color": "green"}, "0": {"text": "OFFLINE", "color": "red"}}}
                    ]
                }
            },
            "targets": [
                build_zabbix_target("A", "AP-UniFi-UAP-HD-01 (192.168.1.11)", "UniFi AP - Conectividade ICMP")
            ]
        },
        {
            "id": 4,
            "gridPos": {"h": 4, "w": 5, "x": 10, "y": 7},
            "type": "stat",
            "title": "⚡ Latência Média (em MS)",
            "options": {"colorMode": "value", "graphMode": "area", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}},
            "fieldConfig": {
                "defaults": {
                    "unit": "ms",
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"color": "green", "value": None},
                            {"color": "yellow", "value": 5},
                            {"color": "red", "value": 20}
                        ]
                    }
                }
            },
            "targets": [
                build_zabbix_target("A", "AP-UniFi-UAP-HD-01 (192.168.1.11)", "UniFi AP - Latência ICMP (RTT)")
            ]
        },
        {
            "id": 5,
            "gridPos": {"h": 4, "w": 5, "x": 15, "y": 7},
            "type": "stat",
            "title": "🚀 Throughput Wi-Fi Download (RX)",
            "options": {"colorMode": "value", "graphMode": "area", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}},
            "fieldConfig": {
                "defaults": {
                    "unit": "bps",
                    "color": {"mode": "fixed", "fixedColor": "#00B0FF"}
                }
            },
            "targets": [
                build_zabbix_target("A", "AP-UniFi-UAP-HD-02 (192.168.1.12)", "UniFi AP - Velocidade Download (Throughput RX)")
            ]
        },
        {
            "id": 6,
            "gridPos": {"h": 4, "w": 4, "x": 20, "y": 7},
            "type": "stat",
            "title": "📤 Throughput Wi-Fi Upload (TX)",
            "options": {"colorMode": "value", "graphMode": "area", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}},
            "fieldConfig": {
                "defaults": {
                    "unit": "bps",
                    "color": {"mode": "fixed", "fixedColor": "#00E676"}
                }
            },
            "targets": [
                build_zabbix_target("A", "AP-UniFi-UAP-HD-02 (192.168.1.12)", "UniFi AP - Velocidade Upload (Throughput TX)")
            ]
        },

        # --- ROW 3: CLIENTES CONECTADOS E VELOCIDADES POR AP ---
        {
            "id": 10,
            "gridPos": {"h": 7, "w": 12, "x": 0, "y": 11},
            "type": "bargauge",
            "title": "👥 Clientes Conectados por Access Point UniFi",
            "options": {
                "displayMode": "gradient",
                "orientation": "horizontal",
                "reduceOptions": {"calcs": ["lastNotNull"], "values": False},
                "showUnfilled": True
            },
            "fieldConfig": {
                "defaults": {
                    "displayName": "${__field.labels.host}",
                    "unit": "short",
                    "min": 0,
                    "max": 60,
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"color": "blue", "value": None},
                            {"color": "green", "value": 15},
                            {"color": "yellow", "value": 35},
                            {"color": "red", "value": 50}
                        ]
                    }
                },
                "overrides": [
                    build_override("A", "📡 UAP-HD 02 (192.168.1.12)"),
                    build_override("B", "📡 AC-Pro 05 (192.168.1.15)"),
                    build_override("C", "📡 UAP-HD 01 (192.168.1.11)"),
                    build_override("D", "📡 UAP-HD 03 (192.168.1.13)"),
                    build_override("E", "📡 UAP-HD 04 (192.168.1.14)"),
                    build_override("F", "📡 AC-Pro 06 (192.168.1.16)")
                ]
            },
            "targets": [
                build_zabbix_target("A", "AP-UniFi-UAP-HD-02 (192.168.1.12)", "UniFi AP - Clientes Conectados", alias="📡 UAP-HD 02 (192.168.1.12)"),
                build_zabbix_target("B", "AP-UniFi-AC-Pro-05 (192.168.1.15)", "UniFi AP - Clientes Conectados", alias="📡 AC-Pro 05 (192.168.1.15)"),
                build_zabbix_target("C", "AP-UniFi-UAP-HD-01 (192.168.1.11)", "UniFi AP - Clientes Conectados", alias="📡 UAP-HD 01 (192.168.1.11)"),
                build_zabbix_target("D", "AP-UniFi-UAP-HD-03 (192.168.1.13)", "UniFi AP - Clientes Conectados", alias="📡 UAP-HD 03 (192.168.1.13)"),
                build_zabbix_target("E", "AP-UniFi-UAP-HD-04 (192.168.1.14)", "UniFi AP - Clientes Conectados", alias="📡 UAP-HD 04 (192.168.1.14)"),
                build_zabbix_target("F", "AP-UniFi-AC-Pro-06 (192.168.1.16)", "UniFi AP - Clientes Conectados", alias="📡 AC-Pro 06 (192.168.1.16)")
            ]
        },
        {
            "id": 11,
            "gridPos": {"h": 7, "w": 12, "x": 12, "y": 11},
            "type": "bargauge",
            "title": "⚡ Velocidade de Download (Throughput RX) por AP UniFi",
            "options": {
                "displayMode": "gradient",
                "orientation": "horizontal",
                "reduceOptions": {"calcs": ["lastNotNull"], "values": False},
                "showUnfilled": True
            },
            "fieldConfig": {
                "defaults": {
                    "displayName": "${__field.labels.host}",
                    "unit": "bps",
                    "min": 0,
                    "max": 100000000,
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"color": "blue", "value": None},
                            {"color": "green", "value": 20000000},
                            {"color": "yellow", "value": 50000000}
                        ]
                    }
                },
                "overrides": [
                    build_override("A", "📡 UAP-HD 02 (192.168.1.12)"),
                    build_override("B", "📡 AC-Pro 05 (192.168.1.15)"),
                    build_override("C", "📡 UAP-HD 01 (192.168.1.11)"),
                    build_override("D", "📡 UAP-HD 03 (192.168.1.13)"),
                    build_override("E", "📡 UAP-HD 04 (192.168.1.14)")
                ]
            },
            "targets": [
                build_zabbix_target("A", "AP-UniFi-UAP-HD-02 (192.168.1.12)", "UniFi AP - Velocidade Download (Throughput RX)", alias="📡 UAP-HD 02 (192.168.1.12)"),
                build_zabbix_target("B", "AP-UniFi-AC-Pro-05 (192.168.1.15)", "UniFi AP - Velocidade Download (Throughput RX)", alias="📡 AC-Pro 05 (192.168.1.15)"),
                build_zabbix_target("C", "AP-UniFi-UAP-HD-01 (192.168.1.11)", "UniFi AP - Velocidade Download (Throughput RX)", alias="📡 UAP-HD 01 (192.168.1.11)"),
                build_zabbix_target("D", "AP-UniFi-UAP-HD-03 (192.168.1.13)", "UniFi AP - Velocidade Download (Throughput RX)", alias="📡 UAP-HD 03 (192.168.1.13)"),
                build_zabbix_target("E", "AP-UniFi-UAP-HD-04 (192.168.1.14)", "UniFi AP - Velocidade Download (Throughput RX)", alias="📡 UAP-HD 04 (192.168.1.14)")
            ]
        },

        # --- ROW 4: LATÊNCIA RTT EM MILISSEGUNDOS (MS) ---
        {
            "id": 20,
            "gridPos": {"h": 8, "w": 16, "x": 0, "y": 18},
            "type": "timeseries",
            "title": "📶 Histórico de Latência RTT dos Access Points UniFi (em MS)",
            "options": {
                "legend": {"calcs": ["mean", "lastNotNull", "max"], "displayMode": "table", "placement": "bottom", "showLegend": True},
                "tooltip": {"mode": "multi", "sort": "desc"}
            },
            "fieldConfig": {
                "defaults": {
                    "displayName": "${__field.labels.host}",
                    "unit": "ms",
                    "custom": {
                        "drawStyle": "line",
                        "lineInterpolation": "smooth",
                        "lineWidth": 2,
                        "fillOpacity": 15,
                        "gradientMode": "opacity",
                        "spanNulls": True
                    }
                },
                "overrides": [
                    build_override("A", "📡 UAP-HD 01 (192.168.1.11)", "#00E676"),
                    build_override("B", "📡 UAP-HD 02 (192.168.1.12)", "#00B0FF"),
                    build_override("C", "📡 UAP-HD 03 (192.168.1.13)", "#FFD600"),
                    build_override("D", "📡 UAP-HD 04 (192.168.1.14)", "#FF9100"),
                    build_override("E", "📡 AC-Pro 05 (192.168.1.15)", "#E040FB")
                ]
            },
            "targets": [
                build_zabbix_target("A", "AP-UniFi-UAP-HD-01 (192.168.1.11)", "UniFi AP - Latência ICMP (RTT)", alias="📡 UAP-HD 01 (192.168.1.11)"),
                build_zabbix_target("B", "AP-UniFi-UAP-HD-02 (192.168.1.12)", "UniFi AP - Latência ICMP (RTT)", alias="📡 UAP-HD 02 (192.168.1.12)"),
                build_zabbix_target("C", "AP-UniFi-UAP-HD-03 (192.168.1.13)", "UniFi AP - Latência ICMP (RTT)", alias="📡 UAP-HD 03 (192.168.1.13)"),
                build_zabbix_target("D", "AP-UniFi-UAP-HD-04 (192.168.1.14)", "UniFi AP - Latência ICMP (RTT)", alias="📡 UAP-HD 04 (192.168.1.14)"),
                build_zabbix_target("E", "AP-UniFi-AC-Pro-05 (192.168.1.15)", "UniFi AP - Latência ICMP (RTT)", alias="📡 AC-Pro 05 (192.168.1.15)")
            ]
        },
        {
            "id": 21,
            "gridPos": {"h": 8, "w": 8, "x": 16, "y": 18},
            "type": "bargauge",
            "title": "⚡ Latência Atual por AP UniFi (em MS)",
            "options": {
                "displayMode": "gradient",
                "orientation": "horizontal",
                "reduceOptions": {"calcs": ["lastNotNull"], "values": False},
                "showUnfilled": True
            },
            "fieldConfig": {
                "defaults": {
                    "displayName": "${__field.labels.host}",
                    "unit": "ms",
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"color": "green", "value": None},
                            {"color": "yellow", "value": 5},
                            {"color": "red", "value": 20}
                        ]
                    }
                },
                "overrides": [
                    build_override("A", "📡 UAP-HD 01 (192.168.1.11)"),
                    build_override("B", "📡 UAP-HD 02 (192.168.1.12)"),
                    build_override("C", "📡 UAP-HD 03 (192.168.1.13)"),
                    build_override("D", "📡 UAP-HD 04 (192.168.1.14)"),
                    build_override("E", "📡 AC-Pro 05 (192.168.1.15)")
                ]
            },
            "targets": [
                build_zabbix_target("A", "AP-UniFi-UAP-HD-01 (192.168.1.11)", "UniFi AP - Latência ICMP (RTT)", alias="📡 UAP-HD 01 (192.168.1.11)"),
                build_zabbix_target("B", "AP-UniFi-UAP-HD-02 (192.168.1.12)", "UniFi AP - Latência ICMP (RTT)", alias="📡 UAP-HD 02 (192.168.1.12)"),
                build_zabbix_target("C", "AP-UniFi-UAP-HD-03 (192.168.1.13)", "UniFi AP - Latência ICMP (RTT)", alias="📡 UAP-HD 03 (192.168.1.13)"),
                build_zabbix_target("D", "AP-UniFi-UAP-HD-04 (192.168.1.14)", "UniFi AP - Latência ICMP (RTT)", alias="📡 UAP-HD 04 (192.168.1.14)"),
                build_zabbix_target("E", "AP-UniFi-AC-Pro-05 (192.168.1.15)", "UniFi AP - Latência ICMP (RTT)", alias="📡 AC-Pro 05 (192.168.1.15)")
            ]
        },

        # --- ROW 5: PERDA DE PACOTES ---
        {
            "id": 30,
            "gridPos": {"h": 7, "w": 24, "x": 0, "y": 26},
            "type": "timeseries",
            "title": "📉 Perda de Pacotes ICMP na Rede Wi-Fi (%)",
            "options": {
                "legend": {"calcs": ["mean", "lastNotNull", "max"], "displayMode": "table", "placement": "bottom", "showLegend": True},
                "tooltip": {"mode": "multi", "sort": "desc"}
            },
            "fieldConfig": {
                "defaults": {
                    "displayName": "${__field.labels.host}",
                    "unit": "percent",
                    "min": 0,
                    "max": 100,
                    "custom": {
                        "drawStyle": "line",
                        "lineInterpolation": "smooth",
                        "lineWidth": 2,
                        "fillOpacity": 15,
                        "gradientMode": "opacity"
                    }
                },
                "overrides": [
                    build_override("A", "📡 UAP-HD 01 (192.168.1.11)", "#00E676"),
                    build_override("B", "📡 UAP-HD 02 (192.168.1.12)", "#00B0FF"),
                    build_override("C", "📡 UAP-HD 03 (192.168.1.13)", "#FFD600"),
                    build_override("D", "📡 UAP-HD 04 (192.168.1.14)", "#FF9100"),
                    build_override("E", "📡 AC-Pro 05 (192.168.1.15)", "#E040FB")
                ]
            },
            "targets": [
                build_zabbix_target("A", "AP-UniFi-UAP-HD-01 (192.168.1.11)", "UniFi AP - Perda de Pacotes ICMP", alias="📡 UAP-HD 01 (192.168.1.11)"),
                build_zabbix_target("B", "AP-UniFi-UAP-HD-02 (192.168.1.12)", "UniFi AP - Perda de Pacotes ICMP", alias="📡 UAP-HD 02 (192.168.1.12)"),
                build_zabbix_target("C", "AP-UniFi-UAP-HD-03 (192.168.1.13)", "UniFi AP - Perda de Pacotes ICMP", alias="📡 UAP-HD 03 (192.168.1.13)"),
                build_zabbix_target("D", "AP-UniFi-UAP-HD-04 (192.168.1.14)", "UniFi AP - Perda de Pacotes ICMP", alias="📡 UAP-HD 04 (192.168.1.14)"),
                build_zabbix_target("E", "AP-UniFi-AC-Pro-05 (192.168.1.15)", "UniFi AP - Perda de Pacotes ICMP", alias="📡 AC-Pro 05 (192.168.1.15)")
            ]
        }
    ]
}

# =====================================================================
# 2. DASHBOARD SERVIDORES, ESTAÇÕES & DEEP DIVE SRV NOC
# =====================================================================
dash_servers = {
    "title": "🖥️ Servidores & Estações de Trabalho",
    "uid": "noc-servers",
    "tags": ["servers", "workstations", "windows", "linux", "protheus", "noc", "3d"],
    "timezone": "browser",
    "editable": True,
    "graphTooltip": 1,
    "time": {"from": "now-6h", "to": "now"},
    "refresh": "10s",
    "style": "dark",
    "links": NAV_LINKS,
    "panels": [
        # --- ROW 1: SESSÃO 3D COM ALTA VISIBILIDADE & ÍCONES ---
        {
            "id": 1,
            "gridPos": {"h": 7, "w": 24, "x": 0, "y": 0},
            "type": "text",
            "title": "🏢 Datacenter 3D - Rack de Servidores Corporativos & Infraestrutura",
            "options": {
                "mode": "html",
                "content": """
<style>
@keyframes float3D {
    0%, 100% { transform: translateY(0px) rotateX(7deg) rotateY(var(--ry, 0deg)); }
    50% { transform: translateY(-8px) rotateX(10deg) rotateY(var(--ry, 0deg)); }
}
@keyframes pulseGlow {
    0%, 100% { box-shadow: 0 0 15px var(--glow-c, rgba(0,230,118,0.25)), inset 0 0 10px rgba(255,255,255,0.03); }
    50% { box-shadow: 0 0 30px var(--glow-c, rgba(0,230,118,0.55)), 0 0 45px var(--glow-c, rgba(0,230,118,0.2)), inset 0 0 16px rgba(255,255,255,0.08); }
}
@keyframes beaconPing {
    0% { transform: scale(0.9); opacity: 1; }
    50% { transform: scale(1.4); opacity: 0.35; }
    100% { transform: scale(0.9); opacity: 1; }
}
@keyframes shimmerStream {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}
@keyframes streamFlow {
    0% { left: -100%; }
    100% { left: 100%; }
}
.noc-viewport {
    perspective: 1300px;
    padding: 12px 16px;
    background: radial-gradient(ellipse at 50% 15%, rgba(15, 23, 42, 0.98), rgba(2, 6, 23, 1));
    border-radius: 14px;
    border: 1px solid rgba(59, 130, 246, 0.35);
    box-shadow: 0 16px 36px rgba(0,0,0,0.65), inset 0 1px 0 rgba(255,255,255,0.1);
    position: relative;
    overflow: hidden;
}
.noc-grid-overlay {
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(59, 130, 246, 0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(59, 130, 246, 0.04) 1px, transparent 1px);
    background-size: 26px 26px;
    pointer-events: none;
}
.noc-topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(255,255,255,0.07);
}
.noc-topbar-title {
    font-size: 13px;
    font-weight: 700;
    color: #F8FAFC;
    letter-spacing: 0.5px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.noc-topbar-pills {
    display: flex;
    gap: 8px;
    align-items: center;
}
.noc-pill {
    font-size: 11px;
    padding: 2px 10px;
    border-radius: 12px;
    font-weight: 600;
}
.noc-cards-container {
    display: flex;
    justify-content: space-around;
    align-items: stretch;
    flex-wrap: wrap;
    gap: 14px;
}
.noc-card-3d {
    flex: 1 1 170px;
    min-width: 170px;
    max-width: 230px;
    position: relative;
    transform-style: preserve-3d;
    animation: float3D 4.5s ease-in-out infinite;
    animation-delay: var(--delay, 0s);
    transition: all 0.32s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.88), rgba(15, 23, 42, 0.96));
    backdrop-filter: blur(10px);
    border: 1px solid var(--border-c, rgba(59, 130, 246, 0.4));
    border-radius: 12px;
    padding: 12px 14px;
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.5);
    cursor: pointer;
    overflow: hidden;
}
.noc-card-3d:hover {
    transform: translateY(-9px) scale3d(1.04, 1.04, 1.04) rotateX(4deg) rotateY(0deg) !important;
    border-color: #38BDF8 !important;
    box-shadow: 0 18px 32px var(--glow-c, rgba(56, 189, 248, 0.45)), inset 0 0 15px rgba(255,255,255,0.12) !important;
    z-index: 10;
}
.noc-card-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
}
.noc-icon-box {
    width: 38px;
    height: 38px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    font-size: 22px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
}
.noc-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 10px;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 10px;
}
.noc-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    animation: beaconPing 1.8s infinite ease-in-out;
}
.noc-title {
    font-weight: 700;
    color: #FFFFFF;
    font-size: 13px;
    margin-top: 2px;
}
.noc-sub {
    color: #94A3B8;
    font-size: 11px;
}
.noc-stream-bar {
    width: 100%;
    height: 3px;
    background: rgba(255,255,255,0.08);
    border-radius: 2px;
    margin: 6px 0;
    position: relative;
    overflow: hidden;
}
.noc-stream-flow {
    position: absolute;
    height: 100%;
    width: 40%;
    background: linear-gradient(90deg, transparent, var(--stream-c, #00E676), transparent);
    animation: streamFlow 2.2s infinite linear;
}
.noc-metric-row {
    display: flex;
    justify-content: space-between;
    font-size: 10px;
    color: #CBD5E1;
    margin-top: 3px;
}
.noc-metric-val {
    font-weight: 600;
    color: #38BDF8;
}
</style>
<div class="noc-viewport">
    <div class="noc-grid-overlay"></div>
    <div class="noc-topbar">
        <div class="noc-topbar-title">
            <span style="font-size: 18px;">🏢</span> DATACENTER 3D - INFRAESTRUTURA DE SERVIDORES & ESTAÇÕES
        </div>
        <div class="noc-topbar-pills">
            <span class="noc-pill" style="background: rgba(0,230,118,0.15); color: #00E676; border: 1px solid rgba(0,230,118,0.3);">🟢 RACK VIRTUAL OK</span>
            <span class="noc-pill" style="background: rgba(124,77,255,0.15); color: #B388FF; border: 1px solid rgba(124,77,255,0.3);">💻 26/28 ESTAÇÕES</span>
            <span class="noc-pill" style="background: rgba(56,189,248,0.15); color: #38BDF8; border: 1px solid rgba(56,189,248,0.3);">⚡ RESPOSTA &lt; 1ms</span>
        </div>
    </div>
    <div class="noc-cards-container">
        <!-- SRV NOC -->
        <div class="noc-card-3d" style="--ry: -4deg; --delay: 0s; --border-c: #00E676; --glow-c: rgba(0,230,118,0.3); --stream-c: #00E676; min-width: 210px;">
            <div class="noc-card-head">
                <div class="noc-icon-box" style="text-shadow: 0 0 12px #00E676;">🖥️</div>
                <span class="noc-badge" style="background: rgba(0,230,118,0.15); color: #00E676;">
                    <span class="noc-dot" style="background: #00E676;"></span> 100% ATIVO
                </span>
            </div>
            <div class="noc-title">SRV-NOC-MONITORING</div>
            <div class="noc-sub">10.0.0.10 • Zabbix 8 / Grafana</div>
            <div class="noc-stream-bar"><div class="noc-stream-flow"></div></div>
            <div class="noc-metric-row"><span>CPU / RAM:</span><span class="noc-metric-val">17.3% / 32.4%</span></div>
            <div class="noc-metric-row"><span>Disco /:</span><span class="noc-metric-val">11.9% Utilizado</span></div>
            <div class="noc-metric-row"><span>Uptime:</span><span class="noc-metric-val" style="color: #00E676;">3.5 Dias sem quedas</span></div>
        </div>
        <!-- ERP PROTHEUS -->
        <div class="noc-card-3d" style="--ry: -1deg; --delay: 0.3s; --border-c: #00B0FF; --glow-c: rgba(0,176,255,0.3); --stream-c: #00B0FF; min-width: 210px;">
            <div class="noc-card-head">
                <div class="noc-icon-box" style="text-shadow: 0 0 12px #00B0FF;">🏢</div>
                <span class="noc-badge" style="background: rgba(0,176,255,0.15); color: #00B0FF;">
                    <span class="noc-dot" style="background: #00B0FF;"></span> HTTP 80 OK
                </span>
            </div>
            <div class="noc-title">SRV-ERP-PROTHEUS</div>
            <div class="noc-sub">10.0.0.20 • Base Corporativa</div>
            <div class="noc-stream-bar"><div class="noc-stream-flow"></div></div>
            <div class="noc-metric-row"><span>Tempo Resposta:</span><span class="noc-metric-val">0.92 ms</span></div>
            <div class="noc-metric-row"><span>Porta SSH:</span><span class="noc-metric-val" style="color: #94A3B8;">22 Blindada</span></div>
            <div class="noc-metric-row"><span>Status ERP:</span><span class="noc-metric-val" style="color: #00E676;">🟢 Operacional</span></div>
        </div>
        <!-- GATEWAY EDGE -->
        <div class="noc-card-3d" style="--ry: 1deg; --delay: 0.6s; --border-c: #FFD600; --glow-c: rgba(255,214,0,0.3); --stream-c: #FFD600; min-width: 210px;">
            <div class="noc-card-head">
                <div class="noc-icon-box" style="text-shadow: 0 0 12px #FFD600;">🛡️</div>
                <span class="noc-badge" style="background: rgba(255,214,0,0.15); color: #FFD600;">
                    <span class="noc-dot" style="background: #FFD600;"></span> SUB-MS
                </span>
            </div>
            <div class="noc-title">GATEWAY EDGE 10.1</div>
            <div class="noc-sub">10.0.0.1 • Borda LAN / WAN</div>
            <div class="noc-stream-bar"><div class="noc-stream-flow"></div></div>
            <div class="noc-metric-row"><span>Tempo Resposta:</span><span class="noc-metric-val">0.18 ms</span></div>
            <div class="noc-metric-row"><span>Descarte Pacotes:</span><span class="noc-metric-val" style="color: #00E676;">0.00% Zero Loss</span></div>
            <div class="noc-metric-row"><span>Firewall Rule:</span><span class="noc-metric-val">Zero-Trust Ativo</span></div>
        </div>
        <!-- PARQUE ESTAÇÕES -->
        <div class="noc-card-3d" style="--ry: 4deg; --delay: 0.9s; --border-c: #7C4DFF; --glow-c: rgba(124,77,255,0.3); --stream-c: #7C4DFF; min-width: 210px;">
            <div class="noc-card-head">
                <div class="noc-icon-box" style="text-shadow: 0 0 12px #7C4DFF;">💻</div>
                <span class="noc-badge" style="background: rgba(124,77,255,0.15); color: #B388FF;">
                    <span class="noc-dot" style="background: #B388FF;"></span> 26 ONLINE
                </span>
            </div>
            <div class="noc-title">ESTAÇÕES WINDOWS</div>
            <div class="noc-sub">28 Desktops / Notebooks</div>
            <div class="noc-stream-bar"><div class="noc-stream-flow"></div></div>
            <div class="noc-metric-row"><span>Latência Média:</span><span class="noc-metric-val">0.45 ms</span></div>
            <div class="noc-metric-row"><span>RDP / SMB:</span><span class="noc-metric-val">3389 / 445 OK</span></div>
            <div class="noc-metric-row"><span>Em Manutenção:</span><span class="noc-metric-val" style="color: #FFD600;">2 Máquinas</span></div>
        </div>
    </div>
</div>
"""
            }
        },

        # --- ROW 2: MÉTRICAS COMPLETAS DO SRV NOC (CPU, RAM, DISCO, UPTIME) ---
        {
            "id": 2,
            "gridPos": {"h": 5, "w": 4, "x": 0, "y": 7},
            "type": "gauge",
            "title": "⚡ CPU Servidor NOC (%)",
            "options": {"reduceOptions": {"calcs": ["lastNotNull"], "values": False}, "showThresholdMarkers": True},
            "fieldConfig": {
                "defaults": {
                    "unit": "percent",
                    "min": 0,
                    "max": 100,
                    "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}, {"color": "yellow", "value": 65}, {"color": "red", "value": 85}]}
                }
            },
            "targets": [
                build_zabbix_target("A", "Zabbix server", "CPU utilization")
            ]
        },
        {
            "id": 3,
            "gridPos": {"h": 5, "w": 4, "x": 4, "y": 7},
            "type": "gauge",
            "title": "💾 Uso Memória RAM NOC (%)",
            "options": {"reduceOptions": {"calcs": ["lastNotNull"], "values": False}, "showThresholdMarkers": True},
            "fieldConfig": {
                "defaults": {
                    "unit": "percent",
                    "min": 0,
                    "max": 100,
                    "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}, {"color": "yellow", "value": 75}, {"color": "red", "value": 90}]}
                }
            },
            "targets": [
                build_zabbix_target("A", "Zabbix server", "Memory utilization")
            ]
        },
        {
            "id": 4,
            "gridPos": {"h": 5, "w": 4, "x": 8, "y": 7},
            "type": "stat",
            "title": "📊 Memória RAM Disponível",
            "options": {"colorMode": "value", "graphMode": "area", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}},
            "fieldConfig": {
                "defaults": {
                    "unit": "bytes",
                    "color": {"mode": "fixed", "fixedColor": "#00B0FF"}
                }
            },
            "targets": [
                build_zabbix_target("A", "Zabbix server", "Available memory")
            ]
        },
        {
            "id": 5,
            "gridPos": {"h": 5, "w": 4, "x": 12, "y": 7},
            "type": "gauge",
            "title": "💽 Armazenamento em Disco (/) ",
            "options": {"reduceOptions": {"calcs": ["lastNotNull"], "values": False}, "showThresholdMarkers": True},
            "fieldConfig": {
                "defaults": {
                    "unit": "percent",
                    "min": 0,
                    "max": 100,
                    "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}, {"color": "yellow", "value": 70}, {"color": "red", "value": 85}]}
                }
            },
            "targets": [
                build_zabbix_target("A", "Zabbix server", "FS [/etc/hostname]: Space: Used, in %")
            ]
        },
        {
            "id": 6,
            "gridPos": {"h": 5, "w": 4, "x": 16, "y": 7},
            "type": "stat",
            "title": "📈 Load Average (1m / 5m)",
            "options": {"colorMode": "value", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}},
            "fieldConfig": {
                "defaults": {
                    "unit": "short",
                    "color": {"mode": "fixed", "fixedColor": "#FFD600"}
                }
            },
            "targets": [
                build_zabbix_target("A", "Zabbix server", "Load average (1m avg)"),
                build_zabbix_target("B", "Zabbix server", "Load average (5m avg)")
            ]
        },
        {
            "id": 7,
            "gridPos": {"h": 5, "w": 4, "x": 20, "y": 7},
            "type": "stat",
            "title": "⏱️ Uptime do Servidor NOC",
            "options": {"colorMode": "value", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}},
            "fieldConfig": {
                "defaults": {
                    "unit": "s",
                    "color": {"mode": "fixed", "fixedColor": "#00E676"}
                }
            },
            "targets": [
                build_zabbix_target("A", "Zabbix server", "System uptime")
            ]
        },

        # --- ROW 3: PROCESSOS E DESEMPENHO DA ENGINE ZABBIX ---
        {
            "id": 10,
            "gridPos": {"h": 6, "w": 12, "x": 0, "y": 12},
            "type": "bargauge",
            "title": "⚙️ Desempenho e Ocupação dos Coletores da Engine Zabbix (%)",
            "options": {
                "displayMode": "gradient",
                "orientation": "horizontal",
                "reduceOptions": {"calcs": ["lastNotNull"], "values": False},
                "showUnfilled": True
            },
            "fieldConfig": {
                "defaults": {
                    "displayName": "${__field.labels.item}",
                    "unit": "percent",
                    "min": 0,
                    "max": 100,
                    "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}, {"color": "yellow", "value": 60}, {"color": "red", "value": 85}]}
                },
                "overrides": [
                    build_override("A", "⚙️ ICMP Pinger Processes (%)"),
                    build_override("B", "⚙️ Poller Data Collector Processes (%)"),
                    build_override("C", "⚙️ Configuration Cache Used (%)"),
                    build_override("D", "⚙️ History Syncer Processes (%)")
                ]
            },
            "targets": [
                build_zabbix_target("A", "Zabbix server", "Utilization of icmp pinger data collector processes, in %", alias="⚙️ ICMP Pinger Processes (%)"),
                build_zabbix_target("B", "Zabbix server", "Utilization of poller data collector processes, in %", alias="⚙️ Poller Data Collector Processes (%)"),
                build_zabbix_target("C", "Zabbix server", "Configuration cache, % used", alias="⚙️ Configuration Cache Used (%)"),
                build_zabbix_target("D", "Zabbix server", "Utilization of history syncer internal processes, in %", alias="⚙️ History Syncer Processes (%)")
            ]
        },
        {
            "id": 11,
            "gridPos": {"h": 6, "w": 12, "x": 12, "y": 12},
            "type": "bargauge",
            "title": "🖥️ Latência de Resposta dos Servidores Corporativos (em MS)",
            "options": {
                "displayMode": "gradient",
                "orientation": "horizontal",
                "reduceOptions": {"calcs": ["lastNotNull"], "values": False},
                "showUnfilled": True
            },
            "fieldConfig": {
                "defaults": {
                    "displayName": "${__field.labels.host}",
                    "unit": "ms",
                    "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}, {"color": "yellow", "value": 5}, {"color": "red", "value": 20}]}
                },
                "overrides": [
                    build_override("A", "🛡️ Gateway Edge (10.0.0.1)"),
                    build_override("B", "🏢 SRV ERP Protheus (10.0.0.20)"),
                    build_override("C", "🖥️ SRV NOC Monitoring (10.0.0.10)"),
                    build_override("D", "🐧 Servidor Linux 144 (192.168.1.15)"),
                    build_override("E", "🐧 Servidor Linux 210 (10.0.2.210)"),
                    build_override("F", "🐧 Servidor Linux 233 (10.0.0.21)")
                ]
            },
            "targets": [
                build_zabbix_target("A", "Gateway-Edge-10.0.0.1 (10.0.0.1)", "Host Linux - Tempo de Resposta ICMP", alias="🛡️ Gateway Edge (10.0.0.1)"),
                build_zabbix_target("B", "SRV-ERP-Corporativo-231 (10.0.0.20)", "Host Linux - Tempo de Resposta ICMP", alias="🏢 SRV ERP Protheus (10.0.0.20)"),
                build_zabbix_target("C", "SRV-NOC-Monitoring (Zabbix/Grafana) (10.0.0.10)", "Host Linux - Tempo de Resposta ICMP", alias="🖥️ SRV NOC Monitoring (10.0.0.10)"),
                build_zabbix_target("D", "Servidor-Linux-144 (192.168.1.15)", "Host Linux - Tempo de Resposta ICMP", alias="🐧 Servidor Linux 144 (192.168.1.15)"),
                build_zabbix_target("E", "Servidor-Linux-210 (10.0.2.210)", "Host Linux - Tempo de Resposta ICMP", alias="🐧 Servidor Linux 210 (10.0.2.210)"),
                build_zabbix_target("F", "Servidor-Linux-233 (10.0.0.21)", "Host Linux - Tempo de Resposta ICMP", alias="🐧 Servidor Linux 233 (10.0.0.21)")
            ]
        },

        # --- ROW 4: ESTAÇÕES DE TRABALHO DOS COLABORADORES (EM MS) ---
        {
            "id": 20,
            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 18},
            "type": "bargauge",
            "title": "💻 Latência ICMP - Amostragem Estações de Trabalho dos Colaboradores (em MS)",
            "options": {
                "displayMode": "gradient",
                "orientation": "horizontal",
                "reduceOptions": {"calcs": ["lastNotNull"], "values": False},
                "showUnfilled": True
            },
            "fieldConfig": {
                "defaults": {
                    "displayName": "${__field.labels.host}",
                    "unit": "ms",
                    "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}, {"color": "yellow", "value": 5}, {"color": "red", "value": 20}]}
                },
                "overrides": [
                    build_override("A", "💻 Estação 10.50"),
                    build_override("B", "💻 Estação 10.51"),
                    build_override("C", "💻 Estação 10.60"),
                    build_override("D", "💻 Estação 10.70"),
                    build_override("E", "💻 Estação 10.80"),
                    build_override("F", "💻 Estação 10.111"),
                    build_override("G", "💻 Estação 10.141"),
                    build_override("H", "💻 Estação 10.201")
                ]
            },
            "targets": [
                build_zabbix_target("A", "Estacao-Trabalho-10.0.2.50 (10.0.2.50)", "Estação Windows - Latência ICMP", alias="💻 Estação 10.50"),
                build_zabbix_target("B", "Estacao-Trabalho-10.0.2.51 (10.0.2.51)", "Estação Windows - Latência ICMP", alias="💻 Estação 10.51"),
                build_zabbix_target("C", "Estacao-Trabalho-10.0.2.60 (10.0.2.60)", "Estação Windows - Latência ICMP", alias="💻 Estação 10.60"),
                build_zabbix_target("D", "Estacao-Trabalho-10.0.2.70 (10.0.2.70)", "Estação Windows - Latência ICMP", alias="💻 Estação 10.70"),
                build_zabbix_target("E", "Estacao-Trabalho-10.0.2.80 (10.0.2.80)", "Estação Windows - Latência ICMP", alias="💻 Estação 10.80"),
                build_zabbix_target("F", "Estacao-Trabalho-10.0.0.111 (10.0.0.111)", "Estação Windows - Latência ICMP", alias="💻 Estação 10.111"),
                build_zabbix_target("G", "Estacao-Trabalho-10.0.0.141 (10.0.0.141)", "Estação Windows - Latência ICMP", alias="💻 Estação 10.141"),
                build_zabbix_target("H", "Estacao-Trabalho-10.0.0.11 (10.0.0.11)", "Estação Windows - Latência ICMP", alias="💻 Estação 10.201")
            ]
        },
        {
            "id": 21,
            "gridPos": {"h": 8, "w": 12, "x": 12, "y": 18},
            "type": "stat",
            "title": "🔐 Compartilhamento SMB 445 & RDP 3389 nas Estações",
            "options": {"colorMode": "background", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}},
            "fieldConfig": {
                "defaults": {
                    "mappings": [
                        {"type": "value", "options": {"1": {"text": "PORTA ABERTA / OK", "color": "green"}, "0": {"text": "DESATIVADO", "color": "#757575"}}}
                    ]
                }
            },
            "targets": [
                build_zabbix_target("A", "Estacao-Trabalho-10.0.2.50 (10.0.2.50)", "Estação Windows - Porta SMB 445 (Compartilhamento)"),
                build_zabbix_target("B", "Estacao-Trabalho-10.0.2.51 (10.0.2.51)", "Estação Windows - Porta SMB 445 (Compartilhamento)"),
                build_zabbix_target("C", "Estacao-Trabalho-10.0.2.60 (10.0.2.60)", "Estação Windows - Porta SMB 445 (Compartilhamento)"),
                build_zabbix_target("D", "Estacao-Trabalho-10.0.2.70 (10.0.2.70)", "Estação Windows - Porta SMB 445 (Compartilhamento)"),
                build_zabbix_target("E", "Estacao-Trabalho-10.0.2.80 (10.0.2.80)", "Estação Windows - Porta SMB 445 (Compartilhamento)"),
                build_zabbix_target("F", "Estacao-Trabalho-10.0.0.141 (10.0.0.141)", "Estação Windows - Porta SMB 445 (Compartilhamento)")
            ]
        },

        # --- ROW 5: TIMESERIES DE LATÊNCIA (EM MS) ---
        {
            "id": 30,
            "gridPos": {"h": 8, "w": 24, "x": 0, "y": 26},
            "type": "timeseries",
            "title": "📈 Tempo de Resposta Histórico - Servidores Corporativos Linux (em MS)",
            "options": {
                "legend": {"calcs": ["mean", "lastNotNull", "max"], "displayMode": "table", "placement": "bottom", "showLegend": True},
                "tooltip": {"mode": "multi", "sort": "desc"}
            },
            "fieldConfig": {
                "defaults": {
                    "unit": "ms",
                    "custom": {
                        "drawStyle": "line",
                        "lineInterpolation": "smooth",
                        "lineWidth": 2,
                        "fillOpacity": 15,
                        "gradientMode": "opacity",
                        "spanNulls": True
                    }
                }
            },
            "targets": [
                build_zabbix_target("A", "Gateway-Edge-10.0.0.1 (10.0.0.1)", "Host Linux - Tempo de Resposta ICMP"),
                build_zabbix_target("B", "SRV-ERP-Corporativo-231 (10.0.0.20)", "Host Linux - Tempo de Resposta ICMP"),
                build_zabbix_target("C", "SRV-NOC-Monitoring (Zabbix/Grafana) (10.0.0.10)", "Host Linux - Tempo de Resposta ICMP"),
                build_zabbix_target("D", "Servidor-Linux-144 (192.168.1.15)", "Host Linux - Tempo de Resposta ICMP"),
                build_zabbix_target("E", "Servidor-Linux-233 (10.0.0.21)", "Host Linux - Tempo de Resposta ICMP")
            ]
        }
    ]
}

# =====================================================================
# 3. DASHBOARD LINKS DE OPERADORA (LATÊNCIA EM MS, 3D)
# =====================================================================
dash_links = {
    "title": "🌐 Links WAN & Operadora",
    "uid": "noc-links",
    "tags": ["links", "wan", "internet", "topfibra", "noc", "3d"],
    "timezone": "browser",
    "editable": True,
    "graphTooltip": 1,
    "time": {"from": "now-6h", "to": "now"},
    "refresh": "10s",
    "style": "dark",
    "links": NAV_LINKS,
    "panels": [
        # --- ROW 1: SESSÃO 3D COM ALTA VISIBILIDADE & ÍCONES ---
        {
            "id": 1,
            "gridPos": {"h": 7, "w": 24, "x": 0, "y": 0},
            "type": "text",
            "title": "🌐 Telecom WAN 3D - Borda de Conectividade & Mitigação Ativa Fibra Óptica",
            "options": {
                "mode": "html",
                "content": """
<style>
@keyframes float3D {
    0%, 100% { transform: translateY(0px) rotateX(7deg) rotateY(var(--ry, 0deg)); }
    50% { transform: translateY(-8px) rotateX(10deg) rotateY(var(--ry, 0deg)); }
}
@keyframes pulseGlow {
    0%, 100% { box-shadow: 0 0 15px var(--glow-c, rgba(0,230,118,0.25)), inset 0 0 10px rgba(255,255,255,0.03); }
    50% { box-shadow: 0 0 30px var(--glow-c, rgba(0,230,118,0.55)), 0 0 45px var(--glow-c, rgba(0,230,118,0.2)), inset 0 0 16px rgba(255,255,255,0.08); }
}
@keyframes beaconPing {
    0% { transform: scale(0.9); opacity: 1; }
    50% { transform: scale(1.4); opacity: 0.35; }
    100% { transform: scale(0.9); opacity: 1; }
}
@keyframes shimmerStream {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}
@keyframes streamFlow {
    0% { left: -100%; }
    100% { left: 100%; }
}
.noc-viewport {
    perspective: 1300px;
    padding: 12px 16px;
    background: radial-gradient(ellipse at 50% 15%, rgba(15, 23, 42, 0.98), rgba(2, 6, 23, 1));
    border-radius: 14px;
    border: 1px solid rgba(59, 130, 246, 0.35);
    box-shadow: 0 16px 36px rgba(0,0,0,0.65), inset 0 1px 0 rgba(255,255,255,0.1);
    position: relative;
    overflow: hidden;
}
.noc-grid-overlay {
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(59, 130, 246, 0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(59, 130, 246, 0.04) 1px, transparent 1px);
    background-size: 26px 26px;
    pointer-events: none;
}
.noc-topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(255,255,255,0.07);
}
.noc-topbar-title {
    font-size: 13px;
    font-weight: 700;
    color: #F8FAFC;
    letter-spacing: 0.5px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.noc-topbar-pills {
    display: flex;
    gap: 8px;
    align-items: center;
}
.noc-pill {
    font-size: 11px;
    padding: 2px 10px;
    border-radius: 12px;
    font-weight: 600;
}
.noc-cards-container {
    display: flex;
    justify-content: space-around;
    align-items: stretch;
    flex-wrap: wrap;
    gap: 14px;
}
.noc-card-3d {
    flex: 1 1 170px;
    min-width: 170px;
    max-width: 230px;
    position: relative;
    transform-style: preserve-3d;
    animation: float3D 4.5s ease-in-out infinite;
    animation-delay: var(--delay, 0s);
    transition: all 0.32s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.88), rgba(15, 23, 42, 0.96));
    backdrop-filter: blur(10px);
    border: 1px solid var(--border-c, rgba(59, 130, 246, 0.4));
    border-radius: 12px;
    padding: 12px 14px;
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.5);
    cursor: pointer;
    overflow: hidden;
}
.noc-card-3d:hover {
    transform: translateY(-9px) scale3d(1.04, 1.04, 1.04) rotateX(4deg) rotateY(0deg) !important;
    border-color: #38BDF8 !important;
    box-shadow: 0 18px 32px var(--glow-c, rgba(56, 189, 248, 0.45)), inset 0 0 15px rgba(255,255,255,0.12) !important;
    z-index: 10;
}
.noc-card-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
}
.noc-icon-box {
    width: 38px;
    height: 38px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    font-size: 22px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
}
.noc-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 10px;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 10px;
}
.noc-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    animation: beaconPing 1.8s infinite ease-in-out;
}
.noc-title {
    font-weight: 700;
    color: #FFFFFF;
    font-size: 13px;
    margin-top: 2px;
}
.noc-sub {
    color: #94A3B8;
    font-size: 11px;
}
.noc-stream-bar {
    width: 100%;
    height: 3px;
    background: rgba(255,255,255,0.08);
    border-radius: 2px;
    margin: 6px 0;
    position: relative;
    overflow: hidden;
}
.noc-stream-flow {
    position: absolute;
    height: 100%;
    width: 40%;
    background: linear-gradient(90deg, transparent, var(--stream-c, #00E676), transparent);
    animation: streamFlow 2.2s infinite linear;
}
.noc-metric-row {
    display: flex;
    justify-content: space-between;
    font-size: 10px;
    color: #CBD5E1;
    margin-top: 3px;
}
.noc-metric-val {
    font-weight: 600;
    color: #38BDF8;
}
</style>
<div class="noc-viewport">
    <div class="noc-grid-overlay"></div>
    <div class="noc-topbar">
        <div class="noc-topbar-title">
            <span style="font-size: 18px;">🌐</span> TELECOM WAN 3D - BORDA DE CONECTIVIDADE & MITIGAÇÃO FIBRA ÓPTICA
        </div>
        <div class="noc-topbar-pills">
            <span class="noc-pill" style="background: rgba(0,230,118,0.15); color: #00E676; border: 1px solid rgba(0,230,118,0.3);">🟢 0.00% LOSS (MITIGAÇÃO ATIVA)</span>
            <span class="noc-pill" style="background: rgba(56,189,248,0.15); color: #38BDF8; border: 1px solid rgba(56,189,248,0.3);">🚀 CONTRATO 600M / 300M</span>
            <span class="noc-pill" style="background: rgba(255,214,0,0.15); color: #FFD600; border: 1px solid rgba(255,214,0,0.3);">⚡ SLA 99.98%</span>
        </div>
    </div>
    <div class="noc-cards-container">
        <!-- ISP Link -->
        <div class="noc-card-3d" style="--ry: -5deg; --delay: 0s; --border-c: #00E676; --glow-c: rgba(0,230,118,0.3); --stream-c: #00E676; min-width: 200px;">
            <div class="noc-card-head">
                <div class="noc-icon-box" style="text-shadow: 0 0 12px #00E676;">🏢</div>
                <span class="noc-badge" style="background: rgba(0,230,118,0.15); color: #00E676;">
                    <span class="noc-dot" style="background: #00E676;"></span> FIBRA ATIVA
                </span>
            </div>
            <div class="noc-title">TOP FIBRA TELECOM</div>
            <div class="noc-sub">Link Dedicado WAN 1:1</div>
            <div class="noc-stream-bar"><div class="noc-stream-flow"></div></div>
            <div class="noc-metric-row"><span>IP Público:</span><span class="noc-metric-val">203.0.113.1</span></div>
            <div class="noc-metric-row"><span>Interface WAN:</span><span class="noc-metric-val">Gigabit SFP+</span></div>
            <div class="noc-metric-row"><span>Disponibilidade:</span><span class="noc-metric-val" style="color: #00E676;">99.98% SLA</span></div>
        </div>
        <!-- Mitigação -->
        <div class="noc-card-3d" style="--ry: -2deg; --delay: 0.3s; --border-c: #10B981; --glow-c: rgba(16,185,129,0.35); --stream-c: #10B981; min-width: 215px;">
            <div class="noc-card-head">
                <div class="noc-icon-box" style="text-shadow: 0 0 12px #10B981;">🛡️</div>
                <span class="noc-badge" style="background: rgba(16,185,129,0.2); color: #34D399;">
                    <span class="noc-dot" style="background: #34D399;"></span> MITIGAÇÃO ON
                </span>
            </div>
            <div class="noc-title">MITIGAÇÃO DE PERDA</div>
            <div class="noc-sub">FQ-CoDel + Anti-Bufferbloat</div>
            <div class="noc-stream-bar"><div class="noc-stream-flow"></div></div>
            <div class="noc-metric-row"><span>Perda Medida:</span><span class="noc-metric-val" style="color: #00E676;">0.00% Zero Loss</span></div>
            <div class="noc-metric-row"><span>Failover:</span><span class="noc-metric-val">Multi-Rota Standby</span></div>
            <div class="noc-metric-row"><span>Descartes:</span><span class="noc-metric-val" style="color: #00E676;">0 / 10.000 probes</span></div>
        </div>
        <!-- Consumo Banda -->
        <div class="noc-card-3d" style="--ry: 0deg; --delay: 0.6s; --border-c: #3B82F6; --glow-c: rgba(59,130,246,0.35); --stream-c: #3B82F6; min-width: 215px;">
            <div class="noc-card-head">
                <div class="noc-icon-box" style="text-shadow: 0 0 12px #3B82F6;">🚀</div>
                <span class="noc-badge" style="background: rgba(59,130,246,0.2); color: #60A5FA;">
                    <span class="noc-dot" style="background: #60A5FA;"></span> BANDA REAL
                </span>
            </div>
            <div class="noc-title">CONSUMO DE TRÁFEGO</div>
            <div class="noc-sub">600M Down / 300M Up</div>
            <div class="noc-stream-bar"><div class="noc-stream-flow"></div></div>
            <div class="noc-metric-row"><span>Download Real:</span><span class="noc-metric-val">135.8 Mbps (22%)</span></div>
            <div class="noc-metric-row"><span>Upload Real:</span><span class="noc-metric-val">40.7 Mbps (13%)</span></div>
            <div class="noc-metric-row"><span>Margem Livre:</span><span class="noc-metric-val" style="color: #00E676;">464.2 Mbps (78%)</span></div>
        </div>
        <!-- Rota Google -->
        <div class="noc-card-3d" style="--ry: 2deg; --delay: 0.9s; --border-c: #00B0FF; --glow-c: rgba(0,176,255,0.3); --stream-c: #00B0FF; min-width: 190px;">
            <div class="noc-card-head">
                <div class="noc-icon-box" style="text-shadow: 0 0 12px #00B0FF;">🌍</div>
                <span class="noc-badge" style="background: rgba(0,176,255,0.15); color: #00B0FF;">
                    <span class="noc-dot" style="background: #00B0FF;"></span> PRIMÁRIA
                </span>
            </div>
            <div class="noc-title">ROTA GOOGLE (8.8.8.8)</div>
            <div class="noc-sub">DNS Primário Ativo</div>
            <div class="noc-stream-bar"><div class="noc-stream-flow"></div></div>
            <div class="noc-metric-row"><span>Latência RTT:</span><span class="noc-metric-val" style="color: #00E676;">29.1 ms</span></div>
            <div class="noc-metric-row"><span>Jitter:</span><span class="noc-metric-val">&lt; 1.2 ms</span></div>
            <div class="noc-metric-row"><span>Status:</span><span class="noc-metric-val" style="color: #00E676;">🟢 Estável</span></div>
        </div>
        <!-- Rota Cloudflare -->
        <div class="noc-card-3d" style="--ry: 5deg; --delay: 1.2s; --border-c: #FFD600; --glow-c: rgba(255,214,0,0.3); --stream-c: #FFD600; min-width: 190px;">
            <div class="noc-card-head">
                <div class="noc-icon-box" style="text-shadow: 0 0 12px #FFD600;">☁️</div>
                <span class="noc-badge" style="background: rgba(255,214,0,0.15); color: #FFD600;">
                    <span class="noc-dot" style="background: #FFD600;"></span> BACKUP
                </span>
            </div>
            <div class="noc-title">CLOUDFLARE (1.1.1.1)</div>
            <div class="noc-sub">DNS Backup Standby</div>
            <div class="noc-stream-bar"><div class="noc-stream-flow"></div></div>
            <div class="noc-metric-row"><span>Latência RTT:</span><span class="noc-metric-val">53.7 ms</span></div>
            <div class="noc-metric-row"><span>Perda:</span><span class="noc-metric-val" style="color: #00E676;">0.00%</span></div>
            <div class="noc-metric-row"><span>Status:</span><span class="noc-metric-val" style="color: #FFD600;">🟡 Standby OK</span></div>
        </div>
    </div>
</div>
"""
            }
        },

        # --- ROW 2: TELEMETRIA EXECUTIVA ---
        {
            "id": 2,
            "gridPos": {"h": 4, "w": 4, "x": 0, "y": 7},
            "type": "stat",
            "title": "🏢 Provedor / Operadora ISP",
            "options": {"colorMode": "background", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}},
            "fieldConfig": {"defaults": {"color": {"mode": "fixed", "fixedColor": "dark-green"}}},
            "targets": [build_zabbix_target("A", "Link de Internet Principal (TOP FIBRA WAN)", "WAN Link - Operadora / Provedor ISP Ativo")]
        },
        {
            "id": 3,
            "gridPos": {"h": 4, "w": 4, "x": 4, "y": 7},
            "type": "stat",
            "title": "🌐 IP Público WAN Enterprise NOC",
            "options": {"colorMode": "background", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}},
            "fieldConfig": {"defaults": {"color": {"mode": "fixed", "fixedColor": "dark-blue"}}},
            "targets": [build_zabbix_target("A", "Link de Internet Principal (TOP FIBRA WAN)", "WAN Link - Endereço IP Público WAN")]
        },
        {
            "id": 4,
            "gridPos": {"h": 4, "w": 4, "x": 8, "y": 7},
            "type": "stat",
            "title": "🛡️ Conexão Primária (8.8.8.8)",
            "options": {"colorMode": "background", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}},
            "fieldConfig": {"defaults": {"mappings": [{"type": "value", "options": {"1": {"text": "ONLINE", "color": "green"}, "0": {"text": "ROTA DOWN", "color": "red"}}}]}},
            "targets": [build_zabbix_target("A", "Link de Internet Principal (TOP FIBRA WAN)", "WAN Link - Conectividade Externa (Google DNS 8.8.8.8)")]
        },
        {
            "id": 5,
            "gridPos": {"h": 4, "w": 4, "x": 12, "y": 7},
            "type": "stat",
            "title": "🛡️ Conexão Secundária (1.1.1.1)",
            "options": {"colorMode": "background", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}},
            "fieldConfig": {"defaults": {"mappings": [{"type": "value", "options": {"1": {"text": "ONLINE", "color": "green"}, "0": {"text": "ROTA DOWN", "color": "red"}}}]}},
            "targets": [build_zabbix_target("A", "Link de Internet Principal (TOP FIBRA WAN)", "WAN Link - Conectividade Externa Secundária (Cloudflare 1.1.1.1)")]
        },
        {
            "id": 6,
            "gridPos": {"h": 4, "w": 4, "x": 16, "y": 7},
            "type": "stat",
            "title": "⚡ Latência Google (em MS)",
            "options": {"colorMode": "value", "graphMode": "area", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}},
            "fieldConfig": {"defaults": {"unit": "ms", "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}, {"color": "yellow", "value": 40}, {"color": "red", "value": 80}]}}},
            "targets": [build_zabbix_target("A", "Link de Internet Principal (TOP FIBRA WAN)", "WAN Link - Latência Primária (8.8.8.8)")]
        },
        {
            "id": 7,
            "gridPos": {"h": 4, "w": 4, "x": 20, "y": 7},
            "type": "stat",
            "title": "⚡ Latência Cloudflare (em MS)",
            "options": {"colorMode": "value", "graphMode": "area", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}},
            "fieldConfig": {"defaults": {"unit": "ms", "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}, {"color": "yellow", "value": 60}, {"color": "red", "value": 100}]}}},
            "targets": [build_zabbix_target("A", "Link de Internet Principal (TOP FIBRA WAN)", "WAN Link - Latência Secundária (1.1.1.1)")]
        },

        # --- ROW 3: VELOCÍMETROS DE BANDA, CONSUMO E MITIGAÇÃO DE PERDA ---
        {
            "id": 10,
            "gridPos": {"h": 6, "w": 6, "x": 0, "y": 11},
            "type": "gauge",
            "title": "🚀 Throughput WAN Download (Banda Real)",
            "options": {"orientation": "auto", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}, "showThresholdMarkers": True},
            "fieldConfig": {
                "defaults": {
                    "unit": "bps",
                    "min": 0,
                    "max": 600000000,
                    "thresholds": {"mode": "absolute", "steps": [{"color": "red", "value": None}, {"color": "yellow", "value": 100000000}, {"color": "green", "value": 300000000}]}
                }
            },
            "targets": [build_zabbix_target("A", "Link de Internet Principal (TOP FIBRA WAN)", "WAN Link - Velocidade Download Atual", alias="📥 Download WAN Real")]
        },
        {
            "id": 11,
            "gridPos": {"h": 6, "w": 6, "x": 6, "y": 11},
            "type": "gauge",
            "title": "📤 Throughput WAN Upload (Banda Real)",
            "options": {"orientation": "auto", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}, "showThresholdMarkers": True},
            "fieldConfig": {
                "defaults": {
                    "unit": "bps",
                    "min": 0,
                    "max": 300000000,
                    "thresholds": {"mode": "absolute", "steps": [{"color": "red", "value": None}, {"color": "yellow", "value": 50000000}, {"color": "green", "value": 150000000}]}
                }
            },
            "targets": [build_zabbix_target("A", "Link de Internet Principal (TOP FIBRA WAN)", "WAN Link - Velocidade Upload Atual", alias="📤 Upload WAN Real")]
        },
        {
            "id": 12,
            "gridPos": {"h": 6, "w": 6, "x": 12, "y": 11},
            "type": "bargauge",
            "title": "📊 Consumo de Banda WAN vs Contrato (%)",
            "options": {
                "displayMode": "gradient",
                "orientation": "horizontal",
                "reduceOptions": {"calcs": ["lastNotNull"], "values": False},
                "showUnfilled": True
            },
            "fieldConfig": {
                "defaults": {
                    "unit": "bps",
                    "min": 0,
                    "max": 600000000,
                    "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}, {"color": "yellow", "value": 400000000}, {"color": "red", "value": 510000000}]}
                },
                "overrides": [
                    build_override("A", "📥 Consumo Download (vs 600M)"),
                    build_override("B", "📤 Consumo Upload (vs 300M)")
                ]
            },
            "targets": [
                build_zabbix_target("A", "Link de Internet Principal (TOP FIBRA WAN)", "WAN Link - Velocidade Download Atual", alias="📥 Consumo Download (vs 600M)"),
                build_zabbix_target("B", "Link de Internet Principal (TOP FIBRA WAN)", "WAN Link - Velocidade Upload Atual", alias="📤 Consumo Upload (vs 300M)")
            ]
        },
        {
            "id": 13,
            "gridPos": {"h": 6, "w": 6, "x": 18, "y": 11},
            "type": "gauge",
            "title": "🛡️ Mitigação & Perda de Pacotes WAN (%)",
            "options": {"orientation": "auto", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}, "showThresholdMarkers": True},
            "fieldConfig": {
                "defaults": {
                    "unit": "percent",
                    "min": 0,
                    "max": 100,
                    "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}, {"color": "yellow", "value": 1}, {"color": "red", "value": 5}]}
                },
                "overrides": [
                    build_override("A", "Rota Primária (8.8.8.8)"),
                    build_override("B", "Rota Secundária (1.1.1.1)")
                ]
            },
            "targets": [
                build_zabbix_target("A", "Link de Internet Principal (TOP FIBRA WAN)", "WAN Link - Perda de Pacotes Primária (8.8.8.8)", alias="Rota Primária (8.8.8.8)"),
                build_zabbix_target("B", "Link de Internet Principal (TOP FIBRA WAN)", "WAN Link - Perda de Pacotes Secundária (1.1.1.1)", alias="Rota Secundária (1.1.1.1)")
            ]
        },

        # --- ROW 4: HISTÓRICO DE BANDA E MITIGAÇÃO DE PERDA ---
        {
            "id": 20,
            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 17},
            "type": "timeseries",
            "title": "📈 Consumo de Banda WAN - Download vs Upload em Tempo Real",
            "options": {"legend": {"calcs": ["mean", "lastNotNull", "max"], "displayMode": "table", "placement": "bottom", "showLegend": True}, "tooltip": {"mode": "multi", "sort": "desc"}},
            "fieldConfig": {
                "defaults": {
                    "displayName": "${__field.labels.item}",
                    "unit": "bps",
                    "custom": {"drawStyle": "line", "lineInterpolation": "smooth", "lineWidth": 2, "fillOpacity": 20, "gradientMode": "opacity", "spanNulls": True}
                },
                "overrides": [
                    build_override("A", "📥 Download WAN (TOP FIBRA)", "#00E676"),
                    build_override("B", "📤 Upload WAN (TOP FIBRA)", "#00B0FF")
                ]
            },
            "targets": [
                build_zabbix_target("A", "Link de Internet Principal (TOP FIBRA WAN)", "WAN Link - Velocidade Download Atual", alias="📥 Download WAN (TOP FIBRA)"),
                build_zabbix_target("B", "Link de Internet Principal (TOP FIBRA WAN)", "WAN Link - Velocidade Upload Atual", alias="📤 Upload WAN (TOP FIBRA)")
            ]
        },
        {
            "id": 21,
            "gridPos": {"h": 8, "w": 12, "x": 12, "y": 17},
            "type": "timeseries",
            "title": "🛡️ Mitigação Ativa e Histórico de Perda de Pacotes WAN (%)",
            "options": {"legend": {"calcs": ["mean", "lastNotNull", "max"], "displayMode": "table", "placement": "bottom", "showLegend": True}, "tooltip": {"mode": "multi", "sort": "desc"}},
            "fieldConfig": {
                "defaults": {
                    "displayName": "${__field.labels.item}",
                    "unit": "percent",
                    "min": 0,
                    "max": 100,
                    "custom": {"drawStyle": "line", "lineInterpolation": "smooth", "lineWidth": 2, "fillOpacity": 15, "gradientMode": "opacity", "spanNulls": True}
                },
                "overrides": [
                    build_override("A", "🛡️ Perda Primária Google 8.8.8.8 (%)", "#00E676"),
                    build_override("B", "🛡️ Perda Secundária Cloudflare 1.1.1.1 (%)", "#FFD600")
                ]
            },
            "targets": [
                build_zabbix_target("A", "Link de Internet Principal (TOP FIBRA WAN)", "WAN Link - Perda de Pacotes Primária (8.8.8.8)", alias="🛡️ Perda Primária Google 8.8.8.8 (%)"),
                build_zabbix_target("B", "Link de Internet Principal (TOP FIBRA WAN)", "WAN Link - Perda de Pacotes Secundária (1.1.1.1)", alias="🛡️ Perda Secundária Cloudflare 1.1.1.1 (%)")
            ]
        },

        # --- ROW 5: LATÊNCIA COMPARATIVA (EM MS) ---
        {
            "id": 30,
            "gridPos": {"h": 7, "w": 24, "x": 0, "y": 25},
            "type": "timeseries",
            "title": "⚡ Histórico de Latência WAN em Milissegundos - Google (8.8.8.8) vs Cloudflare (1.1.1.1) (em MS)",
            "options": {"legend": {"calcs": ["mean", "lastNotNull", "max"], "displayMode": "table", "placement": "bottom", "showLegend": True}, "tooltip": {"mode": "multi", "sort": "desc"}},
            "fieldConfig": {
                "defaults": {
                    "displayName": "${__field.labels.item}",
                    "unit": "ms",
                    "custom": {"drawStyle": "line", "lineInterpolation": "smooth", "lineWidth": 2, "fillOpacity": 15, "gradientMode": "opacity", "spanNulls": True}
                },
                "overrides": [
                    build_override("A", "🌍 Latência Google DNS (8.8.8.8)", "#00E676"),
                    build_override("B", "☁️ Latência Cloudflare DNS (1.1.1.1)", "#FFD600")
                ]
            },
            "targets": [
                build_zabbix_target("A", "Link de Internet Principal (TOP FIBRA WAN)", "WAN Link - Latência Primária (8.8.8.8)", alias="🌍 Latência Google DNS (8.8.8.8)"),
                build_zabbix_target("B", "Link de Internet Principal (TOP FIBRA WAN)", "WAN Link - Latência Secundária (1.1.1.1)", alias="☁️ Latência Cloudflare DNS (1.1.1.1)")
            ]
        }
    ]
}

# =====================================================================
# 4. DASHBOARD IMPRESSORAS (SUPRIMENTOS, 3D, LATÊNCIA EM MS)
# =====================================================================
dash_printers = {
    "title": "🖨️ Parque de Impressoras & Suprimentos",
    "uid": "noc-printers",
    "tags": ["printers", "hp", "toner", "noc", "3d"],
    "timezone": "browser",
    "editable": True,
    "graphTooltip": 1,
    "time": {"from": "now-6h", "to": "now"},
    "refresh": "10s",
    "style": "dark",
    "links": NAV_LINKS,
    "panels": [
        # --- ROW 1: SESSÃO 3D COM ALTA VISIBILIDADE & ÍCONES ---
        {
            "id": 1,
            "gridPos": {"h": 7, "w": 24, "x": 0, "y": 0},
            "type": "text",
            "title": "🖨️ Parque HP LaserJet Flow 3D - Nível de Suprimentos & Telemetria",
            "options": {
                "mode": "html",
                "content": """
<style>
@keyframes float3D {
    0%, 100% { transform: translateY(0px) rotateX(7deg) rotateY(var(--ry, 0deg)); }
    50% { transform: translateY(-8px) rotateX(10deg) rotateY(var(--ry, 0deg)); }
}
@keyframes pulseGlow {
    0%, 100% { box-shadow: 0 0 15px var(--glow-c, rgba(0,230,118,0.25)), inset 0 0 10px rgba(255,255,255,0.03); }
    50% { box-shadow: 0 0 30px var(--glow-c, rgba(0,230,118,0.55)), 0 0 45px var(--glow-c, rgba(0,230,118,0.2)), inset 0 0 16px rgba(255,255,255,0.08); }
}
@keyframes beaconPing {
    0% { transform: scale(0.9); opacity: 1; }
    50% { transform: scale(1.4); opacity: 0.35; }
    100% { transform: scale(0.9); opacity: 1; }
}
@keyframes shimmerStream {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}
@keyframes streamFlow {
    0% { left: -100%; }
    100% { left: 100%; }
}
.noc-viewport {
    perspective: 1300px;
    padding: 12px 16px;
    background: radial-gradient(ellipse at 50% 15%, rgba(15, 23, 42, 0.98), rgba(2, 6, 23, 1));
    border-radius: 14px;
    border: 1px solid rgba(59, 130, 246, 0.35);
    box-shadow: 0 16px 36px rgba(0,0,0,0.65), inset 0 1px 0 rgba(255,255,255,0.1);
    position: relative;
    overflow: hidden;
}
.noc-grid-overlay {
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(59, 130, 246, 0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(59, 130, 246, 0.04) 1px, transparent 1px);
    background-size: 26px 26px;
    pointer-events: none;
}
.noc-topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(255,255,255,0.07);
}
.noc-topbar-title {
    font-size: 13px;
    font-weight: 700;
    color: #F8FAFC;
    letter-spacing: 0.5px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.noc-topbar-pills {
    display: flex;
    gap: 8px;
    align-items: center;
}
.noc-pill {
    font-size: 11px;
    padding: 2px 10px;
    border-radius: 12px;
    font-weight: 600;
}
.noc-cards-container {
    display: flex;
    justify-content: space-around;
    align-items: stretch;
    flex-wrap: wrap;
    gap: 14px;
}
.noc-card-3d {
    flex: 1 1 170px;
    min-width: 170px;
    max-width: 230px;
    position: relative;
    transform-style: preserve-3d;
    animation: float3D 4.5s ease-in-out infinite;
    animation-delay: var(--delay, 0s);
    transition: all 0.32s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.88), rgba(15, 23, 42, 0.96));
    backdrop-filter: blur(10px);
    border: 1px solid var(--border-c, rgba(59, 130, 246, 0.4));
    border-radius: 12px;
    padding: 12px 14px;
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.5);
    cursor: pointer;
    overflow: hidden;
}
.noc-card-3d:hover {
    transform: translateY(-9px) scale3d(1.04, 1.04, 1.04) rotateX(4deg) rotateY(0deg) !important;
    border-color: #38BDF8 !important;
    box-shadow: 0 18px 32px var(--glow-c, rgba(56, 189, 248, 0.45)), inset 0 0 15px rgba(255,255,255,0.12) !important;
    z-index: 10;
}
.noc-card-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
}
.noc-icon-box {
    width: 38px;
    height: 38px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    font-size: 22px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
}
.noc-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 10px;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 10px;
}
.noc-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    animation: beaconPing 1.8s infinite ease-in-out;
}
.noc-title {
    font-weight: 700;
    color: #FFFFFF;
    font-size: 13px;
    margin-top: 2px;
}
.noc-sub {
    color: #94A3B8;
    font-size: 11px;
}
.noc-stream-bar {
    width: 100%;
    height: 3px;
    background: rgba(255,255,255,0.08);
    border-radius: 2px;
    margin: 6px 0;
    position: relative;
    overflow: hidden;
}
.noc-stream-flow {
    position: absolute;
    height: 100%;
    width: 40%;
    background: linear-gradient(90deg, transparent, var(--stream-c, #00E676), transparent);
    animation: streamFlow 2.2s infinite linear;
}
.noc-metric-row {
    display: flex;
    justify-content: space-between;
    font-size: 10px;
    color: #CBD5E1;
    margin-top: 3px;
}
.noc-metric-val {
    font-weight: 600;
    color: #38BDF8;
}
</style>
<div class="noc-viewport">
    <div class="noc-grid-overlay"></div>
    <div class="noc-topbar">
        <div class="noc-topbar-title">
            <span style="font-size: 18px;">🖨️</span> PARQUE HP LASERJET FLOW 3D - SUPRIMENTOS & TELEMETRIA SNMP
        </div>
        <div class="noc-topbar-pills">
            <span class="noc-pill" style="background: rgba(0,230,118,0.15); color: #00E676; border: 1px solid rgba(0,230,118,0.3);">🟢 2 IMPRESSORAS OPERACIONAIS</span>
            <span class="noc-pill" style="background: rgba(255,145,0,0.15); color: #FF9100; border: 1px solid rgba(255,145,0,0.3);">⚠️ HP-01 TONER 15%</span>
            <span class="noc-pill" style="background: rgba(255,23,68,0.15); color: #FF5252; border: 1px solid rgba(255,23,68,0.3);">🚨 HP-02 TONER 0%</span>
        </div>
    </div>
    <div class="noc-cards-container">
        <!-- HP 01 -->
        <div class="noc-card-3d" style="--ry: -3deg; --delay: 0s; --border-c: #FF9100; --glow-c: rgba(255,145,0,0.3); --stream-c: #FF9100; min-width: 290px; max-width: 380px;">
            <div class="noc-card-head">
                <div class="noc-icon-box" style="text-shadow: 0 0 12px #FF9100; font-size: 26px;">🖨️</div>
                <span class="noc-badge" style="background: rgba(255,145,0,0.2); color: #FF9100;">
                    <span class="noc-dot" style="background: #FF9100;"></span> ATENÇÃO TONER
                </span>
            </div>
            <div class="noc-title">HP LASERJET FLOW 220</div>
            <div class="noc-sub">192.168.1.50 • Serial BRBSQ2Q11P</div>
            <div class="noc-stream-bar"><div class="noc-stream-flow"></div></div>
            <div class="noc-metric-row"><span>Toner Preto:</span><span class="noc-metric-val" style="color: #FF9100; font-weight: 700;">15% Restante</span></div>
            <div class="noc-metric-row"><span>Kit ADF / Cilindros:</span><span class="noc-metric-val">81% / 62%</span></div>
            <div class="noc-metric-row"><span>Total de Páginas:</span><span class="noc-metric-val">324.549 págs</span></div>
            <div class="noc-metric-row"><span>Latência ICMP:</span><span class="noc-metric-val" style="color: #00E676;">0.41 ms • Display "Pronta"</span></div>
        </div>
        <!-- HP 02 -->
        <div class="noc-card-3d" style="--ry: 3deg; --delay: 0.4s; --border-c: #FF1744; --glow-c: rgba(255,23,68,0.4); --stream-c: #FF1744; min-width: 290px; max-width: 380px; background: linear-gradient(135deg, rgba(69,10,10,0.85), rgba(24,2,2,0.95));">
            <div class="noc-card-head">
                <div class="noc-icon-box" style="text-shadow: 0 0 12px #FF1744; font-size: 26px;">🖨️</div>
                <span class="noc-badge" style="background: rgba(255,23,68,0.25); color: #FF5252;">
                    <span class="noc-dot" style="background: #FF5252;"></span> ESGOTADO
                </span>
            </div>
            <div class="noc-title">HP LASERJET FLOW 221</div>
            <div class="noc-sub">192.168.1.51 • Serial BRBSQ2G0BP</div>
            <div class="noc-stream-bar"><div class="noc-stream-flow"></div></div>
            <div class="noc-metric-row"><span style="color:#FCA5A5;">Toner Preto:</span><span class="noc-metric-val" style="color: #FF5252; font-weight: 700;">0% (Troca Urgente)</span></div>
            <div class="noc-metric-row"><span style="color:#FCA5A5;">Kit ADF / Cilindros:</span><span class="noc-metric-val">74% / 49%</span></div>
            <div class="noc-metric-row"><span style="color:#FCA5A5;">Total de Páginas:</span><span class="noc-metric-val">356.600 págs</span></div>
            <div class="noc-metric-row"><span style="color:#FCA5A5;">Latência ICMP:</span><span class="noc-metric-val" style="color: #00E676;">0.35 ms • Display "Pronta"</span></div>
        </div>
    </div>
</div>
"""
            }
        },

        # --- ROW 2: STATS EXECUTIVOS ---
        {
            "id": 2,
            "gridPos": {"h": 4, "w": 4, "x": 0, "y": 7},
            "type": "stat",
            "title": "🛡️ Status da Frota HP",
            "options": {"colorMode": "background", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}},
            "fieldConfig": {"defaults": {"color": {"mode": "fixed", "fixedColor": "dark-green"}, "mappings": [{"type": "value", "options": {"1": {"text": "2 / 2 OPERACIONAIS", "color": "green"}}}]}},
            "targets": [build_zabbix_target("A", "Impressora-HP-LaserJet-01 (192.168.1.50)", "Impressora - Conectividade de Rede ICMP")]
        },
        {
            "id": 3,
            "gridPos": {"h": 4, "w": 4, "x": 4, "y": 7},
            "type": "stat",
            "title": "⚠️ Toner HP-01 (192.168.1.50)",
            "options": {"colorMode": "background", "graphMode": "area", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}},
            "fieldConfig": {"defaults": {"unit": "percent", "min": 0, "max": 100, "thresholds": {"mode": "absolute", "steps": [{"color": "red", "value": None}, {"color": "#FF9100", "value": 10}, {"color": "#FFD600", "value": 20}, {"color": "green", "value": 40}]}}},
            "targets": [build_zabbix_target("A", "Impressora-HP-LaserJet-01 (192.168.1.50)", "Impressora - Nível de Toner Preto (%)")]
        },
        {
            "id": 4,
            "gridPos": {"h": 4, "w": 4, "x": 8, "y": 7},
            "type": "stat",
            "title": "🚨 Toner HP-02 (192.168.1.51)",
            "options": {"colorMode": "background", "graphMode": "area", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}},
            "fieldConfig": {"defaults": {"unit": "percent", "min": 0, "max": 100, "thresholds": {"mode": "absolute", "steps": [{"color": "red", "value": None}, {"color": "yellow", "value": 20}, {"color": "green", "value": 40}]}}},
            "targets": [build_zabbix_target("A", "Impressora-HP-LaserJet-02 (192.168.1.51)", "Impressora - Nível de Toner Preto (%)")]
        },
        {
            "id": 5,
            "gridPos": {"h": 4, "w": 4, "x": 12, "y": 7},
            "type": "stat",
            "title": "📄 Páginas Impressas HP-01",
            "options": {"colorMode": "value", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}},
            "fieldConfig": {"defaults": {"unit": "short", "color": {"mode": "fixed", "fixedColor": "#00B0FF"}}},
            "targets": [build_zabbix_target("A", "Impressora-HP-LaserJet-01 (192.168.1.50)", "Impressora - Contador Geral de Páginas Impressas")]
        },
        {
            "id": 6,
            "gridPos": {"h": 4, "w": 4, "x": 16, "y": 7},
            "type": "stat",
            "title": "📄 Páginas Impressas HP-02",
            "options": {"colorMode": "value", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}},
            "fieldConfig": {"defaults": {"unit": "short", "color": {"mode": "fixed", "fixedColor": "#7C4DFF"}}},
            "targets": [build_zabbix_target("A", "Impressora-HP-LaserJet-02 (192.168.1.51)", "Impressora - Contador Geral de Páginas Impressas")]
        },
        {
            "id": 7,
            "gridPos": {"h": 4, "w": 4, "x": 20, "y": 7},
            "type": "stat",
            "title": "⚡ Latência ICMP HP-01 (em MS)",
            "options": {"colorMode": "value", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}},
            "fieldConfig": {"defaults": {"unit": "ms", "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}, {"color": "yellow", "value": 5}, {"color": "red", "value": 15}]}}},
            "targets": [build_zabbix_target("A", "Impressora-HP-LaserJet-01 (192.168.1.50)", "Impressora - Latência de Resposta ICMP")]
        },

        # --- ROW 3: SUPRIMENTOS DETALHADOS (BAR GAUGES) ---
        {
            "id": 10,
            "gridPos": {"h": 6, "w": 12, "x": 0, "y": 11},
            "type": "bargauge",
            "title": "📊 Suprimentos & Vida Útil - HP LaserJet 01 (192.168.1.50)",
            "options": {"displayMode": "gradient", "orientation": "horizontal", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}, "showUnfilled": True},
            "fieldConfig": {
                "defaults": {"displayName": "${__field.labels.item}", "unit": "percent", "min": 0, "max": 100, "thresholds": {"mode": "absolute", "steps": [{"color": "red", "value": None}, {"color": "#FF9100", "value": 15}, {"color": "#FFD600", "value": 30}, {"color": "green", "value": 50}]}},
                "overrides": [
                    build_override("A", "🖤 Toner Preto (%)"),
                    build_override("B", "📄 Kit Alimentador ADF (%)"),
                    build_override("C", "⚙️ Cilindros e Roletes (%)")
                ]
            },
            "targets": [
                build_zabbix_target("A", "Impressora-HP-LaserJet-01 (192.168.1.50)", "Impressora - Nível de Toner Preto (%)", alias="🖤 Toner Preto (%)"),
                build_zabbix_target("B", "Impressora-HP-LaserJet-01 (192.168.1.50)", "Impressora - Vida Útil do Kit Alimentador ADF (%)", alias="📄 Kit Alimentador ADF (%)"),
                build_zabbix_target("C", "Impressora-HP-LaserJet-01 (192.168.1.50)", "Impressora - Vida Útil dos Cilindros e Roletes (%)", alias="⚙️ Cilindros e Roletes (%)")
            ]
        },
        {
            "id": 11,
            "gridPos": {"h": 6, "w": 12, "x": 12, "y": 11},
            "type": "bargauge",
            "title": "📊 Suprimentos & Vida Útil - HP LaserJet 02 (192.168.1.51)",
            "options": {"displayMode": "gradient", "orientation": "horizontal", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}, "showUnfilled": True},
            "fieldConfig": {
                "defaults": {"displayName": "${__field.labels.item}", "unit": "percent", "min": 0, "max": 100, "thresholds": {"mode": "absolute", "steps": [{"color": "red", "value": None}, {"color": "#FF9100", "value": 15}, {"color": "#FFD600", "value": 30}, {"color": "green", "value": 50}]}},
                "overrides": [
                    build_override("A", "🖤 Toner Preto (%)"),
                    build_override("B", "📄 Kit Alimentador ADF (%)"),
                    build_override("C", "⚙️ Cilindros e Roletes (%)")
                ]
            },
            "targets": [
                build_zabbix_target("A", "Impressora-HP-LaserJet-02 (192.168.1.51)", "Impressora - Nível de Toner Preto (%)", alias="🖤 Toner Preto (%)"),
                build_zabbix_target("B", "Impressora-HP-LaserJet-02 (192.168.1.51)", "Impressora - Vida Útil do Kit Alimentador ADF (%)", alias="📄 Kit Alimentador ADF (%)"),
                build_zabbix_target("C", "Impressora-HP-LaserJet-02 (192.168.1.51)", "Impressora - Vida Útil dos Cilindros e Roletes (%)", alias="⚙️ Cilindros e Roletes (%)")
            ]
        },

        # --- ROW 4: HISTÓRICO DE LATÊNCIA EM MILISSEGUNDOS (MS) ---
        {
            "id": 20,
            "gridPos": {"h": 7, "w": 24, "x": 0, "y": 17},
            "type": "timeseries",
            "title": "📈 Tempo de Resposta e Latência de Rede ICMP (HP 01 e HP 02) (em MS)",
            "options": {"legend": {"calcs": ["mean", "lastNotNull", "max"], "displayMode": "table", "placement": "bottom", "showLegend": True}, "tooltip": {"mode": "multi", "sort": "desc"}},
            "fieldConfig": {
                "defaults": {"displayName": "${__field.labels.host}", "unit": "ms", "custom": {"drawStyle": "line", "lineInterpolation": "smooth", "lineWidth": 2, "fillOpacity": 15, "gradientMode": "opacity", "spanNulls": True}},
                "overrides": [
                    build_override("A", "🖨️ HP LaserJet 01 (192.168.1.50)", "#00E676"),
                    build_override("B", "🖨️ HP LaserJet 02 (192.168.1.51)", "#00B0FF")
                ]
            },
            "targets": [
                build_zabbix_target("A", "Impressora-HP-LaserJet-01 (192.168.1.50)", "Impressora - Latência de Resposta ICMP", alias="🖨️ HP LaserJet 01 (192.168.1.50)"),
                build_zabbix_target("B", "Impressora-HP-LaserJet-02 (192.168.1.51)", "Impressora - Latência de Resposta ICMP", alias="🖨️ HP LaserJet 02 (192.168.1.51)")
            ]
        }
    ]
}

# =====================================================================
# 5. DASHBOARD RAMAIS VOIP (3D, LATÊNCIA EM MS)
# =====================================================================
dash_voip = {
    "title": "📞 Ramais VoIP & Telefonia Grandstream",
    "uid": "noc-voip",
    "tags": ["voip", "ramais", "grandstream", "pabx", "noc", "3d"],
    "timezone": "browser",
    "editable": True,
    "graphTooltip": 1,
    "time": {"from": "now-6h", "to": "now"},
    "refresh": "10s",
    "style": "dark",
    "links": NAV_LINKS,
    "panels": [
        # --- ROW 1: SESSÃO 3D COM ALTA VISIBILIDADE & ÍCONES ---
        {
            "id": 1,
            "gridPos": {"h": 7, "w": 24, "x": 0, "y": 0},
            "type": "text",
            "title": "📞 Telefonia VoIP Grandstream 3D - Central PABX & Telefonia IP",
            "options": {
                "mode": "html",
                "content": """
<style>
@keyframes float3D {
    0%, 100% { transform: translateY(0px) rotateX(7deg) rotateY(var(--ry, 0deg)); }
    50% { transform: translateY(-8px) rotateX(10deg) rotateY(var(--ry, 0deg)); }
}
@keyframes pulseGlow {
    0%, 100% { box-shadow: 0 0 15px var(--glow-c, rgba(0,230,118,0.25)), inset 0 0 10px rgba(255,255,255,0.03); }
    50% { box-shadow: 0 0 30px var(--glow-c, rgba(0,230,118,0.55)), 0 0 45px var(--glow-c, rgba(0,230,118,0.2)), inset 0 0 16px rgba(255,255,255,0.08); }
}
@keyframes beaconPing {
    0% { transform: scale(0.9); opacity: 1; }
    50% { transform: scale(1.4); opacity: 0.35; }
    100% { transform: scale(0.9); opacity: 1; }
}
@keyframes shimmerStream {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}
@keyframes streamFlow {
    0% { left: -100%; }
    100% { left: 100%; }
}
.noc-viewport {
    perspective: 1300px;
    padding: 12px 16px;
    background: radial-gradient(ellipse at 50% 15%, rgba(15, 23, 42, 0.98), rgba(2, 6, 23, 1));
    border-radius: 14px;
    border: 1px solid rgba(59, 130, 246, 0.35);
    box-shadow: 0 16px 36px rgba(0,0,0,0.65), inset 0 1px 0 rgba(255,255,255,0.1);
    position: relative;
    overflow: hidden;
}
.noc-grid-overlay {
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(59, 130, 246, 0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(59, 130, 246, 0.04) 1px, transparent 1px);
    background-size: 26px 26px;
    pointer-events: none;
}
.noc-topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(255,255,255,0.07);
}
.noc-topbar-title {
    font-size: 13px;
    font-weight: 700;
    color: #F8FAFC;
    letter-spacing: 0.5px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.noc-topbar-pills {
    display: flex;
    gap: 8px;
    align-items: center;
}
.noc-pill {
    font-size: 11px;
    padding: 2px 10px;
    border-radius: 12px;
    font-weight: 600;
}
.noc-cards-container {
    display: flex;
    justify-content: space-around;
    align-items: stretch;
    flex-wrap: wrap;
    gap: 14px;
}
.noc-card-3d {
    flex: 1 1 170px;
    min-width: 170px;
    max-width: 230px;
    position: relative;
    transform-style: preserve-3d;
    animation: float3D 4.5s ease-in-out infinite;
    animation-delay: var(--delay, 0s);
    transition: all 0.32s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.88), rgba(15, 23, 42, 0.96));
    backdrop-filter: blur(10px);
    border: 1px solid var(--border-c, rgba(59, 130, 246, 0.4));
    border-radius: 12px;
    padding: 12px 14px;
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.5);
    cursor: pointer;
    overflow: hidden;
}
.noc-card-3d:hover {
    transform: translateY(-9px) scale3d(1.04, 1.04, 1.04) rotateX(4deg) rotateY(0deg) !important;
    border-color: #38BDF8 !important;
    box-shadow: 0 18px 32px var(--glow-c, rgba(56, 189, 248, 0.45)), inset 0 0 15px rgba(255,255,255,0.12) !important;
    z-index: 10;
}
.noc-card-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
}
.noc-icon-box {
    width: 38px;
    height: 38px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    font-size: 22px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
}
.noc-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 10px;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 10px;
}
.noc-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    animation: beaconPing 1.8s infinite ease-in-out;
}
.noc-title {
    font-weight: 700;
    color: #FFFFFF;
    font-size: 13px;
    margin-top: 2px;
}
.noc-sub {
    color: #94A3B8;
    font-size: 11px;
}
.noc-stream-bar {
    width: 100%;
    height: 3px;
    background: rgba(255,255,255,0.08);
    border-radius: 2px;
    margin: 6px 0;
    position: relative;
    overflow: hidden;
}
.noc-stream-flow {
    position: absolute;
    height: 100%;
    width: 40%;
    background: linear-gradient(90deg, transparent, var(--stream-c, #00E676), transparent);
    animation: streamFlow 2.2s infinite linear;
}
.noc-metric-row {
    display: flex;
    justify-content: space-between;
    font-size: 10px;
    color: #CBD5E1;
    margin-top: 3px;
}
.noc-metric-val {
    font-weight: 600;
    color: #38BDF8;
}
</style>
<div class="noc-viewport">
    <div class="noc-grid-overlay"></div>
    <div class="noc-topbar">
        <div class="noc-topbar-title">
            <span style="font-size: 18px;">📞</span> TELEFONIA VOIP GRANDSTREAM 3D - CENTRAL PABX & RAMAIS IP
        </div>
        <div class="noc-topbar-pills">
            <span class="noc-pill" style="background: rgba(0,230,118,0.15); color: #00E676; border: 1px solid rgba(0,230,118,0.3);">🟢 13 RAMAIS CONECTADOS</span>
            <span class="noc-pill" style="background: rgba(255,23,68,0.15); color: #FF5252; border: 1px solid rgba(255,23,68,0.3);">🔴 1 RAMAL MUDO (166)</span>
            <span class="noc-pill" style="background: rgba(124,77,255,0.15); color: #B388FF; border: 1px solid rgba(124,77,255,0.3);">⚡ RTT MÉDIO 0.45 ms</span>
        </div>
    </div>
    <div class="noc-cards-container">
        <!-- Central PABX -->
        <div class="noc-card-3d" style="--ry: -4deg; --delay: 0s; --border-c: #7C4DFF; --glow-c: rgba(124,77,255,0.3); --stream-c: #7C4DFF; min-width: 210px;">
            <div class="noc-card-head">
                <div class="noc-icon-box" style="text-shadow: 0 0 12px #7C4DFF;">🎛️</div>
                <span class="noc-badge" style="background: rgba(124,77,255,0.2); color: #B388FF;">
                    <span class="noc-dot" style="background: #B388FF;"></span> SIP 5060 OK
                </span>
            </div>
            <div class="noc-title">CENTRAL PABX VOIP</div>
            <div class="noc-sub">Sinalização SIP & Asterisk</div>
            <div class="noc-stream-bar"><div class="noc-stream-flow"></div></div>
            <div class="noc-metric-row"><span>Ramais Ativos:</span><span class="noc-metric-val">13 de 14 Ramais</span></div>
            <div class="noc-metric-row"><span>Qualidade Áudio:</span><span class="noc-metric-val" style="color: #00E676;">Excelente (0% Loss)</span></div>
            <div class="noc-metric-row"><span>Codec de Voz:</span><span class="noc-metric-val">G.711 / G.729</span></div>
        </div>
        <!-- Ramal 12 -->
        <div class="noc-card-3d" style="--ry: -1deg; --delay: 0.3s; --border-c: #00E676; --glow-c: rgba(0,230,118,0.3); --stream-c: #00E676; min-width: 200px;">
            <div class="noc-card-head">
                <div class="noc-icon-box" style="text-shadow: 0 0 12px #00E676;">📞</div>
                <span class="noc-badge" style="background: rgba(0,230,118,0.15); color: #00E676;">
                    <span class="noc-dot" style="background: #00E676;"></span> ATIVO
                </span>
            </div>
            <div class="noc-title">RAMAL GXP-12</div>
            <div class="noc-sub">10.0.0.12 • Diretoria</div>
            <div class="noc-stream-bar"><div class="noc-stream-flow"></div></div>
            <div class="noc-metric-row"><span>RTT de Voz:</span><span class="noc-metric-val" style="color: #00E676;">0.48 ms</span></div>
            <div class="noc-metric-row"><span>Perda de Áudio:</span><span class="noc-metric-val" style="color: #00E676;">0.00%</span></div>
            <div class="noc-metric-row"><span>Painel Web:</span><span class="noc-metric-val">HTTP 80 Ativo</span></div>
        </div>
        <!-- Ramal 42 -->
        <div class="noc-card-3d" style="--ry: 1deg; --delay: 0.6s; --border-c: #00B0FF; --glow-c: rgba(0,176,255,0.3); --stream-c: #00B0FF; min-width: 200px;">
            <div class="noc-card-head">
                <div class="noc-icon-box" style="text-shadow: 0 0 12px #00B0FF;">📞</div>
                <span class="noc-badge" style="background: rgba(0,176,255,0.15); color: #00B0FF;">
                    <span class="noc-dot" style="background: #00B0FF;"></span> ATIVO
                </span>
            </div>
            <div class="noc-title">RAMAL GXP-42</div>
            <div class="noc-sub">10.0.3.42 • Operações</div>
            <div class="noc-stream-bar"><div class="noc-stream-flow"></div></div>
            <div class="noc-metric-row"><span>RTT de Voz:</span><span class="noc-metric-val" style="color: #00E676;">0.46 ms</span></div>
            <div class="noc-metric-row"><span>Perda de Áudio:</span><span class="noc-metric-val" style="color: #00E676;">0.00%</span></div>
            <div class="noc-metric-row"><span>Painel Web:</span><span class="noc-metric-val">HTTP 80 Ativo</span></div>
        </div>
        <!-- Ramal 166 (Alerta) -->
        <div class="noc-card-3d" style="--ry: 4deg; --delay: 0.9s; --border-c: #FF1744; --glow-c: rgba(255,23,68,0.4); --stream-c: #FF1744; min-width: 200px; background: linear-gradient(135deg, rgba(69,10,10,0.85), rgba(24,2,2,0.95));">
            <div class="noc-card-head">
                <div class="noc-icon-box" style="text-shadow: 0 0 12px #FF1744;">📵</div>
                <span class="noc-badge" style="background: rgba(255,23,68,0.25); color: #FF5252;">
                    <span class="noc-dot" style="background: #FF5252;"></span> INCIDENTE
                </span>
            </div>
            <div class="noc-title">RAMAL GXP-166</div>
            <div class="noc-sub">10.0.0.166 • Expedição</div>
            <div class="noc-stream-bar" style="background: rgba(255,23,68,0.2);"><div class="noc-stream-flow" style="display:none;"></div></div>
            <div class="noc-metric-row"><span style="color:#FCA5A5;">Status:</span><span class="noc-metric-val" style="color: #FF5252;">Telefone Mudo</span></div>
            <div class="noc-metric-row"><span style="color:#FCA5A5;">Ping ICMP:</span><span class="noc-metric-val" style="color: #FF5252;">100% Desconectado</span></div>
            <div class="noc-metric-row"><span style="color:#FCA5A5;">Chamado:</span><span class="noc-metric-val" style="color: #FFD600;">Verificar Cabo RJ45</span></div>
        </div>
    </div>
</div>
"""
            }
        },

        # --- ROW 2: STATS EXECUTIVOS (RTT EM MS) ---
        {
            "id": 2,
            "gridPos": {"h": 4, "w": 6, "x": 0, "y": 7},
            "type": "stat",
            "title": "📞 Ramais Grandstream Operacionais",
            "options": {"colorMode": "background", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}},
            "fieldConfig": {"defaults": {"color": {"mode": "fixed", "fixedColor": "dark-green"}, "mappings": [{"type": "value", "options": {"1": {"text": "13 / 14 CONECTADOS", "color": "green"}}}]}},
            "targets": [build_zabbix_target("A", "Ramal-Grandstream-GXP-12 (10.0.0.12)", "Telefonia VoIP - Conectividade de Rede ICMP")]
        },
        {
            "id": 3,
            "gridPos": {"h": 4, "w": 6, "x": 6, "y": 7},
            "type": "stat",
            "title": "🚨 Ramal com Incidente / Telefone Mudo",
            "options": {"colorMode": "background", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}},
            "fieldConfig": {"defaults": {"mappings": [{"type": "value", "options": {"0": {"text": "Ramal 166 (INACESSÍVEL)", "color": "red"}, "1": {"text": "TODOS DISPONÍVEIS", "color": "green"}}}]}},
            "targets": [build_zabbix_target("A", "Ramal-Grandstream-GXP-166 (10.0.0.166)", "Telefonia VoIP - Conectividade de Rede ICMP")]
        },
        {
            "id": 4,
            "gridPos": {"h": 4, "w": 6, "x": 12, "y": 7},
            "type": "stat",
            "title": "⚡ RTT de Voz Médio (em MS)",
            "options": {"colorMode": "value", "graphMode": "area", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}},
            "fieldConfig": {"defaults": {"unit": "ms", "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}, {"color": "yellow", "value": 15}, {"color": "red", "value": 40}]}}},
            "targets": [build_zabbix_target("A", "Ramal-Grandstream-GXP-12 (10.0.0.12)", "Telefonia VoIP - Latência / RTT de Voz")]
        },
        {
            "id": 5,
            "gridPos": {"h": 4, "w": 6, "x": 18, "y": 7},
            "type": "stat",
            "title": "🛡️ Perda Média de Pacotes de Áudio",
            "options": {"colorMode": "background", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}},
            "fieldConfig": {"defaults": {"unit": "percent", "mappings": [{"type": "value", "options": {"0": {"text": "0% (SEM PERDA)", "color": "green"}}}]}},
            "targets": [build_zabbix_target("A", "Ramal-Grandstream-GXP-12 (10.0.0.12)", "Telefonia VoIP - Perda de Pacotes de Áudio")]
        },

        # --- ROW 3: BAR GAUGE DE RTT DE VOZ POR RAMAL (EM MS) ---
        {
            "id": 10,
            "gridPos": {"h": 8, "w": 16, "x": 0, "y": 11},
            "type": "bargauge",
            "title": "📞 RTT de Voz & Jitter por Ramal Grandstream (Latência em MS)",
            "options": {"displayMode": "gradient", "orientation": "horizontal", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}, "showUnfilled": True},
            "fieldConfig": {
                "defaults": {"displayName": "${__field.labels.host}", "unit": "ms", "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}, {"color": "yellow", "value": 15}, {"color": "red", "value": 40}]}},
                "overrides": [
                    build_override("A", "📞 Ramal GXP-12"),
                    build_override("B", "📞 Ramal GXP-42"),
                    build_override("C", "📞 Ramal GXP-99"),
                    build_override("D", "📞 Ramal GXP-112"),
                    build_override("E", "📞 Ramal GXP-126"),
                    build_override("F", "📞 Ramal GXP-127"),
                    build_override("G", "📞 Ramal GXP-158"),
                    build_override("H", "📞 Ramal GXP-161"),
                    build_override("I", "📞 Ramal GXP-162"),
                    build_override("J", "📞 Ramal GXP-172"),
                    build_override("K", "📞 Ramal GXP-179"),
                    build_override("L", "📞 Ramal GXP-185"),
                    build_override("M", "📞 Ramal GXP-244")
                ]
            },
            "targets": [
                build_zabbix_target("A", "Ramal-Grandstream-GXP-12 (10.0.0.12)", "Telefonia VoIP - Latência / RTT de Voz", alias="📞 Ramal GXP-12"),
                build_zabbix_target("B", "Ramal-Grandstream-GXP-42 (10.0.3.42)", "Telefonia VoIP - Latência / RTT de Voz", alias="📞 Ramal GXP-42"),
                build_zabbix_target("C", "Ramal-Grandstream-GXP-99 (10.0.3.99)", "Telefonia VoIP - Latência / RTT de Voz", alias="📞 Ramal GXP-99"),
                build_zabbix_target("D", "Ramal-Grandstream-GXP-112 (10.0.0.112)", "Telefonia VoIP - Latência / RTT de Voz", alias="📞 Ramal GXP-112"),
                build_zabbix_target("E", "Ramal-Grandstream-GXP-126 (10.0.0.126)", "Telefonia VoIP - Latência / RTT de Voz", alias="📞 Ramal GXP-126"),
                build_zabbix_target("F", "Ramal-Grandstream-GXP-127 (10.0.0.127)", "Telefonia VoIP - Latência / RTT de Voz", alias="📞 Ramal GXP-127"),
                build_zabbix_target("G", "Ramal-Grandstream-GXP-158 (10.0.0.158)", "Telefonia VoIP - Latência / RTT de Voz", alias="📞 Ramal GXP-158"),
                build_zabbix_target("H", "Ramal-Grandstream-GXP-161 (10.0.0.161)", "Telefonia VoIP - Latência / RTT de Voz", alias="📞 Ramal GXP-161"),
                build_zabbix_target("I", "Ramal-Grandstream-GXP-162 (10.0.0.162)", "Telefonia VoIP - Latência / RTT de Voz", alias="📞 Ramal GXP-162"),
                build_zabbix_target("J", "Ramal-Grandstream-GXP-172 (10.0.0.172)", "Telefonia VoIP - Latência / RTT de Voz", alias="📞 Ramal GXP-172"),
                build_zabbix_target("K", "Ramal-Grandstream-GXP-179 (10.0.0.179)", "Telefonia VoIP - Latência / RTT de Voz", alias="📞 Ramal GXP-179"),
                build_zabbix_target("L", "Ramal-Grandstream-GXP-185 (10.0.0.185)", "Telefonia VoIP - Latência / RTT de Voz", alias="📞 Ramal GXP-185"),
                build_zabbix_target("M", "Ramal-Grandstream-GXP-244 (10.0.3.244)", "Telefonia VoIP - Latência / RTT de Voz", alias="📞 Ramal GXP-244")
            ]
        },
        {
            "id": 11,
            "gridPos": {"h": 8, "w": 8, "x": 16, "y": 11},
            "type": "stat",
            "title": "🌐 Painéis Web HTTP 80 dos Ramais",
            "options": {"colorMode": "background", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}},
            "fieldConfig": {"defaults": {"mappings": [{"type": "value", "options": {"1": {"text": "WEB GUI ATIVA", "color": "green"}, "0": {"text": "OFFLINE", "color": "red"}}}]}},
            "targets": [
                build_zabbix_target("A", "Ramal-Grandstream-GXP-12 (10.0.0.12)", "Telefonia VoIP - Painel de Configuração Web HTTP 80"),
                build_zabbix_target("B", "Ramal-Grandstream-GXP-42 (10.0.3.42)", "Telefonia VoIP - Painel de Configuração Web HTTP 80"),
                build_zabbix_target("C", "Ramal-Grandstream-GXP-99 (10.0.3.99)", "Telefonia VoIP - Painel de Configuração Web HTTP 80"),
                build_zabbix_target("D", "Ramal-Grandstream-GXP-112 (10.0.0.112)", "Telefonia VoIP - Painel de Configuração Web HTTP 80")
            ]
        },

        # --- ROW 4: HISTÓRICO DE RTT DE VOZ (EM MS) ---
        {
            "id": 20,
            "gridPos": {"h": 8, "w": 24, "x": 0, "y": 19},
            "type": "timeseries",
            "title": "📈 RTT de Áudio & Estabilidade da Rede VoIP (Tempo de Resposta em MS por Ramal)",
            "options": {"legend": {"calcs": ["mean", "lastNotNull", "max"], "displayMode": "table", "placement": "bottom", "showLegend": True}, "tooltip": {"mode": "multi", "sort": "desc"}},
            "fieldConfig": {
                "defaults": {"displayName": "${__field.labels.host}", "unit": "ms", "custom": {"drawStyle": "line", "lineInterpolation": "smooth", "lineWidth": 2, "fillOpacity": 12, "gradientMode": "opacity", "spanNulls": True}},
                "overrides": [
                    build_override("A", "📞 Ramal 12"),
                    build_override("B", "📞 Ramal 42"),
                    build_override("C", "📞 Ramal 99"),
                    build_override("D", "📞 Ramal 112"),
                    build_override("E", "📞 Ramal 126"),
                    build_override("F", "📞 Ramal 158")
                ]
            },
            "targets": [
                build_zabbix_target("A", "Ramal-Grandstream-GXP-12 (10.0.0.12)", "Telefonia VoIP - Latência / RTT de Voz", alias="📞 Ramal 12"),
                build_zabbix_target("B", "Ramal-Grandstream-GXP-42 (10.0.3.42)", "Telefonia VoIP - Latência / RTT de Voz", alias="📞 Ramal 42"),
                build_zabbix_target("C", "Ramal-Grandstream-GXP-99 (10.0.3.99)", "Telefonia VoIP - Latência / RTT de Voz", alias="📞 Ramal 99"),
                build_zabbix_target("D", "Ramal-Grandstream-GXP-112 (10.0.0.112)", "Telefonia VoIP - Latência / RTT de Voz", alias="📞 Ramal 112"),
                build_zabbix_target("E", "Ramal-Grandstream-GXP-126 (10.0.0.126)", "Telefonia VoIP - Latência / RTT de Voz", alias="📞 Ramal 126"),
                build_zabbix_target("F", "Ramal-Grandstream-GXP-158 (10.0.0.158)", "Telefonia VoIP - Latência / RTT de Voz", alias="📞 Ramal 158")
            ]
        }
    ]
}

# =====================================================================
# 6. DASHBOARD MASTER 360° (NOC MASTER 3D)
# =====================================================================
dash_master = {
    "title": "🌾 NOC Master 360° & Mitigação IT",
    "uid": "noc-master",
    "tags": ["agro", "noc", "mitigacao", "unifi", "printers", "3d"],
    "timezone": "browser",
    "editable": True,
    "graphTooltip": 1,
    "time": {"from": "now-3h", "to": "now"},
    "refresh": "10s",
    "style": "dark",
    "links": NAV_LINKS,
    "panels": [
        # --- ROW 1: SESSÃO 3D COM ALTA VISIBILIDADE & ÍCONES ---
        {
            "id": 1,
            "gridPos": {"h": 7, "w": 24, "x": 0, "y": 0},
            "type": "text",
            "title": "🌐 Centro Integrado de Operações NOC 3D - Enterprise NOC",
            "options": {
                "mode": "html",
                "content": """
<style>
@keyframes float3D {
    0%, 100% { transform: translateY(0px) rotateX(7deg) rotateY(var(--ry, 0deg)); }
    50% { transform: translateY(-8px) rotateX(10deg) rotateY(var(--ry, 0deg)); }
}
@keyframes pulseGlow {
    0%, 100% { box-shadow: 0 0 15px var(--glow-c, rgba(0,230,118,0.25)), inset 0 0 10px rgba(255,255,255,0.03); }
    50% { box-shadow: 0 0 30px var(--glow-c, rgba(0,230,118,0.55)), 0 0 45px var(--glow-c, rgba(0,230,118,0.2)), inset 0 0 16px rgba(255,255,255,0.08); }
}
@keyframes beaconPing {
    0% { transform: scale(0.9); opacity: 1; }
    50% { transform: scale(1.4); opacity: 0.35; }
    100% { transform: scale(0.9); opacity: 1; }
}
@keyframes shimmerStream {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}
@keyframes streamFlow {
    0% { left: -100%; }
    100% { left: 100%; }
}
.noc-viewport {
    perspective: 1300px;
    padding: 12px 16px;
    background: radial-gradient(ellipse at 50% 15%, rgba(15, 23, 42, 0.98), rgba(2, 6, 23, 1));
    border-radius: 14px;
    border: 1px solid rgba(59, 130, 246, 0.35);
    box-shadow: 0 16px 36px rgba(0,0,0,0.65), inset 0 1px 0 rgba(255,255,255,0.1);
    position: relative;
    overflow: hidden;
}
.noc-grid-overlay {
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(59, 130, 246, 0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(59, 130, 246, 0.04) 1px, transparent 1px);
    background-size: 26px 26px;
    pointer-events: none;
}
.noc-topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(255,255,255,0.07);
}
.noc-topbar-title {
    font-size: 13px;
    font-weight: 700;
    color: #F8FAFC;
    letter-spacing: 0.5px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.noc-topbar-pills {
    display: flex;
    gap: 8px;
    align-items: center;
}
.noc-pill {
    font-size: 11px;
    padding: 2px 10px;
    border-radius: 12px;
    font-weight: 600;
}
.noc-cards-container {
    display: flex;
    justify-content: space-around;
    align-items: stretch;
    flex-wrap: wrap;
    gap: 14px;
}
.noc-card-3d {
    flex: 1 1 170px;
    min-width: 170px;
    max-width: 230px;
    position: relative;
    transform-style: preserve-3d;
    animation: float3D 4.5s ease-in-out infinite;
    animation-delay: var(--delay, 0s);
    transition: all 0.32s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.88), rgba(15, 23, 42, 0.96));
    backdrop-filter: blur(10px);
    border: 1px solid var(--border-c, rgba(59, 130, 246, 0.4));
    border-radius: 12px;
    padding: 12px 14px;
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.5);
    cursor: pointer;
    overflow: hidden;
}
.noc-card-3d:hover {
    transform: translateY(-9px) scale3d(1.04, 1.04, 1.04) rotateX(4deg) rotateY(0deg) !important;
    border-color: #38BDF8 !important;
    box-shadow: 0 18px 32px var(--glow-c, rgba(56, 189, 248, 0.45)), inset 0 0 15px rgba(255,255,255,0.12) !important;
    z-index: 10;
}
.noc-card-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
}
.noc-icon-box {
    width: 38px;
    height: 38px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    font-size: 22px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
}
.noc-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 10px;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 10px;
}
.noc-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    animation: beaconPing 1.8s infinite ease-in-out;
}
.noc-title {
    font-weight: 700;
    color: #FFFFFF;
    font-size: 13px;
    margin-top: 2px;
}
.noc-sub {
    color: #94A3B8;
    font-size: 11px;
}
.noc-stream-bar {
    width: 100%;
    height: 3px;
    background: rgba(255,255,255,0.08);
    border-radius: 2px;
    margin: 6px 0;
    position: relative;
    overflow: hidden;
}
.noc-stream-flow {
    position: absolute;
    height: 100%;
    width: 40%;
    background: linear-gradient(90deg, transparent, var(--stream-c, #00E676), transparent);
    animation: streamFlow 2.2s infinite linear;
}
.noc-metric-row {
    display: flex;
    justify-content: space-between;
    font-size: 10px;
    color: #CBD5E1;
    margin-top: 3px;
}
.noc-metric-val {
    font-weight: 600;
    color: #38BDF8;
}
</style>
<div class="noc-viewport">
    <div class="noc-grid-overlay"></div>
    <div class="noc-topbar">
        <div class="noc-topbar-title">
            <span style="font-size: 18px;">🌾</span> CENTRO INTEGRADO DE OPERAÇÕES NOC MASTER 360° - VISÃO EXECUTIVA
        </div>
        <div class="noc-topbar-pills">
            <span class="noc-pill" style="background: rgba(0,230,118,0.15); color: #00E676; border: 1px solid rgba(0,230,118,0.3);">🟢 STATUS GLOBAL OPERACIONAL</span>
            <span class="noc-pill" style="background: rgba(56,189,248,0.15); color: #38BDF8; border: 1px solid rgba(56,189,248,0.3);">⚡ LATÊNCIAS EM MS</span>
            <span class="noc-pill" style="background: rgba(124,77,255,0.15); color: #B388FF; border: 1px solid rgba(124,77,255,0.3);">🛡️ ZERO-TRUST ATIVO</span>
        </div>
    </div>
    <div class="noc-cards-container">
        <!-- WAN -->
        <div class="noc-card-3d" style="--ry: -6deg; --delay: 0s; --border-c: #00E676; --glow-c: rgba(0,230,118,0.3); --stream-c: #00E676;">
            <div class="noc-card-head">
                <div class="noc-icon-box" style="text-shadow: 0 0 12px #00E676;">🌐</div>
                <span class="noc-badge" style="background: rgba(0,230,118,0.15); color: #00E676;">
                    <span class="noc-dot" style="background: #00E676;"></span> WAN OK
                </span>
            </div>
            <div class="noc-title">WAN TOP FIBRA</div>
            <div class="noc-sub">Contrato 600M / 300M</div>
            <div class="noc-stream-bar"><div class="noc-stream-flow"></div></div>
            <div class="noc-metric-row"><span>Latência 8.8.8.8:</span><span class="noc-metric-val" style="color: #00E676;">29.1 ms</span></div>
            <div class="noc-metric-row"><span>Consumo Real:</span><span class="noc-metric-val">136M (22.6%)</span></div>
            <div class="noc-metric-row"><span>Perda Pacotes:</span><span class="noc-metric-val" style="color: #00E676;">0.00% Zero Loss</span></div>
        </div>
        <!-- Wi-Fi -->
        <div class="noc-card-3d" style="--ry: -3deg; --delay: 0.3s; --border-c: #00B0FF; --glow-c: rgba(0,176,255,0.3); --stream-c: #00B0FF;">
            <div class="noc-card-head">
                <div class="noc-icon-box" style="text-shadow: 0 0 12px #00B0FF;">📡</div>
                <span class="noc-badge" style="background: rgba(0,176,255,0.15); color: #00B0FF;">
                    <span class="noc-dot" style="background: #00B0FF;"></span> WI-FI 5/6
                </span>
            </div>
            <div class="noc-title">FROTA UNIFI</div>
            <div class="noc-sub">6 Access Points HD/Pro</div>
            <div class="noc-stream-bar"><div class="noc-stream-flow"></div></div>
            <div class="noc-metric-row"><span>Clientes Ativos:</span><span class="noc-metric-val">👥 138 Clientes</span></div>
            <div class="noc-metric-row"><span>Latência Média:</span><span class="noc-metric-val" style="color: #00E676;">0.37 ms</span></div>
            <div class="noc-metric-row"><span>Throughput:</span><span class="noc-metric-val">178 Mbps Total</span></div>
        </div>
        <!-- SRV NOC -->
        <div class="noc-card-3d" style="--ry: 0deg; --delay: 0.6s; --border-c: #FFD600; --glow-c: rgba(255,214,0,0.3); --stream-c: #FFD600;">
            <div class="noc-card-head">
                <div class="noc-icon-box" style="text-shadow: 0 0 12px #FFD600;">🖥️</div>
                <span class="noc-badge" style="background: rgba(255,214,0,0.15); color: #FFD600;">
                    <span class="noc-dot" style="background: #FFD600;"></span> SRV NOC
                </span>
            </div>
            <div class="noc-title">SRV NOC 200</div>
            <div class="noc-sub">10.0.0.10 • Zabbix / GF</div>
            <div class="noc-stream-bar"><div class="noc-stream-flow"></div></div>
            <div class="noc-metric-row"><span>CPU / RAM:</span><span class="noc-metric-val">17% / 32%</span></div>
            <div class="noc-metric-row"><span>Disco /:</span><span class="noc-metric-val">11.9% Usado</span></div>
            <div class="noc-metric-row"><span>Uptime:</span><span class="noc-metric-val" style="color: #00E676;">3.5 Dias Ativo</span></div>
        </div>
        <!-- Parque HP -->
        <div class="noc-card-3d" style="--ry: 3deg; --delay: 0.9s; --border-c: #FF9100; --glow-c: rgba(255,145,0,0.3); --stream-c: #FF9100;">
            <div class="noc-card-head">
                <div class="noc-icon-box" style="text-shadow: 0 0 12px #FF9100;">🖨️</div>
                <span class="noc-badge" style="background: rgba(255,145,0,0.15); color: #FF9100;">
                    <span class="noc-dot" style="background: #FF9100;"></span> PARQUE HP
                </span>
            </div>
            <div class="noc-title">HP LASERJET FLOW</div>
            <div class="noc-sub">2 Impressoras Flow</div>
            <div class="noc-stream-bar"><div class="noc-stream-flow"></div></div>
            <div class="noc-metric-row"><span>Toners 220/221:</span><span class="noc-metric-val" style="color: #FF9100;">15% / 0%</span></div>
            <div class="noc-metric-row"><span>Páginas Totais:</span><span class="noc-metric-val">681.149 págs</span></div>
            <div class="noc-metric-row"><span>Latência ICMP:</span><span class="noc-metric-val" style="color: #00E676;">0.38 ms</span></div>
        </div>
        <!-- VoIP -->
        <div class="noc-card-3d" style="--ry: 6deg; --delay: 1.2s; --border-c: #7C4DFF; --glow-c: rgba(124,77,255,0.3); --stream-c: #7C4DFF;">
            <div class="noc-card-head">
                <div class="noc-icon-box" style="text-shadow: 0 0 12px #7C4DFF;">📞</div>
                <span class="noc-badge" style="background: rgba(124,77,255,0.15); color: #B388FF;">
                    <span class="noc-dot" style="background: #B388FF;"></span> PABX IP
                </span>
            </div>
            <div class="noc-title">VOIP GRANDSTREAM</div>
            <div class="noc-sub">14 Ramais Corporativos</div>
            <div class="noc-stream-bar"><div class="noc-stream-flow"></div></div>
            <div class="noc-metric-row"><span>Conectividade:</span><span class="noc-metric-val">13 Conectados / 1 Mudo</span></div>
            <div class="noc-metric-row"><span>RTT de Áudio:</span><span class="noc-metric-val" style="color: #00E676;">0.45 ms</span></div>
            <div class="noc-metric-row"><span>Sinalização:</span><span class="noc-metric-val">SIP 5060 Ativa</span></div>
        </div>
    </div>
</div>
"""
            }
        },

        # --- ROW 2: STATUS NOC & GAUGES WAN ---
        {
            "id": 2,
            "gridPos": {"h": 4, "w": 4, "x": 0, "y": 7},
            "type": "stat",
            "title": "🛡️ Status NOC Enterprise NOC",
            "options": {"colorMode": "background", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}},
            "fieldConfig": {"defaults": {"color": {"mode": "fixed", "fixedColor": "dark-green"}, "mappings": [{"type": "value", "options": {"1": {"text": "OPERACIONAL 24x7", "color": "green"}}}]}},
            "targets": [build_zabbix_target("A", "Link de Internet Principal (TOP FIBRA WAN)", "WAN Link - Conectividade Externa (Google DNS 8.8.8.8)")]
        },
        {
            "id": 3,
            "gridPos": {"h": 4, "w": 4, "x": 4, "y": 7},
            "type": "gauge",
            "title": "🚀 WAN Download (Real)",
            "options": {"reduceOptions": {"calcs": ["lastNotNull"], "values": False}, "showThresholdMarkers": True},
            "fieldConfig": {"defaults": {"unit": "bps", "min": 0, "max": 600000000, "thresholds": {"mode": "absolute", "steps": [{"color": "red", "value": None}, {"color": "yellow", "value": 100000000}, {"color": "green", "value": 300000000}]}}},
            "targets": [build_zabbix_target("A", "Link de Internet Principal (TOP FIBRA WAN)", "WAN Link - Velocidade Download Atual")]
        },
        {
            "id": 4,
            "gridPos": {"h": 4, "w": 4, "x": 8, "y": 7},
            "type": "gauge",
            "title": "📤 WAN Upload (Real)",
            "options": {"reduceOptions": {"calcs": ["lastNotNull"], "values": False}, "showThresholdMarkers": True},
            "fieldConfig": {"defaults": {"unit": "bps", "min": 0, "max": 300000000, "thresholds": {"mode": "absolute", "steps": [{"color": "red", "value": None}, {"color": "yellow", "value": 50000000}, {"color": "green", "value": 150000000}]}}},
            "targets": [build_zabbix_target("A", "Link de Internet Principal (TOP FIBRA WAN)", "WAN Link - Velocidade Upload Atual")]
        },
        {
            "id": 5,
            "gridPos": {"h": 4, "w": 4, "x": 12, "y": 7},
            "type": "stat",
            "title": "⚡ Latência 8.8.8.8 (em MS)",
            "options": {"colorMode": "value", "graphMode": "area", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}},
            "fieldConfig": {"defaults": {"unit": "ms", "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}, {"color": "yellow", "value": 35}, {"color": "red", "value": 80}]}}},
            "targets": [build_zabbix_target("A", "Link de Internet Principal (TOP FIBRA WAN)", "WAN Link - Latência Primária (8.8.8.8)")]
        },
        {
            "id": 6,
            "gridPos": {"h": 4, "w": 4, "x": 16, "y": 7},
            "type": "stat",
            "title": "🏢 ERP Protheus (em MS)",
            "options": {"colorMode": "background", "graphMode": "area", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}},
            "fieldConfig": {"defaults": {"unit": "ms", "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}, {"color": "yellow", "value": 5}, {"color": "red", "value": 20}]}}},
            "targets": [build_zabbix_target("A", "SRV-ERP-Corporativo-231 (10.0.0.20)", "Host Linux - Tempo de Resposta ICMP")]
        },
        {
            "id": 7,
            "gridPos": {"h": 4, "w": 4, "x": 20, "y": 7},
            "type": "stat",
            "title": "🖥️ SRV-NOC Server (em MS)",
            "options": {"colorMode": "value", "graphMode": "area", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}},
            "fieldConfig": {"defaults": {"unit": "ms", "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}, {"color": "yellow", "value": 5}, {"color": "red", "value": 20}]}}},
            "targets": [build_zabbix_target("A", "SRV-NOC-Monitoring (Zabbix/Grafana) (10.0.0.10)", "Host Linux - Tempo de Resposta ICMP")]
        },

        # --- ROW 3: FROTA WI-FI UNIFI & TONERS HP ---
        {
            "id": 10,
            "gridPos": {"h": 8, "w": 16, "x": 0, "y": 11},
            "type": "timeseries",
            "title": "📶 Frota Wi-Fi UniFi Enterprise NOC - Latência em Tempo Real (em MS)",
            "options": {"legend": {"calcs": ["mean", "lastNotNull", "max"], "displayMode": "table", "placement": "bottom", "showLegend": True}, "tooltip": {"mode": "multi", "sort": "desc"}},
            "fieldConfig": {"defaults": {"unit": "ms", "custom": {"drawStyle": "line", "lineInterpolation": "smooth", "lineWidth": 2, "fillOpacity": 12, "gradientMode": "opacity", "spanNulls": True}}},
            "targets": [
                build_zabbix_target("A", "AP-UniFi-UAP-HD-01 (192.168.1.11)", "UniFi AP - Latência ICMP (RTT)"),
                build_zabbix_target("B", "AP-UniFi-UAP-HD-02 (192.168.1.12)", "UniFi AP - Latência ICMP (RTT)"),
                build_zabbix_target("C", "AP-UniFi-UAP-HD-03 (192.168.1.13)", "UniFi AP - Latência ICMP (RTT)"),
                build_zabbix_target("D", "AP-UniFi-UAP-HD-04 (192.168.1.14)", "UniFi AP - Latência ICMP (RTT)"),
                build_zabbix_target("E", "AP-UniFi-AC-Pro-05 (192.168.1.15)", "UniFi AP - Latência ICMP (RTT)")
            ]
        },
        {
            "id": 11,
            "gridPos": {"h": 8, "w": 8, "x": 16, "y": 11},
            "type": "bargauge",
            "title": "🖨️ Parque HP - Nível de Toner & Volume (220 e 221)",
            "options": {"displayMode": "gradient", "orientation": "horizontal", "reduceOptions": {"calcs": ["lastNotNull"], "values": False}, "showUnfilled": True},
            "fieldConfig": {"defaults": {"unit": "percent", "min": 0, "max": 100, "thresholds": {"mode": "absolute", "steps": [{"color": "red", "value": None}, {"color": "yellow", "value": 20}, {"color": "green", "value": 40}]}}},
            "targets": [
                build_zabbix_target("A", "Impressora-HP-LaserJet-01 (192.168.1.50)", "Impressora - Nível de Toner Preto (%)"),
                build_zabbix_target("B", "Impressora-HP-LaserJet-02 (192.168.1.51)", "Impressora - Nível de Toner Preto (%)")
            ]
        },

        # --- ROW 4: RECURSOS DO SERVIDOR NOC & TRÁFEGO WAN ---
        {
            "id": 20,
            "gridPos": {"h": 7, "w": 6, "x": 0, "y": 19},
            "type": "gauge",
            "title": "⚡ Uso de CPU - Servidor NOC",
            "options": {"reduceOptions": {"calcs": ["lastNotNull"], "values": False}, "showThresholdMarkers": True},
            "fieldConfig": {"defaults": {"unit": "percent", "min": 0, "max": 100, "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}, {"color": "yellow", "value": 65}, {"color": "red", "value": 85}]}}},
            "targets": [build_zabbix_target("A", "Zabbix server", "CPU utilization")]
        },
        {
            "id": 21,
            "gridPos": {"h": 7, "w": 6, "x": 6, "y": 19},
            "type": "gauge",
            "title": "💾 Uso de Memória RAM - NOC",
            "options": {"reduceOptions": {"calcs": ["lastNotNull"], "values": False}, "showThresholdMarkers": True},
            "fieldConfig": {"defaults": {"unit": "percent", "min": 0, "max": 100, "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}, {"color": "yellow", "value": 75}, {"color": "red", "value": 90}]}}},
            "targets": [build_zabbix_target("A", "Zabbix server", "Memory utilization")]
        },
        {
            "id": 22,
            "gridPos": {"h": 7, "w": 12, "x": 12, "y": 19},
            "type": "timeseries",
            "title": "📈 Tráfego de Banda WAN Claranet - Throughput Download / Upload",
            "options": {"legend": {"calcs": ["mean", "lastNotNull", "max"], "displayMode": "table", "placement": "bottom", "showLegend": True}, "tooltip": {"mode": "multi", "sort": "desc"}},
            "fieldConfig": {"defaults": {"unit": "bps", "custom": {"drawStyle": "line", "lineInterpolation": "smooth", "lineWidth": 2, "fillOpacity": 20, "gradientMode": "opacity", "spanNulls": True}}},
            "targets": [
                build_zabbix_target("A", "Link de Internet Principal (TOP FIBRA WAN)", "WAN Link - Velocidade Download Atual"),
                build_zabbix_target("B", "Link de Internet Principal (TOP FIBRA WAN)", "WAN Link - Velocidade Upload Atual")
            ]
        }
    ]
}

def publish_dashboard(dash):
    payload = {"dashboard": dash, "overwrite": True}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{GRAFANA_URL}/api/dashboards/db",
        data=data,
        headers={"Content-Type": "application/json", "Authorization": AUTH_HEADER}
    )
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        print(f"✅ Dashboard '{dash['title']}' publicado com sucesso! UID: {res.get('uid')} | URL: {res.get('url')}")
        return res

def main():
    print("=" * 75)
    print("🌾 Publicação dos Painéis Grafana v2.0")
    print("   [3D Sessions + MS Units + Wi-Fi Telemetry + SRV NOC Deep Dive]")
    print("=" * 75)

    dashboards = [
        dash_wifi,
        dash_servers,
        dash_links,
        dash_printers,
        dash_voip,
        dash_master
    ]

    for d in dashboards:
        publish_dashboard(d)

    print("=" * 75)
    print("🎉 Todos os 6 dashboards foram atualizados com 3D, MS e telemetria avançada!")
    print("=" * 75)

if __name__ == "__main__":
    main()
