Public Class USBKeyboardInterface
    Inherits USBInterface
    Public keys As New List(Of Byte)

    Public Sub New(Optional verbose As Byte = 0)
        MyBase.new(0, 0, 3, 0, 0, 0, verbose, Nothing, Nothing)
        Me.name = "USB keyboard interface"
        Me.endpoints(3) = New USBEndpoint(3, _
                                   USBEndpoint.enum_direction._in, _
                                   USBEndpoint.enum_transfer_type._interrupt, _
                                   USBEndpoint.enum_sync_type._none, _
                                   USBEndpoint.enum_usage_type._data, _
                                   16384, _
                                   10, _
                                   AddressOf Me.handle_buffer_available)
        Me.endpoints(3).set_interface(Me)
        Me.descriptors.Add(USB.desc_type._hid, AddressOf Me.hid_descriptor)
        Me.descriptors.Add(USB.desc_type._report, AddressOf Me.report_descriptor)
        keys.AddRange(New Byte() {0, 0, 0, 0, 0, 0, 0, 0, 0, 0})
        '        # "l<KEY UP>s<KEY UP><ENTER><KEY UP>"
        keys.AddRange(New Byte() {&HF, 0, &H16, 0, &H28, 0})
    End Sub

    Public Function hid_descriptor(n As Byte) As Byte()
        Return New Byte() {&H9, &H21, &H10, &H1, &H0, &H1, &H22, &H2B, &H0}
    End Function

    Public Function report_descriptor(n As Byte) As Byte()
        Return New Byte() {&H5, &H1, &H9, &H6, &HA1, &H1, &H5, &H7, &H19, &HE0, &H29, &HE7, &H15, &H0, &H25, &H1, &H75, &H1, &H95, &H8, &H81, &H2, &H95, &H1, &H75, &H8, &H81, &H1, &H19, &H0, &H29, &H65, &H15, &H0, &H25, &H65, &H75, &H8, &H95, &H1, &H81, &H0, &HC0}
    End Function

    Public Sub handle_buffer_available()
        If Me.keys.Count = 0 Then Exit Sub
        Dim letter As Byte = Me.keys(0)
        Me.keys.RemoveAt(0)
        Me.type_letter(letter)
    End Sub

    Public Sub type_letter(letter As Byte, Optional modifiers As Byte = 0)
        Dim data() As Byte = New Byte() {0, 0, letter}
        If Me.verbose > 2 Then Debug.Print(Me.name & " sending keypress 0x" & letter.ToString("X2"))
        Me.configuration.device.maxusb_app.send_on_endpoint(3, data, Me.endpoints(3).max_packet_size)
    End Sub
End Class

Public Class USBKeyboardDevice
    Inherits USBDevice
    
    Public Sub New(maxusb_app As MAXUSBApp, Optional verbose As Byte = 0)
        MyBase.new(maxusb_app, 0, 0, 0, 64, &H610B, &H4653, &H3412, "Maxim", "MAX3420E Enum Code", "S/N3420E", New USBConfiguration() {New USBConfiguration(1, "Emulated Keyboard", New USBInterface() {New USBKeyboardInterface})}, Nothing, verbose)
        Me.name = "USB Keyboard device"
    End Sub
End Class
