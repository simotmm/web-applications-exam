import sqlite3
from datetime import datetime
path="db/podcast.db"
ADMIN=-2


#utenti: getters
def getUtenti():
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    query="SELECT * FROM utenti"
    cursor.execute(query)
    utenti=cursor.fetchall()
    cursor.close()
    conn.close()

    return utenti

def getUtenteByCod(codU):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    query="SELECT *\
           FROM utenti\
           WHERE utenti.codU=?"

    cursor.execute(query, (codU,))
    utente=cursor.fetchone()
    cursor.close()
    conn.close()

    return utente

def getUtenteByUsername(username):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    query="SELECT *\
           FROM utenti\
           WHERE utenti.username=?"

    cursor.execute(query, (username,))
    utente=cursor.fetchone()
    cursor.close()
    conn.close()

    return utente

def getUtentiByCategoria(categoria):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    utenti=2

    query="SELECT DISTINCT utenti.codU, utenti.username, utenti.nickname,\
                  utenti.propic, utenti.creatore\
           FROM utenti, serie\
           WHERE utenti.codU=serie.codU AND\
                 serie.categoria=?"

    cursor.execute(query, (categoria,))
    utenti=cursor.fetchall()
    cursor.close()
    conn.close()

    return utenti

def getFollowersPubbliciBySerie(codS):
    return getSeguaci(codS, 1)

def getFollowersPrivatiByserie(codS):
    return getSeguaci(codS, 0)

def getSeguitiBySerie(codS):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    query="SELECT * FROM seguiti WHERE codS=?"

    cursor.execute(query, (codS,))
    s=cursor.fetchall()
    cursor.close()
    conn.close()

    return s

def getSeguaci(codS, pubblico):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    query="SELECT DISTINCT utenti.nickname, utenti.codU, utenti.username, utenti.propic\
           FROM utenti, seguiti\
           WHERE utenti.codU=seguiti.codU AND seguiti.codS=?\
                 AND seguiti.pubblico=?"
          
    cursor.execute(query, (codS, pubblico))
    serie=cursor.fetchall()
    cursor.close()
    conn.close()

    return serie


#commenti: getters
def getCommenti():
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    query="SELECT commenti.testo, commenti.data,\
                  utenti.nickname, utenti.username, utenti.codU,\
                  episodi.titolo, episodi.codE, codC\
           FROM utenti, episodi, commenti\
           WHERE commenti.codU=utenti.codU AND episodi.codE=commenti.codE"
    cursor.execute(query)
    commenti=cursor.fetchall()
    cursor.close()
    conn.close()

    return commenti

def getCommentoByCod(codC):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    query="SELECT *\
           FROM commenti\
           WHERE commenti.codC=?"
          
    cursor.execute(query, (codC,))
    commento=cursor.fetchone()
    cursor.close()
    conn.close()

    return commento

def getCommentiByEpisodio(codE):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    query="SELECT commenti.codU, commenti.codC, commenti.codE,\
           commenti.testo, commenti.data, utenti.username, utenti.propic\
           FROM commenti, utenti, episodi\
           WHERE utenti.codU=commenti.codU AND\
                 episodi.codE=commenti.codE AND episodi.codE=?"
    cursor.execute(query, (codE,))
    commenti=cursor.fetchall()
    cursor.close()
    conn.close()

    return commenti


#seguiti: getters
def getSeguiti():
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    query="SELECT * FROM seguiti"
          
    cursor.execute(query)
    tabella=cursor.fetchall()
    cursor.close()
    conn.close()

    return tabella

#serie: getters
def getSerie():
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    query="SELECT DISTINCT serie.codS, serie.titolo, serie.descrizione, serie.categoria, serie.file,\
                  utenti.nickname, utenti.username, utenti.propic\
           FROM utenti, serie\
           WHERE utenti.codU=serie.codU"
    cursor.execute(query)
    serie=cursor.fetchall()
    cursor.close()
    conn.close()

    return serie

