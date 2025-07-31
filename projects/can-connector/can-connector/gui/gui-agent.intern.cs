using System;
using System.Linq;
using agents;
using contracts;
using program_ns.processing;
using serial;
using utility.can;

namespace program_ns.gui;

internal sealed partial class
GUI_Agent
{
    private void
    msg_init
    (Main_Form_Agent a_form) =>
        send_message(a_agent => a_agent.msg_init(this, a_form));

    private void
    msg_open_can_finished
    (Message_Result a_result, bool a_is_reopen) =>
        try_send_message(a_agent => a_agent.msg_open_can_finished(a_result, a_is_reopen));

    private void
    msg_new_can_error_received
    (string a_message, uint a_count) =>
        try_send_message(a_agent => a_agent.msg_new_can_error_received(a_message, a_count));

    private void
    msg_new_can_message_received
    (CAN_ID a_id, byte[] a_data) =>
        try_send_message(a_agent => a_agent.msg_new_can_message_received(a_id, a_data));

    #region send_event_adapter

    private void
    msg_command_finished
    (Product.Command a_command) =>
        try_send_message(a_agent => a_agent.msg_command_finished(a_command));

    private void
    msg_command_invalid
    (Product.Command a_command, string a_message) =>
        try_send_message(a_agent => a_agent.msg_command_invalid(a_command, a_message));

    private void
    msg_new_send_count
    (uint a_count) =>
        try_send_message(a_agent => a_agent.msg_new_send_count(a_count));

    private void
    msg_send_once_finished() =>
        try_send_message(static a_agent => a_agent.msg_send_once_finished());

    private void
    msg_send_stop_finished() =>
        try_send_message(static a_agent => a_agent.msg_send_stop_finished());

    private void
    msg_new_message_register_parsed
    (Product.Message_Register a_register, CAN_Message_Parsed a_message) =>
        try_send_message(a_agent => a_agent.msg_new_message_register_parsed(a_register, a_message));

    private void
    msg_new_status_register_parsed
    (Product.Status_Register a_register, byte a_status) =>
        try_send_message(a_agent => a_agent.msg_new_status_register_parsed(a_register, a_status));

    private void
    msg_new_can_message_sent
    (CAN_Message_Parsed a_message) =>
        try_send_message(a_agent => a_agent.msg_new_can_message_sent(a_message));

    private void
    msg_can_error
    (string a_message) =>
        try_send_message(a_agent => a_agent.msg_can_error(a_message));

    #endregion

    #region upgrade_event_adapter

    private void
    msg_bootloader_exited() =>
        try_send_message(static a_agent => a_agent.msg_bootloader_exited());

    private void
    msg_firmware_parse_fail
    (string a_message) =>
        try_send_message(a_agent => a_agent.msg_firmware_parse_fail(a_message));

    private void
    msg_firmware_parse_success
    (CAN_Bootloader a_upgrader) =>
        try_send_message(a_agent => a_agent.msg_firmware_parse_success(a_upgrader));

    private void
    msg_firmware_upgrade_fail
    (string a_message) =>
        try_send_message(a_agent => a_agent.msg_firmware_upgrade_fail(a_message));

    private void
    msg_firmware_upgrade_success() =>
        try_send_message(static a_agent => a_agent.msg_firmware_upgrade_success());

    private void
    msg_firmware_upgrade_progress
    (int a_bytes_transferred, string a_status) =>
        try_send_message(a_agent => a_agent.msg_firmware_upgrade_progress(a_bytes_transferred, a_status));

    private void
    msg_new_message_register_parsed_bootloader
    (CAN_Message_Parsed a_message) =>
        try_send_message(a_agent => a_agent.msg_new_message_register_parsed_bootloader(a_message));

    private void
    msg_new_can_message_sent_bootloader
    (CAN_Message_Parsed a_message) =>
        try_send_message(a_agent => a_agent.msg_new_can_message_sent_bootloader(a_message));

    private void
    msg_can_error_bootloader
    (string a_message) =>
        try_send_message(a_agent => a_agent.msg_can_error_bootloader(a_message));

    #endregion
}

