from aiogram import Router, F
from aiogram.filters import state
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, \
    BufferedInputFile
from aiogram.fsm.context import FSMContext
import aiohttp


from sozlamalar import API_URL
from states import RegistrationState,AddExpense, XarajatStates

router = Router()


def get_main_keyboard(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💵 Balance", callback_data="balance")],
        [InlineKeyboardButton(text="📝 Bugungi xarajatlar", callback_data="view_today")],
        [InlineKeyboardButton(text="💸 Bugungi qarzlar", callback_data="view_debts")],
        [
            InlineKeyboardButton(
                text="Saytni ochish",
            web_app=WebAppInfo(url=f"https://doston2006.pythonanywhere.com/api/statistika/{user_id}/")
            )
        ],
        [InlineKeyboardButton(text="📄 Hisobot" , callback_data="hisobot")],
        [InlineKeyboardButton(text="🤖 Bot haqida" , callback_data="haqida")],
    ])
@router.message(F.text == "/start")
async def start_cmd(msg: Message, state: FSMContext):
    telegram_id = msg.from_user.id

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}check_user/{telegram_id}/") as resp:
            if resp.status == 200:
                data = await resp.json()
                if data.get("exists"):
                    await msg.answer("👋 Salom, qaytganingizdan xursandmiz!")
                    keyboard = get_main_keyboard(telegram_id)
                    await msg.answer("Assalomu alaykum xush kelibsiz\n Qandey amal bajarmoqchisiz?", reply_markup=keyboard)
                    return

    await msg.answer("Salom! Ismingizni kiriting:")
    await state.set_state(RegistrationState.first_name)


@router.message(RegistrationState.first_name)
async def get_first_name(msg: Message, state: FSMContext):
    await state.update_data(first_name=msg.text)
    await msg.answer("Familiyangizni kiriting:")
    await state.set_state(RegistrationState.last_name)



@router.message(RegistrationState.last_name)
async def get_last_name(msg: Message, state: FSMContext):
    await state.update_data(last_name=msg.text)
    data = await state.get_data()

    payload = {
        "telegram_id": msg.from_user.id,
        "first_name": data.get("first_name"),
        "last_name": data.get("last_name"),
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(API_URL + "register_user/", json=payload) as resp:
                if resp.status in [200, 201]:
                    await msg.answer("✅ Ma'lumotlaringiz saqlandi.")
                else:
                    await msg.answer(f"❌ Serverda xatolik: {resp.status}")
        except Exception as e:
            await msg.answer(f"❌ Xatolik: {str(e)[:100]}")  # uzun bo‘lsa kesiladi



    keyboard = get_main_keyboard(msg.from_user.id)
    await msg.answer("\t\t🏠 Bosh sahifa", reply_markup=keyboard)

@router.callback_query(F.data == "balance")
async def balance_start(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer("💰 Kiritmoqchi bo'lgan balansingizni qiymatini kiriting (faqat son):")
    await state.set_state(AddExpense.waiting_for_balance)


@router.message(AddExpense.waiting_for_balance)
async def process_balance(message: Message, state: FSMContext):
    try:
        amount = int(message.text)
    except ValueError:
        return await message.answer("❌ Iltimos, faqat raqam kiriting!")

    telegram_id = message.from_user.id

    async with aiohttp.ClientSession() as session:
        resp = await session.get(API_URL + f"get_balance/{telegram_id}/")
        result = await resp.json()

    old_balance = result.get("balance", 0)
    new_balance = old_balance + amount

    data = {
        "telegram_id": telegram_id,
        "text": str(amount),
        "amount": amount,
        "category": "Balance"
    }

    async with aiohttp.ClientSession() as session:
        await session.post(API_URL + "add_expense/", json=data)

    await message.answer(f"✅ Balansingiz yangilandi: {new_balance} so'm")
    await state.clear()
    keyboard = get_main_keyboard(message.from_user.id)
    await message.answer("\t\t🏠 Bosh sahifa", reply_markup=keyboard)

@router.callback_query(F.data == "haqida")
async def haqida_start(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.edit_text(
        "Bu bot orqali o'z daramotlarizni , Xarajatlaringizni , Qarzlaringizni hisoblab borishingiz mumkin \n "
        "Balance bo'limida o'z balansingizni kiritib borasiz va umumiy balance hisoblanib boriladi \n"
        "Bu sizni shu vaqtgacha qancha pul topganizni ko'rsatadi.\n"
        "Botni ishlatishda namunalarga qarab qiymat kiriting.",
        reply_markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="orqaga")]
        ])

    )

