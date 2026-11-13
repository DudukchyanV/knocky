"""Pages for search queries: knocky.ru/priglashenie/<slug>/ (SEO plan 8.4).
Uses the same template as the design pages (tools/build_design_pages.py).
Usage: python3 tools/build_landing_pages.py"""
import sys, pathlib, html
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_design_pages as B

R, e = B.R, html.escape
B.CSS += """
.lp-hero{padding:18px 0 48px;max-width:760px}
.lp-hero h1{font-size:clamp(30px,4.4vw,52px);line-height:1.08;margin:10px 0 16px}
.lp-hero p{font-size:18px;color:var(--muted);margin:0 0 26px}
.lp-sec{padding:0 0 56px}.lp-sec h2{font-size:clamp(22px,2.6vw,32px);line-height:1.15;margin:0 0 22px}
.lp-sec>p{max-width:720px;font-size:17px;margin:0 0 14px}
.steps{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px;counter-reset:s;margin:0;padding:0;list-style:none}
.steps li{background:var(--surface);border-radius:18px;padding:22px 20px;counter-increment:s}
.steps li:before{content:counter(s);display:grid;place-items:center;width:34px;height:34px;border-radius:50%;background:var(--seal);color:#fff;font:600 15px/1 var(--f-disp);margin:0 0 14px}
.steps b,.feats b{display:block;font-size:17px;margin:0 0 6px}.steps span,.feats span{font-size:15px;color:var(--muted)}
.feats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin:0;padding:0;list-style:none}
.feats li{background:var(--soft);border-radius:18px;padding:22px 20px}
.faq{max-width:760px}.faq details{background:var(--surface);border-radius:16px;margin:0 0 10px;padding:0 20px}
.faq summary{cursor:pointer;list-style:none;padding:18px 0;font-weight:700;font-size:16px}.faq summary::-webkit-details-marker{display:none}
.faq summary:after{content:"+";float:right;color:var(--seal);font-size:20px;line-height:1}.faq details[open] summary:after{content:"-"}
.faq details p{margin:0 0 18px;color:var(--muted)}
.lp-end{background:var(--ink);color:#fff;border-radius:24px;padding:40px 32px;margin:0 0 64px}
.lp-end h2{font-size:clamp(22px,2.6vw,32px);margin:0 0 10px}.lp-end p{color:#D9CCCF;margin:0 0 22px;max-width:560px}
.lp-rel{display:flex;flex-wrap:wrap;gap:10px;margin:0;padding:0;list-style:none}
.lp-rel a{display:inline-block;padding:10px 16px;border-radius:999px;background:var(--surface);text-decoration:none;font-weight:700;font-size:15px}
.lp-rel a:hover{color:var(--seal)}
@media (max-width:860px){.steps{grid-template-columns:repeat(2,minmax(0,1fr))}.feats{grid-template-columns:1fr}}
@media (max-width:480px){.steps{grid-template-columns:1fr}.lp-end{padding:30px 20px}}
"""

