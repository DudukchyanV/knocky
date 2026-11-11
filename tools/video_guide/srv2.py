import os,sys,json
os.environ["KNOCKY_DATA"]=sys.argv[1]
sys.path.insert(0,"server/app")
import main as m, uvicorn
m.init_db()
pl=json.load(open(sys.argv[2]))
d=m.clean_data(pl)
t=m.now()
with m.db() as c:
    c.execute("INSERT INTO users(email,created,consent_at) VALUES('maria@mail.ru',1,1)")
    tok=m.new_session(c,1)
    c.execute("INSERT INTO invitations(id,user_id,tpl,data,created,updated,slug) VALUES('inv1',1,?,?,?,?,'maria-denis')",(d["tpl"],json.dumps(d,ensure_ascii=False),t,t))
    m.publish_paid(c,"inv1","robokassa")
    rows=[("Ольга Смирнова",1,2,"Будем вдвоем с мужем"),("Алексей Петров",1,1,""),("Ирина и Сергей",1,2,"Без мяса, пожалуйста"),("Дмитрий Козлов",0,1,"К сожалению, буду в командировке"),("Анна Волкова",1,1,"Ура!"),("Екатерина",1,3,"С детьми")]
    for i,(n,a,pp,cm) in enumerate(rows):
        c.execute("INSERT INTO rsvp(inv_id,name,attend,people,comment,created,updated) VALUES('inv1',?,?,?,?,?,?)",(n,a,pp,cm,t-3600*(i+1),t-3600*(i+1)))
open(sys.argv[1]+"/tok","w").write(tok)
m.ORIGINS.add("http://127.0.0.1:8765")
uvicorn.run(m.app,host="127.0.0.1",port=8765,log_level="warning")
