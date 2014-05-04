Public Class USBConfiguration
    Public configuration_index As Byte
    Public configuration_string As String
    Public configuration_string_index As Byte
    Public interfaces As New Dictionary(Of Byte, USBInterface)
    Public attributes As Byte
    Public max_power As Byte
    Public device As USBDevice

    Public Sub New()

    End Sub

    Public Sub New(configuration_index As Byte, configuration_string As String, interfaces() As USBInterface)
        Me.configuration_index = configuration_index
        Me.configuration_string = configuration_string
        Me.configuration_string_index = 0
        Me.attributes = &HE0
        Me.max_power = &H1
        Me.device = Nothing

        For Each i As USBInterface In interfaces
            Me.interfaces.Add(i.number, i)
            i.set_configuration(Me)
        Next
    End Sub

    Public Sub set_device(device As USBDevice)
        Me.device = device
    End Sub

    Public Sub set_configuration_string_index(i As Byte)
        Me.configuration_string_index = i
    End Sub

    Public Overridable Function get_descriptor(n As Byte) As Byte()
        Dim interface_descriptors As New List(Of Byte)
        interface_descriptors.AddRange(New Byte() {9, 2, 0, 0, Me.interfaces.Count, Me.configuration_index, Me.configuration_string_index, Me.attributes, Me.max_power})
        For Each i As USBInterface In interfaces.Values
            interface_descriptors.AddRange(i.get_descriptor(0))
        Next
        Dim total_len As UInt16 = interface_descriptors.Count
        interface_descriptors(2) = total_len And 255
        interface_descriptors(3) = total_len \ 256 And 255
        Return interface_descriptors.ToArray
    End Function

End Class
