$utf8NoBom = New-Object System.Text.UTF8Encoding($False)  
$content = 'line1 ?? test'  
[System.IO.File]::WriteAllText('seasons/01-xianxia/chronicle/_test.txt', $content, $utf8NoBom)  
