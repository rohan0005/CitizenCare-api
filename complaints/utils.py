from .models import ActivityLog

def create_activity_log(complaint, user, action, old_value="", new_value=""):
	activityLog = ActivityLog.objects.create(
		complaint=complaint,
		user=user,
		action=action,
		old_value=old_value,
		new_value=new_value
		)

	return activityLog
