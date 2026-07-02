from ..models.vet_dashboard_model import VetDashboardModel


class VetController:
    def __init__(self, vet_id):
        self.vet_id = vet_id
        self.model = VetDashboardModel(vet_id)

    def fetch_recent_pets(self):
        return self.model.fetch_recent_pets()

    def fetch_alerts(self):
        return self.model.fetch_alerts()

    def fetch_unread_count(self):
        return self.model.fetch_unread_count()

    def mark_all_read(self):
        return self.model.mark_all_read()

    def mark_notification_read(self, notification_id):
        return self.model.mark_notification_read(notification_id)

    def fetch_metrics(self):
        return self.model.fetch_metrics()