@router.callback_query(F.data == "orqaga")
async def orqaga_start(call: CallbackQuery, state: FSMContext):
    await call.answer()
    keyboard = get_main_keyboard(call.message.from_user.id)
    await call.message.answer("\t\t🏠 Bosh sahifa", reply_markup=keyboard)


def make_qarz_buttons(qarzlar: list):
    buttons = []
    for item in qarzlar:
        btn = InlineKeyboardButton(
            text=f"{item['person_name']} - {item['amount']} so'm",
            callback_data=f"delete_qarz:{item['id']}"
        )
        buttons.append([btn])
    back_button = InlineKeyboardButton(text="🔙 Orqaga", callback_data="qarz_ro'yxati")
    buttons.append([back_button])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.callback_query(F.data == "view_debts")
async def view_debts_handler(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer(
        f"Siz bugun qarz berdingizmi yoki oldizmi?",
       reply_markup= InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Qarz berdim", callback_data="qarz_berdim")],
            [InlineKeyboardButton(text="➖ Qarz oldim ", callback_data="qarz_oldim")],
           [InlineKeyboardButton(text="📋 Qarzlar ro'yxati" , callback_data="qarz_ro'yxati")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_update")],
        ])
    )



@router.callback_query(F.data == "qarz_ro'yxati")
async def qarz_royxati(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[

            [InlineKeyboardButton(text="Qarz berganlarim", callback_data="qarzlar:berdim")],
            [InlineKeyboardButton(text="Qarz olganlarim", callback_data="qarzlar:oldim")],
            [InlineKeyboardButton(text="Orqaga", callback_data="back_qarz")],

    ])
    await callback.message.edit_text("Qarzlar bo'limi:", reply_markup=keyboard)

@router.callback_query(F.data == "back_qarz")
async def back_qarz(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.edit_text(
        f"Siz bugun qarz berdingizmi yoki oldizmi?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Qarz berdim", callback_data="qarz_berdim")],
            [InlineKeyboardButton(text="➖ Qarz oldim ", callback_data="qarz_oldim")],
            [InlineKeyboardButton(text="📋 Qarzlar ro'yxati", callback_data="qarz_ro'yxati")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_update")],
        ])
    )

@router.callback_query(F.data.startswith("qarzlar:"))
async def show_qarzlar(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    tur = callback.data.split(":")[1]

    data = await state.get_data()
    deleted_ids = data.get("deleted_qarz_ids", [])

    async with aiohttp.ClientSession() as session:
        url = f"{API_URL}qarzlar_list/{user_id}/{tur}/"
        async with session.get(url) as resp:
            if resp.status != 200:
                await callback.message.answer("Qarzlar ro'yxatini olishda xatolik yuz berdi.")
                return
            qarzlar = await resp.json()

    filtered = [q for q in qarzlar if q["id"] not in deleted_ids]

    if not filtered:
        await callback.message.answer("Sizda bu turdagi qarz yozuvlari mavjud emas.")
    else:
        await callback.message.edit_text(f"Qarzlar ro'yxati \n{'Kimning qarzini ochirmoqchisiz' if tur == 'berdim' else 'Kimga qarzingizni berdingiz' }:", reply_markup=make_qarz_buttons(filtered))


@router.callback_query(F.data.startswith("delete_qarz:"))
async def delete_qarz_html_only(callback: CallbackQuery, state: FSMContext):
    qarz_id = int(callback.data.split(":")[1])
    await callback.answer("Jadvaldan o'chirildi.", show_alert=True)
    await callback.message.edit_reply_markup()

    await callback.message.delete()

    await callback.message.answer(
        "Asosiy menyu:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Qarz berdim", callback_data="qarz_berdim")],
            [InlineKeyboardButton(text="➖ Qarz oldim", callback_data="qarz_oldim")],
            [InlineKeyboardButton(text="📋 Qarzlar ro'yxati", callback_data="qarz_ro'yxati")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_update")],
        ])
    )

    async with aiohttp.ClientSession() as session:
        await session.post(f"{API_URL}delete_qarz/{qarz_id}/")




