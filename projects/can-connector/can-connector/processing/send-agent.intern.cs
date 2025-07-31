using System;
using System.Threading.Tasks;
using agents;
using contracts;
using utility.can;

namespace program_ns.processing;

internal sealed partial class
Send_Agent
{
    private void
    msg_send_once_finished() =>
        try_send_message(static a_agent => a_agent.msg_send_once_finished());

    private void
    msg_update_send_count
    (uint? a_count) =>
        try_send_message(a_agent => a_agent.msg_update_send_count(a_count));

    private void
    msg_command_sent
    (Product.Command a_command) =>
        try_send_message(a_agent => a_agent.msg_command_sent(a_command));

    private void
    msg_notify_command_finished
    (Product.Command a_command) =>
        try_send_message(a_agent => a_agent.msg_notify_command_finished(a_command));
}

internal sealed partial class
Send_Agent
{
    public sealed class
    Intern : Agent_Intern<Intern>
    {
        private sealed class
        Event_Adapter_Dummy : Event_Adapter
        {
            public Event_Adapter_Dummy() : base() { }
            public override void send_stop_finished() { }
            public override void send_once_finished() { }
            public override void command_finished(Product.Command a_command) { }
            public override void command_failed(Product.Command a_command, string a_message) { }
            public override void new_send_count(uint a_count) { }
            public override void new_message_register_parsed(Product.Message_Register a_register, CAN_Message_Parsed a_message) { }
            public override void new_status_register_parsed(Product.Status_Register a_register, byte a_status) { }
            public override void new_can_message_sent(CAN_Message_Parsed a_message) { }
            public override void can_error(string a_message) { }
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

                    if(a_agent.m_event_adapter is not Event_Adapter_Dummy)
                    {
                        return s_recv_only;
                    }

                    a_scheduler.wait_messages();

                    return this;
                }
            }

            private sealed class
            Recv_Only : State_Base<Intern>
            {
                protected override State_Base<Intern>?
                iter
                (Intern a_agent, Scheduler a_scheduler)
                {
                    if(!a_scheduler.process_messages())
                    {
                        return null;
                    }

                    if(a_agent.m_command_deadline is not null)
                    {
                        return s_waiting_response_recv_only;
                    }

                    if(a_agent.m_send_count is null)
                    {
                        return s_send_recv_indef;
                    }

                    if(a_agent.m_send_count is not 0)
                    {
                        return s_send_recv;
                    }

                    if(a_agent.m_can_error is not null)
                    {
                        return s_can_error;
                    }

                    a_scheduler.wait_messages();

                    return this;
                }
            }

            private sealed class
            Send_Recv : State_Base<Intern>
            {
                protected override void
                init
                (Intern a_agent, State_Base<Intern> a_prev) =>
                    a_agent.m_deadline = Monotonic.current_tick;

                protected override State_Base<Intern>?
                iter
                (Intern a_agent, Scheduler a_scheduler)
                {
                    Contracts.assert(a_agent.m_send_count is not null);

                    if(!a_scheduler.process_messages())
                    {
                        return null;
                    }

                    if(a_agent.m_command_deadline is not null)
                    {
                        return s_waiting_response_send_recv;
                    }

                    if(a_agent.m_can_error is not null)
                    {
                        a_agent.m_send_count = 0;
                    }

                    if(a_agent.m_send_count is 0)
                    {
                        if(a_agent.m_outbound_send is not 0)
                        {
                            return s_stop_sending;
                        }

                        a_agent.m_event_adapter.send_stop_finished();

                        return s_recv_only;
                    }

                    if(Monotonic.current_tick >= a_agent.m_deadline)
                    {
                        --a_agent.m_send_count;

                        a_agent.send();

                        a_agent.m_deadline += a_agent.m_send_interval;
                    }

                    a_scheduler.wait_messages(a_agent.m_deadline);

                    return this;
                }
            }

            private sealed class
            Send_Recv_Indef : State_Base<Intern>
            {
                protected override void
                init
                (Intern a_agent, State_Base<Intern> a_prev) => 
                    a_agent.m_deadline = Monotonic.current_tick;

                protected override State_Base<Intern>?
                iter
                (Intern a_agent, Scheduler a_scheduler)
                {
                    if(!a_scheduler.process_messages())
                    {
                        return null;
                    }

                    if(a_agent.m_command_deadline is not null)
                    {
                        return s_waiting_response_send_recv_indef;
                    }

                    if(a_agent.m_can_error is not null)
                    {
                        a_agent.m_send_count = 0;
                    }

                    if(a_agent.m_send_count is not null)
                    {
                        if(a_agent.m_outbound_send is not 0)
                        {
                            return s_stop_sending;
                        }

                        a_agent.m_event_adapter.send_stop_finished();

                        return s_recv_only;
                    }

                    if(Monotonic.current_tick >= a_agent.m_deadline)
                    {
                        a_agent.send();

                        a_agent.m_deadline += a_agent.m_send_interval;
                    }

                    a_scheduler.wait_messages(a_agent.m_deadline);

                    return this;
                }
            }

            private sealed class
            Stop_Sending : State_Base<Intern>
            {
                protected override State_Base<Intern>?
                iter
                (Intern a_agent, Scheduler a_scheduler)
                {
                    if(!a_scheduler.process_messages())
                    {
                        return null;
                    }

                    if(a_agent.m_outbound_send is 0)
                    {
                        a_agent.m_event_adapter.send_stop_finished();

                        return s_recv_only;
                    }

                    a_scheduler.wait_messages();

                    return this;
                }
            }

            private static void
            waiting_response_init
            (Intern a_agent)
            {
                Contracts.assert(a_agent.m_command_deadline is not null);

                a_agent.m_deadline = a_agent.m_command_deadline.Value;
            }

            private static State_Base<Intern>?
            waiting_response_iter
            (
                State_Base<Intern> a_this,
                Intern a_agent,
                Scheduler a_scheduler,
                State_Base<Intern> a_next_state
            )
            {
                if(!a_scheduler.process_messages())
                {
                    return null;
                }

                var a_product = a_agent.m_product;

                if(a_product.check_pending_command_completed() is Product.Command a_command)
                {
                    a_agent.m_command_deadline = null;

                    a_product.clear_pending_command();

                    a_agent.notify_command_finished(a_command);

                    return a_next_state;
                }

                if(a_agent.m_can_error is not null)
                {
                    a_agent.m_command_deadline = null;

                    a_agent.m_event_adapter.command_failed(a_product.get_pending_command(), "communication error");

                    a_product.clear_pending_command();

                    return a_next_state;
                }

                if(Monotonic.current_tick >= a_agent.m_deadline)
                {
                    a_agent.m_command_deadline = null;

                    a_agent.m_event_adapter.command_failed(a_product.get_pending_command(), "no response before timeout");

                    a_product.clear_pending_command();

                    return a_next_state;
                }

                a_scheduler.wait_messages(a_agent.m_deadline);

                return a_this;
            }

            private sealed class
            Waiting_Response_Recv_Only : State_Base<Intern>
            {
                protected override void
                init
                (Intern a_agent, State_Base<Intern> a_prev) =>
                    waiting_response_init(a_agent);

                protected override State_Base<Intern>?
                iter
                (Intern a_agent, Scheduler a_scheduler) =>
                    waiting_response_iter(this, a_agent, a_scheduler, s_recv_only);
            }

            private sealed class
            Waiting_Response_Send_Recv : State_Base<Intern>
            {
                protected override void
                init
                (Intern a_agent, State_Base<Intern> a_prev) =>
                    waiting_response_init(a_agent);

                protected override State_Base<Intern>?
                iter
                (Intern a_agent, Scheduler a_scheduler) =>
                    waiting_response_iter(this, a_agent, a_scheduler, s_send_recv);
            }

            private sealed class
            Waiting_Response_Send_Recv_Indef : State_Base<Intern>
            {
                protected override void
                init
                (Intern a_agent, State_Base<Intern> a_prev) =>
                    waiting_response_init(a_agent);

                protected override State_Base<Intern>?
                iter
                (Intern a_agent, Scheduler a_scheduler) =>
                    waiting_response_iter(this, a_agent, a_scheduler, s_send_recv_indef);
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
                        return s_recv_only;
                    }

                    a_scheduler.wait_messages();

                    return this;
                }
            }

            public static readonly Init s_init = new();
            private static readonly Recv_Only s_recv_only = new();
            private static readonly Send_Recv s_send_recv = new();
            private static readonly Send_Recv_Indef s_send_recv_indef = new();
            private static readonly Stop_Sending s_stop_sending = new();
            private static readonly Waiting_Response_Recv_Only s_waiting_response_recv_only = new();
            private static readonly Waiting_Response_Send_Recv s_waiting_response_send_recv = new();
            private static readonly Waiting_Response_Send_Recv_Indef s_waiting_response_send_recv_indef = new();
            private static readonly CAN_Error s_can_error = new();
        }

        public
        Intern
        (
            string a_name,
            CAN_Interface a_can_agent,
            Config_Data a_config,
            Product a_product
        ) :
        base(a_name)
        {
            m_can_agent = a_can_agent;
            m_config = a_config;
            m_product = a_product;
            m_state = new(State.s_init);
            m_event_adapter = new Event_Adapter_Dummy();
            m_current_dest = a_product.default_destination;
            m_current_query = a_product.default_query;
            m_send_count = 0;
            m_send_interval = DEFAULT_SEND_INTERVAL;
            m_outbound_send = 0;
            m_outbound_command = 0;
            m_deadline = 0;
            m_command_deadline = null;
            m_can_error = null;
        }

        private readonly CAN_Interface m_can_agent;
        private readonly Config_Data m_config;
        private readonly Product m_product;
        private readonly State_Machine<Intern> m_state;
        private Event_Adapter m_event_adapter;
        private Product.Destination? m_current_dest;
        private Product.Query? m_current_query;
        private uint? m_send_count;
        private uint m_send_interval;
        private uint m_outbound_send;
        private uint m_outbound_command;
        private long m_deadline;
        private long? m_command_deadline;
        (bool sent, string message)? m_can_error;

        #region messages

        public void
        msg_set_event_adapter
        (Event_Adapter a_adapter) => m_event_adapter = a_adapter;

        public void
        msg_set_send_dest
        (Product.Destination a_dest) => m_current_dest = a_dest;

        public void
        msg_enter_bootloader
        (Send_Agent a_extern)
        {
            Contracts.assert(m_product.enter_bootloader_command is not null);

            var a_command = m_product.enter_bootloader_command;

            if(m_can_error is not null)
            {
                m_event_adapter.command_failed(a_command, $"communication error: {nameof(msg_enter_bootloader)}");

                return;
            }

            m_product.add_new_command(m_current_dest, a_command);

            while(m_product.try_get_outgoing_can_message(out var a_message))
            {
                send_can_message(a_message.id, a_message.data.ToArray(), a_sent => a_extern.msg_command_sent(a_command));

                ++m_outbound_command;

                m_event_adapter.new_can_message_sent(a_message);
            }
        }

        public void
        msg_start_sending
        (uint a_ms, uint? a_count, Product.Query a_query)
        {
            m_send_interval = a_ms;
            m_send_count = a_count;
            m_current_query = a_query;
        }

        public void
        msg_update_send_count
        (uint? a_count)
        {
            if(a_count is not null)
            {
                m_event_adapter.new_send_count(a_count.Value);
            }

            Contracts.assert(m_outbound_send is not 0);

            --m_outbound_send;
        }

        public void
        msg_stop_sending() => m_send_count = 0;

        public void
        msg_send_once
        (Send_Agent a_extern, Product.Query a_query)
        {
            if(m_can_error is not null)
            {
                m_event_adapter.send_once_finished();

                return;
            }

            m_product.add_new_query(m_current_dest, a_query);

            while(m_product.try_get_outgoing_can_message(out var a_message))
            {
                send_can_message(a_message.id, a_message.data.ToArray(), a_sent => a_extern.msg_send_once_finished());

                ++m_outbound_send;

                m_event_adapter.new_can_message_sent(a_message);
            }
        }

        public void
        msg_send_once_finished()
        {
            Contracts.assert(m_outbound_send is not 0);

            if(--m_outbound_send is not 0)
            {
                return;
            }

            m_event_adapter.send_once_finished();
        }

        public void
        msg_command
        (Send_Agent a_extern, Product.Command a_command, string[] a_args)
        {
            if(m_can_error is not null)
            {
                m_event_adapter.command_failed(a_command, $"communication error: {nameof(msg_command)}");

                return;
            }

            try
            {
                m_product.add_new_command(m_current_dest, a_command, a_args);
            }
            catch(Exception a_except)
            {
                m_event_adapter.command_failed(a_command, a_except.Message);

                return;
            }

            while(m_product.try_get_outgoing_can_message(out var a_message))
            {
                send_can_message(a_message.id, a_message.data.ToArray(), a_sent => a_extern.msg_command_sent(a_command));

                ++m_outbound_command;

                m_event_adapter.new_can_message_sent(a_message);
            }
        }

        public void
        msg_command_sent
        (Product.Command a_command)
        {
            Contracts.assert(m_outbound_command is not 0);

            if(--m_outbound_command is not 0)
            {
                return;
            }

            if(a_command.response_timeout is uint a_timeout)
            {
                m_command_deadline = Monotonic.current_tick + a_timeout;

                return;
            }

            notify_command_finished(a_command);
        }

        public void
        msg_notify_command_finished
        (Product.Command a_command) =>
            m_event_adapter.command_finished(a_command);

        public void
        msg_can_message_received
        (CAN_ID a_recv_id, byte[] a_recv_data)
        {
            if(m_can_error is not null)
            {
                return;
            }

            m_product.add_new_can_message(a_recv_id, a_recv_data);

            while(m_product.try_get_mess_register_parsed(out var a_update))
            {
                var (a_register, a_message) = a_update;

                m_event_adapter.new_message_register_parsed(a_register, a_message);
            }

            while(m_product.try_get_stat_register_parsed(out var a_update))
            {
                var (a_register, a_status) = a_update;

                m_event_adapter.new_status_register_parsed(a_register, a_status);
            }
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

        private void
        send()
        {
            var a_extern = try_get_extern<Send_Agent>();

            if(a_extern is null)
            {
                return;
            }

            Contracts.assert(m_current_query is not null);

            var a_count = m_send_count;

            m_product.add_new_query(m_current_dest, m_current_query);

            while(m_product.try_get_outgoing_can_message(out var a_message))
            {
                send_can_message(a_message.id, a_message.data.ToArray(), a_sent => a_extern.msg_update_send_count(a_count));

                ++m_outbound_send;

                m_event_adapter.new_can_message_sent(a_message);
            }
        }

        private void
        notify_command_finished
        (Product.Command a_command)
        {
            var a_extern = try_get_extern<Send_Agent>();

            if(a_extern is null)
            {
                return;
            }

            if(m_config.bootloader is Config_Data.Bootloader_Table a_bootloader_table)
            {
                if(a_command.Equals(m_product.enter_bootloader_command))
                {
                    _ = Task.Delay(a_bootloader_table.reboot_time).ContinueWith(a_task => a_extern.msg_notify_command_finished(a_command));

                    return;
                }
            }

            m_event_adapter.command_finished(a_command);
        }

        protected override void
        run
        (Scheduler a_scheduler) => m_state.run(this, a_scheduler);

        public override void
        Dispose()
        {

        }
    }
}
