Imports System.Text.Encoding
Imports System.IO.Ports
Public Class FaceDancer
    Public serialport As SerialPort
    Public verbose As Byte
    Public monitor_app As GoodFETMonitorApp

    Public Sub New(serialport As SerialPort, Optional verbose As Byte = 0)
        Me.serialport = serialport
        Me.verbose = verbose
        Me.reset()
        Me.monitor_app = New GoodFETMonitorApp(Me, Me.verbose)
        Me.monitor_app.announce_connected()
    End Sub

    Public Sub halt()
        Me.serialport.DtrEnable = True
        Me.serialport.RtsEnable = True
        System.Threading.Thread.Sleep(100)
    End Sub

    Public Sub reset()
        If Me.verbose > 0 Then Debug.Print("Facedancer resetting...")
        If Not Me.serialport.IsOpen Then Me.serialport.Open()
        Me.halt()
        Me.serialport.DtrEnable = False
        System.Threading.Thread.Sleep(100)

        Me.readcmd()
        If Me.verbose > 0 Then Debug.Print("Facedancer reset")
    End Sub

    Public Function read(n As Integer) As Byte()
        Dim buf(n - 1) As Byte
        Dim c As Integer = 0
        Do
            c = c + Me.serialport.Read(buf, c, n - c)
        Loop Until c = n
        If Me.verbose > 3 Then Debug.Print("Facedancer received " & buf.Length & " bytes; " & Me.serialport.BytesToRead & " bytes remaining")
        If Me.verbose > 2 Then Debug.Print("Facedancer Rx:" & BitConverter.ToString(buf))
        Return buf
    End Function

    Public Function readcmd() As FacedancerCommand
        Dim buf() As Byte = Me.read(4)
        Dim app As Byte = buf(0)
        Dim verb As Byte = buf(1)
        Dim length As UInt16 = buf(2) + buf(3) * 256
        Dim data() As Byte = Nothing
        If length > 0 Then
            data = Me.read(length)
            If data.Length <> length Then Throw New Exception("Facedancer expected " & length & " bytes but received only " & data.Length)
        End If
        Dim cmd As New FacedancerCommand(app, verb, data)
        If Me.verbose > 1 Then Debug.Print("Facedancer Rx command:" & cmd.ToString)
        Return cmd
    End Function

    Public Sub write(buf() As Byte)
        If Me.verbose > 2 Then Debug.Print("Facedancer Tx:" & BitConverter.ToString(buf))
        Me.serialport.Write(buf, 0, buf.Length)
    End Sub

    Public Sub writecmd(c As FacedancerCommand)
        Me.write(c.as_bytestring())
        If Me.verbose > 1 Then Debug.Print("Facedancer Tx comand: " & c.ToString())
    End Sub
End Class

Public Class FacedancerCommand
    Public app As Byte
    Public verb As Byte
    Public data() As Byte

    Public Sub New(app As Byte, verb As Byte, data() As Byte)
        Me.app = app
        Me.verb = verb
        If data Is Nothing Then
            Me.data = New Byte() {}
        Else
            Me.data = data
        End If
    End Sub

    Public Overrides Function ToString() As String
        Return "app 0x" & app.ToString("X2") & ", verb 0x" & verb.ToString("X2") & ", len " & Me.data.Length & " " & BitConverter.ToString(Me.data)
    End Function

    Public Function long_string() As String
        Dim sb As New Text.StringBuilder()
        sb.AppendLine("app: " & Me.app)
        sb.AppendLine("verb: " & Me.verb)
        sb.AppendLine("len: " & Me.data.Length)
        If Me.data.Length > 0 Then
            Try
                sb.Append(UTF8.GetString(Me.data))
            Catch e As Exception
                sb.Append(BitConverter.ToString(Me.data))
            End Try
        End If
        Return sb.ToString
    End Function

    Public Function as_bytestring() As Byte()
        Dim length As UInt16 = Me.data.Length
        Dim buf(length + 3) As Byte
        buf(0) = Me.app
        buf(1) = Me.verb
        buf(2) = length And 255
        buf(3) = length \ 256
        Array.Copy(Me.data, 0, buf, 4, data.Length)
        Return buf
    End Function
End Class

Public Class FacedancerApp
    Public app_name As String = "override_this"
    Public app_num As Byte = 0
    Public enable_app_cmd As FacedancerCommand
    Public device As FaceDancer
    Public verbose As Byte

    Public Sub New(app_name As String, app_num As Byte, device As FaceDancer, verbose As Byte)
        Me.app_name = app_name
        Me.app_num = app_num
        Me.device = device
        Me.verbose = verbose
        Me.init_commands()
        If Me.verbose > 0 Then Debug.Print(Me.app_name & " initialized")
    End Sub

    Public Sub New(device As FaceDancer, verbose As Byte)
        Me.device = device
        Me.verbose = verbose
        Me.init_commands()
        If Me.verbose > 0 Then Debug.Print(Me.app_name & " initialized")
    End Sub

    Public Overridable Sub init_commands()
    End Sub

    Public Sub enable()
        For i As Integer = 0 To 3
            Me.device.writecmd(Me.enable_app_cmd)
            Me.device.readcmd()
        Next
        If Me.verbose > 0 Then Debug.Print("enabled")
    End Sub
End Class

Public Class GoodFETMonitorApp
    Inherits FacedancerApp

    Public Sub New(device As FaceDancer, Optional verbose As Byte = 0)
        MyBase.New("GoodFET monitor", 0, device, verbose)
    End Sub

    Public Function read_byte(addr) As Byte
        Dim data() As Byte = New Byte() {addr And 255, addr \ 256}
        Dim cmd As New FacedancerCommand(0, 2, data)
        Me.device.writecmd(cmd)
        Dim resp As FacedancerCommand = Me.device.readcmd()
        Return resp.data(0)
    End Function

    Public Function get_infostring() As Byte()
        Return New Byte() {Me.read_byte(&HFF0), Me.read_byte(&HFF1)}
    End Function

    Public Function get_clocking() As Byte()
        Return New Byte() {Me.read_byte(&H57), Me.read_byte(&H56)}
    End Function

    Public Sub print_info()
        Dim infostring As String = BitConverter.ToString(get_infostring)
        Dim clocking As String = BitConverter.ToString(get_clocking)
        Debug.Print("MCU " & infostring)
        Debug.Print("clocked at " & clocking)
    End Sub

    Public Sub list_apps()
        Dim cmd As New FacedancerCommand(Me.app_num, &H82, New Byte() {1})
        Me.device.writecmd(cmd)
        Dim resp As FacedancerCommand = Me.device.readcmd
        Debug.Print("build date: " & UTF8.GetString(resp.data))
        Debug.Print("firmware apps")
        Do
            resp = Me.device.readcmd
            If resp.data.Length > 0 Then Debug.Print(UTF8.GetString(resp.data))
        Loop Until resp.data.Length = 0
    End Sub

    Public Function echo(s As String) As Boolean
        Dim buf() As Byte = UTF8.GetBytes(s)
        Dim cmd As New FacedancerCommand(Me.app_num, &H81, buf)
        Me.device.writecmd(cmd)
        Dim resp As FacedancerCommand = Me.device.readcmd
        If resp.data.Length <> buf.Length Then Return False
        For i = 0 To buf.Length - 1
            If buf(i) <> resp.data(i) Then Return False
        Next
        Return True
    End Function

    Public Sub announce_connected()
        Dim cmd As New FacedancerCommand(Me.app_num, &HB1, Nothing)
        Me.device.writecmd(cmd)
        Dim resp As FacedancerCommand = Me.device.readcmd()
    End Sub
End Class
