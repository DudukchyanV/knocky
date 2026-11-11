Видео-гайд «Приглашение по ссылке за 6 шагов» (11.11.2026), 1080x1920, 30 с.
1. node film1.js <dir>/f1 - сайт (из репозитория, без сети): дизайн, цвета и блоки, данные, взгляд гостя; пишет payload.json.
2. python3 srv2.py <tmp> <dir>/f1/payload.json & ; node film2.js <tmp> <dir>/f2 - кабинет: ссылка и ответы (тестовые данные).
3. Скопировать рядом шрифты Unbounded-VF.ttf, Manrope-VF.ttf (из server/app/static/assets/f/*.woff через fontTools) и seal.png;
   python3 compose.py test (кадры для проверки) / full -> out/knocky_guide.mp4.
Готовое видео: Knocky Goods/Видео/knocky_guide.mp4 на компьютере владельца.
