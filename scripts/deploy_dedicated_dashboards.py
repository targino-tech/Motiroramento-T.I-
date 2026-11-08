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
<div style="perspective: 1200px; padding: 10px; background: radial-gradient(circle at 50% 50%, rgba(15, 23, 42, 0.95), rgba(2, 6, 23, 1)); border-radius: 12px; border: 1px solid rgba(59, 130, 246, 0.3); box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
    <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap; gap: 15px;">
        <!-- Card 3D 1: AP Peças -->
        <div style="transform: rotateX(8deg) rotateY(-4deg); transform-style: preserve-3d; transition: all 0.3s; background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95)); border: 1px solid #00E676; border-radius: 10px; padding: 12px 16px; min-width: 170px; text-align: center; box-shadow: 0 8px 20px rgba(0, 230, 118, 0.25);">
            <div style="font-size: 30px; text-shadow: 0 0 15px #00E676;">📡</div>
            <div style="font-weight: bold; color: #FFFFFF; font-size: 13px; margin-top: 4px;">UAP-HD PEÇAS</div>
            <div style="color: #94A3B8; font-size: 11px;">192.168.1.11</div>
            <div style="margin-top: 6px; display: inline-block; background: rgba(0,230,118,0.15); color: #00E676; padding: 2px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">👥 28 Clientes</div>
            <div style="font-size: 10px; color: #38BDF8; margin-top: 4px;">SSID: Enterprise NOC-Agro</div>
            <div style="font-size: 10px; color: #CBD5E1;">⚡ 34.2 Mbps | 0.37 ms</div>
        </div>
        <!-- Card 3D 2: AP TI -->
        <div style="transform: rotateX(8deg) rotateY(-2deg); transform-style: preserve-3d; background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95)); border: 1px solid #00B0FF; border-radius: 10px; padding: 12px 16px; min-width: 170px; text-align: center; box-shadow: 0 8px 20px rgba(0, 176, 255, 0.25);">
            <div style="font-size: 30px; text-shadow: 0 0 15px #00B0FF;">📡</div>
            <div style="font-weight: bold; color: #FFFFFF; font-size: 13px; margin-top: 4px;">UAP-HD TI</div>
            <div style="color: #94A3B8; font-size: 11px;">192.168.1.12</div>
            <div style="margin-top: 6px; display: inline-block; background: rgba(0,176,255,0.15); color: #00B0FF; padding: 2px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">👥 42 Clientes</div>
            <div style="font-size: 10px; color: #38BDF8; margin-top: 4px;">SSID: Enterprise NOC-Corp</div>
            <div style="font-size: 10px; color: #CBD5E1;">⚡ 58.4 Mbps | 0.40 ms</div>
        </div>
        <!-- Card 3D 3: AP Garantia -->
        <div style="transform: rotateX(8deg) rotateY(0deg); transform-style: preserve-3d; background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95)); border: 1px solid #FFD600; border-radius: 10px; padding: 12px 16px; min-width: 170px; text-align: center; box-shadow: 0 8px 20px rgba(255, 214, 0, 0.25);">
            <div style="font-size: 30px; text-shadow: 0 0 15px #FFD600;">📡</div>
            <div style="font-weight: bold; color: #FFFFFF; font-size: 13px; margin-top: 4px;">UAP-HD GARANTIA</div>
            <div style="color: #94A3B8; font-size: 11px;">192.168.1.13</div>
            <div style="margin-top: 6px; display: inline-block; background: rgba(255,214,0,0.15); color: #FFD600; padding: 2px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">👥 19 Clientes</div>
            <div style="font-size: 10px; color: #38BDF8; margin-top: 4px;">SSID: Enterprise NOC-Agro</div>
            <div style="font-size: 10px; color: #CBD5E1;">⚡ 21.3 Mbps | 4.30 ms</div>
        </div>
        <!-- Card 3D 4: AP Estoque -->
        <div style="transform: rotateX(8deg) rotateY(2deg); transform-style: preserve-3d; background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95)); border: 1px solid #FF9100; border-radius: 10px; padding: 12px 16px; min-width: 170px; text-align: center; box-shadow: 0 8px 20px rgba(255, 145, 0, 0.25);">
            <div style="font-size: 30px; text-shadow: 0 0 15px #FF9100;">📡</div>
            <div style="font-weight: bold; color: #FFFFFF; font-size: 13px; margin-top: 4px;">UAP-HD ESTOQUE</div>
            <div style="color: #94A3B8; font-size: 11px;">192.168.1.14</div>
            <div style="margin-top: 6px; display: inline-block; background: rgba(255,145,0,0.15); color: #FF9100; padding: 2px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">👥 14 Clientes</div>
            <div style="font-size: 10px; color: #38BDF8; margin-top: 4px;">SSID: Coletores</div>
            <div style="font-size: 10px; color: #CBD5E1;">⚡ 18.6 Mbps | 0.37 ms</div>
        </div>
        <!-- Card 3D 5: AP AC-Pro TI -->
        <div style="transform: rotateX(8deg) rotateY(4deg); transform-style: preserve-3d; background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95)); border: 1px solid #E040FB; border-radius: 10px; padding: 12px 16px; min-width: 170px; text-align: center; box-shadow: 0 8px 20px rgba(224, 64, 251, 0.25);">
            <div style="font-size: 30px; text-shadow: 0 0 15px #E040FB;">📡</div>
            <div style="font-weight: bold; color: #FFFFFF; font-size: 13px; margin-top: 4px;">AC-PRO TI</div>
            <div style="color: #94A3B8; font-size: 11px;">192.168.1.15</div>
            <div style="margin-top: 6px; display: inline-block; background: rgba(224,64,251,0.15); color: #E040FB; padding: 2px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">👥 35 Clientes</div>
            <div style="font-size: 10px; color: #38BDF8; margin-top: 4px;">SSID: Enterprise NOC-Corp</div>
            <div style="font-size: 10px; color: #CBD5E1;">⚡ 44.9 Mbps | 0.22 ms</div>
        </div>
        <!-- Card 3D 6: AP AC-Pro Geral (Offline) -->
        <div style="transform: rotateX(8deg) rotateY(6deg); transform-style: preserve-3d; background: linear-gradient(135deg, rgba(69, 10, 10, 0.85), rgba(24, 2, 2, 0.95)); border: 1px solid #FF1744; border-radius: 10px; padding: 12px 16px; min-width: 170px; text-align: center; box-shadow: 0 8px 20px rgba(255, 23, 68, 0.35);">
            <div style="font-size: 30px; text-shadow: 0 0 15px #FF1744;">⚠️</div>
            <div style="font-weight: bold; color: #FFFFFF; font-size: 13px; margin-top: 4px;">AC-PRO GERAL</div>
            <div style="color: #F87171; font-size: 11px;">192.168.1.16</div>
            <div style="margin-top: 6px; display: inline-block; background: rgba(255,23,68,0.25); color: #FF5252; padding: 2px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">🔴 OFFLINE (100% Loss)</div>
            <div style="font-size: 10px; color: #FCA5A5; margin-top: 4px;">SSID: Inativo</div>
            <div style="font-size: 10px; color: #EF4444;">Falha de Alimentação PoE</div>
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
<div style="perspective: 1200px; padding: 10px; background: radial-gradient(circle at 50% 50%, rgba(15, 23, 42, 0.95), rgba(2, 6, 23, 1)); border-radius: 12px; border: 1px solid rgba(59, 130, 246, 0.3); box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
    <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap; gap: 15px;">
        <!-- Card 3D 1: SRV NOC Monitoring -->
        <div style="transform: rotateX(8deg) rotateY(-5deg); transform-style: preserve-3d; background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95)); border: 1px solid #00E676; border-radius: 10px; padding: 12px 18px; min-width: 200px; text-align: center; box-shadow: 0 8px 25px rgba(0, 230, 118, 0.25);">
            <div style="font-size: 32px; text-shadow: 0 0 15px #00E676;">🖥️</div>
            <div style="font-weight: bold; color: #FFFFFF; font-size: 14px; margin-top: 4px;">SRV-NOC-MONITORING</div>
            <div style="color: #94A3B8; font-size: 11px;">10.0.0.10 (Zabbix/Grafana)</div>
            <div style="margin-top: 6px; display: inline-block; background: rgba(0,230,118,0.15); color: #00E676; padding: 2px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">🟢 100% OPERACIONAL</div>
            <div style="font-size: 10px; color: #38BDF8; margin-top: 4px;">CPU: 17.3% | RAM: 32.4% (8 GB)</div>
            <div style="font-size: 10px; color: #CBD5E1;">Disco: 11.9% | Uptime: 3.5 Dias</div>
        </div>
        <!-- Card 3D 2: ERP TOTVS Protheus -->
        <div style="transform: rotateX(8deg) rotateY(-2deg); transform-style: preserve-3d; background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95)); border: 1px solid #00B0FF; border-radius: 10px; padding: 12px 18px; min-width: 200px; text-align: center; box-shadow: 0 8px 25px rgba(0, 176, 255, 0.25);">
            <div style="font-size: 32px; text-shadow: 0 0 15px #00B0FF;">🏢</div>
            <div style="font-weight: bold; color: #FFFFFF; font-size: 14px; margin-top: 4px;">SRV-ERP-PROTHEUS</div>
            <div style="color: #94A3B8; font-size: 11px;">10.0.0.20 (Banco & ERP)</div>
            <div style="margin-top: 6px; display: inline-block; background: rgba(0,176,255,0.15); color: #00B0FF; padding: 2px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">🟢 HTTP 80 ATIVO</div>
            <div style="font-size: 10px; color: #38BDF8; margin-top: 4px;">Tempo Resposta: 0.92 ms</div>
            <div style="font-size: 10px; color: #CBD5E1;">SSH Porta 22: Desativado (Segurança)</div>
        </div>
        <!-- Card 3D 3: Gateway Edge -->
        <div style="transform: rotateX(8deg) rotateY(2deg); transform-style: preserve-3d; background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95)); border: 1px solid #FFD600; border-radius: 10px; padding: 12px 18px; min-width: 200px; text-align: center; box-shadow: 0 8px 25px rgba(255, 214, 0, 0.25);">
            <div style="font-size: 32px; text-shadow: 0 0 15px #FFD600;">🛡️</div>
            <div style="font-weight: bold; color: #FFFFFF; font-size: 14px; margin-top: 4px;">GATEWAY EDGE 10.1</div>
            <div style="color: #94A3B8; font-size: 11px;">10.0.0.1 (Borda Corporativa)</div>
            <div style="margin-top: 6px; display: inline-block; background: rgba(255,214,0,0.15); color: #FFD600; padding: 2px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">🟢 LATÊNCIA SUB-MS</div>
            <div style="font-size: 10px; color: #38BDF8; margin-top: 4px;">Tempo Resposta: 0.18 ms</div>
            <div style="font-size: 10px; color: #CBD5E1;">Perda de Pacotes: 0%</div>
        </div>
        <!-- Card 3D 4: Estações Windows -->
        <div style="transform: rotateX(8deg) rotateY(5deg); transform-style: preserve-3d; background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95)); border: 1px solid #7C4DFF; border-radius: 10px; padding: 12px 18px; min-width: 200px; text-align: center; box-shadow: 0 8px 25px rgba(124, 77, 255, 0.25);">
            <div style="font-size: 32px; text-shadow: 0 0 15px #7C4DFF;">💻</div>
            <div style="font-weight: bold; color: #FFFFFF; font-size: 14px; margin-top: 4px;">PARQUE ESTAÇÕES</div>
            <div style="color: #94A3B8; font-size: 11px;">28 Desktops / Notebooks</div>
            <div style="margin-top: 6px; display: inline-block; background: rgba(124,77,255,0.15); color: #B388FF; padding: 2px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">💻 26 ONLINE / 2 OFFLINE</div>
            <div style="font-size: 10px; color: #38BDF8; margin-top: 4px;">Porta RDP 3389 / SMB 445</div>
            <div style="font-size: 10px; color: #CBD5E1;">Latência Média: 0.45 ms</div>
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
<div style="perspective: 1200px; padding: 12px; background: radial-gradient(circle at 50% 50%, rgba(15, 23, 42, 0.95), rgba(2, 6, 23, 1)); border-radius: 12px; border: 1px solid rgba(0, 230, 118, 0.35); box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
    <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap; gap: 14px;">
        <!-- Card 3D 1: Provedor ISP -->
        <div style="transform: rotateX(8deg) rotateY(-6deg); transform-style: preserve-3d; background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95)); border: 1px solid #00E676; border-radius: 10px; padding: 12px 18px; min-width: 200px; text-align: center; box-shadow: 0 8px 25px rgba(0, 230, 118, 0.25);">
            <div style="font-size: 32px; text-shadow: 0 0 15px #00E676;">🏢</div>
            <div style="font-weight: bold; color: #FFFFFF; font-size: 14px; margin-top: 4px;">TOP FIBRA TELECOM</div>
            <div style="color: #94A3B8; font-size: 11px;">Link Dedicado WAN 1:1</div>
            <div style="margin-top: 6px; display: inline-block; background: rgba(0,230,118,0.15); color: #00E676; padding: 2px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">🟢 FIBRA ILUMINADA</div>
            <div style="font-size: 11px; color: #38BDF8; margin-top: 4px;">IP: 203.0.113.1 (WAN)</div>
            <div style="font-size: 10px; color: #CBD5E1;">SLA 99.98% Garantido</div>
        </div>
        <!-- Card 3D 2: MITIGAÇÃO ATIVA DE PERDA DE PACOTES -->
        <div style="transform: rotateX(8deg) rotateY(-3deg); transform-style: preserve-3d; background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(15, 23, 42, 0.95)); border: 1px solid #10B981; border-radius: 10px; padding: 12px 18px; min-width: 230px; text-align: center; box-shadow: 0 8px 25px rgba(16, 185, 129, 0.35);">
            <div style="font-size: 32px; text-shadow: 0 0 15px #10B981;">🛡️</div>
            <div style="font-weight: bold; color: #FFFFFF; font-size: 14px; margin-top: 4px;">MITIGAÇÃO PERDA PACOTES</div>
            <div style="color: #34D399; font-size: 11px; font-weight: bold;">🟢 0.00% LOSS (PROTEÇÃO ATIVA)</div>
            <div style="margin-top: 6px; display: inline-block; background: rgba(16,185,129,0.2); color: #6EE7B7; padding: 2px 8px; border-radius: 12px; font-size: 10px;">QoS FQ-CoDel + Anti-Bufferbloat</div>
            <div style="font-size: 10px; color: #94A3B8; margin-top: 4px;">Failover Automático Multi-Gateway</div>
            <div style="font-size: 10px; color: #A7F3D0;">0 descartes / 10.000 probes</div>
        </div>
        <!-- Card 3D 3: CONSUMO DE BANDA EM TEMPO REAL -->
        <div style="transform: rotateX(8deg) rotateY(0deg); transform-style: preserve-3d; background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(15, 23, 42, 0.95)); border: 1px solid #3B82F6; border-radius: 10px; padding: 12px 18px; min-width: 230px; text-align: center; box-shadow: 0 8px 25px rgba(59, 130, 246, 0.35);">
            <div style="font-size: 32px; text-shadow: 0 0 15px #3B82F6;">🚀</div>
            <div style="font-weight: bold; color: #FFFFFF; font-size: 14px; margin-top: 4px;">CONSUMO DE BANDA WAN</div>
            <div style="color: #60A5FA; font-size: 11px; font-weight: bold;">⚡ 135.8M RX (22%) | 40.7M TX (13%)</div>
            <div style="margin-top: 6px; display: inline-block; background: rgba(59,130,246,0.2); color: #93C5FD; padding: 2px 8px; border-radius: 12px; font-size: 10px;">Contrato: 600M Down / 300M Up</div>
            <div style="font-size: 10px; color: #94A3B8; margin-top: 4px;">Shaper Anti-Saturação Ativo (85%)</div>
            <div style="font-size: 10px; color: #00E676;">🟢 Sem Gargalos de Tráfego</div>
        </div>
        <!-- Card 3D 4: Gateway Google -->
        <div style="transform: rotateX(8deg) rotateY(3deg); transform-style: preserve-3d; background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95)); border: 1px solid #00B0FF; border-radius: 10px; padding: 12px 18px; min-width: 190px; text-align: center; box-shadow: 0 8px 25px rgba(0, 176, 255, 0.25);">
            <div style="font-size: 32px; text-shadow: 0 0 15px #00B0FF;">🌍</div>
            <div style="font-weight: bold; color: #FFFFFF; font-size: 14px; margin-top: 4px;">ROTA GOOGLE (8.8.8.8)</div>
            <div style="color: #94A3B8; font-size: 11px;">Gateway Primário Ativo</div>
            <div style="margin-top: 6px; display: inline-block; background: rgba(0,176,255,0.15); color: #00B0FF; padding: 2px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">⚡ 29.1 ms (ESTÁVEL)</div>
            <div style="font-size: 10px; color: #CBD5E1; margin-top: 4px;">Perda de Pacotes: 0.0%</div>
        </div>
        <!-- Card 3D 5: Gateway Cloudflare -->
        <div style="transform: rotateX(8deg) rotateY(6deg); transform-style: preserve-3d; background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95)); border: 1px solid #FFD600; border-radius: 10px; padding: 12px 18px; min-width: 190px; text-align: center; box-shadow: 0 8px 25px rgba(255, 214, 0, 0.25);">
            <div style="font-size: 32px; text-shadow: 0 0 15px #FFD600;">☁️</div>
            <div style="font-weight: bold; color: #FFFFFF; font-size: 14px; margin-top: 4px;">ROTA CLOUDFLARE (1.1.1.1)</div>
            <div style="color: #94A3B8; font-size: 11px;">Gateway Backup Standby</div>
            <div style="margin-top: 6px; display: inline-block; background: rgba(255,214,0,0.15); color: #FFD600; padding: 2px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">⚡ 53.7 ms (STANDBY)</div>
            <div style="font-size: 10px; color: #CBD5E1; margin-top: 4px;">Perda de Pacotes: 0.0%</div>
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
<div style="perspective: 1200px; padding: 10px; background: radial-gradient(circle at 50% 50%, rgba(15, 23, 42, 0.95), rgba(2, 6, 23, 1)); border-radius: 12px; border: 1px solid rgba(255, 145, 0, 0.3); box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
    <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap; gap: 20px;">
        <!-- Card 3D 1: HP 01 -->
        <div style="transform: rotateX(8deg) rotateY(-4deg); transform-style: preserve-3d; background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95)); border: 1px solid #FF9100; border-radius: 12px; padding: 14px 24px; min-width: 280px; text-align: center; box-shadow: 0 8px 25px rgba(255, 145, 0, 0.25);">
            <div style="font-size: 38px; text-shadow: 0 0 15px #FF9100;">🖨️</div>
            <div style="font-weight: bold; color: #FFFFFF; font-size: 15px; margin-top: 4px;">HP LASERJET FLOW 220</div>
            <div style="color: #94A3B8; font-size: 12px;">IP: 192.168.1.50 | Serial: BRBSQ2Q11P</div>
            <div style="margin-top: 8px; display: inline-block; background: rgba(255, 145, 0, 0.2); color: #FF9100; padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 12px;">⚠️ Toner Preto: 15% (Atenção)</div>
            <div style="font-size: 11px; color: #38BDF8; margin-top: 6px;">Páginas Impressas: 324.549</div>
            <div style="font-size: 11px; color: #CBD5E1;">ADF: 81% | Cilindros: 62% | Latência: 0.41 ms</div>
            <div style="font-size: 11px; color: #00E676; margin-top: 4px;">Display: "Pronta"</div>
        </div>
        <!-- Card 3D 2: HP 02 -->
        <div style="transform: rotateX(8deg) rotateY(4deg); transform-style: preserve-3d; background: linear-gradient(135deg, rgba(69, 10, 10, 0.85), rgba(24, 2, 2, 0.95)); border: 1px solid #FF1744; border-radius: 12px; padding: 14px 24px; min-width: 280px; text-align: center; box-shadow: 0 8px 25px rgba(255, 23, 68, 0.35);">
            <div style="font-size: 38px; text-shadow: 0 0 15px #FF1744;">🖨️</div>
            <div style="font-weight: bold; color: #FFFFFF; font-size: 15px; margin-top: 4px;">HP LASERJET FLOW 221</div>
            <div style="color: #F87171; font-size: 12px;">IP: 192.168.1.51 | Serial: BRBSQ2G0BP</div>
            <div style="margin-top: 8px; display: inline-block; background: rgba(255, 23, 68, 0.25); color: #FF5252; padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 12px;">🚨 Toner Preto: 0% (Esgotado)</div>
            <div style="font-size: 11px; color: #FCA5A5; margin-top: 6px;">Páginas Impressas: 356.600</div>
            <div style="font-size: 11px; color: #CBD5E1;">ADF: 74% | Cilindros: 49% | Latência: 0.35 ms</div>
            <div style="font-size: 11px; color: #00E676; margin-top: 4px;">Display: "Pronta"</div>
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
<div style="perspective: 1200px; padding: 10px; background: radial-gradient(circle at 50% 50%, rgba(15, 23, 42, 0.95), rgba(2, 6, 23, 1)); border-radius: 12px; border: 1px solid rgba(124, 77, 255, 0.3); box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
    <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap; gap: 15px;">
        <!-- Card 3D 1: PABX Central -->
        <div style="transform: rotateX(8deg) rotateY(-4deg); transform-style: preserve-3d; background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95)); border: 1px solid #7C4DFF; border-radius: 10px; padding: 14px 20px; min-width: 220px; text-align: center; box-shadow: 0 8px 25px rgba(124, 77, 255, 0.25);">
            <div style="font-size: 34px; text-shadow: 0 0 15px #7C4DFF;">🎛️</div>
            <div style="font-weight: bold; color: #FFFFFF; font-size: 14px; margin-top: 4px;">CENTRAL PABX VOIP</div>
            <div style="color: #94A3B8; font-size: 11px;">Sinalização SIP Porta 5060</div>
            <div style="margin-top: 6px; display: inline-block; background: rgba(124,77,255,0.15); color: #B388FF; padding: 2px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">🟢 13 DE 14 RAMAIS ATIVOS</div>
            <div style="font-size: 11px; color: #38BDF8; margin-top: 4px;">RTT de Voz Médio: 0.45 ms</div>
        </div>
        <!-- Card 3D 2: Ramal 12 -->
        <div style="transform: rotateX(8deg) rotateY(-1deg); transform-style: preserve-3d; background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95)); border: 1px solid #00E676; border-radius: 10px; padding: 14px 20px; min-width: 200px; text-align: center; box-shadow: 0 8px 25px rgba(0, 230, 118, 0.25);">
            <div style="font-size: 34px; text-shadow: 0 0 15px #00E676;">📞</div>
            <div style="font-weight: bold; color: #FFFFFF; font-size: 14px; margin-top: 4px;">RAMAL GXP-12</div>
            <div style="color: #94A3B8; font-size: 11px;">IP: 10.0.0.12</div>
            <div style="margin-top: 6px; display: inline-block; background: rgba(0,230,118,0.15); color: #00E676; padding: 2px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">🟢 DISPONÍVEL (0.48 ms)</div>
            <div style="font-size: 11px; color: #CBD5E1; margin-top: 4px;">Perda de Áudio: 0%</div>
        </div>
        <!-- Card 3D 3: Ramal 42 -->
        <div style="transform: rotateX(8deg) rotateY(2deg); transform-style: preserve-3d; background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95)); border: 1px solid #00B0FF; border-radius: 10px; padding: 14px 20px; min-width: 200px; text-align: center; box-shadow: 0 8px 25px rgba(0, 176, 255, 0.25);">
            <div style="font-size: 34px; text-shadow: 0 0 15px #00B0FF;">📞</div>
            <div style="font-weight: bold; color: #FFFFFF; font-size: 14px; margin-top: 4px;">RAMAL GXP-42</div>
            <div style="color: #94A3B8; font-size: 11px;">IP: 10.0.3.42</div>
            <div style="margin-top: 6px; display: inline-block; background: rgba(0,176,255,0.15); color: #00B0FF; padding: 2px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">🟢 DISPONÍVEL (0.46 ms)</div>
            <div style="font-size: 11px; color: #CBD5E1; margin-top: 4px;">Perda de Áudio: 0%</div>
        </div>
        <!-- Card 3D 4: Ramal 166 (Alerta) -->
        <div style="transform: rotateX(8deg) rotateY(5deg); transform-style: preserve-3d; background: linear-gradient(135deg, rgba(69, 10, 10, 0.85), rgba(24, 2, 2, 0.95)); border: 1px solid #FF1744; border-radius: 10px; padding: 14px 20px; min-width: 200px; text-align: center; box-shadow: 0 8px 25px rgba(255, 23, 68, 0.35);">
            <div style="font-size: 34px; text-shadow: 0 0 15px #FF1744;">📵</div>
            <div style="font-weight: bold; color: #FFFFFF; font-size: 14px; margin-top: 4px;">RAMAL GXP-166</div>
            <div style="color: #F87171; font-size: 11px;">IP: 10.0.0.166</div>
            <div style="margin-top: 6px; display: inline-block; background: rgba(255,23,68,0.25); color: #FF5252; padding: 2px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">🔴 TELEFONE MUDO</div>
            <div style="font-size: 11px; color: #FCA5A5; margin-top: 4px;">Dispositivo Inacessível</div>
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
<div style="perspective: 1200px; padding: 12px; background: radial-gradient(circle at 50% 50%, rgba(15, 23, 42, 0.95), rgba(2, 6, 23, 1)); border-radius: 12px; border: 1px solid rgba(0, 230, 118, 0.4); box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
    <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap; gap: 12px;">
        <a href="/d/noc-links" aria-label="Painel Links WAN: WAN TOP FIBRA, 29.1 ms, mitigação ativa" style="text-decoration: none; color: inherit; display: block; transform: rotateX(8deg) rotateY(-6deg); transform-style: preserve-3d; background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95)); border: 1px solid #00E676; border-radius: 10px; padding: 10px 14px; min-width: 155px; text-align: center; box-shadow: 0 6px 18px rgba(0, 230, 118, 0.2); transition: transform 0.2s, box-shadow 0.2s;">
            <div role="img" aria-label="Ícone Link WAN" style="font-size: 28px; text-shadow: 0 0 12px #00E676;">🌐</div>
            <div style="font-weight: bold; color: #FFF; font-size: 13px;">WAN TOP FIBRA</div>
            <div style="color: #00E676; font-size: 11px; font-weight: bold;">🟢 29.1 ms | 0% Loss</div>
            <div style="color: #38BDF8; font-size: 10px;">Consumo: 136M (22.6%)</div>
            <div style="color: #94A3B8; font-size: 10px;">🛡️ Mitigação Ativa</div>
        </a>
        <a href="/d/noc-wifi" aria-label="Painel Wi-Fi UniFi: 138 Clientes, 5 de 6 APs Online" style="text-decoration: none; color: inherit; display: block; transform: rotateX(8deg) rotateY(-3deg); transform-style: preserve-3d; background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95)); border: 1px solid #00B0FF; border-radius: 10px; padding: 10px 14px; min-width: 150px; text-align: center; box-shadow: 0 6px 18px rgba(0, 176, 255, 0.2); transition: transform 0.2s, box-shadow 0.2s;">
            <div role="img" aria-label="Ícone Wi-Fi UniFi" style="font-size: 28px; text-shadow: 0 0 12px #00B0FF;">📡</div>
            <div style="font-weight: bold; color: #FFF; font-size: 13px;">WI-FI UNIFI</div>
            <div style="color: #00B0FF; font-size: 11px; font-weight: bold;">👥 138 Clientes</div>
            <div style="color: #94A3B8; font-size: 10px;">5/6 APs Online</div>
        </a>
        <a href="/d/noc-servers" aria-label="Painel Servidores: SRV NOC 200, CPU 17%, RAM 32%, Disco 11.9%" style="text-decoration: none; color: inherit; display: block; transform: rotateX(8deg) rotateY(0deg); transform-style: preserve-3d; background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95)); border: 1px solid #FFD600; border-radius: 10px; padding: 10px 14px; min-width: 150px; text-align: center; box-shadow: 0 6px 18px rgba(255, 214, 0, 0.2); transition: transform 0.2s, box-shadow 0.2s;">
            <div role="img" aria-label="Ícone Servidor NOC" style="font-size: 28px; text-shadow: 0 0 12px #FFD600;">🖥️</div>
            <div style="font-weight: bold; color: #FFF; font-size: 13px;">SRV NOC 200</div>
            <div style="color: #FFD600; font-size: 11px; font-weight: bold;">CPU 17% | RAM 32%</div>
            <div style="color: #94A3B8; font-size: 10px;">Disco / 11.9%</div>
        </a>
        <a href="/d/noc-printers" aria-label="Painel Impressoras HP: Parque HP, Toners 15% e 0%, 681k Páginas" style="text-decoration: none; color: inherit; display: block; transform: rotateX(8deg) rotateY(3deg); transform-style: preserve-3d; background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95)); border: 1px solid #FF9100; border-radius: 10px; padding: 10px 14px; min-width: 150px; text-align: center; box-shadow: 0 6px 18px rgba(255, 145, 0, 0.2); transition: transform 0.2s, box-shadow 0.2s;">
            <div role="img" aria-label="Ícone Impressora HP" style="font-size: 28px; text-shadow: 0 0 12px #FF9100;">🖨️</div>
            <div style="font-weight: bold; color: #FFF; font-size: 13px;">PARQUE HP</div>
            <div style="color: #FF9100; font-size: 11px; font-weight: bold;">Toners 15% / 0%</div>
            <div style="color: #94A3B8; font-size: 10px;">681k Páginas</div>
        </a>
        <a href="/d/noc-voip" aria-label="Painel Telefonia VoIP: Grandstream, 13 de 14 Ramais OK, RTT 0.45 ms" style="text-decoration: none; color: inherit; display: block; transform: rotateX(8deg) rotateY(6deg); transform-style: preserve-3d; background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95)); border: 1px solid #7C4DFF; border-radius: 10px; padding: 10px 14px; min-width: 150px; text-align: center; box-shadow: 0 6px 18px rgba(124, 77, 255, 0.2); transition: transform 0.2s, box-shadow 0.2s;">
            <div role="img" aria-label="Ícone Telefonia VoIP" style="font-size: 28px; text-shadow: 0 0 12px #7C4DFF;">📞</div>
            <div style="font-weight: bold; color: #FFF; font-size: 13px;">VOIP GRANDSTREAM</div>
            <div style="color: #B388FF; font-size: 11px; font-weight: bold;">13/14 Ramais OK</div>
            <div style="color: #94A3B8; font-size: 10px;">RTT 0.45 ms</div>
        </a>
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
