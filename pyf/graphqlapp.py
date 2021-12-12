from typing_extensions import Required

#from sqlalchemy.sql.sqltypes import Boolean
from graphene import ObjectType, Field, ID, String, List, DateTime, Mutation, Boolean
from graphene import Schema as GSchema

from starlette.graphql import GraphQLApp
#from starlette_graphene import GraphQLApp

import graphene

#import models.BaseEntities as BaseEntities

from contextlib import contextmanager

def attachGraphQL(app, sessionFunc, bindPoint='/gql'):
    """Attaches a Swagger endpoint to a FastAPI

    Parameters
    ----------
    app: FastAPI
        app to bind to
    prepareSession: lambda : session
        callable which returns a db session
    """
    assert callable(sessionFunc), "sessionFunc must be a function creating a session"

    # class Mutations(ObjectType):
    #     create_user = CreateUser.Field()
    #     update_user = UpdateUser.Field()

    def createQueryRoot():

        from graphqltypes.User import UserType, UserRootResolverById
        from graphqltypes.Group import GroupType, GroupRootResolverById, GroupRootResolverByName
        from graphqltypes.GroupType import GroupTypeType
        from graphqltypes.Role import RoleType
        from graphqltypes.RoleType import RoleTypeType, RoleTypeRootResolverById, RoleTypeRootResolverByName
        from graphqltypes.Event import EventType

        class Query(ObjectType):
            user = Field(UserType, id=ID(required=True), resolver=UserRootResolverById)
            group = Field(GroupType, id=ID(required=True), resolver=GroupRootResolverById)
            group_by_name = Field(GroupType, name=String(required=True), resolver=GroupRootResolverByName)
            roletype = Field(RoleTypeType, id=ID(required=True), resolver=RoleTypeRootResolverById)
            roletype_by_name = Field(RoleTypeType, name=String(required=True), resolver=RoleTypeRootResolverByName)

        return Query

    #router = fastapi.APIRouter()
    #https://github.com/graphql-python/graphene-sqlalchemy/issues/292
    #router = APIRouter()

    session_scope = contextmanager(sessionFunc)

    # class SessionMiddleware(object):
    #     # this does not work because of default resolvers
    #     def resolve(self, next, root, info, **args):
    #         print('SessionMiddleware Action')
    #         with session_scope() as session:
    #             print('info.context', info.context)
    #             info.context['session'] = session
    #             print('query for', args.keys())
    #             return next(root, info, **args)

    class localSchema(graphene.Schema):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)

        def execute(self, *args, **kwargs):
            with session_scope() as session:
                if 'context' in kwargs:
                    newkwargs = {**kwargs, 'context': {**kwargs['context'], 'session': session}}
                else:
                    newkwargs = {**kwargs, 'context': {'session': session}}
                return super().execute(*args, **newkwargs)

        async def execute_async(self, *args, **kwargs):
            with session_scope() as session:
                if 'context' in kwargs:
                    newkwargs = {**kwargs, 'context': {**kwargs['context'], 'session': session}}
                else:
                    newkwargs = {**kwargs, 'context': {'session': session}}
                return await super().execute_async(*args, **newkwargs)



    #graphql_app = GraphQLApp(schema=graphene.Schema(query=Query, mutation=Mutations), context_value={'session': None})#, middleware=[SessionMiddleware()])
    #app.add_route("/gql/", graphql_app)
    
    #graphql_app = GraphQLApp(schema=localSchema(query=Query, mutation=Mutations))
    #graphql_app = GraphQLApp(schema=localSchema(query=createQueryRoot(), mutation=Mutations))
    graphql_app = GraphQLApp(schema=localSchema(query=createQueryRoot()))
    
    app.add_route(bindPoint, graphql_app)

