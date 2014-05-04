Module Module1
    Dim canceled As Boolean = False
    Dim dev As USBPassthroughDevice
    Dim u As MAXUSBApp

    Public Function getDevConName(symbolicName As String) As String
        Dim pos1 = InStrRev(symbolicName, "\")
        Dim pos2 = InStrRev(symbolicName, "#") - 1
        Return symbolicName.Substring(pos1, pos2 - pos1).Replace("#", "\")
    End Function

    Public Sub devConReset(devInfo As LibUsbDotNet.Main.UsbRegistry)
        Dim exe As String = IIf(Environment.Is64BitOperatingSystem, "devcon_x64.exe", "devcon_i386.exe")
        Dim p As Process
        Dim psi As New ProcessStartInfo()
        psi.RedirectStandardOutput = True
        psi.RedirectStandardError = True
        psi.UseShellExecute = False
        p = Process.Start(exe, "remove ""@" & getDevConName(devInfo.SymbolicName) & """")
        p.WaitForExit()
        p = Process.Start(exe, "rescan")
        p.WaitForExit()
    End Sub

    Sub Main()
        Dim sp As New System.IO.Ports.SerialPort("COM11", 115200, IO.Ports.Parity.None)
        sp.ReadTimeout = 2000
        Dim fd As New FaceDancer(sp, 1)
        u = New MAXUSBApp(fd, 1)

        Dim devLibList As LibUsbDotNet.Main.UsbRegDeviceList = LibUsbDotNet.UsbDevice.AllLibUsbDevices
        Dim devLib As LibUsbDotNet.UsbDevice = Nothing

        devConReset(devLibList(0))
        While devLib Is Nothing
            devLibList(0).Open(devLib)
            System.Threading.Thread.Sleep(100)
        End While

        Dim dev As New USBPassthroughDevice(devLib, u, 4)

        For Each i As LibUsbDotNet.Info.UsbInterfaceInfo In devLib.Configs(0).InterfaceInfoList
            For Each e As LibUsbDotNet.Info.UsbEndpointInfo In i.EndpointInfoList
                Debug.Print(i.Descriptor.InterfaceID & ":" & e.Descriptor.EndpointID & ":" & e.Descriptor.Attributes)
            Next
        Next
        dev.connect()

        dev.run()
    End Sub

    Sub cleanup(sender As Object, e As ConsoleCancelEventArgs)
        e.Cancel = True
        canceled = True
        If Not dev Is Nothing Then dev.disconnect()
        u.looping = False
    End Sub

    Sub test()
        Dim sp As New System.IO.Ports.SerialPort("COM11", 115200, IO.Ports.Parity.None)
        sp.ReadTimeout = 2000
        Dim fd As New FaceDancer(sp)
        fd.monitor_app.print_info()
        fd.monitor_app.list_apps()

        If fd.monitor_app.echo("I am the very model of a modern major general.") Then
            Debug.Print("echo succeeded")
        Else
            Debug.Print("echo failed")
        End If
    End Sub

End Module
