from config.database import db_session
from models.resource import Resource
from tasks.tfrunner import tf_apply

session = next(db_session())
resource = (
    session.query(Resource)
    .filter(Resource.workspace_id == "da325ac6-3639-4d79-9014-943f09fbdc8f")
    .first()
)

resource_id = str(resource.id)
task_id = tf_apply.apply_async(args=[resource_id], task_id=resource_id)
