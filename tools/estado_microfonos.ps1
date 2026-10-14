# Volumen y silencio de cada micrófono según Windows (Core Audio), para
# diagnosticar un micrófono que Windows detecta pero que graba silencio.
#   powershell -File C:\clip_assistance\tools\estado_microfonos.ps1 [-QuitarSilencio DGM20]
param([string]$QuitarSilencio = "")
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

[Guid("5CDF2C82-841E-4546-9722-0CF74078229A"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IAudioEndpointVolume {
    int RegisterControlChangeNotify(IntPtr p); int UnregisterControlChangeNotify(IntPtr p);
    int GetChannelCount(out uint c); int SetMasterVolumeLevel(float l, Guid g); int SetMasterVolumeLevelScalar(float l, Guid g);
    int GetMasterVolumeLevel(out float l); int GetMasterVolumeLevelScalar(out float l);
    int SetChannelVolumeLevel(uint n, float l, Guid g); int SetChannelVolumeLevelScalar(uint n, float l, Guid g);
    int GetChannelVolumeLevel(uint n, out float l); int GetChannelVolumeLevelScalar(uint n, out float l);
    int SetMute([MarshalAs(UnmanagedType.Bool)] bool m, IntPtr g); int GetMute(out bool m);
}
[Guid("D666063F-1587-4E43-81F1-B948E807363F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IMMDevice {
    int Activate(ref Guid iid, int ctx, IntPtr p, [MarshalAs(UnmanagedType.IUnknown)] out object o);
    int OpenPropertyStore(int a, out IPropertyStore s); int GetId([MarshalAs(UnmanagedType.LPWStr)] out string id); int GetState(out int st);
}
[Guid("886d8eeb-8cf2-4446-8d02-cdba1dbdcf99"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IPropertyStore { int GetCount(out int c); int GetAt(int i, out PROPERTYKEY k); int GetValue(ref PROPERTYKEY k, out PROPVARIANT v); }
[StructLayout(LayoutKind.Sequential)] public struct PROPERTYKEY { public Guid fmtid; public int pid; }
[StructLayout(LayoutKind.Explicit)] public struct PROPVARIANT { [FieldOffset(0)] public short vt; [FieldOffset(8)] public IntPtr p; }
[Guid("0BD7A1BE-7A1A-44DB-8397-CC5392387B5E"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IMMDeviceCollection { int GetCount(out uint c); int Item(uint i, out IMMDevice d); }
[Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IMMDeviceEnumerator {
    int EnumAudioEndpoints(int flow, int mask, out IMMDeviceCollection c);
    int GetDefaultAudioEndpoint(int flow, int role, out IMMDevice d);
}
[ComImport, Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")] class MMDeviceEnumerator { }

public static class Microfonos {
    public static string Estado(string quitar) {
        var en = (IMMDeviceEnumerator)new MMDeviceEnumerator();
        IMMDeviceCollection col; en.EnumAudioEndpoints(1, 1, out col);   // captura, activos
        IMMDevice def; string defId = "";
        if (en.GetDefaultAudioEndpoint(1, 0, out def) == 0) def.GetId(out defId);
        uint n; col.GetCount(out n);
        var sb = new System.Text.StringBuilder();
        var kName = new PROPERTYKEY { fmtid = new Guid("a45c254e-df1c-4efd-8020-67d146a850e0"), pid = 14 };
        for (uint i = 0; i < n; i++) {
            IMMDevice d; col.Item(i, out d);
            string id; d.GetId(out id);
            IPropertyStore ps; d.OpenPropertyStore(0, out ps);
            PROPVARIANT pv; ps.GetValue(ref kName, out pv);
            string nombre = Marshal.PtrToStringUni(pv.p);
            Guid iid = typeof(IAudioEndpointVolume).GUID; object o;
            d.Activate(ref iid, 23, IntPtr.Zero, out o);
            var v = (IAudioEndpointVolume)o;
            if (quitar.Length > 0 && nombre.Contains(quitar)) sb.AppendLine("SetMute(false) -> HRESULT 0x" + v.SetMute(false, IntPtr.Zero).ToString("X8"));
            float vol; v.GetMasterVolumeLevelScalar(out vol); bool mute; v.GetMute(out mute);
            sb.AppendLine(String.Format("{0}{1}: volumen {2:0}%, silenciado: {3}", id == defId ? "[PREDETERMINADO] " : "", nombre, vol * 100, mute ? "SÍ" : "no"));
        }
        return sb.ToString();
    }
}
"@
[Microfonos]::Estado($QuitarSilencio)
