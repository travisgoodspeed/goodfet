Public Class USBVendor
    Implements IRequest_Handler

    Public ReadOnly Property get_request_handlers As Dictionary(Of Byte, Action(Of USBDeviceRequest)) Implements IRequest_Handler.get_request_handlers
        Get
            Return request_handlers
        End Get
    End Property

    Public name As String = "generic USB device vendor"
    Public request_handlers As New Dictionary(Of Byte, Action(Of USBDeviceRequest))
    Public device As USBDevice
    Public verbose As Byte

    Public Sub New(Optional verbose As Byte = 0)
        Me.device = Nothing
        Me.verbose = verbose
        Me.setup_request_handlers()
    End Sub

    Public Sub set_device(device As USBDevice)
        Me.device = device
    End Sub

    Public Overridable Sub setup_request_handlers()
        '        """To be overridden for subclasses to modify self.request_handlers"""

    End Sub
End Class
