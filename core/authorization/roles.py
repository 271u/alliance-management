ALLIANCE_VIEWER = "Alliance Viewer"
ALLIANCE_MANAGER = "Alliance Manager"
ALLIANCE_MODERATOR = "Alliance Moderator"


VIEWER_PERMISSIONS = {
    "core.view_player",
    "core.view_comment",
    "core.view_trainrotationentry",
}


MANAGER_PERMISSIONS = VIEWER_PERMISSIONS | {
    "core.change_player",
    "core.add_comment",
    "core.manage_train_rotation",
}


MODERATOR_PERMISSIONS = MANAGER_PERMISSIONS | {
    "core.delete_comment",
    "core.view_auditlog",
}

ROLE_PERMISSIONS = {
    ALLIANCE_VIEWER: VIEWER_PERMISSIONS,
    ALLIANCE_MANAGER: MANAGER_PERMISSIONS,
    ALLIANCE_MODERATOR: MODERATOR_PERMISSIONS,
}
