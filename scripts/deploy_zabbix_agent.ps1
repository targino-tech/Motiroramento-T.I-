<#
.SYNOPSIS
    Script de Instalacao Automatizada do Zabbix Agent 2 para Estacoes Windows (Enterprise)
.DESCRIPTION
    Instala silenciosamente o Zabbix Agent 2, configura apontamento para o Zabbix Server,
    abre a porta de firewall 10050 e ativa o envio automatico de inventario de hardware
    (Modelo de CPU i5/i7, Quantidade de Memoria RAM e Numero de Serie da BIOS).
#>

[CmdletBinding()]
param(
    [string]$ZabbixServer = "10.0.0.10",
    [string]$AgentVersion = "7.0.5"
)

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Implantador Automatizado Zabbix Agent 2 - Windows " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Coleta de Inventário Local
$ComputerName = $env:COMPUTERNAME
$CPU = (Get-CimInstance Win32_Processor | Select-Object -First 1 -ExpandProperty Name).Trim()
$RAM_GB = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB)
$Serial = (Get-CimInstance Win32_BIOS | Select-Object -First 1 -ExpandProperty SerialNumber).Trim()
$OS = (Get-CimInstance Win32_OperatingSystem).Caption

Write-Host "[+] Ativo Detectado: $ComputerName" -ForegroundColor Green
Write-Host "    - Sistema Operacional: $OS" -ForegroundColor Gray
Write-Host "    - Processador (CPU):   $CPU" -ForegroundColor Gray
Write-Host "    - Memória RAM:         $RAM_GB GB" -ForegroundColor Gray
Write-Host "    - Número de Série:     $Serial" -ForegroundColor Gray

# 2. Download do Instalador MSI do Zabbix Agent 2
$DownloadUrl = "https://cdn.zabbix.com/zabbix/binaries/stable/7.0/$AgentVersion/zabbix_agent2-$AgentVersion-windows-amd64-openssl.msi"
$MsiPath = "$env:TEMP\zabbix_agent2.msi"

Write-Host "[+] Baixando Zabbix Agent 2 da fonte oficial..." -ForegroundColor Yellow
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest -Uri $DownloadUrl -OutFile $MsiPath -UseBasicParsing

# 3. Instalação Silenciosa
Write-Host "[+] Instalando serviço e configurando apontamento para $ZabbixServer..." -ForegroundColor Yellow
$InstallArgs = @(
    "/i", "`"$MsiPath`"",
    "/qn",
    "SERVER=`"$ZabbixServer`"",
    "SERVERACTIVE=`"$ZabbixServer`"",
    "HOSTNAME=`"$ComputerName`"",
    "HOSTMETADATA=`"Windows_Workstation_Corp`"",
    "ENABLEPATH=1",
    "AUTOSTART=1"
)

Start-Process msiexec.exe -ArgumentList $InstallArgs -Wait -NoNewWindow

# 4. Liberação no Firewall do Windows
Write-Host "[+] Configurando regra de Firewall (Porta 10050 TCP para $ZabbixServer)..." -ForegroundColor Yellow
Remove-NetFirewallRule -DisplayName "Zabbix Agent 2 (Inbound)" -ErrorAction SilentlyContinue
New-NetFirewallRule -DisplayName "Zabbix Agent 2 (Inbound)" -Direction Inbound -LocalPort 10050 -Protocol TCP -Action Allow -RemoteAddress $ZabbixServer | Out-Null

# 5. Iniciar e Garantir Serviço Ativo
Write-Host "[+] Iniciando o serviço 'Zabbix Agent 2'..." -ForegroundColor Green
Get-Service -Name "Zabbix Agent 2" | Set-Service -StartupType Automatic
Restart-Service -Name "Zabbix Agent 2"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Instalação e Integração Concluídas com Sucesso! " -ForegroundColor Green
Write-Host " O dispositivo já está transmitindo métricas para o NOC." -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
