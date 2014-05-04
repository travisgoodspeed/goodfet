Public Class USBEndpoint
    Implements IRequest_Recipient
    Implements IRequest_Handler

    Public Enum enum_direction
        _out = &H0
        _in = &H1
    End Enum

    Public Enum enum_transfer_type
        _control = &H0
        _isochronous = &H1
        _bulk = &H2
        _interrupt = &H3
    End Enum

    Public Enum enum_sync_type
        _none = &H0
        _async = &H1
        _adaptive = &H2
        _synchronous = &H3
    End Enum

    Public Enum enum_usage_type
        _data = &H0
        _feedback = &H1
        _implicit_feedback = &H2
    End Enum

    Public number As Byte
    Public direction As enum_direction
    Public transfer_type As enum_transfer_type
    Public sync_type As enum_sync_type
    Public usage_type As enum_usage_type
    Public max_packet_size As UInt16
    Public interval As Byte
    Public handler As Action(Of Byte())
    Public _interface As USBInterface

    Public request_handlers As New Dictionary(Of Byte, Action(Of USBDeviceRequest))

    Public ReadOnly Property get_request_handlers As Dictionary(Of Byte, Action(Of USBDeviceRequest)) Implements IRequest_Handler.get_request_handlers
        Get
            Return request_handlers
        End Get
    End Property

    Public Sub New()

    End Sub

    Public ReadOnly Property get_device_class As USBClass Implements IRequest_Recipient.get_device_class
        Get
            Return _interface.get_device_class
        End Get
    End Property
    Public ReadOnly Property get_device_vendor As USBVendor Implements IRequest_Recipient.get_device_vendor
        Get
            Return _interface.get_device_vendor
        End Get
    End Property

    Public Sub New(number As Byte, direction As enum_direction, transfer_type As enum_transfer_type, sync_type As enum_sync_type, usage_type As enum_usage_type, max_packet_size As UInt16, interval As Byte, handler As Action(Of Byte()))
        Me.number = number
        Me.direction = direction
        Me.transfer_type = transfer_type
        Me.sync_type = sync_type
        Me.usage_type = usage_type
        Me.max_packet_size = max_packet_size
        Me.interval = interval
        Me.handler = handler
        Me._interface = Nothing
        request_handlers.Add(1, AddressOf Me.handle_clear_feature_request)
    End Sub

    Public Sub handle_clear_feature_request(req As USBDeviceRequest)
        Debug.Print("received CLEAR_FEATURE request for endpoint " & Me.number & " with value " & req.value)
        Me._interface.configuration.device.maxusb_app.send_on_endpoint(0, New Byte() {}, Me._interface.configuration.device.max_packet_size_ep0)
    End Sub

    Public Sub set_interface(_interface As USBInterface)
        Me._interface = _interface
    End Sub

    Public Function get_descriptor(n As Byte) As Byte()
        Dim address As Byte = (Me.direction * 128) Or (Me.number And &HF)
        Dim attributes As Byte = (Me.transfer_type And &H3) Or ((Me.sync_type And &H3) * 4) Or ((Me.usage_type And &H3) * 16)
        Return New Byte() {7, 5, address, attributes, Me.max_packet_size And 255, Me.max_packet_size \ 256 And 255, Me.interval}
    End Function
End Class