def getSerieByCod(codS):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    query="SELECT *\
           FROM serie\
           WHERE serie.codS=?"
          
    cursor.execute(query, (codS,))
    serie=cursor.fetchone()
    cursor.close()
    conn.close()

    return serie

def getSerieByUtente(codU):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    query="SELECT *\
           FROM serie\
           WHERE serie.codU= ? "
    cursor.execute(query, (codU,))
    serie=cursor.fetchall()
    cursor.close()
    conn.close()

    return serie


def getFollowersByUtente(codU):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    query="SELECT DISTINCT utenti.codU, utenti.username,\
                           utenti.nickname, utenti.propic,\
                           utenti.creatore\
            FROM utenti, seguiti, \
                 (SELECT DISTINCT * FROM serie WHERE codU=?) AS s\
            WHERE utenti.codU=seguiti.codU AND seguiti.codS=s.codS"

    cursor.execute(query, (codU,))
    followers=cursor.fetchall()
    cursor.close()
    conn.close()

    return followers

def getSerieByCategoria(categoria):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    query="SELECT serie.codS, serie.codU, serie.titolo,\
                  serie.descrizione, serie.categoria,\
                  utenti.username, serie.file\
           FROM serie, utenti\
           WHERE serie.codU=utenti.codU AND serie.categoria= ?"
    cursor.execute(query, (categoria,))
    serie=cursor.fetchall()
    cursor.close()
    conn.close()

    return serie

def getSerieSeguitePubblicamente(codU):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    
    query="SELECT serie.codS, serie.codU, serie.titolo,\
                  serie.descrizione, serie.categoria, serie.file,\
                  seguiti.pubblico, utenti.username\
           FROM serie, seguiti, utenti\
           WHERE serie.codS=seguiti.codS AND\
                 utenti.codU=serie.codU AND\
                 seguiti.pubblico=1 AND seguiti.codU=?"
          
    cursor.execute(query, (codU,))
    serie=cursor.fetchall()
    cursor.close()
    conn.close()

    #ritorna serie(codS, codU, titolo, descrizione, categoria,\
    #              file, pubblico, username)
    return serie

def getSerieSeguitePrivatamente(codU):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    
    query="SELECT serie.codS, serie.codU, serie.titolo,\
                  serie.descrizione, serie.categoria, serie.file,\
                  seguiti.pubblico, utenti.username\
           FROM serie, seguiti, utenti\
           WHERE serie.codS=seguiti.codS AND\
                 utenti.codU=serie.codU AND\
                 seguiti.pubblico=0 AND seguiti.codU=?"
          
    cursor.execute(query, (codU,))
    serie=cursor.fetchall()
    cursor.close()
    conn.close()

    return serie


def getSerieSeguite(codU):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    
    query="SELECT serie.codS, serie.codU, serie.titolo,\
                  serie.descrizione, serie.categoria, serie.file,\
                  seguiti.pubblico, utenti.username\
           FROM serie, seguiti, utenti\
           WHERE serie.codS=seguiti.codS AND\
                 utenti.codU=serie.codU AND\
                 seguiti.codU=?"
          
    cursor.execute(query, (codU,))
    serie=cursor.fetchall()
    cursor.close()
    conn.close()

    return serie

#episodi: getters
def getEpisodi():
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    query="SELECT * FROM episodi ORDER BY data ASC"
    cursor.execute(query)
    episodi=cursor.fetchall()
    cursor.close()
    conn.close()

    return episodi

def getEpisodiByUtente(codU):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    query="SELECT episodi.codE, episodi.codU, episodi.codS,\
                  episodi.titolo, episodi.descrizione,\
                  episodi.data, episodi.file\
           FROM episodi\
           WHERE episodi.codU=?\
           ORDER BY data ASC"

    cursor.execute(query, (codU,))
    episodi=cursor.fetchall()
    cursor.close()
    conn.close()

    return episodi