internal sealed partial class
GUI_Agent
{
    public sealed class
    Intern : Agent_Intern<Intern>
    {
        private sealed class
        Send_Event_Adapter : Send_Agent.Event_Adapter
        {
            public
            Send_Event_Adapter
            (GUI_Agent a_agent) :
            base() => m_agent = a_agent;

            public override void command_finished(Product.Command a_command) => m_agent.msg_command_finished(a_command);
            public override void command_failed(Product.Command a_command, string a_message) => m_agent.msg_command_invalid(a_command, a_message);
            public override void new_send_count(uint a_count) => m_agent.msg_new_send_count(a_count);
            public override void send_once_finished() => m_agent.msg_send_once_finished();
            public override void send_stop_finished() => m_agent.msg_send_stop_finished();

            public override void
            new_message_register_parsed
            (Product.Message_Register a_register, CAN_Message_Parsed a_message) =>
                m_agent.msg_new_message_register_parsed(a_register, a_message);

            public override void
            new_status_register_parsed
            (Product.Status_Register a_register, byte a_status) =>
                m_agent.msg_new_status_register_parsed(a_register, a_status);

            public override void
            new_can_message_sent
            (CAN_Message_Parsed a_message) =>
                m_agent.msg_new_can_message_sent(a_message);

            public override void can_error(string a_message) => m_agent.msg_can_error(a_message);

            private readonly GUI_Agent m_agent;
        }

        private sealed class
        upgrade_event_adapter : Upgrade_Agent.Event_Adapter
        {
            public
            upgrade_event_adapter
            (GUI_Agent a_agent) :
            base() => m_agent = a_agent;

            public override void bootloader_exited() => m_agent.msg_bootloader_exited();
            public override void firmware_parse_fail(string a_message) => m_agent.msg_firmware_parse_fail(a_message);
            public override void firmware_parse_success(CAN_Bootloader a_upgrader) => m_agent.msg_firmware_parse_success(a_upgrader);
            public override void firmware_upgrade_fail(string a_message) => m_agent.msg_firmware_upgrade_fail(a_message);
            public override void firmware_upgrade_success() => m_agent.msg_firmware_upgrade_success();

            public override void
            firmware_upgrade_progress
            (int a_bytes_transferred, string a_status) =>
                m_agent.msg_firmware_upgrade_progress(a_bytes_transferred, a_status);

            public override void
            new_message_register_parsed
            (CAN_Message_Parsed a_message) =>
                m_agent.msg_new_message_register_parsed_bootloader(a_message);

            public override void
            new_can_message_sent
            (CAN_Message_Parsed a_message) =>
                m_agent.msg_new_can_message_sent_bootloader(a_message);

            public override void can_error(string a_message) => m_agent.msg_can_error_bootloader(a_message);

            private readonly GUI_Agent m_agent;
        }

        private static class
        State
        {
            public sealed class
            Init : State_Base<Intern>
            {
                protected override State_Base<Intern>?
                iter
                (Intern a_agent, Scheduler a_scheduler)
                {
                    if(!a_scheduler.process_messages())
                    {
                        return null;
                    }

                    do
                    {
                        if(!a_agent.m_connected)
                        {
                            break;
                        }

                        if(a_agent.m_form is null)
                        {
                            break;
                        }

                        return s_idle;
                    }
                    while(false);

                    a_scheduler.wait_messages();

                    return this;
                }
            }

            private sealed class
            Idle : State_Base<Intern>
            {
                protected override void
                init
                (Intern a_agent, State_Base<Intern> a_prev) =>
                    a_agent.m_form.msg_enter_ready_state();

                protected override State_Base<Intern>?
                iter
                (Intern a_agent, Scheduler a_scheduler)
                {
                    if(!a_scheduler.process_messages())
                    {
                        return null;
                    }

                    a_scheduler.wait_messages();

                    return this;
                }
            }

            public static readonly Init s_init = new();
            private static readonly Idle s_idle = new();
        }

        public
        Intern
        (string a_name, CAN_Interface a_can_agent, Config_Data a_config, Product a_product) :
        base(a_name)
        {
            m_can_agent = a_can_agent;
            m_config = a_config;
            m_product = a_product;
            m_send_agent = new($"{a_name}::{nameof(Send_Agent)}", a_can_agent, a_config, a_product);
            m_upgrade_agent = new($"{a_name}::{nameof(Upgrade_Agent)}", a_can_agent, a_config);
            m_state = new(State.s_init);
            m_form = null!;
            m_connected = m_ignore_recv = m_redirect = false;
            m_firmware_upgrader = null;
        }

        private readonly CAN_Interface m_can_agent;
        private readonly Config_Data m_config;
        private readonly Product m_product;
        private readonly Send_Agent m_send_agent;
        private readonly Upgrade_Agent m_upgrade_agent;
        private readonly State_Machine<Intern> m_state;
        private Main_Form_Agent m_form;
        private bool m_connected;
        private bool m_ignore_recv;
        private bool m_redirect;
        private CAN_Bootloader? m_firmware_upgrader;

        #region pub

        public void
        msg_open_can
        (GUI_Agent a_extern, bool a_is_reopen) =>
            m_can_agent.msg_open(m_config, a_result => a_extern.msg_open_can_finished(a_result, a_is_reopen));

        public void
        msg_open_serial
        (GUI_Agent a_extern, bool a_is_reopen, string a_port, int a_baud) =>
            m_can_agent.msg_open
            (
                m_config,
                a_port,
                a_baud,
                a_result => a_extern.msg_open_can_finished(a_result, a_is_reopen)
            );

        public void
        msg_set_send_dest
        (Product.Destination a_dest) =>
            m_send_agent.msg_set_send_dest(a_dest);

        public void
        msg_parse_firmware
        (string a_file_name)
        {
            Contracts.assert(m_config.bootloader is not null);

            m_upgrade_agent.msg_parse_firmware(a_file_name);
        }

        public void
        msg_upgrade_firmware
        (CAN_Bootloader a_upgrader)
        {
            Contracts.assert(m_product.enter_bootloader_command is not null && m_firmware_upgrader is null);

            m_send_agent.msg_enter_bootloader();

            m_firmware_upgrader = a_upgrader;
        }

        public void
        msg_enter_bootloader()
        {
            Contracts.assert(m_product.enter_bootloader_command is not null);

            m_send_agent.msg_enter_bootloader();
        }

        public void
        msg_exit_bootloader()
        {
            Contracts.assert(m_product.enter_bootloader_command is not null);

            m_upgrade_agent.msg_exit_bootloader();
        }

        public void
        msg_set_recv_interval
        (uint a_ms) => m_can_agent.msg_set_poll_interval(a_ms);

        public void
        msg_ignore_recv
        (bool a_ignore) => m_ignore_recv = a_ignore;

        public void
        msg_start_sending
        (uint a_ms, uint? a_count, Product.Query a_query) =>
            m_send_agent.msg_start_sending(a_ms, a_count, a_query);

        public void
        msg_stop_sending() =>
            m_send_agent.msg_stop_sending();

        public void
        msg_send_once
        (Product.Query a_query) =>
            m_send_agent.msg_send_once(a_query);

        public void
        msg_command
        (Product.Command a_command, string[] a_args) =>
            m_send_agent.msg_command(a_command, a_args);

        #endregion

        public void
        msg_init
        (GUI_Agent a_extern, Main_Form_Agent a_form)
        {
            m_form = a_form;

            m_form.msg_enable_features(m_config);

            m_send_agent.msg_set_event_adapter(new Send_Event_Adapter(a_extern));

            m_upgrade_agent.msg_set_event_adapter(new upgrade_event_adapter(a_extern));

            if(m_can_agent is Komodo_CAN_Interface)
            {
                m_can_agent.msg_set_max_error_count(MAX_CAN_ERRORS);
            }

            if(m_can_agent is Modbus_CAN_Interface)
            {
                m_can_agent.msg_set_max_error_count(MAX_MODBUS_ERRORS);
            }

            m_can_agent.msg_error_listener_add("error-listener", a_extern.msg_new_can_error_received);

            m_can_agent.msg_recv_listener_add("recv-listener", a_extern.msg_new_can_message_received);

            if(m_can_agent is Serial_CAN_Interface or Modbus_CAN_Interface)
            {
                m_form.msg_available_ports(Serial_Device.find().ToArray());
            }
        }

        public void
        msg_open_can_finished
        (Message_Result a_result, bool a_is_reopen)
        {
            if(a_result.error is Exception a_error)
            {
                m_form.msg_can_open_failed(a_error.Message);

                return;
            }

            m_connected = true;

            if(a_is_reopen)
            {
                m_form.msg_can_reopened();

                m_send_agent.msg_can_error_clear();

                m_upgrade_agent.msg_can_error_clear();
            }
        }

        public void
        msg_new_can_error_received
        (string a_message, uint a_count)
        {
            if(m_can_agent is Komodo_CAN_Interface && a_count is <= MAX_CAN_ERRORS)
            {
                return;
            }

            if(m_can_agent is Modbus_CAN_Interface && a_count is <= MAX_MODBUS_ERRORS)
            {
                return;
            }

            m_connected = false;

            m_send_agent.msg_can_error(a_message);
        }

        public void
        msg_new_can_message_received
        (CAN_ID a_id, byte[] a_data)
        {
            m_form.msg_bus_activity();
            
            if(m_ignore_recv)
            {
                return;
            }

            if(m_redirect)
            {
                m_upgrade_agent.msg_can_message_received(a_id, a_data);
            }
            else
            {
                m_send_agent.msg_can_message_received(a_id, a_data);
            }
        }

        #region send_event_adapter

        public void
        msg_command_finished
        (Product.Command a_command)
        {
            if(m_config.bootloader is not null)
            {
                if(a_command.Equals(m_product.enter_bootloader_command) && m_firmware_upgrader is not null)
                {
                    m_upgrade_agent.msg_firmware_upgrade_initiate(m_firmware_upgrader);

                    m_firmware_upgrader = null;

                    Contracts.assert(!m_redirect);

                    m_redirect = true;

                    m_form.msg_firmware_upgrade_initiated(true);

                    return;
                }
            }

            m_form.msg_command_finished(a_command);
        }

        public void
        msg_command_invalid
        (Product.Command a_command, string a_message)
        {
            if(m_config.bootloader is not null)
            {
                if(a_command.Equals(m_product.enter_bootloader_command) && m_firmware_upgrader is not null)
                {
                    m_firmware_upgrader = null;

                    Contracts.assert(!m_redirect);

                    m_form.msg_firmware_upgrade_initiated(false);
                }
            }

            m_form.msg_command_invalid(a_message);
        }

        public void
        msg_new_send_count
        (uint a_count) =>
            m_form.msg_update_send_count(a_count);

        public void
        msg_send_once_finished() =>
            m_form.msg_send_once_finished();

        public void
        msg_send_stop_finished() =>
            m_form.msg_send_stop_finished();

        public void
        msg_new_message_register_parsed
        (Product.Message_Register a_register, CAN_Message_Parsed a_message) =>
            m_form.msg_new_can_message_received(a_register, a_message);

        public void
        msg_new_status_register_parsed
        (Product.Status_Register a_register, byte a_status) =>
            m_form.msg_new_status_register_received(a_register, a_status);

        public void
        msg_new_can_message_sent
        (CAN_Message_Parsed a_message) =>
            m_form.msg_new_can_message_sent(a_message);

        public void
        msg_can_error
        (string a_message) =>
            m_upgrade_agent.msg_can_error(a_message);

        #endregion

        #region upgrade_event_adapter

        public void
        msg_bootloader_exited() =>
            m_form.msg_bootloader_exited();

        public void
        msg_firmware_parse_fail
        (string a_message) =>
            m_form.msg_firmware_parse_fail(a_message);

        public void
        msg_firmware_parse_success
        (CAN_Bootloader a_upgrader) =>
            m_form.msg_firmware_upgrade_confirm(a_upgrader);

        public void
        msg_firmware_upgrade_fail
        (string a_message)
        {
            Contracts.assert(m_redirect);

            m_redirect = false;

            m_form.msg_firmware_upgrade_fail(a_message);
        }

        public void
        msg_firmware_upgrade_success()
        {
            Contracts.assert(m_redirect);

            m_redirect = false;

            m_form.msg_firmware_upgrade_success();
        }

        public void
        msg_firmware_upgrade_progress
        (int a_bytes_transferred, string a_status) =>
            m_form.msg_firmware_upgrade_progress(a_bytes_transferred, a_status);

        public void
        msg_new_message_register_parsed_bootloader
        (CAN_Message_Parsed a_message) =>
            m_form.msg_new_can_message_received_bootloader(a_message);

        public void
        msg_new_can_message_sent_bootloader
        (CAN_Message_Parsed a_message) =>
            m_form.msg_new_can_message_sent_bootloader(a_message);

        public void
        msg_can_error_bootloader
        (string a_message) =>
            m_form.msg_can_error(a_message);

        #endregion

        protected override void
        run
        (Scheduler a_scheduler) => m_state.run(this, a_scheduler);

        public override void
        Dispose()
        {
            m_upgrade_agent.Dispose();

            m_send_agent.Dispose();

            if(m_connected)
            {
                m_can_agent.msg_close();
            }
        }
    }
}
