from mini import db

page_tag = db.Table('page_tag', db.metadata,
    db.Column('page_id', db.Integer, db.ForeignKey('wiki_page.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('wiki_tag.id'))
)

class Page(db.Model):
    __tablename__ = "wiki_page"
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(64), unique=True)
    title = db.Column(db.String(128))
    text = db.Column(db.Text)

    tags = db.relationship("Tag", backref="pages", secondary=page_tag)

class Tag(db.Model):
    __tablename__ = "wiki_tag"
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(64), unique=True)
