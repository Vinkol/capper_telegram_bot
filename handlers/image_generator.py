# handlers/image_generator.py
import sqlite3
from PIL import Image, ImageDraw, ImageFont

def generate_stats_image():
    # 1. Извлекаем данные из базы
    conn = sqlite3.connect("bets.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT result, odds FROM bets WHERE result != 'pending'")
    closed_bets = cursor.fetchall()
    conn.close()

    total_bets = len(closed_bets)
    
    # Если ставок еще нет, создаем заглушку
    if total_bets == 0:
        wins, loses, returns = 0, 0, 0
        profit = 0.0
        roi = 0.0
        winrate = 0.0
    else:
        wins = sum(1 for b in closed_bets if b[0] == 'win')
        loses = sum(1 for b in closed_bets if b[0] == 'lose')
        returns = sum(1 for b in closed_bets if b[0] == 'return')
        
        # Считаем прибыль во флэтах (выигрыш: кф - 1, проигрыш: -1)
        profit = 0.0
        for result, odds in closed_bets:
            if result == 'win':
                profit += (odds - 1.0)
            elif result == 'lose':
                profit -= 1.0
                
        # Считаем ROI (чистая прибыль / количество ставок * 100%)
        # Ставки с возвратом тоже учитываются как оборот (1 флэт)
        roi = (profit / total_bets) * 100 if total_bets > 0 else 0.0
        
        # Винрейт считаем от ставок с исходом (без учета возвратов)
        decided_bets = wins + loses
        winrate = (wins / decided_bets) * 100 if decided_bets > 0 else 0.0

    # 2. Рисуем картинку
    # Создаем темный фон 800x500 пикселей
    img = Image.new('RGB', (800, 500), color='#1e1e24')
    draw = ImageDraw.Draw(img)

    # Используем стандартный шрифт Windows Arial (если его нет, Pillow подставит дефолтный)
    try:
        font_title = ImageFont.truetype("arial.ttf", 40)
        font_big = ImageFont.truetype("arial.ttf", 60)
        font_main = ImageFont.truetype("arial.ttf", 28)
    except IOError:
        font_title = font_big = font_main = ImageFont.load_default()

    # Рисуем шапку
    draw.text((50, 40), "СТАТИСТИКА ПРОГНОЗОВ", fill='#ffffff', font=font_title)
    draw.line((50, 100, 750, 100), fill='#3f3f46', width=2)

    # Левая колонка: Числа
    draw.text((50, 140), f"Всего ставок: {total_bets}", fill='#a1a1aa', font=font_main)
    draw.text((50, 200), f"✅ Выигрыши: {wins}", fill='#4ade80', font=font_main)
    draw.text((50, 260), f"❌ Проигрыши: {loses}", fill='#f87171', font=font_main)
    draw.text((50, 320), f"🔄 Возвраты: {returns}", fill='#fbbf24', font=font_main)

    # Правая колонка: Итоговые показатели
    # Блок прибыли
    draw.text((450, 140), "ОБЩАЯ ПРИБЫЛЬ:", fill='#a1a1aa', font=font_main)
    profit_color = '#4ade80' if profit >= 0 else '#f87171'
    profit_sign = '+' if profit > 0 else ''
    draw.text((450, 180), f"{profit_sign}{profit:.2f} фл.", fill=profit_color, font=font_big)

    # Блок ROI
    draw.text((450, 280), "ROI:", fill='#a1a1aa', font=font_main)
    draw.text((450, 320), f"{profit_sign}{roi:.1f}%", fill=profit_color, font=font_big)

    # Блок Винрейта внизу
    draw.line((50, 400, 750, 400), fill='#3f3f46', width=2)
    draw.text((50, 430), f"Процент побед (Winrate): {winrate:.1f}%", fill='#ffffff', font=font_main)

    # Сохраняем готовую картинку в корень проекта
    img.save("stats_report.png")
