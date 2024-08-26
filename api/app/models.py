from app import db, bcrypt
from sqlalchemy.ext.hybrid import hybrid_property


# helped by https://www.youtube.com/watch?v=PppslXOR7TA
# https://docs.sqlalchemy.org/en/20/orm/mapped_attributes.html
class Admin(db.Model):
    """Model for an administrtor account

    Attributes:
        username: Admin username
        pass_hash: The hashed user password

    methods:
        verify_password(password): returns boolean value indicating if the password matches that of the user
        to_json(): returns ba json representation of the user
    """

    __tablename__ = "admin"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

    # proxy var for password hashing
    _pass_hash = db.mapped_column(
        "pass_hash", db.String(80), unique=False, nullable=False
    )

    # https://docs.sqlalchemy.org/en/14/orm/extensions/hybrid.html
    @hybrid_property
    def pass_hash(self):
        return self._pass_hash

    @pass_hash.setter
    def pass_hash(self, password):
        """Setter for password, hashes before entry
        Args:
            self: the Admin object
            password: the password to hash and add
        """
        self._pass_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def verify_password(self, password):
        """Verifies a password against user
        Args:
            self: the Admin object
            password: Password to check

        Returns:
            password: Boolean indicating match or not
        """
        return bcrypt.check_password_hash(self.pass_hash, password)

    def to_json(self):
        """Creates a json representation of the user
        Returns:
            admin: A JSON representation of the user
        """
        return {"id": self.id, "username": self.username, "passHash": self.pass_hash}


class GeneList(db.Model):
    """Model for a gene list

    Attributes:
        gene_list: A csv string of the gene list

    methods:
        to_json(): returns ba json representation of the list
    """

    __tablename__ = "gene_list"

    id = db.Column(db.Integer, primary_key=True)
    gene_list = db.Column(db.Text, nullable=False)

    def to_json(self):
        """Creates a json representation of the gene list
        Returns:
            gene_list: A JSON representation of the gene list
        """
        return {"id": self.id, "geneList": self.gene_list}
