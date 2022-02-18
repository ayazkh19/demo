"""
    this file is part of web application in flask framework
    this is partial models file which define the database tabels of application
    and is not workable standalone
    only for demonstration puposes
"""
    

from myproject import db
from werkzeug.security import generate_password_hash
from flask_security import UserMixin
from datetime import date

######################################################################################
################ MODELS  #############################################################
######################################################################################

class Role(db.Model):
    __tablename__ = 'AspNetRoles'
    id = db.Column(db.String(450), primary_key=True)
    name = db.Column(db.String(450), unique=True)
    Description = db.Column(db.String(500),primary_key=False)

# Define the UserRoles association table
class UserRoles(db.Model):
    __tablename__ = 'AspNetUserRoles'
    id = db.Column(db.Integer(), primary_key=True)
    UserId = db.Column(db.String(450), db.ForeignKey('AspNetUsers.id', ondelete='CASCADE'))
    RoleId = db.Column(db.String(450), db.ForeignKey('AspNetRoles.id', ondelete='CASCADE'))

class User(db.Model, UserMixin):
    __tablename__ = "AspNetUsers"
    id  = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(500),primary_key=False)
    email = db.Column(db.String(500),primary_key=False)
    PasswordHash = db.Column(db.String(500),primary_key=False)
    password = db.Column(db.String(500),primary_key=False)
    active = db.Column(db.Boolean)
    NameFirst = db.Column(db.String(500),primary_key=False)
    NameLast = db.Column(db.String(500),primary_key=False)
    EmployeeNumber  = db.Column(db.String(500),primary_key=False)
    FunctionName = db.Column(db.String(500),primary_key=False)

    # relationships
    roles = db.relationship('Role', secondary='AspNetUserRoles')
    projectUsers = db.relationship('ProjectUser', backref="user")

    # initializing user
    def __init__(self,email, username, passwordInput):
        self.username=username
        self.email=email
        self.PasswordHash= generate_password_hash(passwordInput)
        # self.test= test

    def check_password(self,passwordInput):
        return check_password(self.password,passwordInput)

    # print
    def __repr__(self):
        return f"Username is {self.username} user email is {self.email} password is {self.PasswordHash}"

    # json
    def json(self):
        return {'name': self.username}

#################################################################################################
################ MODELS T  ##############################################################
#################################################################################################


class Country(db.Model):
    __tablename__ = 'Country'
    Id = db.Column(db.Integer(), primary_key=True)
    CountryName = db.Column(db.String(450), unique=True)
    CountryNameShort = db.Column(db.String(450), unique=True)

    # relationships
    companies = db.relationship("Company", backref="country")


class Company(db.Model):
    __tablename__ = "Company"
    Id = db.Column(db.Integer(), primary_key=True)
    CompanyName = db.Column(db.String(450), unique=True)
    CompanyWebsite = db.Column(db.String(450), unique=True)
    CompanyDescription = db.Column(db.String(450), unique=True)
    gen_CountryId = db.Column(db.Integer, db.ForeignKey('Country.Id'))

    # relationships
    # country = db.relationship("Country", back_populates="companies")
    support_crafts = db.relationship("SupportCraft", backref="support_craft_company")

    def __init__(self, name, website, desc, country_id):
        self.CompanyName = name
        self.CompanyWebsite = website
        self.CompanyDescription = desc
        self.gen_CountryId = country_id


class Bhd(db.Model):
    __tablename__ = 'Bhd'
    Id = db.Column(db.Integer(), primary_key=True)
    tech_CompanyId = db.Column(db.Integer, db.ForeignKey('Company.Id'))
    BhdName = db.Column(db.String(250), primary_key=False)

    # relationship
    projDredgers = db.relationship('ProjectDredger', back_populates='bhd', cascade="delete, merge, save-update")

    def __init__(self, company_id, bhd_name):
        self.tech_CompanyId = company_id
        self.BhdName = bhd_name


class Csd(db.Model):
    __tablename__ = 'Csd'
    Id = db.Column(db.Integer(), primary_key=True)
    tech_CompanyId = db.Column(db.Integer, db.ForeignKey('Company.Id'))
    CsdName = db.Column(db.String(250), primary_key=False)

    # relationship
    projDredgers = db.relationship('ProjectDredger', back_populates='csd', cascade="delete, merge, save-update")

    def __init__(self, company_id, csd_name):
        self.tech_CompanyId = company_id
        self.CsdName = csd_name


class Tshd(db.Model):
    __tablename__ = 'Tshd'
    Id = db.Column(db.Integer(), primary_key=True)
    tech_CompanyId = db.Column(db.Integer, db.ForeignKey('Company.Id'))
    TshdName = db.Column(db.String(250), primary_key=False)

    # relationship
    projDredgers = db.relationship('ProjectDredger', back_populates='tshd', cascade="delete, merge, save-update")

    def __init__(self, company_id, tshd_name):
        self.tech_CompanyId = company_id
        self.TshdName = tshd_name


class SupportCraftType(db.Model):
    __tablename__ = 'SupportCraftType'
    Id = db.Column(db.Integer(), primary_key=True)
    SupportCraftTypeName = db.Column(db.String(250), primary_key=False)

    # relationships
    supportCrafts = db.relationship("SupportCraft", backref="supportCraftType")

    def __init__(self, name):
        self.SupportCraftTypeName = name