PAGES = [
 dict(slug="elektronnoe-priglashenie", name="Электронное приглашение",
  title="Электронное приглашение на свадьбу - сделать онлайн | Knocky",
  desc="Электронное приглашение на свадьбу по ссылке: красивый дизайн, таймер, карта, программа и ответы гостей. Примерка бесплатно, от 640 ₽, оплата один раз.",
  h1="Электронное приглашение на свадьбу",
  lead="Красивая страница с вашими именами, датой и местом, которую гости открывают по ссылке. Отправить можно в любой мессенджер за минуту, без печати и курьеров.",
  sec1=("Как сделать электронное приглашение", [
   ("Выберите дизайн", "Классика, цветы, акварельные картины, минимализм. У каждого 3 палитры."),
   ("Впишите детали", "Имена, дату, время и адрес. Программу и дресс-код - по желанию."),
   ("Добавьте блоки", "Карта, анкета гостей, именные ссылки, рассадка, фото, вишлист."),
   ("Отправьте ссылку", "После оплаты вы получаете ссылку и отправляете ее гостям."),
  ]),
  sec2=("Чем удобнее бумажного", [
   ("Гости не потеряют", "Приглашение всегда в переписке, адрес и время под рукой в день свадьбы."),
   ("Можно поменять", "Сдвинулось время или площадка - правите в кабинете, ссылка остается той же."),
   ("Маршрут в один тап", "Точка на карте и кнопки Яндекс Карт и 2ГИС."),
   ("Ответы в одном месте", "Гости отмечают «приду / не смогу», вы видите список и скачиваете Excel."),
   ("Таймер до праздника", "Гости видят, сколько дней осталось до свадьбы."),
   ("Дешевле печати", "От 640 ₽ за все приглашение, а не за каждую открытку."),
  ]),
  text=["Электронное приглашение не заменяет теплое отношение к гостям - оно просто снимает рутину. Не нужно печатать открытки, развозить их и обзванивать всех, чтобы узнать, кто придет.",
        "Если хочется сохранить традицию, можно сделать и то, и другое: в Knocky есть печатная версия в PDF с QR-кодом, который ведет на полное приглашение."],
  faq=[
   ("Сколько стоит электронное приглашение на свадьбу?", "От 640 ₽ за базовый набор, все блоки сразу - 1 990 ₽. Оплата один раз, без подписки. Посмотреть дизайн со своими именами можно бесплатно."),
   ("Как гости откроют приглашение?", "Это обычная ссылка. Она открывается в любом браузере на телефоне и компьютере, приложение и регистрация гостям не нужны."),
   ("Можно ли изменить приглашение после отправки?", "Да. Вы правите текст в личном кабинете, а у гостей остается та же ссылка, рассылать заново не нужно."),
   ("Сколько работает ссылка?", "3 месяца с момента оплаты. Продлить до 12 месяцев можно блоком за 150 ₽, в тарифах «Оптимум» и «Все сразу» это уже входит."),
  ]),
 dict(slug="sajt-priglashenie", name="Сайт-приглашение",
  title="Сайт-приглашение на свадьбу - свадебный сайт без программиста | Knocky",
  desc="Сайт-приглашение на свадьбу за вечер: дизайн, программа дня, карта, дресс-код, анкета гостей и вишлист. Без программиста и подписки, от 640 ₽.",
  h1="Сайт-приглашение на свадьбу",
  lead="Свой свадебный сайт со всем, что нужно знать гостям: дата, место, программа, дресс-код и анкета. Собирается в конструкторе за вечер, без программиста.",
  sec1=("Что можно добавить на свадебный сайт", [
   ("Обложка и таймер", "Ваши имена, дата и обратный отсчет до праздника."),
   ("Место и программа", "Карта, маршрут, план дня: сбор гостей, церемония, банкет."),
   ("Дресс-код", "Палитра цветов, чтобы гости не гадали, что надеть."),
   ("Анкета и вишлист", "Ответы гостей и подарки, которые можно забронировать."),
  ]),
  sec2=("Почему сайт, а не просто сообщение", [
   ("Все в одном месте", "Не нужно пересылать адрес, время и пожелания отдельными сообщениями."),
   ("Несколько дней и мест", "Роспись и банкет в разные дни - отдельные вкладки со своим адресом."),
   ("Свой адрес", "Ссылка вида knocky.ru/anna-ilya - ее легко запомнить и продиктовать."),
   ("Именные ссылки", "Обращение к каждому гостю по имени и видно, кто открыл."),
   ("Рассадка", "Гость сразу видит номер своего стола."),
   ("Фото пары", "Ваши снимки прямо на сайте-приглашении."),
  ]),
  text=["Обычно свадебный сайт делают на конструкторах сайтов или заказывают у разработчика. Это долго и дорого: нужно разбираться в настройках, платить подписку и следить за версткой на телефоне.",
        "В Knocky все уже собрано под свадьбу: вы выбираете дизайн и включаете нужные блоки, а сайт сразу хорошо выглядит на любом телефоне."],
  faq=[
   ("Нужно ли что-то программировать?", "Нет. Вы выбираете дизайн, вписываете текст и включаете блоки галочками. Предпросмотр на телефоне видно сразу."),
   ("Сколько стоит сайт-приглашение?", "От 640 ₽, все блоки - 1 990 ₽. Оплата один раз, без ежемесячной подписки и хостинга."),
   ("Можно выбрать свой адрес сайта?", "Да. Адрес собирается из ваших имен, например knocky.ru/anna-ilya, или можно вписать свой, если он свободен."),
   ("Как долго сайт будет работать?", "3 месяца с момента оплаты, с продлением - 12 месяцев. Этого хватает и на подготовку, и на фото после свадьбы."),
  ]),
 dict(slug="otvety-gostej", name="Ответы гостей",
  title="Приглашение на свадьбу с ответом гостей - анкета и список в Excel | Knocky",
  desc="Онлайн-приглашение на свадьбу с анкетой: гости отвечают «приду / не смогу» и сколько их будет, а вы видите таблицу и скачиваете Excel. От 640 ₽.",
  h1="Приглашение на свадьбу с ответом гостей",
  lead="Гости подтверждают присутствие прямо в приглашении, а вы видите все ответы в одной таблице. Больше не нужно обзванивать каждого и вести список вручную.",
  sec1=("Как это работает", [
   ("Гость открывает ссылку", "Видит приглашение и анкету внизу страницы."),
   ("Отвечает за минуту", "Имя, «приду / не смогу», сколько человек, пожелания по меню."),
   ("Вы видите ответ", "В кабинете таблица ответов и счетчики: сколько придет."),
   ("Скачиваете Excel", "Готовый список для площадки и кейтеринга."),
  ]),
  sec2=("Что еще помогает собрать гостей", [
   ("Именные ссылки", "У каждого гостя своя ссылка, имя подставляется в анкету само."),
   ("Кто открыл", "Видно, кто уже посмотрел приглашение, а кто еще нет."),
   ("Ответ можно изменить", "Если планы у гостя поменялись, он просто ответит заново."),
   ("Несколько дней", "Гость отмечает, на какие дни придет, вы видите сводку по каждому."),
   ("Рассадка", "Распределите гостей по столам - каждый увидит свой."),
   ("Без регистрации", "Гостям не нужно ничего скачивать и заводить аккаунт."),
  ]),
  text=["Самая долгая часть подготовки - узнать, кто придет. С анкетой в приглашении ответы собираются сами, а вы в любой момент видите точное число гостей.",
        "Анкета входит в тарифы «Оптимум» и «Все сразу», ее можно добавить и отдельно в конструкторе."],
  faq=[
   ("Что гость указывает в анкете?", "Имя, придет или нет, сколько будет человек и комментарий, например пожелания по меню."),
   ("Где смотреть ответы?", "В личном кабинете: таблица ответов, счетчики и кнопка «Скачать Excel»."),
   ("Может ли гость изменить ответ?", "Да, он открывает ту же ссылку и отвечает заново, в таблице обновится."),
   ("Как узнать, кто еще не ответил?", "С именными ссылками видно каждого гостя: открыл ли он приглашение и что ответил."),
  ]),
]

