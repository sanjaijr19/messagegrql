import json
import graphene
from django.contrib.auth.models import User
from graphene_django import DjangoObjectType
from .models import Dialog, Message

class IntPkMixin(object):
    id = graphene.Int(source='pk')


class UserType(IntPkMixin, DjangoObjectType):
    name = graphene.String()

    class Meta:
        model = User

    def resolve_name(self, info):
        name = 'User {}'.format(self.id)
        if self.first_name and self.last_name:
            name = '{} {}'.format(self.first_name, self.last_name)
        if self.first_name:
            name = self.first_name
        name = getattr(self, 'name', None)
        if name:
            name = name
        if self.username:
            name = self.username
        return name


class DialogType(IntPkMixin, DjangoObjectType):
    class Meta:
        model = Dialog


class MessageType(IntPkMixin, DjangoObjectType):
    user = graphene.Field(UserType)

    class Meta:
        model = Message

    def resolve_user(self, info):
        return self.user
class Query(graphene.ObjectType):
    all_bio = graphene.List(MessageType)

class SaveMessage(graphene.Mutation):
    status = graphene.Int()
    formErrors = graphene.String()
    message = graphene.Field(MessageType)

    class Arguments:
        text = graphene.String()
        dialog_id = graphene.Int()
        user_id = graphene.Int()

    def mutate(root, info, text, dialog_id=None, user_id=None):
        current_user = info.context.user
        if not text:
            return SaveMessage(
                status=400,
                formErrors=json.dumps(
                    {'text': ['Please enter message.']})
            )
        dialog = Dialog.objects.filter(id=dialog_id).first()
        if not dialog and not user_id:
            return SaveMessage(
                status=404,
                formErrors=json.dumps({
                    'text': ['To create dialog should be second user']
                }))
        elif user_id and not dialog:
            user2 = User.objects.filter(id=user_id).first()
            if not user2:
                return SaveMessage(
                    status=404,
                    formErrors=json.dumps({
                        'user_id': ['User not fountd: {}'.format(user_id)]
                    }))
            dialog = Dialog.objects.create(user1=current_user, user2=user2)
        instance = Message.objects.create(
            user=info.context.user,
            text=text,
            dialog=dialog
        )
        return SaveMessage(
            status=201,
            message=instance,
        )

class Mutation(SaveMessage, graphene.ObjectType):
    pass




class GetChat(object):
    dialog = graphene.Field(DialogType,
                            id=graphene.Int())

    message = graphene.Field(MessageType,
                        id=graphene.Int())

    dialog_messages = graphene.List(MessageType)
class GetUser(graphene.ObjectType):
    user = graphene.Field(UserType)

    def resolve_dialog(self, info, **kwargs):
        dialog = None
        current_user = info.context.user
        id = kwargs.get('id')
        if id:
            dialog = Dialog.objects.get(id=id)
            if dialog.user1 != current_user or dialog.user2 != current_user:
                dialog = None
        return dialog

    def resolve_all_messages(self, info, **kwargs):
        return Message.objects.select_related('dialog').all()

    def resolve_message(self, info, **kwargs):
        message = None
        if 'id' in kwargs:
            message = Message.objects.get(id=kwargs.get('id'))
        return message

    def resolve_user(self, info, **kwargs):
        user = None
        if 'id' in kwargs:
            user = User.objects.get(id=kwargs.get('id'))
        return user


class ChatMutation(graphene.ObjectType):
    create_message = SaveMessage.Field()


schema=graphene.Schema(mutation=ChatMutation,query=GetUser)