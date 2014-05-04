Public Class USBClass
    Implements IRequest_Handler

    Public ReadOnly Property get_request_handlers As Dictionary(Of Byte, Action(Of USBDeviceRequest)) Implements IRequest_Handler.get_request_handlers
        Get
            Return request_handlers
        End Get
    End Property

    Public name As String = "generic USB device class"
    Public request_handlers As New Dictionary(Of Byte, Action(Of USBDeviceRequest))
    Public _interface As USBInterface
    Public verbose As Byte

    Public Sub New(Optional verbose As Byte = 0)
        Me._interface = Nothing
        Me.verbose = verbose
        Me.setup_request_handlers()
    End Sub

    Public Sub set_interface(_interface As USBInterface)
        Me._interface = _interface
    End Sub

    Public Overridable Sub setup_request_handlers()
        '        """To be overridden for subclasses to modify self.class_request_handlers"""
    End Sub
End Class
