# Exporta contas de usuário HABILITADAS no AD sem logon há mais de N dias.
# Somente leitura: não altera nem desabilita nada.
# Requer o módulo ActiveDirectory (RSAT) e uma conta com permissão de leitura no domínio.
# Uso:  .\exportar_contas_ad.ps1            (90 dias)
#       .\exportar_contas_ad.ps1 -Dias 120

param([int]$Dias = 90)

Import-Module ActiveDirectory

$saida = Join-Path $PSScriptRoot 'contas_inativas.csv'

Search-ADAccount -AccountInactive -TimeSpan (New-TimeSpan -Days $Dias) -UsersOnly |
    Where-Object { $_.Enabled } |
    Select-Object SamAccountName, Name,
        @{ Name = 'LastLogonDate'; Expression = { if ($_.LastLogonDate) { $_.LastLogonDate.ToString('dd/MM/yyyy') } else { 'nunca' } } } |
    Sort-Object SamAccountName |
    Export-Csv -Path $saida -NoTypeInformation -Encoding UTF8 -Delimiter ';'

Write-Host "Arquivo gerado: $saida"
Write-Host "Obs.: LastLogonDate vem de lastLogonTimestamp, que replica com atraso de 9 a 14 dias entre DCs."
