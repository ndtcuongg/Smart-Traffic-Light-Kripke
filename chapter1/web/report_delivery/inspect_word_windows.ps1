Add-Type -TypeDefinition @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public class ReportWindowInspect {
 public delegate bool WindowCallback(IntPtr hwnd, IntPtr data);
 [DllImport("user32.dll")] public static extern bool EnumWindows(WindowCallback cb,IntPtr data);
 [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hwnd,out uint process);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr hwnd,StringBuilder s,int max);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)] public static extern int GetClassName(IntPtr hwnd,StringBuilder s,int max);
 [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hwnd);
}
"@
$inspectPid=51700
$found=[Collections.Generic.List[object]]::new()
$callback=[ReportWindowInspect+WindowCallback]{ param($handle,$data)
 $windowPid=[uint32]0
 [void][ReportWindowInspect]::GetWindowThreadProcessId($handle,[ref]$windowPid)
 if($windowPid -eq $inspectPid){
  $title=[Text.StringBuilder]::new(500);$className=[Text.StringBuilder]::new(100)
  [void][ReportWindowInspect]::GetWindowText($handle,$title,500)
  [void][ReportWindowInspect]::GetClassName($handle,$className,100)
  $found.Add(@{handle=$handle.ToInt64();title=$title.ToString();class=$className.ToString();visible=[ReportWindowInspect]::IsWindowVisible($handle)})
 }
 return $true
}
[void][ReportWindowInspect]::EnumWindows($callback,[IntPtr]::Zero)
$found | ConvertTo-Json -Depth 3
