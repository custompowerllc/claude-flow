using System;
using System.Threading.Tasks;
using agents;
using contracts;
using utility.can;

namespace program_ns.processing;

internal sealed partial class
Upgrade_Agent
{
    private void
    msg_bootloader_exited() =>
        try_send_message(a_agent => a_agent.msg_bootloader_exited(this));

    private void
    msg_firmware_upgrade_initiated
    (CAN_Bootloader a_upgrader) =>
        try_send_message(a_agent => a_agent.msg_firmware_upgrade_initiated(a_upgrader));

    private void
    msg_notify_bootloader_exited() =>
        try_send_message(static a_agent => a_agent.msg_notify_bootloader_exited());
}

internal sealed partial class
Upgrade_Agent
{
    private sealed class
    Event_Adapter_Dummy : Event_Adapter
    {
        public Event_Adapter_Dummy() : base() { }
        public override void bootloader_exited() { }
        public override void firmware_parse_success(CAN_Bootloader a_upgrader) { }
        public override void firmware_parse_fail(string a_message) { }
        public override void firmware_upgrade_success() { }
        public override void firmware_upgrade_fail(string a_message) { }
        public override void firmware_upgrade_progress(int a_bytes_transferred, string a_status) { }
        public override void new_message_register_parsed(CAN_Message_Parsed a_message) { }
        public override void new_can_message_sent(CAN_Message_Parsed a_message) { }
        public override void can_error(string a_message) { }
    }

    public sealed class
    Intern : Agent_Intern<Intern>
    {
        private static class
        State
        {
            public sealed class
            Idle : State_Base<Intern>
            {
                protected override State_Base<Intern>?
                iter
                (Intern a_agent, Scheduler a_scheduler)
                {
                    if(!a_scheduler.process_messages())
                    {
                        return null;
                    }

                    if(a_agent.m_can_error is not null)
                    {
                        return s_can_error;
                    }

                    if(a_agent.m_firmware_upgrader is not null)
                    {
                        return s_firmware_upgrading;
                    }

                    a_scheduler.wait_messages();

                    return this;
                }
            }

            private sealed class
            Firmware_Upgrading : State_Base<Intern>
            {
                protected override void
                init
                (Intern a_agent, State_Base<Intern> a_prev) =>
                    a_agent.m_deadline = Monotonic.current_tick + 250;

                protected override State_Base<Intern>?
                iter
                (Intern a_agent, Scheduler a_scheduler)
                {
                    if(!a_scheduler.process_messages())
                    {
                        return null;
                    }

                    if(a_agent.m_can_error is not null)
                    {
                        a_agent.firmware_upgrade_fail("communication error");

                        return s_can_error;
                    }

                    if(a_agent.m_firmware_upgrader is null)
                    {
                        return s_idle;
                    }

                    if(Monotonic.current_tick >= a_agent.m_deadline)
                    {
                        a_agent.update_firmware_upgrade_progress(a_agent.m_firmware_upgrader);

                        if(a_agent.m_firmware_upgrader.add_ticks(250))
                        {
                            a_agent.firmware_upgrade_fail("timed out");

                            return s_idle;
                        }

                        a_agent.m_deadline += 250;
                    }

                    a_scheduler.wait_messages(a_agent.m_deadline);

                    return this;
                }
            }

            public sealed class
            CAN_Error : State_Base<Intern>
            {
                protected override void
                init
                (Intern a_agent, State_Base<Intern> a_prev) => a_agent.can_error();

                protected override State_Base<Intern>?
                iter
                (Intern a_agent, Scheduler a_scheduler)
                {
                    if(!a_scheduler.process_messages())
                    {
                        return null;
                    }

                    if(a_agent.m_can_error is null)
                    {
                        return s_idle;
                    }

                    a_scheduler.wait_messages();

                    return this;
                }
            }

            public static readonly Idle s_idle = new();
            private static readonly Firmware_Upgrading s_firmware_upgrading = new();
            private static readonly CAN_Error s_can_error = new();
        }

        public
        Intern
        (string a_name, CAN_Interface a_can_agent, Config_Data a_config) :
        base(a_name)
        {
            m_can_agent = a_can_agent;
            m_config = a_config;
            m_state = new(State.s_idle);
            m_event_adapter = new Event_Adapter_Dummy();
            m_firmware_upgrader = null;
            m_outbound_command = 0;
            m_deadline = 0;
            m_can_error = null;
        }

        private readonly CAN_Interface m_can_agent;
        private readonly Config_Data m_config;
        private readonly State_Machine<Intern> m_state;
        private Event_Adapter m_event_adapter;
        private CAN_Bootloader? m_firmware_upgrader;
        private uint m_outbound_command;
        private long m_deadline;
        (bool sent, string message)? m_can_error;

        #region messages

        public void
        msg_set_event_adapter
        (Event_Adapter a_adapter) => m_event_adapter = a_adapter;

        public void
        msg_parse_firmware
        (string a_file_name)
        {
            Contracts.assert(m_config.bootloader is not null);

            CAN_Bootloader a_upgrader;

            try
            {
                a_upgrader = make_upgrader(a_file_name, m_config.bootloader.Value);
            }
            catch(Exception a_except)
            {
                m_event_adapter.firmware_parse_fail(a_except.Message);

                return;
            }

            m_event_adapter.firmware_parse_success(a_upgrader);
        }

        public void
        msg_firmware_upgrade_initiate
        (Upgrade_Agent a_extern, CAN_Bootloader a_upgrader)
        {
            Contracts.assert(m_config.bootloader is not null && m_firmware_upgrader is null);

            if(m_can_error is not null)
            {
                m_event_adapter.firmware_upgrade_fail($"can_error: {nameof(msg_firmware_upgrade_initiate)}");

                return;
            }

            a_upgrader.initiate();

            if(a_upgrader.try_get_outgoing_can_message(out var a_message))
            {
                send_can_message(a_message.id, a_message.data.ToArray(), a_sent => a_extern.msg_firmware_upgrade_initiated(a_upgrader));

                m_event_adapter.new_can_message_sent(a_message);
            }
            else
            {
                Contracts.unreachable();
            }

            Contracts.assert(!a_upgrader.try_get_outgoing_can_message(out a_message));
        }

        public void
        msg_firmware_upgrade_initiated
        (CAN_Bootloader a_upgrader)
        {
            Contracts.assert(m_firmware_upgrader is null);

            if(m_can_error is not null)
            {
                m_event_adapter.firmware_upgrade_fail($"can_error: {nameof(msg_firmware_upgrade_initiated)}");

                return;
            }

            m_firmware_upgrader = a_upgrader;
        }

        public void
        msg_exit_bootloader
        (Upgrade_Agent a_extern)
        {
            Contracts.assert(m_config.bootloader is not null && m_firmware_upgrader is null);

            if(m_can_error is not null)
            {
                m_event_adapter.bootloader_exited();

                return;
            }

            var a_upgrader = make_upgrader(null, m_config.bootloader.Value);

            a_upgrader.reboot();

            while(a_upgrader.try_get_outgoing_can_message(out var a_message))
            {
                send_can_message(a_message.id, a_message.data.ToArray(), a_sent => a_extern.msg_bootloader_exited());

                ++m_outbound_command;

                m_event_adapter.new_can_message_sent(a_message);
            }
        }

        public void
        msg_bootloader_exited
        (Upgrade_Agent a_extern)
        {
            Contracts.assert(m_outbound_command is not 0);

            if(--m_outbound_command is not 0)
            {
                return;
            }

            Contracts.assert(m_config.bootloader is not null);

            _ = Task.Delay(m_config.bootloader.Value.reboot_time).ContinueWith(a_task => a_extern.msg_notify_bootloader_exited());
        }

        public void
        msg_notify_bootloader_exited() =>
            m_event_adapter.bootloader_exited();

        public void
        msg_can_message_received
        (CAN_ID a_recv_id, byte[] a_recv_data)
        {
            if(m_firmware_upgrader is null || m_can_error is not null)
            {
                return;
            }

            process_firmware_upgrader(m_firmware_upgrader, a_recv_id, a_recv_data);
        }

        public void
        msg_can_error
        (string a_message) => m_can_error ??= (false, a_message);

        public void
        msg_can_error_clear() => m_can_error = null;

        #endregion

        private void
        send_can_message
        (CAN_ID a_id, byte[] a_data, Action<Message_Result<(CAN_ID, byte[])>> a_callback) =>
            m_can_agent.msg_send_direct(a_id, a_data, a_callback);

        private void
        update_firmware_upgrade_progress
        (CAN_Bootloader a_upgrader) =>
            m_event_adapter.firmware_upgrade_progress(a_upgrader.bytes_transferred, a_upgrader.status);

        private void
        process_firmware_upgrader
        (CAN_Bootloader a_upgrader, CAN_ID a_recv_id, byte[] a_recv_data)
        {
            try
            {
                a_upgrader.new_can_message(a_recv_id, a_recv_data);
            }
            catch(Exception a_except)
            {
                firmware_upgrade_fail(a_except.Message);

                return;
            }
            finally
            {
                while(a_upgrader.try_get_incoming_can_message(out var a_message))
                {
                    m_event_adapter.new_message_register_parsed(a_message);
                }
            }

            while(a_upgrader.try_get_outgoing_can_message(out var a_message))
            {
                send_can_message(a_message.id, a_message.data.ToArray(), a_sent => { });

                m_event_adapter.new_can_message_sent(a_message);
            }

            while(a_upgrader.try_get_outgoing_can_data(out var a_data))
            {
                var (a_send_id, a_send_data) = a_data;

                send_can_message(a_send_id, a_send_data, a_sent => { });
            }

            if(a_upgrader.is_finished)
            {
                m_event_adapter.firmware_upgrade_success();

                m_firmware_upgrader = null;
            }
        }

        private void
        firmware_upgrade_fail
        (string a_message)
        {
            m_firmware_upgrader = null;

            m_event_adapter.firmware_upgrade_fail(a_message);
        }

        private void
        can_error()
        {
            Contracts.assert(m_can_error is not null);

            var (a_sent, a_message) = m_can_error.Value;

            if(a_sent)
            {
                return;
            }

            m_event_adapter.can_error(a_message);

            m_can_error = (true, a_message);
        }

        protected override void
        run
        (Scheduler a_scheduler) => m_state.run(this, a_scheduler);

        public override void
        Dispose()
        {

        }

        private static CAN_Bootloader
        make_upgrader
        (string? a_hex_file_name, in Config_Data.Bootloader_Table a_config) =>
            new
            (
                new()
                {
                    hex_file_name = a_hex_file_name,
                    hex_file_content = a_config.hex_file_content,
                    upgrade_tasks = a_config.upgrade_tasks,
                    normal_timeout = a_config.normal_timeout,
                    verify_timeout = a_config.verify_timeout,
                    auto_exit = a_config.auto_exit
                }
            );
    }
}

