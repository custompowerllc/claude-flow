using System;
using System.Collections.Generic;
using System.Collections.Immutable;
using System.Diagnostics.CodeAnalysis;
using System.Threading;
using program_ns.processing.products;
using utility.can;

namespace program_ns.processing;

using Mess_Register_Parsed = ValueTuple<Product.Message_Register, CAN_Message_Parsed>;
using Stat_Register_Parsed = ValueTuple<Product.Status_Register, byte>;

internal abstract class
Product
{
    public static Product
    make
    (Config_Data a_config) =>
        a_config.general.device switch
        {
            nameof(Aerosonde_One) => new Aerosonde_One(a_config),
            nameof(Aerosonde_Two_Lite) => new Aerosonde_Two_Lite(a_config),
            nameof(Aerosonde_Two_AFE) => new Aerosonde_Two_AFE(a_config),
            nameof(Aerosonde_Three) => new Aerosonde_Three(a_config),
            nameof(Aerosonde_Three_Charger) => new Aerosonde_Three_Charger(),
            nameof(Avd_One) => new Avd_One(a_config),
            nameof(Egalet) => new Egalet(),
            nameof(GA_LiFePO4) => new GA_LiFePO4(),
            nameof(GA_LiFePO4_Next) => new GA_LiFePO4_Next(a_config),
            nameof(Sikorsky_One) => new Sikorsky_One(a_config),
            nameof(Universal_Tester) => new Universal_Tester(),
            nameof(GE_Healthcare) => new GE_Healthcare(a_config),
            _ => throw new ArgumentException($"unrecognized device \"{a_config.general.device}\"", nameof(a_config))
        };

    public sealed class
    Destination : IEquatable<Destination>, IComparable, IComparable<Destination>
    {
        public uint id { init; get; }
        public string display_text { init; get; } = string.Empty;
        public override bool Equals(object? a_obj) => Equals(a_obj as Destination);
        public bool Equals(Destination? a_rhs) => a_rhs is not null && id.Equals(a_rhs.id);
        public int CompareTo(object? a_obj) => CompareTo(a_obj as Destination);
        public int CompareTo(Destination? a_rhs) => a_rhs is not null ? id.CompareTo(a_rhs.id) : 1;
        public override int GetHashCode() => id.GetHashCode();
        public override string ToString() => display_text;
    }

    public sealed class
    Message_Register : IEquatable<Message_Register>, IComparable, IComparable<Message_Register>
    {
        public uint id { init; get; }
        public string display_text { init; get; } = string.Empty;
        public override bool Equals(object? a_obj) => Equals(a_obj as Message_Register);
        public bool Equals(Message_Register? a_rhs) => a_rhs is not null && id.Equals(a_rhs.id);
        public int CompareTo(object? a_obj) => CompareTo(a_obj as Message_Register);
        public int CompareTo(Message_Register? a_rhs) => a_rhs is not null ? id.CompareTo(a_rhs.id) : 1;
        public override int GetHashCode() => id.GetHashCode();
        public override string ToString() => display_text;
    }

    public sealed class
    Status_Register : IEquatable<Status_Register>, IComparable, IComparable<Status_Register>
    {
        public uint id { init; get; }
        public string display_text { init; get; } = string.Empty;
        public (string display_text, bool always_reserved) bit7 { init; get; } = (string.Empty, true);
        public (string display_text, bool always_reserved) bit6 { init; get; } = (string.Empty, true);
        public (string display_text, bool always_reserved) bit5 { init; get; } = (string.Empty, true);
        public (string display_text, bool always_reserved) bit4 { init; get; } = (string.Empty, true);
        public (string display_text, bool always_reserved) bit3 { init; get; } = (string.Empty, true);
        public (string display_text, bool always_reserved) bit2 { init; get; } = (string.Empty, true);
        public (string display_text, bool always_reserved) bit1 { init; get; } = (string.Empty, true);
        public (string display_text, bool always_reserved) bit0 { init; get; } = (string.Empty, true);
        public override bool Equals(object? a_obj) => Equals(a_obj as Status_Register);
        public bool Equals(Status_Register? a_rhs) => a_rhs is not null && id.Equals(a_rhs.id);
        public int CompareTo(object? a_obj) => CompareTo(a_obj as Status_Register);
        public int CompareTo(Status_Register? a_rhs) => a_rhs is not null ? id.CompareTo(a_rhs.id) : 1;
        public override int GetHashCode() => id.GetHashCode();
        public override string ToString() => display_text;
    }

    public sealed class
    Query : IEquatable<Query>, IComparable, IComparable<Query>
    {
        public uint id { init; get; }
        public string display_text { init; get; } = string.Empty;
        public override bool Equals(object? a_obj) => Equals(a_obj as Query);
        public bool Equals(Query? a_rhs) => a_rhs is not null && id.Equals(a_rhs.id);
        public int CompareTo(object? a_obj) => CompareTo(a_obj as Query);
        public int CompareTo(Query? a_rhs) => a_rhs is not null ? id.CompareTo(a_rhs.id) : 1;
        public override int GetHashCode() => id.GetHashCode();
        public override string ToString() => display_text;
    }

    public sealed class
    Command : IEquatable<Command>, IComparable, IComparable<Command>
    {
        private static readonly ImmutableArray<(string, string)> s_empty_args = ImmutableArray.Create<(string, string)>();

        public uint id { init; get; }
        public string display_text { init; get; } = string.Empty;
        public ImmutableArray<(string display_text, string default_value)> arguments { init; get; } = s_empty_args;
        public uint? response_timeout { init; get; }
        public override bool Equals(object? a_obj) => Equals(a_obj as Command);
        public bool Equals(Command? a_rhs) => a_rhs is not null && id.Equals(a_rhs.id);
        public int CompareTo(object? a_obj) => CompareTo(a_obj as Command);
        public int CompareTo(Command? a_rhs) => a_rhs is not null ? id.CompareTo(a_rhs.id) : 1;
        public override int GetHashCode() => id.GetHashCode();
        public override string ToString() => display_text;
    }

    protected
    Product()
    {
        m_parsed_mess_register_updates = new();
        m_parsed_stat_register_updates = new();
        m_outgoing_can_messages = new();

        m_destination_map =
        new
        (
            () =>
            {
                var a_set = destination_set;
                var a_dict = new Dictionary<uint, Destination>(a_set.Count);

                foreach(var a_value in a_set)
                {
                    a_dict.Add(a_value.id, a_value);
                }

                return a_dict;
            },
            LazyThreadSafetyMode.ExecutionAndPublication
        );

        m_message_register_map =
        new
        (
            () =>
            {
                var a_set = message_register_set;
                var a_dict = new Dictionary<uint, Message_Register>(a_set.Count);

                foreach(var a_value in a_set)
                {
                    a_dict.Add(a_value.id, a_value);
                }

                return a_dict;
            },
            LazyThreadSafetyMode.ExecutionAndPublication
        );

        m_status_register_map =
        new
        (
            () =>
            {
                var a_set = status_register_set;
                var a_dict = new Dictionary<uint, Status_Register>(a_set.Count);

                foreach(var a_value in a_set)
                {
                    a_dict.Add(a_value.id, a_value);
                }

                return a_dict;
            },
            LazyThreadSafetyMode.ExecutionAndPublication
        );

        m_query_map =
        new
        (
            () =>
            {
                var a_set = query_set;
                var a_dict = new Dictionary<uint, Query>(a_set.Count);

                foreach(var a_value in a_set)
                {
                    a_dict.Add(a_value.id, a_value);
                }

                return a_dict;
            },
            LazyThreadSafetyMode.ExecutionAndPublication
        );

        m_command_map =
        new
        (
            () =>
            {
                var a_set = command_set;
                var a_dict = new Dictionary<uint, Command>(a_set.Count);

                foreach(var a_value in a_set)
                {
                    a_dict.Add(a_value.id, a_value);
                }

                return a_dict;
            },
            LazyThreadSafetyMode.ExecutionAndPublication
        );

        m_pending_command = null;
    }

    private readonly Queue<Mess_Register_Parsed> m_parsed_mess_register_updates;
    private readonly Queue<Stat_Register_Parsed> m_parsed_stat_register_updates;
    private readonly Queue<CAN_Message_Parsed> m_outgoing_can_messages;
    private readonly Lazy<Dictionary<uint, Destination>> m_destination_map;
    private readonly Lazy<Dictionary<uint, Message_Register>> m_message_register_map;
    private readonly Lazy<Dictionary<uint, Status_Register>> m_status_register_map;
    private readonly Lazy<Dictionary<uint, Query>> m_query_map;
    private readonly Lazy<Dictionary<uint, Command>> m_command_map;
    private (Command cmd, bool complete)? m_pending_command;

    public abstract IReadOnlySet<Destination> destination_set { get; }
    public abstract IReadOnlySet<Message_Register> message_register_set { get; }
    public abstract IReadOnlySet<Status_Register> status_register_set { get; }
    public abstract IReadOnlySet<Query> query_set { get; }
    public abstract IReadOnlySet<Command> command_set { get; }
    public abstract Destination? default_destination { get; }
    public abstract Query? default_query { get; }
    public abstract Command? enter_bootloader_command { get; }
    public IReadOnlyDictionary<uint, Destination> destination_map => m_destination_map.Value;
    public IReadOnlyDictionary<uint, Message_Register> message_register_map => m_message_register_map.Value;
    public IReadOnlyDictionary<uint, Status_Register> status_register_map => m_status_register_map.Value;
    public IReadOnlyDictionary<uint, Query> query_map => m_query_map.Value;
    public IReadOnlyDictionary<uint, Command> command_map => m_command_map.Value;

    public void
    add_new_can_message
    (CAN_ID a_id, in ReadOnlySpan<byte> a_data) => new_can_message(a_id, a_data);

    protected abstract void
    new_can_message
    (CAN_ID a_id, in ReadOnlySpan<byte> a_data);

    public void
    add_new_query
    (Destination? a_dest, Query a_query) => new_query(a_dest, a_query);

    protected abstract void
    new_query
    (Destination? a_dest, Query a_query);

    public void
    add_new_command
    (Destination? a_dest, Command a_command) =>
        add_new_command(a_dest, a_command, ReadOnlySpan<string>.Empty);

    public void
    add_new_command
    (Destination? a_dest, Command a_command, in ReadOnlySpan<string> a_args)
    {
        if(a_command.response_timeout is not null)
        {
            if(m_pending_command is not null)
            {
                throw new InvalidOperationException();
            }

            m_pending_command = (a_command, false);

            try
            {
                new_command(a_dest, a_command, a_args);
            }
            catch
            {
                clear_pending_command();

                throw;
            }

            return;
        }

        new_command(a_dest, a_command, a_args);
    }

    protected abstract void
    new_command
    (Destination? a_dest, Command a_command, in ReadOnlySpan<string> a_args);

    public Command
    get_pending_command()
    {
        if(m_pending_command is null)
        {
            throw new InvalidOperationException();
        }

        return m_pending_command.Value.cmd;
    }

    public Command?
    check_pending_command_completed()
    {
        if(m_pending_command is null)
        {
            throw new InvalidOperationException();
        }

        var (a_command, a_completed) = m_pending_command.Value;

        return a_completed ? a_command : null;
    }

    public void
    clear_pending_command()
    {
        if(m_pending_command is null)
        {
            throw new InvalidOperationException();
        }

        m_pending_command = null;
    }

    public void
    set_pending_command_completed()
    {
        if(m_pending_command is null)
        {
            return;
        }

        var (a_command, a_completed) = m_pending_command.Value;

        if(a_completed)
        {
            return;
        }

        m_pending_command = (a_command, true);
    }

    public bool
    try_get_mess_register_parsed
    (out Mess_Register_Parsed a_update) =>
        m_parsed_mess_register_updates.TryDequeue(out a_update);

    public bool
    try_get_stat_register_parsed
    (out Stat_Register_Parsed a_update) =>
        m_parsed_stat_register_updates.TryDequeue(out a_update);

    public bool
    try_get_outgoing_can_message
    ([MaybeNullWhen(false)] out CAN_Message_Parsed a_update) =>
        m_outgoing_can_messages.TryDequeue(out a_update);

    protected void
    add_mess_register_parsed
    (Message_Register a_register, CAN_Message_Parsed a_message) =>
        m_parsed_mess_register_updates.Enqueue((a_register, a_message));

    protected void
    add_stat_register_parsed
    (Status_Register a_register, byte a_status) =>
        m_parsed_stat_register_updates.Enqueue((a_register, a_status));

    protected void
    add_outgoing_can_message
    (CAN_Message_Parsed a_message) =>
        m_outgoing_can_messages.Enqueue(a_message);
}
