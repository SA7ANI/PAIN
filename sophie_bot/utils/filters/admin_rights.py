# Copyright (C) 2019 The Raphielscape Company LLC.
# Copyright (C) 2018 - 2019 MrYacha
# Copyright (C) 2019 Aiogram
#
# This file is part of SophieBot.
#
# SophieBot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License

from dataclasses import dataclass

from aiogram.dispatcher.filters import Filter

from sophie_bot import BOT_ID, dp
from sophie_bot.modules.utils.language import get_strings
from sophie_bot.modules.utils.user_details import check_admin_rights


@dataclass
class UserRestricting(Filter):
    admin: bool = False
    can_post_messages: bool = False
    can_edit_messages: bool = False
    can_delete_messages: bool = False
    can_restrict_members: bool = False
    can_promote_members: bool = False
    can_change_info: bool = False
    can_invite_users: bool = False
    can_pin_messages: bool = False

    ARGUMENTS = {
        "user_admin": "admin",
        "user_can_post_messages": "can_post_messages",
        "user_can_edit_messages": "can_edit_messages",
        "user_can_delete_messages": "can_delete_messages",
        "user_can_restrict_members": "can_restrict_members",
        "user_can_promote_members": "can_promote_members",
        "user_can_change_info": "can_change_info",
        "user_can_invite_users": "can_invite_users",
        "user_can_pin_messages": "can_pin_messages",
    }
    PAYLOAD_ARGUMENT_NAME = "user_member"

    def __post_init__(self):
        self.required_permissions = {
            arg: True for arg in self.ARGUMENTS.values() if getattr(self, arg)
        }

    @classmethod
    def validate(cls, full_config):
        config = {}
        for alias, argument in cls.ARGUMENTS.items():
            if alias in full_config:
                config[argument] = full_config.pop(alias)
        return config

    async def check(self, message):
        # If pm skip checks
        if message.chat.type == 'private':
            return True

        user_id = await self.get_target_id(message)

        if not (p := await check_admin_rights(message.chat.id, user_id, self.required_permissions.keys())) is True:
            await self.no_rights_msg(message, p)

        return True

    async def get_target_id(self, message):
        return message.from_user.id

    async def no_rights_msg(self, message, required_permissions):
        strings = await get_strings(message.chat.id, 'global')
        await message.reply(strings['user_no_right:' + required_permissions])


class BotHasPermissions(UserRestricting):
    ARGUMENTS = {
        "bot_admin": "admin",
        "bot_can_post_messages": "can_post_messages",
        "bot_can_edit_messages": "can_edit_messages",
        "bot_can_delete_messages": "can_delete_messages",
        "bot_can_restrict_members": "can_restrict_members",
        "bot_can_promote_members": "can_promote_members",
        "bot_can_change_info": "can_change_info",
        "bot_can_invite_users": "can_invite_users",
        "bot_can_pin_messages": "can_pin_messages",
    }
    PAYLOAD_ARGUMENT_NAME = "bot_member"

    async def get_target_id(self, message):
        return BOT_ID

    async def no_rights_msg(self, message, required_permissions):
        strings = await get_strings(message.chat.id, 'global')
        await message.reply(strings['bot_no_right:' + required_permissions])


dp.filters_factory.bind(UserRestricting)
dp.filters_factory.bind(BotHasPermissions)
