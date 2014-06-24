# -*- coding: utf-8 -*-

from mini import db
from datetime import datetime
from flask import url_for, Markup

class Member(db.Model):
    __tablename__ = "member"
    id = db.Column(db.Integer, primary_key = True)
    type = db.Column(db.String(30))

    identifier = db.Column(db.String(80), unique=True)
    name = db.Column(db.String(80))

    __mapper_args__ = {
        'polymorphic_identity': __tablename__,
        'polymorphic_on': type
    }

team_members = db.Table('team_members', db.metadata,
    db.Column('team_id', db.Integer, db.ForeignKey('team.id')),
    db.Column('member_id', db.Integer, db.ForeignKey('member.id'))
)

class Team(Member):
    __tablename__ = "team"
    id = db.Column(db.Integer, db.ForeignKey("member.id"), primary_key = True)
    description = db.Column(db.Text)
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    members = db.relationship("Member", backref="teams", secondary=team_members)

    def get_link(self, size=16):
        return Markup('<span class="team"><a href="{1}">{0}</a></span>'.format(self.name, self.get_url()))

    def get_url(self):
        return url_for("team", identifier=self.identifier)
