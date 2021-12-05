from tortoise.models import Model
from tortoise import fields
from uuid import uuid4
from textwrap import dedent
from olgram.settings import DatabaseSettings


class MetaInfo(Model):
    id = fields.IntField(pk=True)
    version = fields.IntField(default=0)

    def __init__(self, **kwargs):
        # Кажется это единственный способ сделать single-instance модель в TortoiseORM :(
        if "id" in kwargs:
            kwargs["id"] = 0
        self.id = 0
        super(MetaInfo, self).__init__(**kwargs)

    class Meta:
        table = '_custom_meta_info'


class Bot(Model):
    id = fields.IntField(pk=True)
    token = fields.CharField(max_length=200, unique=True)
    owner = fields.ForeignKeyField("models.User", related_name="bots")
    name = fields.CharField(max_length=33)
    code = fields.UUIDField(default=uuid4, index=True)
    start_text = fields.TextField(default=dedent("""
    Здравствуйте!
    Напишите ваш вопрос и мы ответим вам в ближайшее время.
    """))
    second_text = fields.TextField(null=True, default=None)

    group_chats = fields.ManyToManyField("models.GroupChat", related_name="bots", on_delete=fields.relational.CASCADE,
                                         null=True)
    group_chat = fields.ForeignKeyField("models.GroupChat", related_name="active_bots",
                                        on_delete=fields.relational.CASCADE,
                                        null=True)

    def decrypted_token(self):
        cryptor = DatabaseSettings.cryptor()
        return cryptor.decrypt(self.token)

    @classmethod
    def encrypted_token(cls, token: str):
        cryptor = DatabaseSettings.cryptor()
        return cryptor.encrypt(token)

    async def super_chat_id(self):
        group_chat = await self.group_chat
        if group_chat:
            return group_chat.chat_id
        return (await self.owner).telegram_id

    class Meta:
        table = 'bot'


class User(Model):
    id = fields.IntField(pk=True)
    telegram_id = fields.BigIntField(index=True, unique=True)

    class Meta:
        table = 'user'


class GroupChat(Model):
    id = fields.IntField(pk=True)
    chat_id = fields.BigIntField(index=True, unique=True)
    name = fields.CharField(max_length=255)

    class Meta:
        table = 'group_chat'
