from marshmallow import validates, ValidationError, validate
from app.extensions import ma, db
from app.models.user import User, PayementCard
from app.models.location import Nation
from app.schemas.location import NationSchema

class DebitCardSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PayementCard
        load_instance = True
        include_fk = True

class UserSchema(ma.SQLAlchemyAutoSchema):
    cards = ma.Nested(DebitCardSchema, many=True)
    nation = ma.Nested(NationSchema, only=['id', 'name', 'code', 'alpha2'])
    class Meta:
        model = User
        load_instance = True
        include_fk = True
        exclude = ['password', 'roles']
        sqla_session = db.session  # This is important

    # Add validation for fields
    email = ma.Email(required=True,
                     error_messages={"required": "Email is required", "invalid": "Invalid email format"})
    name = ma.String(required=True, validate=validate.Length(min=2, max=100),
                     error_messages={"required": "Name is required", "invalid": "Invalid name format"})
    surname = ma.String(required=True, validate=validate.Length(min=2, max=100),
                        error_messages={"required": "Surname is required", "invalid": "Invalid surname format"})
    
    type = ma.String(required=True, attribute="type")

    @validates('nation_id')
    def validate_nation_id(self, value,data_key=None):
        if value is not None and not db.session.get(Nation, value):
            raise ValidationError("Nation with given ID does not exist.")


user_schema = UserSchema()
users_schema = UserSchema(many=True)
debit_card_schema = DebitCardSchema()
debit_cards_schema = DebitCardSchema(many=True) 