@router.callback_query(F.data == "qarz_berdim")
async def show_qarz_names(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(category="berdim")

    buttons = []

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{API_URL}qarz_names/{call.from_user.id}/") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    names = data.get("names", [])
                    for name in names:
                        buttons.append([InlineKeyboardButton(text=name, callback_data=f"select_name:{name}")])
        except:
            names = []

    buttons.append([InlineKeyboardButton(text="➕ Yangi ism", callback_data="add_new_name")])
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_update")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await call.message.answer(
        "Qarz bergan odamni tanlang yoki yangi ism qo‘shing:",
        reply_markup=keyboard
    )



@router.callback_query(F.data == "add_new_name")
async def handle_add_new_name(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.edit_text("Yangi ismni kiriting:")
    await state.set_state(AddExpense.waiting_for_name)


@router.callback_query(F.data.startswith("select_name:"))
async def handle_select_name(call: CallbackQuery, state: FSMContext):
    await call.answer()
    name = call.data.split("select_name:")[1]
    await state.update_data(borrower_name=name)
    await call.message.edit_text(f"{name} uchun qancha qarz berdingiz?")
    await state.set_state(AddExpense.waiting_for_amount)



@router.callback_query(F.data == "qarz_oldim")
async def show_qarz_olganlar(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(category="oldim")
    buttons = []
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}qarz_olganlar/{call.from_user.id}/") as resp:
            if resp.status == 200:
                data = await resp.json()
                names = data.get("names", [])
                for name in names:
                    buttons.append([InlineKeyboardButton(text=name, callback_data=f"select_olgan:{name}")])

    buttons.append([InlineKeyboardButton(text="➕ Yangi ism", callback_data="add_olgan_name")])
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_update")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await call.message.answer("Kimdan qarz oldingiz?", reply_markup=keyboard)


@router.callback_query(F.data.startswith("select_olgan:"))
async def handle_select_olgan(call: CallbackQuery, state: FSMContext):
    await call.answer()
    name = call.data.split("select_olgan:")[1]
    await state.update_data(borrower_name=name)
    await call.message.edit_text(f"{name} dan qancha qarz oldingiz?")
    await state.set_state(AddExpense.waiting_for_amount)


@router.callback_query(F.data == "add_olgan_name")
async def handle_add_olgan_name(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.edit_text("Yangi ismni kiriting (qarz olgan odamingiz):")
    await state.set_state(AddExpense.waiting_for_name)


@router.message(AddExpense.waiting_for_name)
async def get_new_name(msg: Message, state: FSMContext):
    await state.update_data(borrower_name=msg.text)
    await msg.answer("Qarz summasini kiriting:")
    await state.set_state(AddExpense.waiting_for_amount)


@router.message(AddExpense.waiting_for_amount)
async def get_amount(msg: Message, state: FSMContext):
    try:
        amount = int(msg.text.replace(" ", ""))
    except ValueError:
        return await msg.answer("❗ Iltimos, faqat raqam kiriting. Masalan: 120000")

    data = await state.get_data()
    category = data.get("category")
    if not category:
        return await msg.answer("Xatolik: Kategoriya aniqlanmadi. Iltimos, qayta urinib ko‘ring.")

    await state.update_data(amount=amount)

    await msg.answer(
        f"Muddatini yozing, nechanchi sanada {'olasiz' if category == 'berdim' else 'qaytarasiz'} "
        "(masalan: 27-iyul 2025 yoki 27 iyul 2025):"
    )
    await state.set_state(AddExpense.waiting_for_date)


@router.message(AddExpense.waiting_for_date)
async def get_date(msg: Message, state: FSMContext):
    date_text = msg.text.strip()
    data = await state.get_data()

    borrower_name = data.get("borrower_name")
    amount = data.get("amount")
    category = data.get("category")


    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_URL}add_qarz/", json={
            "telegram_id": msg.from_user.id,
            "person_name": borrower_name,
            "category": category,
            "amount": str(amount),
            "date_text": date_text
        }) as resp:
            if resp.status == 200:
                emoji = "➕" if category == "berdim" else "➖"
                await msg.answer(
                    f"✅ {emoji} {borrower_name} {'ga' if category == 'berdim' else 'dan'} {amount} so‘m qarz {'berdingiz' if category == 'berdim' else 'oldingiz'}!")
            else:
                await msg.answer("❌ Saqlashda xatolik yuz berdi.")
    keyboard = get_main_keyboard(msg.from_user.id)
    await msg.answer("Qanday amal bajaramiz?", reply_markup=keyboard)
    await state.clear()

