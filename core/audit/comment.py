from typing import Any

from django.contrib.contenttypes.models import ContentType

from core.audit.helpers import create_audit_log
from core.models.db.auditlog import AuditLog
from core.models.db.comment import Comment
from core.models.db.image_attachment import ImageAttachment


def get_comment_target_data(comment: Comment) -> dict[str, Any]:
    target = comment.content_object

    return {
        "content_type": f"{comment.content_type.app_label}.{comment.content_type.model}",
        "object_id": str(comment.object_id),
        "object_repr": str(target) if target is not None else "Unknown object",
    }


def get_comment_object_repr(comment: Comment) -> str:
    target_data = get_comment_target_data(comment)
    return f"Comment #{comment.id} on {target_data['object_repr']}" # pyright: ignore[reportAttributeAccessIssue]


def get_comment_image_data(comment: Comment) -> list[dict[str, Any]]:
    comment_content_type = ContentType.objects.get_for_model(Comment)

    attachments = (
        ImageAttachment.objects
        .filter(
            content_type=comment_content_type,
            object_id=str(comment.id), # pyright: ignore[reportAttributeAccessIssue]
        )
        .select_related("image")
        .order_by("created_at")
    )

    return [
        {
            "image_id": str(attachment.image.id),
            "filename": attachment.image.original_filename,
            "mime_type": attachment.image.mime_type,
            "size": attachment.image.size,
            "width": attachment.image.width,
            "height": attachment.image.height,
        }
        for attachment in attachments
    ]


def create_comment_created_audit_log(comment: Comment) -> AuditLog:
    target_data = get_comment_target_data(comment)
    images = get_comment_image_data(comment)

    changes = {
        "text": {
            "old": None,
            "new": comment.text,
        },
        "target": {
            "old": None,
            "new": target_data,
        },
        "images": {
            "old": [],
            "new": images,
        },
    }

    image_count = len(images)

    if image_count == 0:
        message = f"Created comment on {target_data['object_repr']}."
    elif image_count == 1:
        message = f"Created comment on {target_data['object_repr']} with 1 image."
    else:
        message = f"Created comment on {target_data['object_repr']} with {image_count} images."

    return create_audit_log(
        model=Comment,
        object_id=str(comment.id), # pyright: ignore[reportAttributeAccessIssue]
        object_repr=get_comment_object_repr(comment),
        action=AuditLog.Action.CREATED,
        changes=changes,
        message=message,
    )


def create_comment_deleted_audit_log(comment: Comment) -> AuditLog:
    target_data = get_comment_target_data(comment)
    images = get_comment_image_data(comment)

    changes = {
        "deleted_at": {
            "old": None,
            "new": comment.deleted_at.isoformat() if comment.deleted_at else None,
        },
        "deleted_by": {
            "old": None,
            "new": str(comment.deleted_by) if comment.deleted_by else None,
        },
        "text": {
            "old": comment.text,
            "new": None,
        },
        "target": {
            "old": target_data,
            "new": target_data,
        },
        "images": {
            "old": images,
            "new": [],
        },
    }

    return create_audit_log(
        model=Comment,
        object_id=str(comment.id), # pyright: ignore[reportAttributeAccessIssue]
        object_repr=get_comment_object_repr(comment),
        action=AuditLog.Action.DELETED,
        changes=changes,
        message=f"Deleted comment on {target_data['object_repr']}.",
    )
