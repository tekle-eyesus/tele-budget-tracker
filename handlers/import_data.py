import pandas as pd
import io
from aiogram import Router, types, F, Bot
from data.database import AsyncSessionLocal, Expense

router = Router()

@router.message(F.document)
async def handle_document_upload(message: types.Message, bot: Bot):
    document = message.document
    file_name = document.file_name.lower() if document.file_name else ""

    if not file_name.endswith('.csv'):
        await message.reply(
            "❌ <b>Unsupported File Type</b>\n\n"
            "I can only import data from <b>.csv</b> files.\n"
            "Please upload a CSV file or use /template to see the format.",
            parse_mode="HTML"
        )
        return 

    await message.reply("⏳ Processing CSV file...")

    try:
        file_obj = io.BytesIO()
        file = await bot.get_file(document.file_id)
        await bot.download_file(file.file_path, file_obj)
        file_obj.seek(0)

        df = pd.read_csv(file_obj)

        df.columns = [c.lower() for c in df.columns]

        required_cols = {'amount', 'category'}
        if not required_cols.issubset(df.columns):
            await message.reply("❌ <b>Format Error:</b> CSV must have columns: <code>amount</code>, <code>category</code>", parse_mode="HTML")
            return

        expenses_to_add = []
        count = 0
        
        for _, row in df.iterrows():
            try:
                amt = float(row['amount'])
                cat = str(row['category']).title()
                desc = str(row['description']) if 'description' in row else None
                
                exp = Expense(
                    user_id=message.from_user.id,
                    amount=amt,
                    category=cat,
                    description=desc
                )
                expenses_to_add.append(exp)
                count += 1
            except (ValueError, TypeError):
                continue # Skip bad rows

        if expenses_to_add:
            async with AsyncSessionLocal() as session:
                session.add_all(expenses_to_add)
                await session.commit()
            
            await message.reply(f"✅ Success! Imported <b>{count}</b> expenses.", parse_mode="HTML")
        else:
            await message.reply("⚠️ No valid data found in CSV.")

    except Exception as e:
        await message.reply(f"❌ Import Failed: {str(e)}")