@router.callback_query(F.data == "back_update")
async def confirm_update(call: CallbackQuery, state: FSMContext):
    await call.answer()
    keyboard = get_main_keyboard(call.message.from_user.id)
    await call.message.edit_text("Qanday amal bajaramiz?", reply_markup=keyboard)
@router.callback_query(F.data == "cancel_update")
async def cancel_update(call: CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    category = data.get("category")

    await state.update_data(update_mode=False)

    await call.message.answer(f"📥 Yangi {category.lower()} qiymatini kiriting:")
    await state.set_state(AddExpense.waiting_for_amount)

@router.callback_query(F.data == "view_today")
async def view_today_handler(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(category="Xarajat")  # Default qiymat
    await call.message.answer("📋 Qanday xarajat qildingiz? (masalan: Non, Kartoshka va h.k...)")
    await state.set_state(XarajatStates.waiting_for_text)

@router.message(XarajatStates.waiting_for_text)
async def get_expense_text(msg: Message, state: FSMContext):
    await state.update_data(text=msg.text.strip())
    await msg.answer("💰 Xarajat summasini kiriting (faqat raqam):")
    await state.set_state(XarajatStates.waiting_for_amounts)

@router.message(XarajatStates.waiting_for_amounts)
async def get_expense_amount(msg: Message, state: FSMContext):
    try:
        amount = int(msg.text.replace(" ", ""))
    except ValueError:
        return await msg.answer("❗ Iltimos, faqat raqam kiriting. Masalan: 120000")

    data = await state.get_data()
    category = data.get("category")
    text = data.get("text")

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_URL}add_xarajat/", json={
            "telegram_id": msg.from_user.id,
            "category": category,
            "text": text,
            "amount": str(amount)
        }) as resp:
            if resp.status == 200:
                await msg.answer(f"✅ {text} uchun {amount} so‘m xarajat saqlandi.")
            else:
                await msg.answer("❌ Saqlashda xatolik yuz berdi.")

    keyboard = get_main_keyboard(msg.from_user.id)
    await msg.answer("\t\t🏠 Bosh sahifa", reply_markup=keyboard)
    await state.clear()

@router.callback_query(F.data == "hisobot")
async def hisobot_handler(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.edit_text(
        f"📄 Haftalik va oylik hisobotni bilmoqchi bo'lsangiz tugmalardan birini tanlang",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🗓️ Kunlik", callback_data="daily")],
            [InlineKeyboardButton(text="🗓️ Haftalik", callback_data="confirm_hisobot")],
            [InlineKeyboardButton(text="🔙 Orqaga" , callback_data="back")],
        ])
    )

@router.callback_query(F.data == "confirm_hisobot")
async def send_weekly_report(call: CallbackQuery):
    await call.answer("📥 Hisobot tayyorlanmoqda...")
    telegram_id = call.from_user.id

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}weekly-pdf/{telegram_id}/") as resp:
            if resp.status == 200:
                pdf_bytes = await resp.read()
                await call.message.answer_document(
                    document=BufferedInputFile(pdf_bytes, filename="haftalik_hisobot.pdf"),
                    caption="✅ Bu haftalik hisobot."
                )
            else:
                await call.message.answer("❌ Hisobotni olishda xatolik yuz berdi.")

    keyboard = get_main_keyboard(call.message.from_user.id)
    await call.message.answer("\t\t🏠 Bosh sahifa", reply_markup=keyboard)


@router.callback_query(F.data == "daily")
async def send_daily_report(call: CallbackQuery):
    await call.answer()

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}daily_report/{call.from_user.id}/") as resp:
            if resp.status == 200:
                data = await resp.json()
                await call.message.edit_text(data["message"], parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_hisobot")],
                                          ])
                                          )
            else:
                await call.message.answer("🚫 Ma'lumotlarni olishda xatolik.")

@router.callback_query(F.data == "back_hisobot")
async def back_hisobot_handler(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer(
        f"📄 Haftalik va oylik hisobotni bilmoqchi bo'lsangiz tugmalardan birini tanlang",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🗓️ Kunlik", callback_data="daily")],
            [InlineKeyboardButton(text="🗓️ Haftalik", callback_data="confirm_hisobot")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back")],
        ])
    )



@router.callback_query(F.data == "back")
async def back_handler(call: CallbackQuery, state: FSMContext):
    await call.answer()
    keyboard = get_main_keyboard(call.message.from_user.id)
    await call.message.edit_text("\t\t🏠 Bosh sahifa", reply_markup=keyboard)




