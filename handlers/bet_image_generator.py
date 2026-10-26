# handlers/bet_image_generator.py
from PIL import Image, ImageDraw, ImageFont

def generate_bet_image(match_name, bet_type, odds):
    # Создаем темный фон 800x400 пикселей для карточки прогноза
    img = Image.new('RGB', (800, 400), color='#141419')
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("arial.ttf", 36)
        font_teams = ImageFont.truetype("arial.ttf", 46)
        font_bet = ImageFont.truetype("arial.ttf", 32)
        font_odds = ImageFont.truetype("arial.ttf", 70)
    except IOError:
        font_title = font_teams = font_bet = font_odds = ImageFont.load_default()

    # Рисуем плашку "ПРОГНОЗ НА МАТЧ"
    draw.rounded_rectangle([50, 30, 400, 90], radius=10, fill='#27272a')
    draw.text((60, 38), "ПРОГНОЗ НА МАТЧ", fill='#38bdf8', font=font_title)

    # Название матча (Команды) - делаем крупно по центру
    draw.text((50, 120), str(match_name), fill='#ffffff', font=font_teams)

    # Разделительная линия
    draw.line((50, 200, 750, 200), fill='#27272a', width=3)

    # Блок со ставкой (Слева внизу)
    draw.text((50, 240), "ВЫБОР КАППЕРА:", fill='#71717a', font=font_bet)
    draw.text((50, 290), str(bet_type), fill='#ffffff', font=font_teams)

    # Блок с коэффициентом (Справа внизу в рамке)
    draw.rounded_rectangle([520, 230, 750, 360], radius=15, fill='#1e293b', outline='#38bdf8', width=2)
    draw.text((540, 240), "КФ.", fill='#38bdf8', font=font_bet)
    draw.text((600, 255), f"{odds:.2f}", fill='#38bdf8', font=font_odds)

    # Сохраняем готовую карточку прогноза
    img.save("bet_card.png")
