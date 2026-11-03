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
                "content": """<style>
@keyframes pulse-glow-green { 0%, 100% { box-shadow: 0 0 15px rgba(0,230,118,0.25), inset 0 0 10px rgba(0,230,118,0.1); } 50% { box-shadow: 0 0 28px rgba(0,230,118,0.6), inset 0 0 18px rgba(0,230,118,0.25); } }
@keyframes pulse-glow-blue { 0%, 100% { box-shadow: 0 0 15px rgba(0,176,255,0.25), inset 0 0 10px rgba(0,176,255,0.1); } 50% { box-shadow: 0 0 28px rgba(0,176,255,0.6), inset 0 0 18px rgba(0,176,255,0.25); } }
@keyframes pulse-glow-amber { 0%, 100% { box-shadow: 0 0 15px rgba(255,214,0,0.25), inset 0 0 10px rgba(255,214,0,0.1); } 50% { box-shadow: 0 0 28px rgba(255,214,0,0.6), inset 0 0 18px rgba(255,214,0,0.25); } }
@keyframes pulse-glow-purple { 0%, 100% { box-shadow: 0 0 15px rgba(168,85,247,0.25), inset 0 0 10px rgba(168,85,247,0.1); } 50% { box-shadow: 0 0 28px rgba(168,85,247,0.6), inset 0 0 18px rgba(168,85,247,0.25); } }
@keyframes pulse-glow-red { 0%, 100% { box-shadow: 0 0 15px rgba(255,23,68,0.35), inset 0 0 10px rgba(255,23,68,0.15); } 50% { box-shadow: 0 0 30px rgba(255,23,68,0.8), inset 0 0 20px rgba(255,23,68,0.3); } }
@keyframes float3d { 0%, 100% { transform: translateY(0px) rotateX(6deg) rotateY(var(--ry, 0deg)); } 50% { transform: translateY(-7px) rotateX(8deg) rotateY(var(--ry, 0deg)); } }
@keyframes radarSweep { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
@keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
@keyframes pulseDot { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.4); opacity: 0.6; } }

.noc-stage-3d {
    perspective: 1400px;
    padding: 16px 14px 18px;
    background: radial-gradient(circle at 50% 20%, rgba(30, 41, 59, 0.75), rgba(15, 23, 42, 0.92) 50%, rgba(2, 6, 23, 0.98) 100%);
    border-radius: 16px;
    border: 1px solid rgba(59, 130, 246, 0.28);
    box-shadow: 0 20px 45px -10px rgba(0, 0, 0, 0.8), inset 0 1px 1px rgba(255,255,255,0.15);
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(12px);
}
.noc-stage-3d::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(56, 189, 248, 0.7), transparent);
}
.noc-grid-cards {
    display: flex;
    justify-content: space-around;
    align-items: stretch;
    flex-wrap: wrap;
    gap: 16px;
    transform-style: preserve-3d;
}
.card-3d-interactive {
    transform-style: preserve-3d;
    transition: transform 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.35s ease, border-color 0.35s ease;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-radius: 14px;
    padding: 14px 16px;
    min-width: 175px;
    text-align: center;
    position: relative;
    cursor: pointer;
    animation: float3d 5s ease-in-out infinite;
}
.card-3d-interactive:hover {
    transform: translateY(-12px) scale(1.04) rotateX(0deg) rotateY(0deg) !important;
    z-index: 10;
}
.card-green {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.14), rgba(15, 23, 42, 0.92) 75%);
    border: 1px solid rgba(0, 230, 118, 0.55);
    box-shadow: 0 12px 28px -5px rgba(0, 230, 118, 0.25);
    animation: float3d 5.5s ease-in-out infinite, pulse-glow-green 4s infinite ease-in-out;
}
.card-blue {
    background: linear-gradient(135deg, rgba(14, 165, 233, 0.14), rgba(15, 23, 42, 0.92) 75%);
    border: 1px solid rgba(0, 176, 255, 0.55);
    box-shadow: 0 12px 28px -5px rgba(0, 176, 255, 0.25);
    animation: float3d 5.2s ease-in-out infinite 0.4s, pulse-glow-blue 4s infinite ease-in-out 0.5s;
}
.card-amber {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.14), rgba(15, 23, 42, 0.92) 75%);
    border: 1px solid rgba(255, 214, 0, 0.55);
    box-shadow: 0 12px 28px -5px rgba(255, 214, 0, 0.25);
    animation: float3d 5.8s ease-in-out infinite 0.8s, pulse-glow-amber 4s infinite ease-in-out 1s;
}
.card-purple {
    background: linear-gradient(135deg, rgba(168, 85, 247, 0.14), rgba(15, 23, 42, 0.92) 75%);
    border: 1px solid rgba(168, 85, 247, 0.55);
    box-shadow: 0 12px 28px -5px rgba(168, 85, 247, 0.25);
    animation: float3d 6s ease-in-out infinite 1.2s, pulse-glow-purple 4s infinite ease-in-out 1.5s;
}
.card-red {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.22), rgba(30, 10, 15, 0.95) 75%);
    border: 1px solid rgba(255, 23, 68, 0.65);
    box-shadow: 0 12px 28px -5px rgba(255, 23, 68, 0.35);
    animation: float3d 4.8s ease-in-out infinite 1.5s, pulse-glow-red 3s infinite ease-in-out;
}
.card-icon-3d {
    font-size: 32px;
    margin-bottom: 4px;
    display: inline-block;
    filter: drop-shadow(0 4px 10px rgba(0,0,0,0.6));
    transition: transform 0.3s;
}
.card-3d-interactive:hover .card-icon-3d {
    transform: scale(1.22) translateZ(25px);
}
.card-title {
    font-weight: 800;
    font-size: 13px;
    letter-spacing: 0.5px;
    color: #FFFFFF;
    text-transform: uppercase;
    margin-bottom: 2px;
}
.card-subtitle {
    color: #94A3B8;
    font-size: 11px;
    font-family: monospace;
}
.badge-pill {
    margin: 8px auto 6px;
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 10px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 0.3px;
}
.live-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    display: inline-block;
    animation: pulseDot 1.6s infinite ease-in-out;
}
.live-dot-green { background: #00E676; box-shadow: 0 0 8px #00E676; }
.live-dot-blue { background: #00B0FF; box-shadow: 0 0 8px #00B0FF; }
.live-dot-amber { background: #FFD600; box-shadow: 0 0 8px #FFD600; }
.live-dot-purple { background: #A855F7; box-shadow: 0 0 8px #A855F7; }
.live-dot-red { background: #FF1744; box-shadow: 0 0 8px #FF1744; }

.badge-green { background: rgba(0, 230, 118, 0.16); color: #00E676; border: 1px solid rgba(0, 230, 118, 0.3); }
.badge-blue { background: rgba(0, 176, 255, 0.16); color: #00B0FF; border: 1px solid rgba(0, 176, 255, 0.3); }
.badge-amber { background: rgba(255, 214, 0, 0.16); color: #FFD600; border: 1px solid rgba(255, 214, 0, 0.3); }
.badge-purple { background: rgba(168, 85, 247, 0.16); color: #C084FC; border: 1px solid rgba(168, 85, 247, 0.3); }
.badge-red { background: rgba(255, 23, 68, 0.22); color: #FF5252; border: 1px solid rgba(255, 23, 68, 0.4); }

.card-info-row {
    font-size: 10.5px;
    color: #CBD5E1;
    margin-top: 3px;
    display: flex;
    justify-content: center;
    gap: 6px;
}
.card-highlight {
    font-size: 11px;
    color: #38BDF8;
    font-weight: 600;
    margin-top: 4px;
}
.cyber-bar {
    width: 100%;
    height: 4px;
    background: rgba(255,255,255,0.08);
    border-radius: 4px;
    overflow: hidden;
    margin-top: 8px;
}
.cyber-bar-fill {
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, #00E676, #00B0FF);
}
</style>
<div class="noc-stage-3d">
    <div class="noc-grid-cards">
        <!-- Card 3D 1: AP Peças -->
        <div class="card-3d-interactive card-green" style="--ry: -4deg;">
            <div class="card-icon-3d" style="text-shadow: 0 0 16px #00E676;">📡</div>
            <div class="card-title">UAP-HD PEÇAS</div>
            <div class="card-subtitle">192.168.1.11</div>
            <div class="badge-pill badge-green"><span class="live-dot live-dot-green"></span> 28 Clientes</div>
            <div class="card-highlight">SSID: Enterprise-Agro</div>
            <div class="card-info-row"><span>⚡ 34.2 Mbps</span><span>•</span><span>0.37 ms</span></div>
            <div class="cyber-bar"><div class="cyber-bar-fill" style="width: 48%; background: linear-gradient(90deg,#00E676,#38BDF8);"></div></div>
        </div>
        <!-- Card 3D 2: AP TI -->
        <div class="card-3d-interactive card-blue" style="--ry: -2deg;">
            <div class="card-icon-3d" style="text-shadow: 0 0 16px #00B0FF;">📡</div>
            <div class="card-title">UAP-HD TI</div>
            <div class="card-subtitle">192.168.1.12</div>
            <div class="badge-pill badge-blue"><span class="live-dot live-dot-blue"></span> 42 Clientes</div>
            <div class="card-highlight">SSID: Enterprise-Corp</div>
            <div class="card-info-row"><span>⚡ 58.4 Mbps</span><span>•</span><span>0.40 ms</span></div>
            <div class="cyber-bar"><div class="cyber-bar-fill" style="width: 72%; background: linear-gradient(90deg,#00B0FF,#818CF8);"></div></div>
        </div>
        <!-- Card 3D 3: AP Garantia -->
        <div class="card-3d-interactive card-amber" style="--ry: 0deg;">
            <div class="card-icon-3d" style="text-shadow: 0 0 16px #FFD600;">📡</div>
            <div class="card-title">UAP-HD GARANTIA</div>
            <div class="card-subtitle">192.168.1.13</div>
            <div class="badge-pill badge-amber"><span class="live-dot live-dot-amber"></span> 19 Clientes</div>
            <div class="card-highlight">SSID: Enterprise-Agro</div>
            <div class="card-info-row"><span>⚡ 21.3 Mbps</span><span>•</span><span>4.30 ms</span></div>
            <div class="cyber-bar"><div class="cyber-bar-fill" style="width: 35%; background: linear-gradient(90deg,#FFD600,#F59E0B);"></div></div>
        </div>
        <!-- Card 3D 4: AP Estoque -->
        <div class="card-3d-interactive card-purple" style="--ry: 2deg;">
            <div class="card-icon-3d" style="text-shadow: 0 0 16px #A855F7;">📡</div>
            <div class="card-title">UAP-HD ESTOQUE</div>
            <div class="card-subtitle">192.168.1.14</div>
            <div class="badge-pill badge-purple"><span class="live-dot live-dot-purple"></span> 14 Clientes</div>
            <div class="card-highlight">SSID: Coletores</div>
            <div class="card-info-row"><span>⚡ 18.6 Mbps</span><span>•</span><span>0.37 ms</span></div>
            <div class="cyber-bar"><div class="cyber-bar-fill" style="width: 25%; background: linear-gradient(90deg,#A855F7,#EC4899);"></div></div>
        </div>
        <!-- Card 3D 5: AP AC-Pro TI -->
        <div class="card-3d-interactive card-blue" style="--ry: 4deg;">
            <div class="card-icon-3d" style="text-shadow: 0 0 16px #38BDF8;">📡</div>
            <div class="card-title">AC-PRO TI</div>
            <div class="card-subtitle">192.168.1.15</div>
            <div class="badge-pill badge-blue"><span class="live-dot live-dot-blue"></span> 35 Clientes</div>
            <div class="card-highlight">SSID: Enterprise-Corp</div>
            <div class="card-info-row"><span>⚡ 44.9 Mbps</span><span>•</span><span>0.22 ms</span></div>
            <div class="cyber-bar"><div class="cyber-bar-fill" style="width: 60%; background: linear-gradient(90deg,#38BDF8,#00E676);"></div></div>
        </div>
        <!-- Card 3D 6: AP AC-Pro Geral (Offline) -->
        <div class="card-3d-interactive card-red" style="--ry: 6deg;">
            <div class="card-icon-3d" style="text-shadow: 0 0 16px #FF1744;">⚠️</div>
            <div class="card-title" style="color: #FCA5A5;">AC-PRO GERAL</div>
            <div class="card-subtitle" style="color: #F87171;">192.168.1.16</div>
            <div class="badge-pill badge-red"><span class="live-dot live-dot-red"></span> OFFLINE (100% Loss)</div>
            <div class="card-highlight" style="color: #FCA5A5;">SSID: Inativo</div>
            <div class="card-info-row" style="color: #EF4444; font-weight: bold;">Falha de PoE Detectada</div>
            <div class="cyber-bar"><div class="cyber-bar-fill" style="width: 100%; background: #EF4444;"></div></div>
        </div>
    </div>
</div>"""
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
                "content": """<style>
@keyframes pulse-glow-green { 0%, 100% { box-shadow: 0 0 15px rgba(0,230,118,0.25), inset 0 0 10px rgba(0,230,118,0.1); } 50% { box-shadow: 0 0 28px rgba(0,230,118,0.6), inset 0 0 18px rgba(0,230,118,0.25); } }
@keyframes pulse-glow-blue { 0%, 100% { box-shadow: 0 0 15px rgba(0,176,255,0.25), inset 0 0 10px rgba(0,176,255,0.1); } 50% { box-shadow: 0 0 28px rgba(0,176,255,0.6), inset 0 0 18px rgba(0,176,255,0.25); } }
@keyframes pulse-glow-amber { 0%, 100% { box-shadow: 0 0 15px rgba(255,214,0,0.25), inset 0 0 10px rgba(255,214,0,0.1); } 50% { box-shadow: 0 0 28px rgba(255,214,0,0.6), inset 0 0 18px rgba(255,214,0,0.25); } }
@keyframes pulse-glow-purple { 0%, 100% { box-shadow: 0 0 15px rgba(168,85,247,0.25), inset 0 0 10px rgba(168,85,247,0.1); } 50% { box-shadow: 0 0 28px rgba(168,85,247,0.6), inset 0 0 18px rgba(168,85,247,0.25); } }
@keyframes pulse-glow-red { 0%, 100% { box-shadow: 0 0 15px rgba(255,23,68,0.35), inset 0 0 10px rgba(255,23,68,0.15); } 50% { box-shadow: 0 0 30px rgba(255,23,68,0.8), inset 0 0 20px rgba(255,23,68,0.3); } }
@keyframes float3d { 0%, 100% { transform: translateY(0px) rotateX(6deg) rotateY(var(--ry, 0deg)); } 50% { transform: translateY(-7px) rotateX(8deg) rotateY(var(--ry, 0deg)); } }
@keyframes radarSweep { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
@keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
@keyframes pulseDot { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.4); opacity: 0.6; } }

.noc-stage-3d {
    perspective: 1400px;
    padding: 16px 14px 18px;
    background: radial-gradient(circle at 50% 20%, rgba(30, 41, 59, 0.75), rgba(15, 23, 42, 0.92) 50%, rgba(2, 6, 23, 0.98) 100%);
    border-radius: 16px;
    border: 1px solid rgba(59, 130, 246, 0.28);
    box-shadow: 0 20px 45px -10px rgba(0, 0, 0, 0.8), inset 0 1px 1px rgba(255,255,255,0.15);
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(12px);
}
.noc-stage-3d::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(56, 189, 248, 0.7), transparent);
}
.noc-grid-cards {
    display: flex;
    justify-content: space-around;
    align-items: stretch;
    flex-wrap: wrap;
    gap: 16px;
    transform-style: preserve-3d;
}
.card-3d-interactive {
    transform-style: preserve-3d;
    transition: transform 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.35s ease, border-color 0.35s ease;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-radius: 14px;
    padding: 14px 16px;
    min-width: 175px;
    text-align: center;
    position: relative;
    cursor: pointer;
    animation: float3d 5s ease-in-out infinite;
}
.card-3d-interactive:hover {
    transform: translateY(-12px) scale(1.04) rotateX(0deg) rotateY(0deg) !important;
    z-index: 10;
}
.card-green {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.14), rgba(15, 23, 42, 0.92) 75%);
    border: 1px solid rgba(0, 230, 118, 0.55);
    box-shadow: 0 12px 28px -5px rgba(0, 230, 118, 0.25);
    animation: float3d 5.5s ease-in-out infinite, pulse-glow-green 4s infinite ease-in-out;
}
.card-blue {
    background: linear-gradient(135deg, rgba(14, 165, 233, 0.14), rgba(15, 23, 42, 0.92) 75%);
    border: 1px solid rgba(0, 176, 255, 0.55);
    box-shadow: 0 12px 28px -5px rgba(0, 176, 255, 0.25);
    animation: float3d 5.2s ease-in-out infinite 0.4s, pulse-glow-blue 4s infinite ease-in-out 0.5s;
}
.card-amber {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.14), rgba(15, 23, 42, 0.92) 75%);
    border: 1px solid rgba(255, 214, 0, 0.55);
    box-shadow: 0 12px 28px -5px rgba(255, 214, 0, 0.25);
    animation: float3d 5.8s ease-in-out infinite 0.8s, pulse-glow-amber 4s infinite ease-in-out 1s;
}
.card-purple {
    background: linear-gradient(135deg, rgba(168, 85, 247, 0.14), rgba(15, 23, 42, 0.92) 75%);
    border: 1px solid rgba(168, 85, 247, 0.55);
    box-shadow: 0 12px 28px -5px rgba(168, 85, 247, 0.25);
    animation: float3d 6s ease-in-out infinite 1.2s, pulse-glow-purple 4s infinite ease-in-out 1.5s;
}
.card-red {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.22), rgba(30, 10, 15, 0.95) 75%);
    border: 1px solid rgba(255, 23, 68, 0.65);
    box-shadow: 0 12px 28px -5px rgba(255, 23, 68, 0.35);
    animation: float3d 4.8s ease-in-out infinite 1.5s, pulse-glow-red 3s infinite ease-in-out;
}
.card-icon-3d {
    font-size: 32px;
    margin-bottom: 4px;
    display: inline-block;
    filter: drop-shadow(0 4px 10px rgba(0,0,0,0.6));
    transition: transform 0.3s;
}
.card-3d-interactive:hover .card-icon-3d {
    transform: scale(1.22) translateZ(25px);
}
.card-title {
    font-weight: 800;
    font-size: 13px;
    letter-spacing: 0.5px;
    color: #FFFFFF;
    text-transform: uppercase;
    margin-bottom: 2px;
}
.card-subtitle {
    color: #94A3B8;
    font-size: 11px;
    font-family: monospace;
}
.badge-pill {
    margin: 8px auto 6px;
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 10px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 0.3px;
}
.live-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    display: inline-block;
    animation: pulseDot 1.6s infinite ease-in-out;
}
.live-dot-green { background: #00E676; box-shadow: 0 0 8px #00E676; }
.live-dot-blue { background: #00B0FF; box-shadow: 0 0 8px #00B0FF; }
.live-dot-amber { background: #FFD600; box-shadow: 0 0 8px #FFD600; }
.live-dot-purple { background: #A855F7; box-shadow: 0 0 8px #A855F7; }
.live-dot-red { background: #FF1744; box-shadow: 0 0 8px #FF1744; }

.badge-green { background: rgba(0, 230, 118, 0.16); color: #00E676; border: 1px solid rgba(0, 230, 118, 0.3); }
.badge-blue { background: rgba(0, 176, 255, 0.16); color: #00B0FF; border: 1px solid rgba(0, 176, 255, 0.3); }
.badge-amber { background: rgba(255, 214, 0, 0.16); color: #FFD600; border: 1px solid rgba(255, 214, 0, 0.3); }
.badge-purple { background: rgba(168, 85, 247, 0.16); color: #C084FC; border: 1px solid rgba(168, 85, 247, 0.3); }
.badge-red { background: rgba(255, 23, 68, 0.22); color: #FF5252; border: 1px solid rgba(255, 23, 68, 0.4); }

.card-info-row {
    font-size: 10.5px;
    color: #CBD5E1;
    margin-top: 3px;
    display: flex;
    justify-content: center;
    gap: 6px;
}
.card-highlight {
    font-size: 11px;
    color: #38BDF8;
    font-weight: 600;
    margin-top: 4px;
}
.cyber-bar {
    width: 100%;
    height: 4px;
    background: rgba(255,255,255,0.08);
    border-radius: 4px;
    overflow: hidden;
    margin-top: 8px;
}
.cyber-bar-fill {
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, #00E676, #00B0FF);
}
</style>
<div class="noc-stage-3d">
    <div class="noc-grid-cards">
        <!-- Card 3D 1: SRV NOC Monitoring -->
        <div class="card-3d-interactive card-green" style="--ry: -5deg; min-width: 210px;">
            <div class="card-icon-3d" style="text-shadow: 0 0 18px #00E676;">🖥️</div>
            <div class="card-title">SRV-NOC-MONITORING</div>
            <div class="card-subtitle">10.0.0.10 (Zabbix/Grafana)</div>
            <div class="badge-pill badge-green"><span class="live-dot live-dot-green"></span> 100% OPERACIONAL</div>
            <div class="card-highlight">CPU: 17.3% | RAM: 32.4% (8 GB)</div>
            <div class="card-info-row"><span>💾 Disco: 11.9%</span><span>•</span><span>⏱️ Uptime: 3.5d</span></div>
            <div class="cyber-bar"><div class="cyber-bar-fill" style="width: 32%; background: linear-gradient(90deg,#00E676,#38BDF8);"></div></div>
        </div>
        <!-- Card 3D 2: ERP TOTVS Protheus -->
        <div class="card-3d-interactive card-blue" style="--ry: -2deg; min-width: 210px;">
            <div class="card-icon-3d" style="text-shadow: 0 0 18px #00B0FF;">🏢</div>
            <div class="card-title">SRV-ERP-PROTHEUS</div>
            <div class="card-subtitle">10.0.0.20 (Banco & ERP)</div>
            <div class="badge-pill badge-blue"><span class="live-dot live-dot-blue"></span> HTTP 80 ATIVO</div>
            <div class="card-highlight">Tempo Resposta: 0.92 ms</div>
            <div class="card-info-row"><span>🛡️ Hardening Rígido</span><span>•</span><span>SSH Restrito</span></div>
            <div class="cyber-bar"><div class="cyber-bar-fill" style="width: 45%; background: linear-gradient(90deg,#00B0FF,#818CF8);"></div></div>
        </div>
        <!-- Card 3D 3: Gateway Edge -->
        <div class="card-3d-interactive card-amber" style="--ry: 2deg; min-width: 210px;">
            <div class="card-icon-3d" style="text-shadow: 0 0 18px #FFD600;">🛡️</div>
            <div class="card-title">GATEWAY EDGE 10.1</div>
            <div class="card-subtitle">10.0.0.1 (Borda Corporativa)</div>
            <div class="badge-pill badge-amber"><span class="live-dot live-dot-amber"></span> LATÊNCIA SUB-MS</div>
            <div class="card-highlight">Tempo Resposta: 0.18 ms</div>
            <div class="card-info-row"><span>⚡ Perda: 0.00%</span><span>•</span><span>Firewall State: OK</span></div>
            <div class="cyber-bar"><div class="cyber-bar-fill" style="width: 15%; background: linear-gradient(90deg,#FFD600,#F59E0B);"></div></div>
        </div>
        <!-- Card 3D 4: Estações Windows -->
        <div class="card-3d-interactive card-purple" style="--ry: 5deg; min-width: 210px;">
            <div class="card-icon-3d" style="text-shadow: 0 0 18px #A855F7;">💻</div>
            <div class="card-title">PARQUE ESTAÇÕES</div>
            <div class="card-subtitle">28 Desktops / Workstations</div>
            <div class="badge-pill badge-purple"><span class="live-dot live-dot-purple"></span> 26 ONLINE / 2 OFFLINE</div>
            <div class="card-highlight">RDP 3389 / SMB 445 Ativos</div>
            <div class="card-info-row"><span>⚡ Latência Média: 0.45 ms</span><span>•</span><span>92.8% Up</span></div>
            <div class="cyber-bar"><div class="cyber-bar-fill" style="width: 93%; background: linear-gradient(90deg,#A855F7,#38BDF8);"></div></div>
        </div>
    </div>
</div>"""
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
                "content": """<style>
@keyframes pulse-glow-green { 0%, 100% { box-shadow: 0 0 15px rgba(0,230,118,0.25), inset 0 0 10px rgba(0,230,118,0.1); } 50% { box-shadow: 0 0 28px rgba(0,230,118,0.6), inset 0 0 18px rgba(0,230,118,0.25); } }
@keyframes pulse-glow-blue { 0%, 100% { box-shadow: 0 0 15px rgba(0,176,255,0.25), inset 0 0 10px rgba(0,176,255,0.1); } 50% { box-shadow: 0 0 28px rgba(0,176,255,0.6), inset 0 0 18px rgba(0,176,255,0.25); } }
@keyframes pulse-glow-amber { 0%, 100% { box-shadow: 0 0 15px rgba(255,214,0,0.25), inset 0 0 10px rgba(255,214,0,0.1); } 50% { box-shadow: 0 0 28px rgba(255,214,0,0.6), inset 0 0 18px rgba(255,214,0,0.25); } }
@keyframes pulse-glow-purple { 0%, 100% { box-shadow: 0 0 15px rgba(168,85,247,0.25), inset 0 0 10px rgba(168,85,247,0.1); } 50% { box-shadow: 0 0 28px rgba(168,85,247,0.6), inset 0 0 18px rgba(168,85,247,0.25); } }
@keyframes pulse-glow-red { 0%, 100% { box-shadow: 0 0 15px rgba(255,23,68,0.35), inset 0 0 10px rgba(255,23,68,0.15); } 50% { box-shadow: 0 0 30px rgba(255,23,68,0.8), inset 0 0 20px rgba(255,23,68,0.3); } }
@keyframes float3d { 0%, 100% { transform: translateY(0px) rotateX(6deg) rotateY(var(--ry, 0deg)); } 50% { transform: translateY(-7px) rotateX(8deg) rotateY(var(--ry, 0deg)); } }
@keyframes radarSweep { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
@keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
@keyframes pulseDot { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.4); opacity: 0.6; } }

.noc-stage-3d {
    perspective: 1400px;
    padding: 16px 14px 18px;
    background: radial-gradient(circle at 50% 20%, rgba(30, 41, 59, 0.75), rgba(15, 23, 42, 0.92) 50%, rgba(2, 6, 23, 0.98) 100%);
    border-radius: 16px;
    border: 1px solid rgba(59, 130, 246, 0.28);
    box-shadow: 0 20px 45px -10px rgba(0, 0, 0, 0.8), inset 0 1px 1px rgba(255,255,255,0.15);
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(12px);
}
.noc-stage-3d::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(56, 189, 248, 0.7), transparent);
}
.noc-grid-cards {
    display: flex;
    justify-content: space-around;
    align-items: stretch;
    flex-wrap: wrap;
    gap: 16px;
    transform-style: preserve-3d;
}
.card-3d-interactive {
    transform-style: preserve-3d;
    transition: transform 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.35s ease, border-color 0.35s ease;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-radius: 14px;
    padding: 14px 16px;
    min-width: 175px;
    text-align: center;
    position: relative;
    cursor: pointer;
    animation: float3d 5s ease-in-out infinite;
}
.card-3d-interactive:hover {
    transform: translateY(-12px) scale(1.04) rotateX(0deg) rotateY(0deg) !important;
    z-index: 10;
}
.card-green {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.14), rgba(15, 23, 42, 0.92) 75%);
    border: 1px solid rgba(0, 230, 118, 0.55);
    box-shadow: 0 12px 28px -5px rgba(0, 230, 118, 0.25);
    animation: float3d 5.5s ease-in-out infinite, pulse-glow-green 4s infinite ease-in-out;
}
.card-blue {
    background: linear-gradient(135deg, rgba(14, 165, 233, 0.14), rgba(15, 23, 42, 0.92) 75%);
    border: 1px solid rgba(0, 176, 255, 0.55);
    box-shadow: 0 12px 28px -5px rgba(0, 176, 255, 0.25);
    animation: float3d 5.2s ease-in-out infinite 0.4s, pulse-glow-blue 4s infinite ease-in-out 0.5s;
}
.card-amber {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.14), rgba(15, 23, 42, 0.92) 75%);
    border: 1px solid rgba(255, 214, 0, 0.55);
    box-shadow: 0 12px 28px -5px rgba(255, 214, 0, 0.25);
    animation: float3d 5.8s ease-in-out infinite 0.8s, pulse-glow-amber 4s infinite ease-in-out 1s;
}
.card-purple {
    background: linear-gradient(135deg, rgba(168, 85, 247, 0.14), rgba(15, 23, 42, 0.92) 75%);
    border: 1px solid rgba(168, 85, 247, 0.55);
    box-shadow: 0 12px 28px -5px rgba(168, 85, 247, 0.25);
    animation: float3d 6s ease-in-out infinite 1.2s, pulse-glow-purple 4s infinite ease-in-out 1.5s;
}
.card-red {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.22), rgba(30, 10, 15, 0.95) 75%);
    border: 1px solid rgba(255, 23, 68, 0.65);
    box-shadow: 0 12px 28px -5px rgba(255, 23, 68, 0.35);
    animation: float3d 4.8s ease-in-out infinite 1.5s, pulse-glow-red 3s infinite ease-in-out;
}
.card-icon-3d {
    font-size: 32px;
    margin-bottom: 4px;
    display: inline-block;
    filter: drop-shadow(0 4px 10px rgba(0,0,0,0.6));
    transition: transform 0.3s;
}
.card-3d-interactive:hover .card-icon-3d {
    transform: scale(1.22) translateZ(25px);
}
.card-title {
    font-weight: 800;
    font-size: 13px;
    letter-spacing: 0.5px;
    color: #FFFFFF;
    text-transform: uppercase;
    margin-bottom: 2px;
}
.card-subtitle {
    color: #94A3B8;
    font-size: 11px;
    font-family: monospace;
}
.badge-pill {
    margin: 8px auto 6px;
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 10px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 0.3px;
}
.live-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    display: inline-block;
    animation: pulseDot 1.6s infinite ease-in-out;
}
.live-dot-green { background: #00E676; box-shadow: 0 0 8px #00E676; }
.live-dot-blue { background: #00B0FF; box-shadow: 0 0 8px #00B0FF; }
.live-dot-amber { background: #FFD600; box-shadow: 0 0 8px #FFD600; }
.live-dot-purple { background: #A855F7; box-shadow: 0 0 8px #A855F7; }
.live-dot-red { background: #FF1744; box-shadow: 0 0 8px #FF1744; }

.badge-green { background: rgba(0, 230, 118, 0.16); color: #00E676; border: 1px solid rgba(0, 230, 118, 0.3); }
.badge-blue { background: rgba(0, 176, 255, 0.16); color: #00B0FF; border: 1px solid rgba(0, 176, 255, 0.3); }
.badge-amber { background: rgba(255, 214, 0, 0.16); color: #FFD600; border: 1px solid rgba(255, 214, 0, 0.3); }
.badge-purple { background: rgba(168, 85, 247, 0.16); color: #C084FC; border: 1px solid rgba(168, 85, 247, 0.3); }
.badge-red { background: rgba(255, 23, 68, 0.22); color: #FF5252; border: 1px solid rgba(255, 23, 68, 0.4); }

.card-info-row {
    font-size: 10.5px;
    color: #CBD5E1;
    margin-top: 3px;
    display: flex;
    justify-content: center;
    gap: 6px;
}
.card-highlight {
    font-size: 11px;
    color: #38BDF8;
    font-weight: 600;
    margin-top: 4px;
}
.cyber-bar {
    width: 100%;
    height: 4px;
    background: rgba(255,255,255,0.08);
    border-radius: 4px;
    overflow: hidden;
    margin-top: 8px;
}
.cyber-bar-fill {
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, #00E676, #00B0FF);
}
</style>
<div class="noc-stage-3d">
    <div class="noc-grid-cards">
        <!-- Card 3D 1: Provedor ISP -->
        <div class="card-3d-interactive card-green" style="--ry: -6deg; min-width: 210px;">
            <div class="card-icon-3d" style="text-shadow: 0 0 18px #00E676;">🏢</div>
            <div class="card-title">TOP FIBRA TELECOM</div>
            <div class="card-subtitle">Link Dedicado WAN 1:1</div>
            <div class="badge-pill badge-green"><span class="live-dot live-dot-green"></span> FIBRA ILUMINADA</div>
            <div class="card-highlight">IP: 203.0.113.1 (BGP/WAN)</div>
            <div class="card-info-row"><span>🌐 SLA 99.98% Garantido</span></div>
            <div class="cyber-bar"><div class="cyber-bar-fill" style="width: 100%; background: linear-gradient(90deg,#00E676,#38BDF8);"></div></div>
        </div>
        <!-- Card 3D 2: MITIGAÇÃO ATIVA DE PERDA DE PACOTES -->
        <div class="card-3d-interactive card-green" style="--ry: -3deg; min-width: 230px;">
            <div class="card-icon-3d" style="text-shadow: 0 0 18px #10B981;">🛡️</div>
            <div class="card-title">MITIGAÇÃO PERDA PACOTES</div>
            <div class="card-subtitle">Zero Packet Loss Engine</div>
            <div class="badge-pill badge-green"><span class="live-dot live-dot-green"></span> 0.00% LOSS (PROTEGIDO)</div>
            <div class="card-highlight">QoS FQ-CoDel + Anti-Bufferbloat</div>
            <div class="card-info-row"><span>🚀 Failover Automático</span><span>•</span><span>0 descartes</span></div>
            <div class="cyber-bar"><div class="cyber-bar-fill" style="width: 100%; background: linear-gradient(90deg,#10B981,#00E676);"></div></div>
        </div>
        <!-- Card 3D 3: CONSUMO DE BANDA EM TEMPO REAL -->
        <div class="card-3d-interactive card-blue" style="--ry: 0deg; min-width: 230px;">
            <div class="card-icon-3d" style="text-shadow: 0 0 18px #3B82F6;">🚀</div>
            <div class="card-title">CONSUMO DE BANDA WAN</div>
            <div class="card-subtitle">Contrato 600M Down / 300M Up</div>
            <div class="badge-pill badge-blue"><span class="live-dot live-dot-blue"></span> 135.8M RX | 40.7M TX</div>
            <div class="card-highlight">Uso: 22.6% Down • 13.5% Up</div>
            <div class="card-info-row"><span>⚡ Shaper Anti-Saturação Ativo (85%)</span></div>
            <div class="cyber-bar"><div class="cyber-bar-fill" style="width: 23%; background: linear-gradient(90deg,#38BDF8,#3B82F6);"></div></div>
        </div>
        <!-- Card 3D 4: Gateway Google -->
        <div class="card-3d-interactive card-blue" style="--ry: 3deg; min-width: 200px;">
            <div class="card-icon-3d" style="text-shadow: 0 0 18px #00B0FF;">🌍</div>
            <div class="card-title">ROTA GOOGLE (8.8.8.8)</div>
            <div class="card-subtitle">Gateway Primário Anycast</div>
            <div class="badge-pill badge-blue"><span class="live-dot live-dot-blue"></span> 29.1 ms (ESTÁVEL)</div>
            <div class="card-highlight">Perda de Pacotes: 0.0%</div>
            <div class="card-info-row"><span>🎯 Jitter: 0.12 ms</span><span>•</span><span>RTT Ótimo</span></div>
            <div class="cyber-bar"><div class="cyber-bar-fill" style="width: 85%; background: linear-gradient(90deg,#00B0FF,#818CF8);"></div></div>
        </div>
        <!-- Card 3D 5: Gateway Cloudflare -->
        <div class="card-3d-interactive card-amber" style="--ry: 6deg; min-width: 200px;">
            <div class="card-icon-3d" style="text-shadow: 0 0 18px #FFD600;">☁️</div>
            <div class="card-title">ROTA CLOUDFLARE (1.1.1.1)</div>
            <div class="card-subtitle">Gateway Backup Standby</div>
            <div class="badge-pill badge-amber"><span class="live-dot live-dot-amber"></span> 53.7 ms (STANDBY)</div>
            <div class="card-highlight">Perda de Pacotes: 0.0%</div>
            <div class="card-info-row"><span>🛡️ Rota de Contingência Ativa</span></div>
            <div class="cyber-bar"><div class="cyber-bar-fill" style="width: 65%; background: linear-gradient(90deg,#FFD600,#F59E0B);"></div></div>
        </div>
    </div>
</div>"""
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
                "content": """<style>
@keyframes pulse-glow-green { 0%, 100% { box-shadow: 0 0 15px rgba(0,230,118,0.25), inset 0 0 10px rgba(0,230,118,0.1); } 50% { box-shadow: 0 0 28px rgba(0,230,118,0.6), inset 0 0 18px rgba(0,230,118,0.25); } }
@keyframes pulse-glow-blue { 0%, 100% { box-shadow: 0 0 15px rgba(0,176,255,0.25), inset 0 0 10px rgba(0,176,255,0.1); } 50% { box-shadow: 0 0 28px rgba(0,176,255,0.6), inset 0 0 18px rgba(0,176,255,0.25); } }
@keyframes pulse-glow-amber { 0%, 100% { box-shadow: 0 0 15px rgba(255,214,0,0.25), inset 0 0 10px rgba(255,214,0,0.1); } 50% { box-shadow: 0 0 28px rgba(255,214,0,0.6), inset 0 0 18px rgba(255,214,0,0.25); } }
@keyframes pulse-glow-purple { 0%, 100% { box-shadow: 0 0 15px rgba(168,85,247,0.25), inset 0 0 10px rgba(168,85,247,0.1); } 50% { box-shadow: 0 0 28px rgba(168,85,247,0.6), inset 0 0 18px rgba(168,85,247,0.25); } }
@keyframes pulse-glow-red { 0%, 100% { box-shadow: 0 0 15px rgba(255,23,68,0.35), inset 0 0 10px rgba(255,23,68,0.15); } 50% { box-shadow: 0 0 30px rgba(255,23,68,0.8), inset 0 0 20px rgba(255,23,68,0.3); } }
@keyframes float3d { 0%, 100% { transform: translateY(0px) rotateX(6deg) rotateY(var(--ry, 0deg)); } 50% { transform: translateY(-7px) rotateX(8deg) rotateY(var(--ry, 0deg)); } }
@keyframes radarSweep { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
@keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
@keyframes pulseDot { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.4); opacity: 0.6; } }

.noc-stage-3d {
    perspective: 1400px;
    padding: 16px 14px 18px;
    background: radial-gradient(circle at 50% 20%, rgba(30, 41, 59, 0.75), rgba(15, 23, 42, 0.92) 50%, rgba(2, 6, 23, 0.98) 100%);
    border-radius: 16px;
    border: 1px solid rgba(59, 130, 246, 0.28);
    box-shadow: 0 20px 45px -10px rgba(0, 0, 0, 0.8), inset 0 1px 1px rgba(255,255,255,0.15);
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(12px);
}
.noc-stage-3d::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(56, 189, 248, 0.7), transparent);
}
.noc-grid-cards {
    display: flex;
    justify-content: space-around;
    align-items: stretch;
    flex-wrap: wrap;
    gap: 16px;
    transform-style: preserve-3d;
}
.card-3d-interactive {
    transform-style: preserve-3d;
    transition: transform 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.35s ease, border-color 0.35s ease;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-radius: 14px;
    padding: 14px 16px;
    min-width: 175px;
    text-align: center;
    position: relative;
    cursor: pointer;
    animation: float3d 5s ease-in-out infinite;
}
.card-3d-interactive:hover {
    transform: translateY(-12px) scale(1.04) rotateX(0deg) rotateY(0deg) !important;
    z-index: 10;
}
.card-green {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.14), rgba(15, 23, 42, 0.92) 75%);
    border: 1px solid rgba(0, 230, 118, 0.55);
    box-shadow: 0 12px 28px -5px rgba(0, 230, 118, 0.25);
    animation: float3d 5.5s ease-in-out infinite, pulse-glow-green 4s infinite ease-in-out;
}
.card-blue {
    background: linear-gradient(135deg, rgba(14, 165, 233, 0.14), rgba(15, 23, 42, 0.92) 75%);
    border: 1px solid rgba(0, 176, 255, 0.55);
    box-shadow: 0 12px 28px -5px rgba(0, 176, 255, 0.25);
    animation: float3d 5.2s ease-in-out infinite 0.4s, pulse-glow-blue 4s infinite ease-in-out 0.5s;
}
.card-amber {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.14), rgba(15, 23, 42, 0.92) 75%);
    border: 1px solid rgba(255, 214, 0, 0.55);
    box-shadow: 0 12px 28px -5px rgba(255, 214, 0, 0.25);
    animation: float3d 5.8s ease-in-out infinite 0.8s, pulse-glow-amber 4s infinite ease-in-out 1s;
}
.card-purple {
    background: linear-gradient(135deg, rgba(168, 85, 247, 0.14), rgba(15, 23, 42, 0.92) 75%);
    border: 1px solid rgba(168, 85, 247, 0.55);
    box-shadow: 0 12px 28px -5px rgba(168, 85, 247, 0.25);
    animation: float3d 6s ease-in-out infinite 1.2s, pulse-glow-purple 4s infinite ease-in-out 1.5s;
}
.card-red {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.22), rgba(30, 10, 15, 0.95) 75%);
    border: 1px solid rgba(255, 23, 68, 0.65);
    box-shadow: 0 12px 28px -5px rgba(255, 23, 68, 0.35);
    animation: float3d 4.8s ease-in-out infinite 1.5s, pulse-glow-red 3s infinite ease-in-out;
}
.card-icon-3d {
    font-size: 32px;
    margin-bottom: 4px;
    display: inline-block;
    filter: drop-shadow(0 4px 10px rgba(0,0,0,0.6));
    transition: transform 0.3s;
}
.card-3d-interactive:hover .card-icon-3d {
    transform: scale(1.22) translateZ(25px);
}
.card-title {
    font-weight: 800;
    font-size: 13px;
    letter-spacing: 0.5px;
    color: #FFFFFF;
    text-transform: uppercase;
    margin-bottom: 2px;
}
.card-subtitle {
    color: #94A3B8;
    font-size: 11px;
    font-family: monospace;
}
.badge-pill {
    margin: 8px auto 6px;
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 10px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 0.3px;
}
.live-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    display: inline-block;
    animation: pulseDot 1.6s infinite ease-in-out;
}
.live-dot-green { background: #00E676; box-shadow: 0 0 8px #00E676; }
.live-dot-blue { background: #00B0FF; box-shadow: 0 0 8px #00B0FF; }
.live-dot-amber { background: #FFD600; box-shadow: 0 0 8px #FFD600; }
.live-dot-purple { background: #A855F7; box-shadow: 0 0 8px #A855F7; }
.live-dot-red { background: #FF1744; box-shadow: 0 0 8px #FF1744; }

.badge-green { background: rgba(0, 230, 118, 0.16); color: #00E676; border: 1px solid rgba(0, 230, 118, 0.3); }
.badge-blue { background: rgba(0, 176, 255, 0.16); color: #00B0FF; border: 1px solid rgba(0, 176, 255, 0.3); }
.badge-amber { background: rgba(255, 214, 0, 0.16); color: #FFD600; border: 1px solid rgba(255, 214, 0, 0.3); }
.badge-purple { background: rgba(168, 85, 247, 0.16); color: #C084FC; border: 1px solid rgba(168, 85, 247, 0.3); }
.badge-red { background: rgba(255, 23, 68, 0.22); color: #FF5252; border: 1px solid rgba(255, 23, 68, 0.4); }

.card-info-row {
    font-size: 10.5px;
    color: #CBD5E1;
    margin-top: 3px;
    display: flex;
    justify-content: center;
    gap: 6px;
}
.card-highlight {
    font-size: 11px;
    color: #38BDF8;
    font-weight: 600;
    margin-top: 4px;
}
.cyber-bar {
    width: 100%;
    height: 4px;
    background: rgba(255,255,255,0.08);
    border-radius: 4px;
    overflow: hidden;
    margin-top: 8px;
}
.cyber-bar-fill {
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, #00E676, #00B0FF);
}
</style>
<div class="noc-stage-3d">
    <div class="noc-grid-cards">
        <!-- Card 3D 1: HP 01 -->
        <div class="card-3d-interactive card-amber" style="--ry: -4deg; min-width: 290px;">
            <div class="card-icon-3d" style="text-shadow: 0 0 20px #FF9100;">🖨️</div>
            <div class="card-title">HP LASERJET FLOW 220</div>
            <div class="card-subtitle">IP: 192.168.1.50 | BRBSQ2Q11P</div>
            <div class="badge-pill badge-amber"><span class="live-dot live-dot-amber"></span> Toner Preto: 15% (Atenção)</div>
            <div class="card-highlight">📄 324.549 Páginas Impressas</div>
            <div class="card-info-row"><span>ADF: 81%</span><span>•</span><span>Cilindros: 62%</span><span>•</span><span>0.41 ms</span></div>
            <div class="card-info-row" style="color: #00E676; font-weight: bold; margin-top: 4px;">🟢 Display Status: "Pronta"</div>
            <div class="cyber-bar"><div class="cyber-bar-fill" style="width: 15%; background: linear-gradient(90deg,#EF4444,#FF9100);"></div></div>
        </div>
        <!-- Card 3D 2: HP 02 -->
        <div class="card-3d-interactive card-red" style="--ry: 4deg; min-width: 290px;">
            <div class="card-icon-3d" style="text-shadow: 0 0 20px #FF1744;">🖨️</div>
            <div class="card-title" style="color: #FCA5A5;">HP LASERJET FLOW 221</div>
            <div class="card-subtitle" style="color: #F87171;">IP: 192.168.1.51 | BRBSQ2G0BP</div>
            <div class="badge-pill badge-red"><span class="live-dot live-dot-red"></span> Toner Preto: 0% (Esgotado)</div>
            <div class="card-highlight" style="color: #FCA5A5;">📄 356.600 Páginas Impressas</div>
            <div class="card-info-row"><span>ADF: 74%</span><span>•</span><span>Cilindros: 49%</span><span>•</span><span>0.35 ms</span></div>
            <div class="card-info-row" style="color: #EF4444; font-weight: bold; margin-top: 4px;">🚨 Substituir Cartucho Imediatamente</div>
            <div class="cyber-bar"><div class="cyber-bar-fill" style="width: 100%; background: #EF4444;"></div></div>
        </div>
    </div>
</div>"""
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
                "content": """<style>
@keyframes pulse-glow-green { 0%, 100% { box-shadow: 0 0 15px rgba(0,230,118,0.25), inset 0 0 10px rgba(0,230,118,0.1); } 50% { box-shadow: 0 0 28px rgba(0,230,118,0.6), inset 0 0 18px rgba(0,230,118,0.25); } }
@keyframes pulse-glow-blue { 0%, 100% { box-shadow: 0 0 15px rgba(0,176,255,0.25), inset 0 0 10px rgba(0,176,255,0.1); } 50% { box-shadow: 0 0 28px rgba(0,176,255,0.6), inset 0 0 18px rgba(0,176,255,0.25); } }
@keyframes pulse-glow-amber { 0%, 100% { box-shadow: 0 0 15px rgba(255,214,0,0.25), inset 0 0 10px rgba(255,214,0,0.1); } 50% { box-shadow: 0 0 28px rgba(255,214,0,0.6), inset 0 0 18px rgba(255,214,0,0.25); } }
@keyframes pulse-glow-purple { 0%, 100% { box-shadow: 0 0 15px rgba(168,85,247,0.25), inset 0 0 10px rgba(168,85,247,0.1); } 50% { box-shadow: 0 0 28px rgba(168,85,247,0.6), inset 0 0 18px rgba(168,85,247,0.25); } }
@keyframes pulse-glow-red { 0%, 100% { box-shadow: 0 0 15px rgba(255,23,68,0.35), inset 0 0 10px rgba(255,23,68,0.15); } 50% { box-shadow: 0 0 30px rgba(255,23,68,0.8), inset 0 0 20px rgba(255,23,68,0.3); } }
@keyframes float3d { 0%, 100% { transform: translateY(0px) rotateX(6deg) rotateY(var(--ry, 0deg)); } 50% { transform: translateY(-7px) rotateX(8deg) rotateY(var(--ry, 0deg)); } }
@keyframes radarSweep { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
@keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
@keyframes pulseDot { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.4); opacity: 0.6; } }

.noc-stage-3d {
    perspective: 1400px;
    padding: 16px 14px 18px;
    background: radial-gradient(circle at 50% 20%, rgba(30, 41, 59, 0.75), rgba(15, 23, 42, 0.92) 50%, rgba(2, 6, 23, 0.98) 100%);
    border-radius: 16px;
    border: 1px solid rgba(59, 130, 246, 0.28);
    box-shadow: 0 20px 45px -10px rgba(0, 0, 0, 0.8), inset 0 1px 1px rgba(255,255,255,0.15);
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(12px);
}
.noc-stage-3d::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(56, 189, 248, 0.7), transparent);
}
.noc-grid-cards {
    display: flex;
    justify-content: space-around;
    align-items: stretch;
    flex-wrap: wrap;
    gap: 16px;
    transform-style: preserve-3d;
}
.card-3d-interactive {
    transform-style: preserve-3d;
    transition: transform 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.35s ease, border-color 0.35s ease;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-radius: 14px;
    padding: 14px 16px;
    min-width: 175px;
    text-align: center;
    position: relative;
    cursor: pointer;
    animation: float3d 5s ease-in-out infinite;
}
.card-3d-interactive:hover {
    transform: translateY(-12px) scale(1.04) rotateX(0deg) rotateY(0deg) !important;
    z-index: 10;
}
.card-green {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.14), rgba(15, 23, 42, 0.92) 75%);
    border: 1px solid rgba(0, 230, 118, 0.55);
    box-shadow: 0 12px 28px -5px rgba(0, 230, 118, 0.25);
    animation: float3d 5.5s ease-in-out infinite, pulse-glow-green 4s infinite ease-in-out;
}
.card-blue {
    background: linear-gradient(135deg, rgba(14, 165, 233, 0.14), rgba(15, 23, 42, 0.92) 75%);
    border: 1px solid rgba(0, 176, 255, 0.55);
    box-shadow: 0 12px 28px -5px rgba(0, 176, 255, 0.25);
    animation: float3d 5.2s ease-in-out infinite 0.4s, pulse-glow-blue 4s infinite ease-in-out 0.5s;
}
.card-amber {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.14), rgba(15, 23, 42, 0.92) 75%);
    border: 1px solid rgba(255, 214, 0, 0.55);
    box-shadow: 0 12px 28px -5px rgba(255, 214, 0, 0.25);
    animation: float3d 5.8s ease-in-out infinite 0.8s, pulse-glow-amber 4s infinite ease-in-out 1s;
}
.card-purple {
    background: linear-gradient(135deg, rgba(168, 85, 247, 0.14), rgba(15, 23, 42, 0.92) 75%);
    border: 1px solid rgba(168, 85, 247, 0.55);
    box-shadow: 0 12px 28px -5px rgba(168, 85, 247, 0.25);
    animation: float3d 6s ease-in-out infinite 1.2s, pulse-glow-purple 4s infinite ease-in-out 1.5s;
}
.card-red {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.22), rgba(30, 10, 15, 0.95) 75%);
    border: 1px solid rgba(255, 23, 68, 0.65);
    box-shadow: 0 12px 28px -5px rgba(255, 23, 68, 0.35);
    animation: float3d 4.8s ease-in-out infinite 1.5s, pulse-glow-red 3s infinite ease-in-out;
}
.card-icon-3d {
    font-size: 32px;
    margin-bottom: 4px;
    display: inline-block;
    filter: drop-shadow(0 4px 10px rgba(0,0,0,0.6));
    transition: transform 0.3s;
}
.card-3d-interactive:hover .card-icon-3d {
    transform: scale(1.22) translateZ(25px);
}
.card-title {
    font-weight: 800;
    font-size: 13px;
    letter-spacing: 0.5px;
    color: #FFFFFF;
    text-transform: uppercase;
    margin-bottom: 2px;
}
.card-subtitle {
    color: #94A3B8;
    font-size: 11px;
    font-family: monospace;
}
.badge-pill {
    margin: 8px auto 6px;
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 10px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 0.3px;
}
.live-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    display: inline-block;
    animation: pulseDot 1.6s infinite ease-in-out;
}
.live-dot-green { background: #00E676; box-shadow: 0 0 8px #00E676; }
.live-dot-blue { background: #00B0FF; box-shadow: 0 0 8px #00B0FF; }
.live-dot-amber { background: #FFD600; box-shadow: 0 0 8px #FFD600; }
.live-dot-purple { background: #A855F7; box-shadow: 0 0 8px #A855F7; }
.live-dot-red { background: #FF1744; box-shadow: 0 0 8px #FF1744; }

.badge-green { background: rgba(0, 230, 118, 0.16); color: #00E676; border: 1px solid rgba(0, 230, 118, 0.3); }
.badge-blue { background: rgba(0, 176, 255, 0.16); color: #00B0FF; border: 1px solid rgba(0, 176, 255, 0.3); }
.badge-amber { background: rgba(255, 214, 0, 0.16); color: #FFD600; border: 1px solid rgba(255, 214, 0, 0.3); }
.badge-purple { background: rgba(168, 85, 247, 0.16); color: #C084FC; border: 1px solid rgba(168, 85, 247, 0.3); }
.badge-red { background: rgba(255, 23, 68, 0.22); color: #FF5252; border: 1px solid rgba(255, 23, 68, 0.4); }

.card-info-row {
    font-size: 10.5px;
    color: #CBD5E1;
    margin-top: 3px;
    display: flex;
    justify-content: center;
    gap: 6px;
}
.card-highlight {
    font-size: 11px;
    color: #38BDF8;
    font-weight: 600;
    margin-top: 4px;
}
.cyber-bar {
    width: 100%;
    height: 4px;
    background: rgba(255,255,255,0.08);
    border-radius: 4px;
    overflow: hidden;
    margin-top: 8px;
}
.cyber-bar-fill {
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, #00E676, #00B0FF);
}
</style>
<div class="noc-stage-3d">
    <div class="noc-grid-cards">
        <!-- Card 3D 1: PABX Central -->
        <div class="card-3d-interactive card-purple" style="--ry: -4deg; min-width: 230px;">
            <div class="card-icon-3d" style="text-shadow: 0 0 18px #A855F7;">🎛️</div>
            <div class="card-title">CENTRAL PABX VOIP</div>
            <div class="card-subtitle">Sinalização SIP Porta 5060</div>
            <div class="badge-pill badge-purple"><span class="live-dot live-dot-purple"></span> 13 DE 14 RAMAIS ATIVOS</div>
            <div class="card-highlight">RTT de Voz Médio: 0.45 ms</div>
            <div class="card-info-row"><span>📞 Codec: G.711u / Opus</span><span>•</span><span>Jitter: 0.08ms</span></div>
            <div class="cyber-bar"><div class="cyber-bar-fill" style="width: 93%; background: linear-gradient(90deg,#A855F7,#38BDF8);"></div></div>
        </div>
        <!-- Card 3D 2: Ramal 12 -->
        <div class="card-3d-interactive card-green" style="--ry: -1deg; min-width: 210px;">
            <div class="card-icon-3d" style="text-shadow: 0 0 18px #00E676;">📞</div>
            <div class="card-title">RAMAL GXP-12</div>
            <div class="card-subtitle">IP: 10.0.0.12 (Diretoria)</div>
            <div class="badge-pill badge-green"><span class="live-dot live-dot-green"></span> DISPONÍVEL (0.48 ms)</div>
            <div class="card-highlight">Perda de Áudio: 0.00%</div>
            <div class="card-info-row"><span>🔊 Áudio HD Cristalline</span><span>•</span><span>MOS: 4.41</span></div>
            <div class="cyber-bar"><div class="cyber-bar-fill" style="width: 95%; background: linear-gradient(90deg,#00E676,#38BDF8);"></div></div>
        </div>
        <!-- Card 3D 3: Ramal 42 -->
        <div class="card-3d-interactive card-blue" style="--ry: 2deg; min-width: 210px;">
            <div class="card-icon-3d" style="text-shadow: 0 0 18px #00B0FF;">📞</div>
            <div class="card-title">RAMAL GXP-42</div>
            <div class="card-subtitle">IP: 10.0.3.42 (Operações)</div>
            <div class="badge-pill badge-blue"><span class="live-dot live-dot-blue"></span> DISPONÍVEL (0.46 ms)</div>
            <div class="card-highlight">Perda de Áudio: 0.00%</div>
            <div class="card-info-row"><span>🔊 Áudio HD Cristalline</span><span>•</span><span>MOS: 4.39</span></div>
            <div class="cyber-bar"><div class="cyber-bar-fill" style="width: 95%; background: linear-gradient(90deg,#00B0FF,#818CF8);"></div></div>
        </div>
        <!-- Card 3D 4: Ramal 166 (Alerta) -->
        <div class="card-3d-interactive card-red" style="--ry: 5deg; min-width: 210px;">
            <div class="card-icon-3d" style="text-shadow: 0 0 18px #FF1744;">📵</div>
            <div class="card-title" style="color: #FCA5A5;">RAMAL GXP-166</div>
            <div class="card-subtitle" style="color: #F87171;">IP: 10.0.0.166 (Almoxarifado)</div>
            <div class="badge-pill badge-red"><span class="live-dot live-dot-red"></span> TELEFONE MUDO</div>
            <div class="card-highlight" style="color: #FCA5A5;">Dispositivo Inacessível</div>
            <div class="card-info-row" style="color: #EF4444; font-weight: bold;">Verificar Cabo RJ45 / Switch</div>
            <div class="cyber-bar"><div class="cyber-bar-fill" style="width: 100%; background: #EF4444;"></div></div>
        </div>
    </div>
</div>"""
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
                "content": """<style>
@keyframes pulse-glow-green { 0%, 100% { box-shadow: 0 0 15px rgba(0,230,118,0.25), inset 0 0 10px rgba(0,230,118,0.1); } 50% { box-shadow: 0 0 28px rgba(0,230,118,0.6), inset 0 0 18px rgba(0,230,118,0.25); } }
@keyframes pulse-glow-blue { 0%, 100% { box-shadow: 0 0 15px rgba(0,176,255,0.25), inset 0 0 10px rgba(0,176,255,0.1); } 50% { box-shadow: 0 0 28px rgba(0,176,255,0.6), inset 0 0 18px rgba(0,176,255,0.25); } }
@keyframes pulse-glow-amber { 0%, 100% { box-shadow: 0 0 15px rgba(255,214,0,0.25), inset 0 0 10px rgba(255,214,0,0.1); } 50% { box-shadow: 0 0 28px rgba(255,214,0,0.6), inset 0 0 18px rgba(255,214,0,0.25); } }
@keyframes pulse-glow-purple { 0%, 100% { box-shadow: 0 0 15px rgba(168,85,247,0.25), inset 0 0 10px rgba(168,85,247,0.1); } 50% { box-shadow: 0 0 28px rgba(168,85,247,0.6), inset 0 0 18px rgba(168,85,247,0.25); } }
@keyframes pulse-glow-red { 0%, 100% { box-shadow: 0 0 15px rgba(255,23,68,0.35), inset 0 0 10px rgba(255,23,68,0.15); } 50% { box-shadow: 0 0 30px rgba(255,23,68,0.8), inset 0 0 20px rgba(255,23,68,0.3); } }
@keyframes float3d { 0%, 100% { transform: translateY(0px) rotateX(6deg) rotateY(var(--ry, 0deg)); } 50% { transform: translateY(-7px) rotateX(8deg) rotateY(var(--ry, 0deg)); } }
@keyframes radarSweep { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
@keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
@keyframes pulseDot { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.4); opacity: 0.6; } }

.noc-stage-3d {
    perspective: 1400px;
    padding: 16px 14px 18px;
    background: radial-gradient(circle at 50% 20%, rgba(30, 41, 59, 0.75), rgba(15, 23, 42, 0.92) 50%, rgba(2, 6, 23, 0.98) 100%);
    border-radius: 16px;
    border: 1px solid rgba(59, 130, 246, 0.28);
    box-shadow: 0 20px 45px -10px rgba(0, 0, 0, 0.8), inset 0 1px 1px rgba(255,255,255,0.15);
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(12px);
}
.noc-stage-3d::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(56, 189, 248, 0.7), transparent);
}
.noc-grid-cards {
    display: flex;
    justify-content: space-around;
    align-items: stretch;
    flex-wrap: wrap;
    gap: 16px;
    transform-style: preserve-3d;
}
.card-3d-interactive {
    transform-style: preserve-3d;
    transition: transform 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.35s ease, border-color 0.35s ease;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-radius: 14px;
    padding: 14px 16px;
    min-width: 175px;
    text-align: center;
    position: relative;
    cursor: pointer;
    animation: float3d 5s ease-in-out infinite;
}
.card-3d-interactive:hover {
    transform: translateY(-12px) scale(1.04) rotateX(0deg) rotateY(0deg) !important;
    z-index: 10;
}
.card-green {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.14), rgba(15, 23, 42, 0.92) 75%);
    border: 1px solid rgba(0, 230, 118, 0.55);
    box-shadow: 0 12px 28px -5px rgba(0, 230, 118, 0.25);
    animation: float3d 5.5s ease-in-out infinite, pulse-glow-green 4s infinite ease-in-out;
}
.card-blue {
    background: linear-gradient(135deg, rgba(14, 165, 233, 0.14), rgba(15, 23, 42, 0.92) 75%);
    border: 1px solid rgba(0, 176, 255, 0.55);
    box-shadow: 0 12px 28px -5px rgba(0, 176, 255, 0.25);
    animation: float3d 5.2s ease-in-out infinite 0.4s, pulse-glow-blue 4s infinite ease-in-out 0.5s;
}
.card-amber {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.14), rgba(15, 23, 42, 0.92) 75%);
    border: 1px solid rgba(255, 214, 0, 0.55);
    box-shadow: 0 12px 28px -5px rgba(255, 214, 0, 0.25);
    animation: float3d 5.8s ease-in-out infinite 0.8s, pulse-glow-amber 4s infinite ease-in-out 1s;
}
.card-purple {
    background: linear-gradient(135deg, rgba(168, 85, 247, 0.14), rgba(15, 23, 42, 0.92) 75%);
    border: 1px solid rgba(168, 85, 247, 0.55);
    box-shadow: 0 12px 28px -5px rgba(168, 85, 247, 0.25);
    animation: float3d 6s ease-in-out infinite 1.2s, pulse-glow-purple 4s infinite ease-in-out 1.5s;
}
.card-red {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.22), rgba(30, 10, 15, 0.95) 75%);
    border: 1px solid rgba(255, 23, 68, 0.65);
    box-shadow: 0 12px 28px -5px rgba(255, 23, 68, 0.35);
    animation: float3d 4.8s ease-in-out infinite 1.5s, pulse-glow-red 3s infinite ease-in-out;
}
.card-icon-3d {
    font-size: 32px;
    margin-bottom: 4px;
    display: inline-block;
    filter: drop-shadow(0 4px 10px rgba(0,0,0,0.6));
    transition: transform 0.3s;
}
.card-3d-interactive:hover .card-icon-3d {
    transform: scale(1.22) translateZ(25px);
}
.card-title {
    font-weight: 800;
    font-size: 13px;
    letter-spacing: 0.5px;
    color: #FFFFFF;
    text-transform: uppercase;
    margin-bottom: 2px;
}
.card-subtitle {
    color: #94A3B8;
    font-size: 11px;
    font-family: monospace;
}
.badge-pill {
    margin: 8px auto 6px;
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 10px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 0.3px;
}
.live-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    display: inline-block;
    animation: pulseDot 1.6s infinite ease-in-out;
}
.live-dot-green { background: #00E676; box-shadow: 0 0 8px #00E676; }
.live-dot-blue { background: #00B0FF; box-shadow: 0 0 8px #00B0FF; }
.live-dot-amber { background: #FFD600; box-shadow: 0 0 8px #FFD600; }
.live-dot-purple { background: #A855F7; box-shadow: 0 0 8px #A855F7; }
.live-dot-red { background: #FF1744; box-shadow: 0 0 8px #FF1744; }

.badge-green { background: rgba(0, 230, 118, 0.16); color: #00E676; border: 1px solid rgba(0, 230, 118, 0.3); }
.badge-blue { background: rgba(0, 176, 255, 0.16); color: #00B0FF; border: 1px solid rgba(0, 176, 255, 0.3); }
.badge-amber { background: rgba(255, 214, 0, 0.16); color: #FFD600; border: 1px solid rgba(255, 214, 0, 0.3); }
.badge-purple { background: rgba(168, 85, 247, 0.16); color: #C084FC; border: 1px solid rgba(168, 85, 247, 0.3); }
.badge-red { background: rgba(255, 23, 68, 0.22); color: #FF5252; border: 1px solid rgba(255, 23, 68, 0.4); }

.card-info-row {
    font-size: 10.5px;
    color: #CBD5E1;
    margin-top: 3px;
    display: flex;
    justify-content: center;
    gap: 6px;
}
.card-highlight {
    font-size: 11px;
    color: #38BDF8;
    font-weight: 600;
    margin-top: 4px;
}
.cyber-bar {
    width: 100%;
    height: 4px;
    background: rgba(255,255,255,0.08);
    border-radius: 4px;
    overflow: hidden;
    margin-top: 8px;
}
.cyber-bar-fill {
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, #00E676, #00B0FF);
}
</style>
<div class="noc-stage-3d">
    <div class="noc-grid-cards">
        <div class="card-3d-interactive card-green" style="--ry: -6deg; min-width: 165px;">
            <div class="card-icon-3d" style="text-shadow: 0 0 16px #00E676;">🌐</div>
            <div class="card-title">WAN TOP FIBRA</div>
            <div class="badge-pill badge-green"><span class="live-dot live-dot-green"></span> 29.1 ms | 0% Loss</div>
            <div class="card-highlight">136M RX (22.6%)</div>
            <div class="card-info-row"><span>🛡️ Mitigação Ativa</span></div>
            <div class="cyber-bar"><div class="cyber-bar-fill" style="width: 23%; background: linear-gradient(90deg,#00E676,#38BDF8);"></div></div>
        </div>
        <div class="card-3d-interactive card-blue" style="--ry: -3deg; min-width: 160px;">
            <div class="card-icon-3d" style="text-shadow: 0 0 16px #00B0FF;">📡</div>
            <div class="card-title">WI-FI UNIFI</div>
            <div class="badge-pill badge-blue"><span class="live-dot live-dot-blue"></span> 138 Clientes</div>
            <div class="card-highlight">5/6 APs Online</div>
            <div class="card-info-row"><span>⚡ 177 Mbps Total</span></div>
            <div class="cyber-bar"><div class="cyber-bar-fill" style="width: 83%; background: linear-gradient(90deg,#00B0FF,#818CF8);"></div></div>
        </div>
        <div class="card-3d-interactive card-amber" style="--ry: 0deg; min-width: 160px;">
            <div class="card-icon-3d" style="text-shadow: 0 0 16px #FFD600;">🖥️</div>
            <div class="card-title">SRV NOC 200</div>
            <div class="badge-pill badge-amber"><span class="live-dot live-dot-amber"></span> CPU 17% | RAM 32%</div>
            <div class="card-highlight">Disco / 11.9%</div>
            <div class="card-info-row"><span>⏱️ Uptime: 3.5d</span></div>
            <div class="cyber-bar"><div class="cyber-bar-fill" style="width: 32%; background: linear-gradient(90deg,#FFD600,#F59E0B);"></div></div>
        </div>
        <div class="card-3d-interactive card-amber" style="--ry: 3deg; min-width: 160px;">
            <div class="card-icon-3d" style="text-shadow: 0 0 16px #FF9100;">🖨️</div>
            <div class="card-title">PARQUE HP</div>
            <div class="badge-pill badge-amber"><span class="live-dot live-dot-amber"></span> Toners 15% / 0%</div>
            <div class="card-highlight">681k Páginas</div>
            <div class="card-info-row"><span>2/2 Impressoras</span></div>
            <div class="cyber-bar"><div class="cyber-bar-fill" style="width: 50%; background: linear-gradient(90deg,#FF9100,#EF4444);"></div></div>
        </div>
        <div class="card-3d-interactive card-purple" style="--ry: 6deg; min-width: 160px;">
            <div class="card-icon-3d" style="text-shadow: 0 0 16px #A855F7;">📞</div>
            <div class="card-title">VOIP GRANDSTREAM</div>
            <div class="badge-pill badge-purple"><span class="live-dot live-dot-purple"></span> 13/14 Ramais OK</div>
            <div class="card-highlight">RTT 0.45 ms</div>
            <div class="card-info-row"><span>Sinal SIP 5060</span></div>
            <div class="cyber-bar"><div class="cyber-bar-fill" style="width: 93%; background: linear-gradient(90deg,#A855F7,#38BDF8);"></div></div>
        </div>
    </div>
</div>"""
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