def getEpisodiSenzaSerieByUtente(codU):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    query="SELECT *\
           FROM episodi\
           WHERE episodi.codU=? AND episodi.codS is NULL\
           ORDER BY data ASC"

    cursor.execute(query, (codU,))
    episodi=cursor.fetchall()
    cursor.close()
    conn.close()

    return episodi

def getEpisodiBySerie(codS):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    query="SELECT * FROM episodi WHERE episodi.codS=? ORDER BY data ASC"

    cursor.execute(query, (codS,))
    episodi=cursor.fetchall()
    cursor.close()
    conn.close()

    return episodi

def getEpisodiPubbliciBySerie(codS, data):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    query="SELECT *\
           FROM episodi\
           WHERE episodi.codS=? AND episodi.data<=?"

    cursor.execute(query, (codS,data))
    episodi=cursor.fetchone()
    cursor.close()
    conn.close()

    return episodi

def getEpisodioByCod(codE):    
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    query="SELECT *\
           FROM episodi\
           WHERE episodi.codE=?"

    cursor.execute(query, (codE,))
    episodio=cursor.fetchone()
    cursor.close()
    conn.close()

    return episodio


#categorie: getters
def getCategorie():
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    query="SELECT * FROM categorie"
    cursor.execute(query)
    categorie=cursor.fetchall()
    cursor.close()
    conn.close()

    return categorie


#utenti: setters
def addUtente(username, password, nickname, propic, creatore):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    success=False
    query="INSERT INTO utenti(username, password, nickname, propic, creatore, privato)\
           VALUES(?,?,?,?,?,?)"

    try:
        cursor.execute(query, 
                      (username, password, nickname, propic, creatore, 0))
        conn.commit()
        success=True
    except Exception as e:
        print("errore", str(e))
        conn.rollback()

    cursor.close()
    conn.close()

    return success

def modificaUtente(codU, username, password, nickname, propic, creatore):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    query="UPDATE utenti\
           SET username=?, password=?, nickname=?,\
               propic=?, creatore=?\
           WHERE codU=?"

    success=False
    try:
        cursor.execute(query, (username, password, nickname, propic, creatore, codU))
        conn.commit()
        success=True
    except Exception as e:
        print("errore", str(e))
        conn.rollback()

    cursor.close()
    conn.close()

    return success

#episodi: setters
def addEpisodio(codU, codS, titolo, descrizione, data, file, serie):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    success=False
    if(serie):  #serie: valore booleano che indica se l'episodio da inserire appartiene a una serie
        query="INSERT INTO episodi(codU, codS, titolo, descrizione, data, file)\
               VALUES(?,?,?,?,?,?)"
    else:
        query="INSERT INTO episodi(codU, titolo, descrizione, data, file)\
               VALUES(?,?,?,?,?)"

    try:
        if(serie):
            cursor.execute(query, 
                          (codU, codS, titolo, descrizione, data, file))
        else:
            cursor.execute(query, 
                          (codU, titolo, descrizione, data, file))
        conn.commit()
        success=True
    except Exception as e:
        print("errore", str(e))
        conn.rollback()

    cursor.close()
    conn.close()

    return success

def modificaEpisodio(codE, codS, titolo, descrizione, data, file):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    if(codS=="NULL"):
        codS=None
    query="UPDATE episodi\
           SET codS=?, titolo=?,\
               descrizione=?, data=?,\
               file=?\
           WHERE codE=?"

    success=False
    try:
        cursor.execute(query, (codS, titolo, descrizione, data, file, codE))
        conn.commit()
        success=True
    except Exception as e:
        print("errore", str(e))
        conn.rollback()

    cursor.close()
    conn.close()

    return success

def eliminaEpisodio(codE):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    conn.execute("PRAGMA foreign_keys = 1")
    cursor=conn.cursor()

    query="DELETE FROM episodi WHERE episodi.codE=?"

    success=False
    try:
        cursor.execute(query, (codE,))
        conn.commit()
        success=True
    except Exception as e:
        print("errore", str(e))
        conn.rollback()

    cursor.close()
    conn.close()

    return success


