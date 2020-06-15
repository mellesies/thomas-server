# -*- coding: utf-8 -*-
"""Schemas for use in resources."""
import logging

from flask import url_for
from marshmallow import post_dump, pre_dump, pre_load

from sqlalchemy.inspection import inspect
from sqlalchemy.orm.collections import InstrumentedList

from .. import util
from .. import db
from ..server import ma

SQLAlchemyAutoSchema = ma.SQLAlchemyAutoSchema

module_name = __name__.split('.')[-1]
log = logging.getLogger(module_name)


class ResourceSchema(SQLAlchemyAutoSchema):
    """Base schema for db.*"""

    # Defining these keys here ensures they are on top in the serialized result.
    # It also means the keys are always in the output if we don't delete them
    # manually later :-(
    resourceType = ma.Method('get_resource_type', dump_only=True)
    _id = ma.Constant(None, dump_only=True)
    _links = ma.Constant(None, dump_only=True)
    _excluded = ma.Constant(None, dump_only=True)
    _embedded = ma.Constant(None, dump_only=True)

    def get_resource_type(self, obj):
        """Return the resource type.

            Defaults to the SQLAlchemy object's classname.
        """
        return obj.__class__.__name__

    @pre_load
    def do_pre_processing(self, obj, **kwargs):
        """Do preprocessing.

        Preprocessing entails the following:
         - Remove any keys starting with an underscore ('_')
         - Remove the key 'resourceType'
        """
        keys = list(obj.keys())

        for key in keys:
            if key.startswith('_'):
                obj.pop(key)

        try:
            obj.pop('resourceType')
        except:
            pass

        return obj

    @post_dump(pass_original=True)
    def do_post_processing(self, in_data, obj, **kwargs):
        """Do post-processing (after serialization)."""
        in_data = self.add_id(in_data, obj, **kwargs)
        in_data = self.add_links(in_data, obj, **kwargs)
        in_data = self.add_embedded(in_data, obj, **kwargs)
        in_data = self.add_excluded(in_data, obj, **kwargs)

        for key in ['_links', '_embedded']:
            if in_data[key] is None:
                in_data.pop(key)

        return in_data

    def add_embedded(self, in_data, obj, **kwargs):
        """Add any embedded resources as specified by context."""
        if not self.context.get('embed'):
            return in_data

        # embed should be a list of related resources to embed
        embed = self.context.get('embed')
        _embedded = {}

        db_class = obj.__class__

        # Interate over the attributes to embed under '_embedded'
        for attr in embed:
            log.debug(f"Trying to embed '{attr}'")
            try:
                value = getattr(obj, attr)
            except AttributeError as e:
                log.error(f"Could not embed '{attr}': {e}")
                continue

            log.debug(f"Found a value of type '{type(value)}'")

            # Determine the class of the attribute to derive the associated
            # Schema. Fall back to jsonifying the SQLAlchemy object if
            # necessary.
            try:
                RemoteClass = getattr(db_class, attr).property.mapper.class_
            except AttributeError as e:
                log.error(f"Could not embed '{attr}': {e}")
                continue

            SchemaClass = globals().get(f'{RemoteClass.__name__}Schema')

            log.debug(f"  RemoteClass: '{RemoteClass}'")
            log.debug(f"  SchemaClass: '{SchemaClass}'")

            if SchemaClass:
                value = SchemaClass().dump(
                    value,
                    many=isinstance(value, InstrumentedList)
                )
            else:
                log.warn(f'Could not serialize "{remote_class}" using schema!?')
                value = db.to_dict(value)

            # Add the serialized attribute to '_embedded'
            _embedded[attr] = value

        # Add the _embedded key in the data
        in_data['_embedded'] = _embedded
        return in_data

    def add_excluded(self, in_data, obj, **kwargs):
        """Add a list of excluded keys."""
        # print(self.exclude)
        in_data['_excluded'] = list(self.exclude)
        return in_data

    def add_id(self, in_data, obj, **kwargs):
        """Add url to self."""
        _id = url_for(obj.clsname().lower(), id_or_operation=obj.id)
        in_data['_id']= _id
        return in_data

    def add_links(self, in_data, obj, **kwargs):
        """Add hyperlinks as specified by context."""
        # log.warn("--- ADD LINKS ---")

        if not self.context.get('links'):
            return in_data

        # Define the basic links to the current object and its collection.
        _links = {
            '_self': url_for(obj.clsname().lower(), id_or_operation=obj.id),
            '_collection': url_for(obj.clsname().lower()),
        }

        # Add any relationships this object might have.
        for attr in inspect(obj.__class__).relationships.keys():
            value = getattr(obj, attr)

            if isinstance(value, InstrumentedList):
                urls = []

                for item in value:
                    endpoint = item.clsname().lower()
                    urls.append(url_for(endpoint, id_or_operation=item.id))

                _links[attr] = urls

            else:
                endpoint = value.clsname().lower()
                _links[attr] = url_for(endpoint, id_or_operation=value.id)

        in_data['_links'] = _links
        return in_data

class NetworkSchema(ResourceSchema):
    """Schema for db.Network"""
    class Meta:
        model = db.Network
        ordered = True
        # exclude = ['json', ]
        # include_fk = True


class RoleSchema(ResourceSchema):
    """Schema for db.Role"""
    class Meta:
        model = db.Role
        ordered = True



class UserSchema(ResourceSchema):
    """Schema for db.User"""
    class Meta:
        model = db.User
        ordered = True

        exclude = [
            'password_hash',
        ]
