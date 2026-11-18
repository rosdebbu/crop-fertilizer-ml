param($src,$dst)
$w = New-Object -ComObject Word.Application
$w.Visible = $false; $w.DisplayAlerts = 0
$d = $w.Documents.Open($src, $false, $true)
$d.ExportAsFixedFormat($dst, 17)
$d.Close(0); $w.Quit()