#serie: setters
def addSerie(codU, titolo, descrizione, categoria, file):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    success=False
    query="INSERT INTO serie(codU, titolo, descrizione, categoria, file)\
           VALUES(?,?,?,?,?)"

    try:
        cursor.execute(query, 
                      (codU, titolo, descrizione, categoria, file))
        conn.commit()
        success=True
    except Exception as e:
        print("errore", str(e))
        conn.rollback()

    cursor.close()
    conn.close()

    return success

def modificaSerie(codS, titolo, descrizione, categoria, file):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    query="UPDATE serie\
           SET titolo=?, descrizione=?,\
               categoria=?, file=?\
           WHERE codS=?"

    success=False
    try:
        cursor.execute(query, (titolo, descrizione, categoria, file, codS))
        conn.commit()
        success=True
    except Exception as e:
        print("errore", str(e))
        conn.rollback()

    cursor.close()
    conn.close()

    return success

def eliminaSerie(codS):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    conn.execute("PRAGMA foreign_keys = 1")
    cursor=conn.cursor()

    newCodS=None
    query="UPDATE episodi\
           SET codS=?\
           WHERE codS=?"

    success1=False
    try:
        cursor.execute(query, (newCodS, codS))
        conn.commit()
        success1=True
    except Exception as e:
        print("errore", str(e))
        conn.rollback()

    cursor.close()
    conn.close()

    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    conn.execute("PRAGMA foreign_keys = 1")
    cursor=conn.cursor()

    query="DELETE FROM serie WHERE serie.codS=?"

    success2=False
    try:
        cursor.execute(query, (codS,))
        conn.commit()
        success2=True
    except Exception as e:
        print("errore", str(e))
        conn.rollback()

    cursor.close()
    conn.close()
    
    return success1 and success2

#seguiti: getters, setters
def getFollow(codU, codS):

    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    query="SELECT * FROM seguiti WHERE codU=? AND codS=?"
          
    cursor.execute(query, (codU, codS))
    follow=cursor.fetchone()

    return follow

def checkFollow(codU, codS):
    f=getFollow(codU, codS)
    if f is None:
        return False
    return len(getFollow(codU, codS))>0

def smettiDiSeguire(codU, codS):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    query="DELETE from seguiti WHERE codU=? AND codS=?"
    success=False

    try:
        cursor.execute(query, (codU, codS))
        conn.commit()
        success=True
    except Exception as e:
        print("errore", str(e))
        conn.rollback()

    cursor.close()
    conn.close()

    return success

def segui(codU, codS):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    
    query="INSERT INTO seguiti(codU, codS)\
           VALUES(?,?)"
    success=False
    try:
        cursor.execute(query, (codU, codS))
        conn.commit()
        success=True
    except Exception as e:
        print("errore", str(e))
        conn.rollback()

    cursor.close()
    conn.close()

    return success

def switchPubblicoFollow(codU, codS):
    follow=getFollow(codU, codS)
    if not follow:
        return False

    pubblico=follow["pubblico"]
    if(pubblico==1):
        pubblico=0
    else:
        pubblico=1

    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    query="UPDATE seguiti\
           SET pubblico=?\
           WHERE codU=? and codS=?"
    success=False

    try:
        cursor.execute(query, (pubblico, codU, codS))
        conn.commit()
        success=True
    except Exception as e:
        print("errore", str(e))
        conn.rollback()

    cursor.close()
    conn.close()

    return success

def getFollowersPubbliciByUtente(codU):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    query="SELECT DISTINCT utenti.codU, utenti.username,\
                           utenti.nickname, utenti.propic,\
                           utenti.creatore\
            FROM utenti, seguiti, \
                 (SELECT DISTINCT * FROM serie WHERE codU=?) AS s\
            WHERE utenti.codU=seguiti.codU AND\
                  seguiti.codS=s.codS AND seguiti.pubblico=1"

    cursor.execute(query, (codU,))
    followers=cursor.fetchall()
    cursor.close()
    conn.close()

    return followers



