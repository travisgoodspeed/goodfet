Public Class USB
    Public Enum state
        _detached = 1
        _attached = 1
        _powered = 2
        _default = 3
        _address = 4
        _configured = 5
        _suspended = 6
    End Enum

    Public Enum request_direction
        _host_to_device = 0
        _device_to_host = 1
    End Enum

    Public Enum request_type
        _standard = 0
        _class = 1
        _vendor = 2
    End Enum

    Public Enum request_recipient
        _device = 0
        _interface = 1
        _endpoint = 2
        _other = 3
    End Enum

    Public Enum feature
        _endpoint_halt = 0
        _device_remote_wakeup = 1
        _test_mode = 2
    End Enum

    Public Enum desc_type
        _device = 1
        _configuration = 2
        _string = 3
        _interface = 4
        _endpoint = 5
        _device_qualifier = 6
        _other_speed_configuration = 7
        _interface_power = 8
        _hid = 33
        _report = 34
    End Enum

    Public Shared if_class_to_desc_type As Dictionary(Of Byte, Byte) = init_if_class_to_desc_type

    Public Shared Function init_if_class_to_desc_type() As Dictionary(Of Byte, Byte)
        Dim tmp As New Dictionary(Of Byte, Byte)
        tmp.Add(3, desc_type._hid)
        Return tmp
    End Function

    Shared Function interface_class_to_descriptor_type(interface_class As Byte) As Byte
        Dim dtype As Byte
        If if_class_to_desc_type.TryGetValue(interface_class, dtype) Then Return dtype Else Return 0
    End Function

End Class
