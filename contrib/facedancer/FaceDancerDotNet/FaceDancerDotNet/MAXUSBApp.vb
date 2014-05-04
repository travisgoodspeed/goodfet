Public Class MAXUSBApp
    Inherits FacedancerApp

    Public read_register_cmd As FacedancerCommand
    Public write_register_cmd As FacedancerCommand
    Public ack_cmd As FacedancerCommand
    Public connected_device As USBDevice
    Public looping As Boolean

    Public Enum reg
        _ep0_fifo = &H0
        _ep1_out_fifo = &H1
        _ep2_in_fifo = &H2
        _ep3_in_fifo = &H3
        _setup_data_fifo = &H4
        _ep0_byte_count = &H5
        _ep1_out_byte_count = &H6
        _ep2_in_byte_count = &H7
        _ep3_in_byte_count = &H8
        _ep_stalls = &H9
        _clr_togs = &HA
        _endpoint_irq = &HB
        _endpoint_interrupt_enable = &HC
        _usb_irq = &HD
        _usb_interrupt_enable = &HE
        _usb_control = &HF
        _cpu_control = &H10
        _pin_control = &H11
        _revision = &H12
        _function_address = &H13
        _io_pins = &H14
    End Enum

    Public Enum bm_endpoint_irq
        is_setup_data_avail = &H20     ' SUDAVIRQ
        is_in3_buffer_avail = &H10     ' IN3BAVIRQ
        is_in2_buffer_avail = &H8     ' IN2BAVIRQ
        is_out1_data_avail = &H4     ' OUT1DAVIRQ
        is_out0_data_avail = &H2     ' OUT0DAVIRQ
        is_in0_buffer_avail = &H1     ' IN0BAVIRQ
    End Enum

    Public Enum bm_usb_control
        _vbgate = &H40
        _connect = &H8
    End Enum

    Public Enum bm_pin_control
        interrupt_level = &H8
        full_duplex = &H10
    End Enum

    Public Sub New(device As FaceDancer, verbose As Byte)
        MyBase.New("MAXUSB", &H40, device, verbose)
        Me.connected_device = Nothing
        Me.enable()
        If Me.verbose > 0 Then
            Dim rev As Integer = Me.read_register(reg._revision)
            Debug.Print(Me.app_name & " revision " & rev)
        End If
        Me.write_register(reg._pin_control, bm_pin_control.interrupt_level Or bm_pin_control.full_duplex)
    End Sub

    Public Overrides Sub init_commands()
        MyBase.init_commands()
        Me.read_register_cmd = New FacedancerCommand(Me.app_num, &H0, Nothing)
        Me.write_register_cmd = New FacedancerCommand(Me.app_num, &H0, Nothing)
        Me.enable_app_cmd = New FacedancerCommand(Me.app_num, &H10, Nothing)
        Me.ack_cmd = New FacedancerCommand(Me.app_num, &H0, New Byte() {&H1})
    End Sub

    Public Function read_register(reg_num As Byte, Optional ack As Boolean = False) As Byte
        If Me.verbose > 1 Then Debug.Print(Me.app_name & " reading register 0x" & reg_num.ToString("X2"))
        Me.read_register_cmd.data = New Byte() {reg_num * 8, 0}
        If ack Then Me.read_register_cmd.data(0) = Me.read_register_cmd.data(0) Or 1
        Me.device.writecmd(Me.read_register_cmd)
        Dim resp As FacedancerCommand = Me.device.readcmd
        If Me.verbose > 2 Then Debug.Print(Me.app_name & " read register 0x" & reg_num.ToString("X2") & " has value 0x" & resp.data(1).ToString("X2"))
        Return resp.data(1)
    End Function

    Public Sub write_register(reg_num As Byte, value As Byte, Optional ack As Boolean = False)
        If Me.verbose > 2 Then Debug.Print(Me.app_name & " writing register 0x" & reg_num.ToString("X2") & " with value 0x" & value.ToString("X2"))
        Me.write_register_cmd.data = New Byte() {(reg_num * 8) Or 2, value}
        If ack Then Me.write_register_cmd.data(0) = Me.write_register_cmd.data(0) Or 1
        Me.device.writecmd(Me.write_register_cmd)
        If reg_num = reg._usb_control And value = bm_usb_control._vbgate Then
        Else
            Me.device.readcmd()
        End If
    End Sub

    Public Function get_version() As Byte
        Return Me.read_register(reg._revision)
    End Function

    Public Sub ack_status_stage()
        If Me.verbose > 5 Then Debug.Print(Me.app_name & " sending ack!")
        Me.device.writecmd(Me.ack_cmd)
        Me.device.readcmd()
    End Sub

    Public Sub connect(usb_device)
        If Me.read_register(reg._usb_control) And bm_usb_control._connect Then
            Me.write_register(reg._usb_control, bm_usb_control._vbgate)
            device.serialport.Close()
            device.serialport.Open()
            System.Threading.Thread.Sleep(100)
        End If

        Me.write_register(reg._usb_control, bm_usb_control._vbgate Or bm_usb_control._connect)
        Me.connected_device = usb_device
        If Me.verbose > 0 Then Debug.Print(Me.app_name & " connected device " & Me.connected_device.name)
    End Sub

    Public Sub disconnect()
        Me.write_register(reg._usb_control, bm_usb_control._vbgate)
        If Me.verbose > 0 Then Debug.Print(Me.app_name & " disconnected device " & Me.connected_device.name)
        Me.connected_device = Nothing
    End Sub

    Public Sub clear_irq_bit(reg As Byte, bit As Byte)
        Me.write_register(reg, bit)
    End Sub

    Public Function read_bytes(reg As Byte, n As Integer)
        If Me.verbose > 2 Then Debug.Print(Me.app_name & " reading " & n & " bytes from register " & reg)
        Dim data(n) As Byte
        data(0) = reg * 8
        Dim cmd As New FacedancerCommand(Me.app_num, &H0, data)
        Me.device.writecmd(cmd)
        Dim resp As FacedancerCommand = Me.device.readcmd
        If Me.verbose > 3 Then Debug.Print(Me.app_name & " read " & resp.data.Length - 1 & " bytes from register " & reg)
        Dim tmp(resp.data.Length - 2) As Byte
        Array.Copy(resp.data, 1, tmp, 0, resp.data.Length - 1)
        Return tmp
    End Function

    Public Sub write_bytes(reg As Byte, data() As Byte)
        Dim tmp(data.Length) As Byte
        tmp(0) = (reg * 8) Or 3
        Array.Copy(data, 0, tmp, 1, data.Length)
        Dim cmd As New FacedancerCommand(Me.app_num, &H0, tmp)
        Me.device.writecmd(cmd)
        Me.device.readcmd()
        If Me.verbose > 3 Then Debug.Print(Me.app_name & " wrote " & data.Length & " bytes to register " & reg)
    End Sub

    'HACK: but given the limitations of the MAX chips, it seems necessary
    Public Sub send_on_endpoint(ep_num As Byte, data() As Byte, packetSize As Byte)
        Dim fifo_reg As Byte
        Dim bc_reg As Byte
        Select Case ep_num
            Case 0
                fifo_reg = reg._ep0_fifo
                bc_reg = reg._ep0_byte_count
            Case 2
                fifo_reg = reg._ep2_in_fifo
                bc_reg = reg._ep2_in_byte_count
            Case 3
                fifo_reg = reg._ep3_in_fifo
                bc_reg = reg._ep3_in_byte_count
            Case Else
                Throw New Exception("endpoint " & ep_num & " not supported")
        End Select
        Dim sent As Integer = 0
        If packetSize > 64 Then packetSize = 64
        While data.Length > packetSize
            Dim tmp(packetSize - 1) As Byte
            Array.Copy(data, 0, tmp, 0, packetSize)
            Me.write_bytes(fifo_reg, tmp)
            Me.write_register(bc_reg, packetSize, True)
            If Me.verbose > 1 Then Debug.Print(Me.app_name & " wrote " & BitConverter.ToString(tmp) & " to endpoint " & ep_num)
            Dim tmp2(data.Length - packetSize - 1) As Byte
            Array.Copy(data, packetSize, tmp2, 0, tmp2.Length)
            data = tmp2
        End While
        Me.write_bytes(fifo_reg, data)
        Me.write_register(bc_reg, data.Length, True)
        If Me.verbose > 1 Then Debug.Print(Me.app_name & " wrote " & BitConverter.ToString(data) & " to endpoint " & ep_num)

    End Sub

    ' HACK: but given the limitations of the MAX chips, it seems necessary
    Public Function read_from_endpoint(ep_num As Byte) As Byte()
        Dim fifo_reg As Byte
        Dim bc_reg As Byte
        Select Case ep_num
            Case 0
                fifo_reg = reg._ep0_fifo
                bc_reg = reg._ep0_byte_count
            Case 1
                fifo_reg = reg._ep1_out_fifo
                bc_reg = reg._ep1_out_byte_count
        End Select

        Dim byte_count As Byte = Me.read_register(bc_reg)
        If byte_count = 0 Then Return New Byte() {}
        Dim data() As Byte = Me.read_bytes(fifo_reg, byte_count)
        If Me.verbose > 1 Then Debug.Print(Me.app_name & " read " & BitConverter.ToString(data) & " from endpoint " & ep_num)
        Return data
    End Function

    Public Sub stall_ep0()
        If Me.verbose > 0 Then Debug.Print(Me.app_name & " stalling endpoint 0")
        Me.write_register(reg._ep_stalls, &H23)
    End Sub

    Public Sub service_irqs()
        looping = True
        While looping
            Dim irq As Byte = Me.read_register(reg._endpoint_irq)
            If Me.verbose > 3 Then Debug.Print(Me.app_name & " read endpoint irq: 0x" & irq.ToString("X2"))
            If Me.verbose > 2 Then
                If irq And (Not (bm_endpoint_irq.is_in0_buffer_avail Or bm_endpoint_irq.is_in2_buffer_avail Or bm_endpoint_irq.is_in3_buffer_avail)) Then
                    Debug.Print(Me.app_name & " notable irq: 0x" & irq.ToString("X2"))
                End If
            End If

            If irq And bm_endpoint_irq.is_setup_data_avail Then
                Me.clear_irq_bit(reg._endpoint_irq, bm_endpoint_irq.is_setup_data_avail)
                Dim buf() As Byte = Me.read_bytes(reg._setup_data_fifo, 8)
                Dim req As New USBDeviceRequest(buf)
                Me.connected_device.handle_request(req)
            Else
                If Me.read_register(reg._ep0_byte_count) > 0 Then
                    Dim data() As Byte = Me.read_from_endpoint(0)
                    If data.Length > 0 Then Me.connected_device.handle_data_available(0, data)
                    'Me.clear_irq_bit(reg._endpoint_irq, bm_endpoint_irq.is_out0_data_avail)
                End If
            End If

            If irq And bm_endpoint_irq.is_out1_data_avail Then
                Dim data() As Byte = Me.read_from_endpoint(1)
                If data.Length > 0 Then Me.connected_device.handle_data_available(1, data)
                Me.clear_irq_bit(reg._endpoint_irq, bm_endpoint_irq.is_out1_data_avail)
            End If

            If Not looping Or connected_device Is Nothing Then Exit Sub

            If irq And bm_endpoint_irq.is_in2_buffer_avail Then Me.connected_device.handle_buffer_available(130)
            If irq And bm_endpoint_irq.is_in3_buffer_avail Then Me.connected_device.handle_buffer_available(131)

        End While
    End Sub

End Class