#categorie
def checkCategoria(nome):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    query="SELECT * FROM categorie WHERE nome=?"
    cursor.execute(query, (nome,))
    risultato=cursor.fetchall()
    cursor.close()
    conn.close()

    return len(risultato)>0


#commenti: setters
def addCommento(codU, codE, testo, data):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    success=False
    query="INSERT INTO commenti(codU, codE, testo, data)\
           VALUES(?,?,?,?)"

    try:
        cursor.execute(query, 
                      (codU, codE, testo, data))
        conn.commit()
        success=True
    except Exception as e:
        print("errore", str(e))
        conn.rollback()

    cursor.close()
    conn.close()

    return success

def modificaCommento(codC, testo, data):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    query="UPDATE commenti\
           SET testo=?, data=?\
           WHERE codC=?"
    success=False

    try:
        cursor.execute(query, (testo, data, codC))
        conn.commit()
        success=True
    except Exception as e:
        print("errore", str(e))
        conn.rollback()

    cursor.close()
    conn.close()

    return success

def eliminaCommento(codC):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    conn.execute("PRAGMA foreign_keys = 1")
    cursor=conn.cursor()

    query="DELETE FROM commenti WHERE commenti.codC=?"
    success=False

    try:
        cursor.execute(query, (codC,))
        conn.commit()
        success=True
    except Exception as e:
        print("errore", str(e))
        conn.rollback()

    cursor.close()
    conn.close()

    return success

def today():
    return ""+datetime.now().strftime("%Y-%m-%d")

def getDB(codU):

    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    
    queryUtenti="SELECT * FROM utenti"
    querySerie="SELECT * FROM serie"
    queryEpisodi="SELECT * FROM episodi WHERE data<=? OR codU=?"
    
    cursor.execute(queryUtenti)
    utenti=cursor.fetchall()

    cursor.execute(querySerie)
    serie=cursor.fetchall()

    if(codU==ADMIN): #codice admin, se voglio vedere l'intero db
        queryEpisodi="SELECT * FROM episodi"
        cursor.execute(queryEpisodi)
    else:
        cursor.execute(queryEpisodi, (today(), codU))

    episodi=cursor.fetchall()

    cursor.close()
    conn.close()

    categorie=getCategorie()
    commenti=getCommenti()

    db={ "episodi": episodi,
         "utenti": utenti,
         "serie": serie,
         "categorie": categorie, 
         "commenti": commenti}

    return db

def switchPrivacyAccount(username):
    privato=getUtenteByUsername(username)["privato"]
    
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    if privato==1:
        privato=0
    else:
        privato=1

    query1="UPDATE utenti\
           SET privato=?\
           WHERE username=?"

    success1=False
    try:
        cursor.execute(query1, (privato, username))
        conn.commit()
        success1=True
    except Exception as e:
        print("errore", str(e))
        conn.rollback()

    cursor.close()
    conn.close()

    if(privato==0):
        return success1

    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    #se il profilo diventa privato allora anche tutti i seguiti diventano privati
    query2="UPDATE seguiti\
            SET pubblico=?\
            WHERE codU=?"
    
    success2=False
    try:
        cursor.execute(query2, (0, getUtenteByUsername(username)["codU"]))
        conn.commit()
        success2=True
    except Exception as e:
        print("errore", str(e))
        conn.rollback()

    cursor.close()
    conn.close()

    return success1 and success2

def cambiaPsw(psw, username):
    conn=sqlite3.connect(path)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    query="UPDATE utenti\
           SET password=?\
           WHERE username=?"
    success=False

    try:
        cursor.execute(query, (psw, username))
        conn.commit()
        success=True
    except Exception as e:
        print("errore", str(e))
        conn.rollback()

    cursor.close()
    conn.close()

    return success