PICK = ["envelope", "wpeony", "glass", "tuscany", "lace", "euca", "arch", "flourish"]

def build(p):
    url = f'/priglashenie/{p["slug"]}/'
    canon = "https://knocky.ru" + url
    cr, ld_cr = B.crumbs([("Главная", "/"), (p["name"], None)])
    st_title, steps = p["sec1"]; ft_title, feats = p["sec2"]
    cards = "".join(B.card(x) for x in [next(d for d in B.D if d["id"] == i) for i in PICK])
    others = [q for q in PAGES if q is not p]
    rel = "".join(f'<li><a href="/priglashenie/{q["slug"]}/">{e(q["h1"])}</a></li>' for q in others) + '<li><a href="/dizain/">Все дизайны</a></li>'
    faq = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in p["faq"])
    body = f"""<div class="wrap">{cr}
<section class="lp-hero"><h1>{e(p["h1"])}</h1><p>{e(p["lead"])}</p>
<div class="cta"><a class="btn btn-seal" href="/#templates">Выбрать дизайн</a><a class="btn btn-line" href="/dizain/">Все дизайны</a></div>
<p class="price">Примерка со своими именами бесплатно. От 640 ₽, оплата один раз.</p></section>
<section class="lp-sec"><h2>{e(st_title)}</h2><ol class="steps">{"".join(f"<li><b>{e(a)}</b><span>{e(b)}</span></li>" for a, b in steps)}</ol></section>
<section class="lp-sec"><h2>{e(ft_title)}</h2><ul class="feats">{"".join(f"<li><b>{e(a)}</b><span>{e(b)}</span></li>" for a, b in feats)}</ul></section>
<section class="lp-sec">{"".join(f"<p>{e(t)}</p>" for t in p["text"])}</section>
<section class="lp-sec more"><h2>Дизайны на любой вкус</h2><div class="cards">{cards}</div></section>
<section class="lp-sec faq"><h2>Вопросы</h2>{faq}</section>
<section class="lp-end"><h2>Примерьте приглашение со своими именами</h2><p>Выберите дизайн и посмотрите, как будет выглядеть ваше приглашение. Бесплатно и без регистрации.</p>
<a class="btn btn-seal" href="/#templates">Выбрать дизайн</a></section>
<section class="lp-sec"><h2>Еще по теме</h2><ul class="lp-rel">{rel}</ul></section>
</div>"""
    ld = [ld_cr, {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]}]
    out = R / "priglashenie" / p["slug"]; out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(B.page(p["title"], p["desc"], canon, body, ld, "/dizain/img/envelope.webp"))

for p in PAGES: build(p)
print("landing pages:", len(PAGES))
