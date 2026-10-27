#!/usr/bin/env python3
"""
generate_mobile_access.py
Gera o QR Code e links seguros de acesso remoto mobile para o Grafana.
"""

import subprocess
import re
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACTS_DIR = os.environ.get("ARTIFACTS_DIR", PROJECT_ROOT)

def get_tunnel_url():
    cmd = ["docker", "logs", "cloudflared"]
    out = subprocess.run(cmd, capture_output=True, text=True)
    matches = re.findall(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", out.stdout + out.stderr)
    if matches:
        return matches[-1]
    return None

def main():
    print("=== OBTENDO URL DO TÚNEL CLOUDFLARE ZERO-TRUST ===")
    url = get_tunnel_url()
    if not url:
        print("[ERRO] Não foi possível encontrar a URL do túnel. Verifique se o container 'cloudflared' está ativo.")
        sys.exit(1)

    print(f"URL Remota Ativa: {url}")

    # Salva em arquivo texto local
    url_file = os.path.join(PROJECT_ROOT, "MOBILE_ACCESS_URL.txt")
    with open(url_file, "w") as f:
        f.write(url + "\n")
    print(f"Salvo em {url_file}")

    # Gera QR Code usando container Python isolado
    qr_local_path = os.path.join(PROJECT_ROOT, "mobile_grafana_qr.png")

    py_script = f"""
import qrcode
qr = qrcode.QRCode(version=1, box_size=10, border=3)
qr.add_data('{url}')
qr.make(fit=True)
img = qr.make_image(fill_color='black', back_color='white')
img.save('/out/mobile_grafana_qr.png')
print('QR Code gerado com sucesso!')
"""

    docker_cmd = [
        "docker", "run", "--rm",
        "-v", f"{PROJECT_ROOT}:/out",
        "python:3-alpine",
        "sh", "-c",
        f"pip install --quiet qrcode pillow && python -c \"{py_script}\""
    ]
    subprocess.run(docker_cmd, check=True)

    if ARTIFACTS_DIR != PROJECT_ROOT and os.path.isdir(ARTIFACTS_DIR):
        qr_artifact_path = os.path.join(ARTIFACTS_DIR, "mobile_grafana_qr.png")
        subprocess.run(["cp", qr_local_path, qr_artifact_path], check=False)

    mobile_user = os.environ.get("MOBILE_VIEWER_USER", "noc.mobile")
    mobile_pass = os.environ.get("MOBILE_VIEWER_PASSWORD", "NocMobile@2026!")

    print("\n" + "="*70)
    print("🚀 ACESSO REMOTO GRAFANA NOC MASTER 360° (MOBILE / QUALQUER REDE)")
    print("="*70)
    print(f"🔗 URL Principal (HTTPS Seguro): {url}")
    print(f"👤 Usuário Celular: {mobile_user}")
    print(f"🔑 Senha:           {mobile_pass}")
    print(f"🔒 Nível:           Viewer (Visualização Protegida, Imune a Cliques Acidentais)")
    print("\n📱 Dashboards Otimizados para Celular (Modo Kiosk Fullscreen):")
    print(f"  🌾 Master NOC 360°:     {url}/d/noc-master?kiosk")
    print(f"  📶 Wi-Fi UniFi:         {url}/d/noc-wifi?kiosk")
    print(f"  🌐 Links WAN Telecom:   {url}/d/noc-links?kiosk")
    print(f"  🖥️ Servidores & NOC:    {url}/d/noc-servers?kiosk")
    print(f"  🖨️ Impressoras HP:      {url}/d/noc-printers?kiosk")
    print(f"  📞 Telefonia & VoIP:    {url}/d/noc-voip?kiosk")
    print("="*70)

if __name__ == "__main__":
    main()
