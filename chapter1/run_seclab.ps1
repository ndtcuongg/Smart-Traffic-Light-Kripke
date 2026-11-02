param([Parameter(Mandatory=$true)][string]$ScriptPath)
$ErrorActionPreference = 'Stop'
$runtimeRoot = Join-Path (Split-Path $PSScriptRoot -Parent) '.chapter1-tools\seclab'
$resolvedScript = (Resolve-Path -LiteralPath $ScriptPath).Path
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public static class Chapter1Python {
 [DllImport("kernel32.dll", CharSet=CharSet.Unicode)] public static extern bool SetDllDirectory(string path);
 [DllImport("kernel32.dll", CharSet=CharSet.Unicode)] public static extern IntPtr LoadLibrary(string path);
 [DllImport("kernel32.dll", CharSet=CharSet.Ansi)] public static extern IntPtr GetProcAddress(IntPtr lib, string name);
 [UnmanagedFunctionPointer(CallingConvention.Cdecl)] public delegate void SetPath([MarshalAs(UnmanagedType.LPWStr)] string path);
 [UnmanagedFunctionPointer(CallingConvention.Cdecl)] public delegate void Initialize();
 [UnmanagedFunctionPointer(CallingConvention.Cdecl)] public delegate int Run([MarshalAs(UnmanagedType.LPStr)] string code);
 [UnmanagedFunctionPointer(CallingConvention.Cdecl)] public delegate int Finalize();
 public static int Execute(string root, string script) {
  SetDllDirectory(root);
  IntPtr lib = LoadLibrary(System.IO.Path.Combine(root, "python314.dll"));
  if (lib == IntPtr.Zero) throw new Exception("Cannot load Python 3.14 runtime");
  var path=(SetPath)Marshal.GetDelegateForFunctionPointer(GetProcAddress(lib,"Py_SetPath"),typeof(SetPath));
  var init=(Initialize)Marshal.GetDelegateForFunctionPointer(GetProcAddress(lib,"Py_Initialize"),typeof(Initialize));
  var run=(Run)Marshal.GetDelegateForFunctionPointer(GetProcAddress(lib,"PyRun_SimpleString"),typeof(Run));
  var fini=(Finalize)Marshal.GetDelegateForFunctionPointer(GetProcAddress(lib,"Py_FinalizeEx"),typeof(Finalize));
  path(root + ";" + System.IO.Path.Combine(root,"base_library.zip")); init();
  string escaped=script.Replace("\\", "/").Replace("'", "\\'");
  int status=run("import runpy; runpy.run_path('"+escaped+"', run_name='__main__')");
  int end=fini(); return status != 0 ? 1 : end;
 }
}
"@
exit [Chapter1Python]::Execute($runtimeRoot, $resolvedScript)
