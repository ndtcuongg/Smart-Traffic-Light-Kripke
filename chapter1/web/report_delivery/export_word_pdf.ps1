$ErrorActionPreference='Stop'; $PID | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'quality_checks/word_export_worker.pid')
$delivery=(Resolve-Path -LiteralPath $PSScriptRoot).Path
$docxPath=Join-Path $delivery 'BIEN_BAN_KIEM_THU_PHAN_MEM_CHUONG_1.docx'
$pdfPath=Join-Path $delivery 'BIEN_BAN_KIEM_THU_PHAN_MEM_CHUONG_1.pdf'
function Stage($message) { Add-Content -LiteralPath (Join-Path $delivery 'quality_checks/export_steps.log') -Value $message -Encoding UTF8 }; Stage('Begin export'); $wordApp=$null
$openedDoc=$null
try {
    $wordApp=New-Object -ComObject Word.Application
    Stage('Word application created'); $wordApp.Options.CheckSpellingAsYouType=$false; $wordApp.Options.CheckGrammarAsYouType=$false; $wordApp.Options.PrintBackground=$false; $wordApp.Options.UpdateLinksAtOpen=$false; $wordApp.Visible=$false
    $wordApp.DisplayAlerts=0
    $wordApp.AutomationSecurity=3
    $wordApp.Options.SaveNormalPrompt=$false
    Stage('Opening DOCX'); $openedDoc=$wordApp.Documents.Open($docxPath,$false,$true,$false)
    Stage('DOCX opened; repaginating'); $openedDoc.Repaginate()
    Stage('Updating fields'); $openedDoc.Fields.Update() | Out-Null
    Stage('Counting pages'); $pages=$openedDoc.ComputeStatistics(2)
    @{status='DOCX_OPENED';application='Microsoft Word';version=$wordApp.Version;read_only=$openedDoc.ReadOnly;page_count=$pages;table_count=$openedDoc.Tables.Count;embedded_images=$openedDoc.InlineShapes.Count} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $delivery 'quality_checks/word_open.json') -Encoding UTF8; Stage('Exporting PDF with explicit options'); $openedDoc.ExportAsFixedFormat($pdfPath,17,$false,0,0,1,999,0,$true,$false,1,$true,$true,$false); Stage('PDF exported')
    $result=@{status='PASS';application='Microsoft Word';version=$wordApp.Version;opened_docx=$openedDoc.Name;read_only=$openedDoc.ReadOnly;page_count=$pages;table_count=$openedDoc.Tables.Count;embedded_images=$openedDoc.InlineShapes.Count;pdf_exported=(Test-Path -LiteralPath $pdfPath)}
    $result | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $delivery 'quality_checks/word_open_export.json') -Encoding UTF8
    $result | ConvertTo-Json
} finally {
    if ($openedDoc) { $openedDoc.Close(0); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($openedDoc) }
    if ($wordApp) { $wordApp.Quit(); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($wordApp) }
}


