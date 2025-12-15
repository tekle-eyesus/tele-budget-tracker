import pandas as pd
import io
from aiogram import Router, types, F, Bot
from data.database import AsyncSessionLocal, Expense

router = Router()

@router.message(F.document)
async def handle_csv_upload(message: types.Message, bot: Bot):
    document = message.document

    # 1. Validation: Is it a CSV?
    if not document.file_name.endswith('.csv'):
        # Ignore non-CSV files (or warn user)
        return 

    await message.reply("⏳ Processing CSV file...")

    try:
        # 2. Download file to Memory (RAM)
        file_obj = io.BytesIO()
        file = await bot.get_file(document.file_id)
        await bot.download_file(file.file_path, file_obj)
        file_obj.seek(0)

        # 3. Read with Pandas
        # Expected columns: "amount", "category", "description" (optional)
        df = pd.read_csv(file_obj)

        # Normalize column names to lowercase
        df.columns = [c.lower() for c in df.columns]

        required_cols = {'amount', 'category'}
        if not required_cols.issubset(df.columns):
            await message.reply("❌ Error: CSV must have columns: `amount`, `category`")
            return

        # 4. Prepare Data for DB
        expenses_to_add = []
        count = 0
        
        for _, row in df.iterrows():
            # Basic validation
            try:
                amt = float(row['amount'])
                cat = str(row['category']).title()
                desc = str(row['description']) if 'description' in row else None
                
                # Create Object
                exp = Expense(
                    user_id=message.from_user.id,
                    amount=amt,
                    category=cat,
                    description=desc
                )
                expenses_to_add.append(exp)
                count += 1
            except ValueError:
                continue # Skip bad rows

        # 5. Bulk Insert
        if expenses_to_add:
            async with AsyncSessionLocal() as session:
                session.add_all(expenses_to_add)
                await session.commit()
            
            await message.reply(f"✅ Success! Imported <b>{count}</b> expenses.", parse_mode="HTML")
        else:
            await message.reply("⚠️ No valid data found in CSV.")

    except Exception as e:
        await message.reply(f"❌ Import Failed: {str(e)}")