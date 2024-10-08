#
# (c) 2024, Yegor Yakubovich, yegoryakubovich.com, personal@yegoryakybovich.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import db_session
from database.repositories.user import UserRepository
from keyboards import create_consultation_in_kb
from routers.main import go_main
from utils import texts
from utils.bot import bot


router = Router(name=__name__)


@router.callback_query(F.data == 'contacts')
@db_session
async def contacts(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    await callback_query.answer()
    tg_user_id = callback_query.from_user.id

    data = await state.get_data()
    for message_id in data['messages_to_delete']:
        await bot.delete_message(chat_id=tg_user_id, message_id=message_id)

    user_repo = UserRepository(session=session)
    user = await user_repo.get_by(obj_in={'tg_user_id': tg_user_id})

    message = await bot.send_photo(
        chat_id=tg_user_id,
        photo=FSInputFile(path=f'static/images/{user.language}/contacts.png'),
        caption=texts[user.language].contacts,
        reply_markup=create_consultation_in_kb(language=user.language),
    )
    data = {'messages_to_delete': [message.message_id]}
    await state.set_data(data=data)
    await state.set_data(data=data)


@router.callback_query(F.data == 'contacts_back')
@db_session
async def kb_back(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback_query.message.delete()

    user_repo = UserRepository(session=session)
    user = await user_repo.get_by(obj_in={'tg_user_id': callback_query.from_user.id})

    await go_main(user=user, state=state)
