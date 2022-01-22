events = {
    "authenticated": "on_ready",
    "multiDeviceStatus": "on_self_multi_device_status",
    "disconnected": "on_disconnect",

    # Message events
    "message:created": "on_message",
    "message:deleted": "on_message_delete",
    "message:updated": "on_message_update",
    "message:reaction_updated": "on_reaction_update",

    # Dm only
    "channel:created": "on_dm_channel_create",
    "channel:deleted": "on_dm_channel_delete",

    # Server based events
    "server:channel_created": "on_channel_create",
    "server:channel_deleted": "on_channel_delete",
    "server:channel_updated": "on_channel_update",

    # Guild/Server based events
    "server:joined": "on_server_join",
    "server:left": "on_server_exit",
    "server:updated": "on_server_update",

    # Member events
    "server:member_added": "on_member_join",
    "server:member_removed": "on_member_exit",

    # Roles events
    "server:roles_updated": "on_role_update",
    "server:role_created": "on_role_create",
    "server:role_deleted": "on_role_delete",

    # When a user gets/loses a role
    "server:role_added_to_member": "on_role_add",
    "server:role_removed_from_member": "on_role_remove",

    "user:typing": "on_typing",
    "user:call_joined": "on_call_join",
    "user:call_left": "on_call_leave",
    "voice:signal_received": "on_voice_signal",

    # Relationship events
    "relationship:added": "on_relationship_add",
    "relationship:deleted": "on_relationship_remove",
    "relationship_accepted": "on_relationship_accept",

    # User events
    "user:updated": "on_user_update",
    "user:status_changed": "on_user_status_change",
    "user:custom_status_changed": "on_user_custom_status_change",
    "user:program_activity_changed": "on_user_program_activity_change",
}
