Public Class USBInterface
    Implements IRequest_Recipient
    Implements IRequest_Handler

    Public name As String = "generic USB interface"
    Public number As Byte
    Public alternate As Byte
    Public iclass As Byte
    Public subclass As Byte
    Public protocol As Byte
    Public string_index As Byte
    Public verbose As Byte
    Public device_class As USBClass
    Public configuration As USBConfiguration

    Public endpoints As New Dictionary(Of Byte, USBEndpoint)

    Public request_handlers As New Dictionary(Of Byte, Action(Of USBDeviceRequest))
    Public descriptors As New Dictionary(Of USB.desc_type, Func(Of Byte, Byte()))

    Public ReadOnly Property get_request_handlers As Dictionary(Of Byte, Action(Of USBDeviceRequest)) Implements IRequest_Handler.get_request_handlers
        Get
            Return request_handlers
        End Get
    End Property

    Public ReadOnly Property get_device_class As USBClass Implements IRequest_Recipient.get_device_class
        Get
            Return device_class
        End Get
    End Property
    Public ReadOnly Property get_device_vendor As USBVendor Implements IRequest_Recipient.get_device_vendor
        Get
            Return configuration.device.get_device_vendor
        End Get
    End Property

    Public Sub New()

    End Sub

    Public Sub New(interface_number As Byte, interface_alternate As Byte, interface_class As Byte, interface_subclass As Byte, interface_protocol As Byte, _
                   interface_string_index As Byte, Optional verbose As Byte = 0, Optional endpoints() As USBEndpoint = Nothing, Optional descriptors As Dictionary(Of USB.desc_type, Func(Of Byte, Byte())) = Nothing)
        Me.number = interface_number
        Me.alternate = interface_alternate
        Me.iclass = interface_class
        Me.subclass = interface_subclass
        Me.protocol = interface_protocol
        Me.string_index = interface_string_index
        If Not endpoints Is Nothing Then
            For Each e As USBEndpoint In endpoints
                Me.endpoints.Add(e.number, e)
            Next
        End If
        If Not descriptors Is Nothing Then Me.descriptors = descriptors
        Me.verbose = verbose
        If Me.descriptors.ContainsKey(USB.desc_type._interface) Then Me.descriptors(USB.desc_type._interface) = AddressOf Me.get_descriptor Else Me.descriptors.Add(USB.desc_type._interface, AddressOf Me.get_descriptor)
        Me.configuration = Nothing
        Me.device_class = Nothing

        Me.request_handlers.Add(6, AddressOf handle_get_descriptor_request)
        Me.request_handlers.Add(11, AddressOf handle_set_interface_request)
        For Each e As USBEndpoint In Me.endpoints.Values
            e.set_interface(Me)
        Next
    End Sub


    Public Sub set_configuration(config As USBConfiguration)
        Me.configuration = config
    End Sub

    '    # USB 2.0 specification, section 9.4.3 (p 281 of pdf)
    '    # HACK: blatant copypasta from USBDevice pains me deeply
    Public Sub handle_get_descriptor_request(req As USBDeviceRequest)
        Dim dtype As Byte = req.value \ 256 And 255
        Dim dindex As Byte = req.value And 255
        Dim lang As UInt16 = req.index
        Dim n As Byte = req.length
        Dim response() As Byte = Nothing
        If Me.verbose > 2 Then Debug.Print(Me.number & " received GET_DESCRIPTOR req " & dtype & ", index " & dindex & ", language 0x" & lang.ToString("X4") & ", length " & n)
        Dim responseFunc As Func(Of Byte, Byte()) = Nothing
        Me.descriptors.TryGetValue(dtype, responseFunc)
        If Not responseFunc Is Nothing Then response = responseFunc(dindex)
        If Not response Is Nothing Then
            n = Math.Min(n, response.Length)
            Dim tmp(n - 1) As Byte
            Array.Copy(response, 0, tmp, 0, n)
            Me.configuration.device.maxusb_app.send_on_endpoint(0, tmp, Me.configuration.device.max_packet_size_ep0)
            If Me.verbose > 5 Then Debug.Print(Me.name & " sent " & n & " bytes in response")
        End If
    End Sub

    Public Sub handle_set_interface_request(req As USBDeviceRequest)
        Me.configuration.device.maxusb_app.stall_ep0()
    End Sub

    Public Overridable Function get_descriptor(n As Byte) As Byte()
        Dim d As New List(Of Byte)
        d.AddRange(New Byte() {9, 4, Me.number, Me.alternate, Me.endpoints.Count, Me.iclass, Me.subclass, Me.protocol, Me.string_index})
        If Me.iclass Then
            Dim iclass_desc_num As Byte = USB.interface_class_to_descriptor_type(Me.iclass)
            If iclass_desc_num > 0 Then d.AddRange(Me.descriptors(iclass_desc_num)(n))
        End If
        For Each e As USBEndpoint In Me.endpoints.Values
            d.AddRange(e.get_descriptor(0))
        Next e
        Return d.ToArray
    End Function

End Class
