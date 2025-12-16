from aiogram import Router, types, F
from sqlalchemy import select, delete
from data.database import AsyncSessionLocal, Subscription
from aiogram.filters import Command

router = Router()

@router.message(Command("addsub"))
async def add_subscription(message: types.Message):
    """
    Usage: /addsub Netflix 15
    """
    args = message.text.split(maxsplit=2)
    if len(args) != 3:
        await message.answer("⚠️ Usage: `/addsub Name Amount`\nExample: `/addsub Netflix 15.99`")
        return

    name = args[1]
    try:
        amount = float(args[2])
    except ValueError:
        await message.answer("❌ Amount must be a number.")
        return

    async with AsyncSessionLocal() as session:
        sub = Subscription(user_id=message.from_user.id, name=name, amount=amount)
        session.add(sub)
        await session.commit()

    await message.answer(f"✅ Added subscription: <b>{name}</b> (${amount:.2f}/mo)", parse_mode="HTML")

@router.message(F.text == "🔄 Subscriptions")
async def list_subscriptions(message: types.Message):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Subscription).where(Subscription.user_id == message.from_user.id))
        subs = result.scalars().all()

    if not subs:
        await message.answer("You have no subscriptions yet.\nAdd one using: `/addsub Name Amount`")
        return

    total = sum(s.amount for s in subs)
    text = "🔄 <b>Monthly Subscriptions</b>\n──────────────────\n"
    
    for s in subs:
        text += f"• {s.name}: <code>${s.amount:.2f}</code> /delete_sub_{s.id}\n"
    
    text += f"──────────────────\n<b>Total Fixed Cost:</b> <code>${total:.2f}</code>"
    
    await message.answer(text, parse_mode="HTML")

@router.message(F.text.startswith("/delete_sub_"))
async def delete_subscription(message: types.Message):
    sub_id = int(message.text.split("_")[2])
    
    async with AsyncSessionLocal() as session:
        await session.execute(delete(Subscription).where(Subscription.id == sub_id))
        await session.commit()
    
    await message.answer("✅ Subscription removed.")