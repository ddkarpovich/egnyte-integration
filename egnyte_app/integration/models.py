from egnyte_app.app import db


class EgnyteIntegration(db.Model):
    """Box API integration settings."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='egnyte_integration')
    access_token = db.Column(db.String(255))
    expires_in = db.Column(db.String(20))
    latest_event_id = db.Column(db.Integer, nullable=True)

    def __str__(self) -> str:
        return self.id
