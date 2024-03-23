from flask import Flask, render_template, request, redirect, flash, url_for
from datetime import date, time, datetime
from flask_session import Session
import dao, os
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from PIL import Image


DEFAULT_PROPIC="default.png"
DEFAULT_SERIE="defaultSerie.png"
IMAGE="img"
AUDIO="audio"
ADMIN=-2


app=Flask(__name__)
app.config["SECRET KEY"]="2dsaff2dsafdfa4fd3"
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
loginManager=LoginManager()
loginManager.login_view="login"
loginManager.init_app(app)
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"]=False
Session(app)


@loginManager.user_loader
def load_user(codU):
    utente=dao.getUtenteByCod(codU)

    if utente is not None:
        user=User(utente["codU"], utente["username"], utente["password"],
              utente["nickname"], utente["propic"], utente["creatore"], utente["privato"])
    else:
        user=None

    return user

@app.errorhandler(404)
def page_not_found(e):
    flash("Errore: pagina non trovata.", "danger")
    return render_template("404.html")

@app.errorhandler(500)
def internal_server_error(e):
    flash("Internal Server Error.", "danger")
    return render_template("404.html")


@app.route("/")
def home():

    serie=dao.getSerie()
    categorie=dao.getCategorie()
    return render_template("home.html", serie=serie, categorie=categorie, db=db())

@app.route("/carica")
@login_required
def carica():
    if(not current_user.is_authenticated):
        flash("Accesso alla pagin non autorizzato, per effettuare un caricamento effettuare il login.", "danger")
        return redirect(url_for("home"))

    if(current_user.creatore==0):
        flash("Accesso alla pagina non autorizzato, per effettuare un caricamento devi possedere un account di tipo 'Content Creator'.", "danger")
        return redirect(url_for("home"))

    serie=dao.getSerieByUtente(current_user.codU)

    return render_template("carica.html", serie=serie, db=db())

def db():
    if(current_user.is_authenticated):
        cod=current_user.codU
    else:
        cod=-1
    db=dao.getDB(cod)
    return db

@app.route("/carica", methods=["POST"])
def caricaPost():
    codU=current_user.codU
    titolo=request.form.get("titolo")
    descrizione=request.form.get("descrizione")
    data=request.form.get("data")
    codS=request.form.get("codS")
    file=request.files['file']
    serie=False
    if(codS!="-1"):
        serie=True
    if(data==""):
        data=datetime.now().strftime("%Y-%m-%d")

    nomeFile=salvaFile(file, titolo, AUDIO, 0, "carica", None, current_user.username)
    if nomeFile=="":
        return redirect(url_for("carica"))

    success=dao.addEpisodio(codU, codS, titolo, descrizione, data, nomeFile, serie)

    if success:
        flash("episodio '"+titolo+"' caricato correttamente.", "success")
        if(serie):
            return redirect(url_for("serie", codS=codS))
        return redirect(url_for("listaSeriePerAutore", username=current_user.username))
    else:
        flash("Errore nel caricamento dell'episodio, riprova.", "danger")

    return redirect(url_for("carica"))

@app.route("/episodi/<int:codE>")
def episodio(codE):
    episodio=dao.getEpisodioByCod(codE)
    if not episodio:
        flash("Errore: episodio inesistente.", "danger")
        return redirect(url_for("home"))

    autore=dao.getUtenteByCod(episodio["codU"])
    commenti=dao.getCommentiByEpisodio(codE)
    serie=dao.getSerieByCod(episodio["codS"])
    altreSerieDellAutore=dao.getSerieByUtente(autore["codU"])

    if(autore["privato"]==1 and (not current_user.is_authenticated or current_user.username!=autore["username"] )):
        flash("Profilo privato.", "primary")
        return render_template("profiloPrivato.html", utente=autore)

    if(serie):
        altreSerieDellaCategoria=dao.getSerieByCategoria(serie["categoria"])
    else:
        altreSerieDellaCategoria=None

    if(len(altreSerieDellAutore)<=1):
        altreSerieDellAutore=None
    if(altreSerieDellaCategoria):
        if(len(altreSerieDellaCategoria)<=1):
            altreSerieDellaCategoria=None

    episodiSerie=None
    if(serie):
        episodiSerie=dao.getEpisodiBySerie(serie["codS"])
        if(len(episodiSerie)<=1):
            episodiSerie=None

    if not(episodio or autore):
        flash("Errore: pagina non trovata.", "danger")
        redirect(url_for("home"))

    dataEpisodio=episodio["data"]
    dataCorrente=today()

    if(dataEpisodio>dataCorrente):
        if(current_user.is_authenticated and autore["codU"]==current_user.codU):
            flash("Visione pagina episodio in anteprima, l'episodio sarà pubblicato in data '"+dataEpisodio+"'.", "primary")
        else:
            flash("Accesso alla pagina non autorizzato.", "danger")
            return redirect(url_for("home"))

    return render_template('episodio.html', episodio=episodio, commenti=commenti,
                           autore=autore, serie=serie, episodiSerie=episodiSerie, db=db(),
                           altreSerieDellAutore=altreSerieDellAutore, dataCorrente=dataCorrente,
                           altreSerieDellaCategoria=altreSerieDellaCategoria, categorie=dao.getCategorie(),
                           )

@app.route("/serie/<int:codS>")
def serie(codS):
    serie=dao.getSerieByCod(codS)
    if not serie:
        flash("Errore: serie inesistente.", "danger")
        return redirect(url_for("home"))

    autore=dao.getUtenteByCod(serie["codU"])
    episodi=dao.getEpisodiBySerie(codS)
    episodiPubblici=dao.getEpisodiPubbliciBySerie(codS, today())
    altreSerieDellAutore=dao.getSerieByUtente(autore["codU"])
    altreSerieDellaCategoria=dao.getSerieByCategoria(serie["categoria"])
    followers=dao.getSeguitiBySerie(codS)
    categorie=dao.getCategorie()

    if(autore["privato"]==1 and (not current_user.is_authenticated or current_user.username!=autore["username"] )):
        flash("Profilo privato.", "primary")
        return render_template("profiloPrivato.html", utente=autore)

    if(len(altreSerieDellAutore)<=1):
        altreSerieDellAutore=None
    if(len(altreSerieDellaCategoria)<=1):
        altreSerieDellaCategoria=None

    if(current_user.is_authenticated):
        follow=dao.checkFollow(current_user.codU, codS)
    else:
        follow=False

    return render_template("serie.html", serie=serie, autore=autore, episodi=episodi,
                           altreSerieDellAutore=altreSerieDellAutore, follow=follow, db=db(),
                           altreSerieDellaCategoria=altreSerieDellaCategoria, dataCorrente=today(),
                           followers=followers, categorie=categorie, episodiPubblici=episodiPubblici)

@app.route("/serie/follow", methods=["POST"])
@login_required
def follow():
    codU=request.form.get("codU")
    codS=request.form.get("codS")
    utente=dao.getUtenteByCod(str(codU))
    serie=dao.getSerieByCod(str(codS))
    autore=dao.getUtenteByCod(serie["codU"])

    if((utente is None) or (serie is None)):
        flash("Errore: serie o utente inesistenti.", "danger")
        return redirect(url_for("home"))

    isFollowing=dao.checkFollow(codU, codS)

    if(autore["username"]==utente["username"] and not isFollowing):
        flash("Non puoi seguire la tua serie.", "primary")
        return redirect(url_for("serie", codS=codS))

    if(isFollowing):
        success=dao.smettiDiSeguire(codU, codS) #se l'utente segue la serie, smette di seguirla
        if(success):
            flash("Hai smesso di seguire la serie '"+serie["titolo"]+"' di @"+autore["username"]+".", "primary")
        else:
            flash("Errore: impossibile smettere di seguire la serie '"+serie["titolo"]+"'.", "danger")
    else:
        success=dao.segui(codU, codS)   #se invece non la segue comincia a seguirla
        if(success):
            flash("Serie '"+serie["titolo"]+"' di @"+autore["username"]+" seguita.", "success")
        else:
            flash("Errore: impossibile seguire la serie '"+serie["titolo"]+"'.", "danger")

    return redirect(url_for("serie", codS=codS))

@app.route("/episodi/nuovoCommento", methods=["POST"])
def nuovoCommento():
    codU=request.form.get("codU")
    codE=request.form.get("codE")
    testo=request.form.get("testo")
    data=datetime.now().strftime("%Y-%m-%d")

    if(len(testo)<1):
        flash("Impossibile pubblicare commento vuoto", "primary")
        return redirect(url_for("episodio", codE=codE))

    success=dao.addCommento(codU, codE, testo, data)
    if(success):
        flash("Commento pubblicato correttamente.", "success")
    else:
        flash("Errore: impossibile pubblicare il commento, riprova.", "danger")

    return redirect(url_for("episodio", codE=codE))

@app.route("/eliminaSerie", methods=["POST"])
@login_required
def eliminaSerie():
    codS=request.form.get("codS")
    serie=dao.getSerieByCod(codS)
    if(serie is None):
        flash("Errore: serie inesistente.", "danger")
        return redirect(url_for("home"))

    if(dao.eliminaSerie(codS)):
        flash("Serie '"+serie["titolo"]+"' eliminata correttamente.", "success")
    else:
        flash("Errore: impossibile eliminare la serie, riprova.", "danger")

    eliminaFile(serie["file"], IMAGE)

    return redirect(url_for("profilo", username=current_user.username))

@app.route("/eliminaCommento", methods=["POST"])
@login_required
def eliminaCommento():
    codC=request.form.get("codC")
    codE=request.form.get("codE")

    if(dao.eliminaCommento(codC)):
        flash("Commento eliminato correttamente.", "success")
    else:
        flash("Errore: impossibile eliminare il commento, riprova.", "danger")

    return redirect(url_for('episodio', codE=codE))

@app.route("/modificaCommento/<int:codC>")
@login_required
def modificaCommento(codC):
    commento=dao.getCommentoByCod(codC)
    if(commento is None):
        flash("Errore: commento inesistente.", "danger")
        return redirect(url_for("home"))
    if(commento["codU"]!=current_user.codU):
        flash("Accesso negato.", "danger")
        return redirect(url_for("home"))
    episodio=dao.getEpisodioByCod(commento["codE"])

    return render_template("modificaCommento.html", commento=commento, episodio=episodio, db=db())

@app.route("/modificaCommentoPost", methods=["POST"])
@login_required
def modificaCommentoPost():
    codC=request.form.get("codC")
    testo=request.form.get("testo")
    data=today()

    if(dao.modificaCommento(codC, testo, data)):
        flash("Commento modificato correttamente.", "success")
    else:
        flash("Errore: impossibile modificare il commento, riprova.", "danger")

    return redirect(url_for("episodio", codE=request.form.get("codE")))

@app.route("/episodi/modificaEpisodio/<int:codE>")
@login_required
def modificaEpisodio(codE):
    episodio=dao.getEpisodioByCod(codE)
    if(episodio is None):
        flash("Errore: episodio inesistente.", "danger")
        return redirect(url_for("home"))
    if(episodio["codU"]!=current_user.codU):
        flash("Accesso negato.", "danger")
        return redirect(url_for("home"))

    serie=dao.getSerieByUtente(episodio["codU"])
    if(episodio["codS"]!=-1):
        serieDiAppartenenza=dao.getSerieByCod(episodio["codS"])
    else:
        serieDiAppartenenza=None

    return render_template("modificaEpisodio.html", episodio=episodio, serie=serie,
    serieDiAppartenenza=serieDiAppartenenza, db=db())

@app.route("/modificaEpisodioPost", methods=["POST"])
@login_required
def modificaEpisodioPost():
    codE=request.form.get("codE")
    codE=str(codE)
    episodio=dao.getEpisodioByCod(codE)
    if episodio is None:
        flash("Errore: episodio inesistente.", "danger")
        return redirect(url_for("home"))


    codS=request.form.get("codS")
    titolo=request.form.get("titolo")
    descrizione=request.form.get("descrizione")
    data=request.form.get("data")
    file=request.files['file']
    nomeFile=file.name

    if(codS==""):
        codS=episodio["codS"]
    if(titolo==""):
        titolo=episodio["titolo"]
    if(descrizione==""):
        descrizione=episodio["descrizione"]
    if(data==""):
        data=episodio["data"]
    if not file:
        nomeFile=episodio["file"]
    else:
        nomeFile=salvaFile(file, titolo+" ", AUDIO, 0, "modificaEpisodio", codE, current_user.username)
        if nomeFile!="":
            eliminaFile(episodio["file"], AUDIO)
        else:
            return redirect(url_for("modificaEpisodio", codE=codE))

    success=dao.modificaEpisodio(codE, codS, titolo, descrizione, data, nomeFile)

    if(success):
        flash("Episodio '"+titolo+"' modificato correttamente.", "success")
        return redirect(url_for("episodio", codE=codE))
    else:
        flash("Errore: impossibile modificare l'episodio, riprova.", "danger")

    return redirect(url_for("modificaEpisodio", codE=codE))

def isString(a):
    b="a string"
    return isinstance(b, a)

@app.route("/eliminaEpisodio", methods=["POST"])
@login_required
def eliminaEpisodio():
    codE=request.form.get("codE")
    codE=str(codE)
    episodio=dao.getEpisodioByCod(codE)
    if episodio is None:
        flash("Episodio inesistente.", "danger")
        return redirect(url_for("home"))

    success=dao.eliminaEpisodio(codE)

    if(success):
        eliminaFile(episodio["file"], AUDIO)
        flash("Episodio eliminato correttamente.", "success")
    else:
        flash("Errore: impossibile eliminare l'episodio.", "danger")

    if(dao.getSerieByCod(episodio["codS"])):
        return redirect(url_for("serie", codS=episodio["codS"]))

    return redirect(url_for("profilo", username=current_user.username))

@app.route("/creaSerie")
@login_required
def creaSerie():
    if(not current_user.is_authenticated):
        flash("Accesso alla pagin non autorizzato, per effettuare un caricamento effettuare il login.", "danger")
        return redirect(url_for("home"))

    if(current_user.creatore==0):
        flash("Accesso alla pagina non autorizzato, per creare una serie devi possedere un account di tipo 'Content Creator'.", "danger")
        return redirect(url_for("home"))

    episodi=dao.getEpisodiByUtente(current_user.codU)
    categorie=dao.getCategorie()

    return render_template("creaSerie.html", episodi=episodi, categorie=categorie, db=db())

@app.route("/creaSerie", methods=["POST"])
def creaSeriePost():
    codU=current_user.codU
    titolo=request.form.get("titolo")
    descrizione=request.form.get("descrizione")
    categoria=request.form.get("categoria")
    file=request.files['file']
    nomeFile=salvaFile(file, titolo, IMAGE, 0, "creaSerie", None, current_user.username)
    if nomeFile=="":
        return redirect(url_for("creaSerie"))

    success=dao.addSerie(codU, titolo, descrizione, categoria, nomeFile)

    if success:
        flash("Serie '"+titolo+"' creata correttamente.", "success")
        return redirect(url_for("home"))
    else:
        flash("Errore nella creazione della serie, riprova.", "danger")

    return redirect(url_for("creaSerie"))

@app.route("/serie/modificaSerie/<int:codS>")
@login_required
def modificaSerie(codS):
    serie=dao.getSerieByCod(codS)
    if serie is None:
        flash("Errore: serie inesistente.", "danger")
        return redirect(url_for("home"))
    if(serie["codU"]!=current_user.codU):
        flash("Accesso negato.", "danger")
        return redirect(url_for("home"))

    episodi=dao.getEpisodiBySerie(codS)
    altriEpisodi=dao.getEpisodiSenzaSerieByUtente(str(serie["codU"]))
    categorie=dao.getCategorie()

    return render_template("modificaSerie.html", serie=serie, categorie=categorie,
                           episodi=episodi, altriEpisodi=altriEpisodi, db=db())

@app.route("/modificaSeriePost", methods=["POST"])
@login_required
def modificaSeriePost():
    codS=str(request.form.get("codS"))
    print(codS)
    serie=dao.getSerieByCod(codS)
    if serie is None:
        flash("Errore: serie inesistente.", "danger")
        return redirect(url_for("home"))

    codS=request.form.get("codS")
    titolo=request.form.get("titolo")
    descrizione=request.form.get("descrizione")
    categoria=request.form.get("categoria")
    file=request.files['file']
    nomeFile=file.name

    if(titolo==""):
        titolo=serie["titolo"]
    if(categoria==""):
        categoria=serie["categoria"]
    if(descrizione==""):
        descrizione=serie["descrizione"]
    if not file:
        nomeFile=serie["file"]
    else:
        nomeFile=salvaFile(file, titolo+" ", IMAGE, 0, "serie", codS, current_user.username)
        if nomeFile!="":
            eliminaFile(serie["file"], IMAGE)
        else:
            return redirect(url_for("modificaSerie", codS=codS))

    success=dao.modificaSerie(codS, titolo, descrizione, categoria, nomeFile)

    if(success):
        flash("Serie '"+titolo+"' modificata correttamente.", "success")
    else:
        flash("Errore: impossibile modificare la serie, riprova.", "danger")

    return redirect(url_for("serie", codS=codS))

@app.route("/addEpisodioASerie", methods=["POST"])
@login_required
def addEpisodioASerie():
    codE=request.form.get("codE")
    codS=request.form.get("codS")
    episodio=dao.getEpisodioByCod(codE)
    serie=dao.getSerieByCod(codS)

    if(serie is None or episodio is None):
        flash("Errore: serie o episodio inesistenti.", "danger")
        return redirect(url_for("home"))
    if(episodio["codS"]==codS):
        flash("L'episodio '"+episodio["titolo"]+"' appartiene già alla serie '"+serie["titolo"]+"'.", "primary")
        return redirect(url_for("serie", codS=codS))
    if(episodio["codU"]!=serie["codU"] or episodio["codU"]!=current_user.codU):
        flash("Errore, non sei il proprietario dell'episodio o della serie.", "danger")

    titolo=episodio["titolo"]
    descrizione=episodio["descrizione"]
    data=episodio["data"]
    file=episodio["file"]

    if(dao.modificaEpisodio(codE, codS, titolo, descrizione, data, file)):
        flash("Episodio '"+titolo+"' aggiunto alla serie '"+serie["titolo"]+"' correttamente.", "success")
    else:
        flash("Errore: impossibile aggiungere l'episodio '"+titolo+"' dalla serie '"+serie["titolo"]+"'.", "success")

    return redirect(url_for("modificaSerie", codS=serie["codS"]))

@app.route("/rimuoviEpisodioDaSerie", methods=["POST"])
@login_required
def rimuoviEpisodioDaSerie():
    codE=request.form.get("codE")
    codS=request.form.get("codS")
    episodio=dao.getEpisodioByCod(codE)
    serie=dao.getSerieByCod(codS)

    if(serie is None or episodio is None):
        flash("Errore: serie o episodio inesistenti.", "danger")
        return redirect(url_for("home"))
    if(str(episodio["codS"])!=str(codS)):
        flash("Errore, l'episodio '"+episodio["titolo"]+"' non appartiene alla serie '"+serie["titolo"]+"'.", "danger")
        return redirect(url_for("home"))
    if(episodio["codU"]!=serie["codU"] or episodio["codU"]!=current_user.codU):
        flash("Errore, non sei il proprietario dell'episodio o della serie.", "danger")


    codS="NULL"
    titolo=episodio["titolo"]
    descrizione=episodio["descrizione"]
    data=episodio["data"]
    file=episodio["file"]

    if(dao.modificaEpisodio(codE, codS, titolo, descrizione, data, file)):
        flash("Episodio '"+titolo+"' rimosso dalla serie '"+serie["titolo"]+"' correttamente.", "success")
    else:
        flash("Errore: impossibile rimuovere l'episodio '"+titolo+"' dalla serie '"+serie["titolo"]+"'.", "success")

    return redirect(url_for("modificaSerie", codS=serie["codS"]))

@app.route("/iscriviti")
def iscriviti():
    return render_template("iscriviti.html", db=db())

@app.route("/iscriviti", methods=["POST"])
def iscrivitiPost():
    username=request.form.get("username")
    if(username.startswith("@")):
        username=username[1:] #rimuove "@" se presente
    password=request.form.get("password")
    nickname=request.form.get("nickname")
    creatore=request.form.get("tipoUtente")

    userInDB=dao.getUtenteByUsername(username)

    if("/" in username):
        flash("Errore: l'username non può contentere '/'.", "danger")

    if userInDB:
        flash("Errore: siste già un utente con username '"+username+"', riprova con un altro username.", "danger")
        return redirect(url_for('iscriviti'))

    file=request.files['immagine_profilo']
    propic=salvaFile(file, "", IMAGE, 1, "iscriviti", None, username)
    if propic=="":
        return redirect(url_for("iscriviti"))

    success = dao.addUtente(username,
                            generate_password_hash(password, method='sha256'),
                            nickname, propic, creatore)

    if success:
        flash("Utente @"+username+" creato correttamente.", "success")
        return redirect(url_for("home"))
    else:
        flash('Errore nella creazione del utente, riprova.', 'danger')

    return redirect(url_for("iscriviti"))

@app.route("/modificaAccount", methods=["POST"])
@login_required
def modificaAccount():
    username=request.form.get("username")
    if(username.startswith("@")):
        username=username[1:] #rimuove "@" se presente
    vecchiaPassword=request.form.get("password")
    nuovaPassword=request.form.get("nuovaPassword")
    confermaPassword=request.form.get("nuovaPassword2")
    nickname=request.form.get("nickname")
    rimuoviPropic=request.form.get("rimuoviPropic")
    upgrade=request.form.get("upgrade")
    file=request.files['immagine_profilo']

    if("/" in username):
        flash("Errore: l'username non può contentere '/'.", "danger")
        return redirect(url_for("account"))

    if(upgrade):
        creatore=1
    else:
        creatore=current_user.creatore

    if(username==current_user.username and nickname==current_user.nickname and confermaPassword=="" and
       creatore==current_user.creatore and vecchiaPassword=="" and nuovaPassword=="" and
       ( (not rimuoviPropic and not file) or (rimuoviPropic and current_user.propic==DEFAULT_PROPIC) )):
       flash("Non hai effettuato alcuna modifica.", "primary")
       return redirect(url_for("account"))

    userInDB=dao.getUtenteByUsername(username)

    if userInDB and current_user.username!=username:
        flash("Impossibile modificare l'account: esiste già un utente con username '"+username+"', riprova con un altro username.", "danger")
        return redirect(url_for("account"))

    """
    flash("vecchiaPassword: "+vecchiaPassword, "primary")
    flash("nuovaPassword: "+nuovaPassword, "primary")
    flash("confermaPassword: "+confermaPassword, "primary")
    flash("nuova!=vecchia: "+str(nuovaPassword!=confermaPassword), "primary")
    flash("check_password_hash(userInDB['password'], vecchiaPassword): "+
           str(check_password_hash(userInDB["password"], vecchiaPassword)), "primary")
     """

    if(nuovaPassword!=""):
        if(nuovaPassword!=confermaPassword):
            flash("Errore: la nuova password non è stata confermata correttamente", "danger")
            return redirect(url_for("account"))
        if(not check_password_hash(current_user.password, vecchiaPassword)):
            flash("Errore: la password inserita non è corretta", "danger")
            return redirect(url_for("account"))
    else:
        nuovaPassword=current_user.password

    if(rimuoviPropic):
        propic=DEFAULT_PROPIC
        eliminaFile(userInDB["propic"], IMAGE)
    elif(file):
        propic=salvaFile(file, "", IMAGE, 1, "iscriviti", None, username)
        eliminaFile(userInDB["propic"], IMAGE)
        if propic=="":
            return redirect(url_for("account"))
    else:
        propic=current_user.propic

    success = dao.modificaUtente(current_user.codU, username,
                            generate_password_hash(nuovaPassword, method='sha256'),
                            nickname, propic, creatore)
    if success:
        flash("Dati dell'account modificati correttamente.", "success")
    else:
        flash("Errore nella modifica dell'account.", "danger")

    return redirect(url_for("account"))


@app.route("/login")
def login():
    return render_template("login.html", db=db())

@app.route("/login", methods=["POST"])
def loginPost():
    username=request.form.get("username")
    password=request.form.get("password")

    utente=checkCredenziali(username, password)
    if not utente:
        flash("Credenziali errate, riprovare.", "danger")
        return redirect(url_for("login"))

    #utenti(codU, username, password, nickname, propic, creatore)
    user=User(utente["codU"], username, password,
              utente["nickname"], utente["propic"], utente["creatore"], utente["privato"])
    login_user(user, True)

    flash("Accesso a '"+username+"' avvenuto correttamente.", "success")
    return redirect(url_for("home"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/user/<string:username>")
def profilo(username):
    utente=dao.getUtenteByUsername(username)
    if not utente:
        flash("pagina non trovata: utente con username '"+username+"' inesistente.", "danger")
        return redirect(url_for("home"))
    codU=utente["codU"]
    episodi=dao.getEpisodiByUtente(codU)
    serie=dao.getSerieByUtente(codU)

    if(utente["privato"]==1 and (not current_user.is_authenticated or current_user.username!=username )):
        return render_template("profiloPrivato.html", utente=utente)

    if(current_user.is_authenticated and current_user.username==username):
        followers=dao.getFollowersByUtente(codU)
    else:
        followers=dao.getFollowersPubbliciByUtente(codU)
    totFollowers=len(dao.getFollowersByUtente(codU))
    serieSeguite=dao.getSerieSeguite(codU)
    totSerieSeguite=len(serieSeguite)
    seriePubbliche=dao.getSerieSeguitePubblicamente(codU)

    return render_template("profilo.html", episodi=episodi, serieCreate=serie, utente=utente,
                           followers=followers, totFollowers=totFollowers, db=db(),
                           totSerieSeguite=totSerieSeguite, totSerieCreate=len(serie),
                           totSerieSeguitePubblicamente=len(seriePubbliche),
                           totSeriePubblicate=len(serie), serieSeguite=serieSeguite,
                           totEpisodi=len(dao.getEpisodiByUtente(codU)) )

@app.route("/utenti")
def utenti():
    utenti=dao.getUtenti()
    return render_template("utenti.html", utenti=utenti, db=db())

def today():
    return ""+datetime.now().strftime("%Y-%m-%d")

def checkImgExt(e):
    if(e=="png" or e=="jpg" or e=="jpeg" or
       e=="jpe" or e=="jfif" or e=="bmp" or
       e=="dib" or e=="gif" or e=="tif" or
       e=="tiff"):
       return True
    return False

def checkAudioExt(e):
    if(e=="mp3" or e=="wav" or e=="flac" or #og: formato nota vocale di whatsapp
       e=="webm" or e=="m4p" or e=="m4a" or e=="ogg"):
        return True
    return False

def checkCredenziali(username, password):
    if(username.startswith("@")):
        username=username[1:] #rimuove "@" se presente
    utente=dao.getUtenteByUsername(username)

    if(utente and check_password_hash(utente["password"], password)):
        return utente
    return False

def PILcropCenter(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))

def PILcropSquare(img):
    #se l'immagine è rettangolare ritorna il quadrato centrale di maggior dimensione
    return PILcropCenter(img, min(img.size), min(img.size))

def vai(url, parametroUrl):
    if(parametroUrl is None):
        return redirect(url_for(url))
    if url=="serie" or url=="modificaSerie":
        return redirect(url_for(url, codS=parametroUrl))
    if url=="episodio" or url=="modificaEpisodio":
        return redirect(url_for(url, codE=parametroUrl))
    if url=="modificaCommento":
        return redirect(url_for(url, codC=parametroUrl))



def salvaFile(file, titolo, tipo, propic, url, parametroUrl, username):

    if not file:
        if(tipo==IMAGE and propic):
            return DEFAULT_PROPIC
        elif(tipo==IMAGE and not propic):
            return DEFAULT_SERIE
        else:
            return ""

    ext = file.filename.split('.')[-1] #se ci sono più "." nel nome viene diviso all'ultima occorrenza di "." ([-1])
    timestamp=datetime.now().strftime("%H-%M-%S") #per evitare nomi di file uguali
    nomeFile=username.lower()+"_ep_"+titolo.lower()+timestamp+"."+ext
    nomeFile=nomeFile.replace(" ", "_")
    nomeFile=nomeFile.replace("/", "-")
    nomeFile=nomeFile.replace(":", "-")

    #gestione file audio
    if(tipo==AUDIO):
        if(not checkAudioExt(ext)):
            flash("formato file audio non accettato, riprova.", "danger")
            return ""
    #gestione file immagine
    else:
        if(not checkImgExt(ext)):
            flash("formato file immagine non accettato, riprova.", "danger")
            return ""
        img=Image.open(file)
        file=PILcropSquare(img)

    file.save("static/"+tipo+"/"+nomeFile)

    return nomeFile

def eliminaFile(nomeFile, tipo):
    if(nomeFile==DEFAULT_PROPIC or nomeFile==DEFAULT_SERIE):
        return
    try:
        percorso="static/"+tipo+"/"
        os.remove(percorso+nomeFile)
        print("File '"+nomeFile+"' eliminato correttamente da '"+percorso+"'")
    except OSError as error:
        print(error)
        print("File '"+nomeFile+"' non trovato in '"+percorso+"'")

#prova
@app.route("/episodioNew/<int:codE>")
def episodioNew(codE):
    episodio=dao.getEpisodioByCod(codE)
    if not episodio:
        flash("episodio inesistente.", "danger")
        return redirect(url_for("home"))

    autore=dao.getUtenteByCod(episodio["codU"])
    commenti=dao.getCommentiByEpisodio(codE)
    serie=dao.getSerieByCod(episodio["codS"])
    altreSerieDellAutore=dao.getSerieByUtente(autore["codU"])
    if(serie):
        altreSerieDellaCategoria=dao.getSerieByCategoria(serie["categoria"])
    else:
        altreSerieDellaCategoria=None

    if(len(altreSerieDellAutore)<=1):
        altreSerieDellAutore=None
    if(altreSerieDellaCategoria):
        if(len(altreSerieDellaCategoria)<=1):
            altreSerieDellaCategoria=None

    episodiSerie=None
    if(serie):
        episodiSerie=dao.getEpisodiBySerie(serie["codS"])
        if(len(episodiSerie)<=1):
            episodiSerie=None

    if not(episodio or autore):
        flash("pagina non trovata.", "danger")
        redirect(url_for("home"))

    dataEpisodio=episodio["data"]
    dataCorrente=today()

    if(dataEpisodio>dataCorrente):
        if(current_user.is_authenticated and autore["codU"]==current_user.codU):
            flash("Visione pagina episodio in anteprima, l'episodio sarà pubblicato in data '"+dataEpisodio+"'.", "primary")
        else:
            flash("accesso alla pagina non autorizzato.", "danger")
            return redirect(url_for("home"))

    if(current_user.is_authenticated):
        cod=current_user.codU
    else:
        cod=-1
    db=dao.getDB(cod)

    return render_template('episodioNew.html', episodio=episodio, commenti=commenti,
                           autore=autore, serie=serie, episodiSerie=episodiSerie, db=db(),
                           altreSerieDellAutore=altreSerieDellAutore, dataCorrente=dataCorrente,
                           altreSerieDellaCategoria=altreSerieDellaCategoria)

@app.route("/serie/categorie/<string:categoria>")
def listaSeriePerCategoria(categoria):
    if(not dao.checkCategoria(categoria)):
        flash("Errore: categoria '"+categoria+"' non esistente del database.", "danger")
        return redirect(url_for("home"))

    serie=dao.getSerieByCategoria(categoria)
    categorie=dao.getCategorie()
    creators=dao.getUtentiByCategoria(categoria)

    return render_template("listaSeriePerCategoria.html", serie=serie, categoria=categoria, categorie=categorie, creators=creators, db=db())

@app.route("/<string:username>/serie")
def listaSeriePerAutore(username):
    autore=dao.getUtenteByUsername(username)
    if(not autore):
        flash("Pagina non trovata.", "danger")
        return redirect(url_for("home"))
    serie=dao.getSerieByUtente(autore["codU"])
    altriEpisodi=dao.getEpisodiSenzaSerieByUtente(autore["codU"])
    followers=dao.getFollowersByUtente(autore["codU"])
    seguiti=dao.getSerieSeguite(autore["codU"])

    if(autore["privato"]==1 and (not current_user.is_authenticated or current_user.username!=username )):
        flash("Il profilo di @"+username+" è privato.", "primary")
        return render_template("profiloPrivato.html", utente=autore)

    return render_template("listaSeriePerAutore.html", db=db(), followers=followers,
                            autore=autore, serie=serie, seguiti=seguiti, totSeguiti=len(seguiti),
                            altriEpisodi=altriEpisodi, totFollowers=len(followers))

@app.route("/<string:username>/following")
def listaSerieSeguite(username):
    utente=dao.getUtenteByUsername(username)
    if(not utente):
        flash("Pagina non trovata.", "danger")
        return redirect(url_for("home"))

    if(utente["privato"]==1 and (not current_user.is_authenticated or current_user.username!=username )):
        flash("Il profilo di @"+username+" è privato, impossibile accedere alla lista delle serie seguite.", "primary")
        return render_template("profiloPrivato.html", utente=utente)


    if(current_user.is_authenticated and current_user.username==username):
        followers=dao.getFollowersByUtente(utente["codU"])
    else:
        followers=dao.getFollowersPubbliciByUtente(utente["codU"])

    totFollowers=len(dao.getFollowersByUtente(utente["codU"]))

    seriePrivate=dao.getSerieSeguitePrivatamente(utente["codU"])
    seriePubbliche=dao.getSerieSeguitePubblicamente(utente["codU"])
    serieSeguite=dao.getSerieSeguite(utente["codU"])
    seguiti=dao.getSerieSeguite(utente["codU"])

    return render_template("listaSerieSeguite.html",
                            utente=utente, seriePrivate=seriePrivate,
                            followers=followers, totSeguiti=len(seguiti),
                            seriePubbliche=seriePubbliche, totSerieSeguite=len(serieSeguite),
                            totFollowers=totFollowers, db=db())

@app.route("/switchPubblicoFollow", methods=["POST"])
@login_required
def switchPubblicoFollow():
    codU=request.form.get("codU")
    codS=request.form.get("codS")
    pubblico=request.form.get("pubblico")
    utente=dao.getUtenteByCod(str(codU))
    serie=dao.getSerieByCod(str(codS))
    autore=dao.getUtenteByCod(serie["codU"])

    if((utente is None) or (serie is None)):
        flash("Errore: serie o utente inesistenti.", "danger")
        return redirect(url_for("home"))

    isPubblico=dao.getFollow(codU, codS)["pubblico"]

    if(dao.switchPubblicoFollow(codU, codS)):
        if(isPubblico):
            flash("Serie '"+serie["titolo"]+"' di @"+autore["username"]+" rimossa dal tuo profilo, ora il follow è privato.", "primary")
        else:
            flash("Serie '"+serie["titolo"]+"' di @"+autore["username"]+" aggiunta al profilo, ora il follow è pubblico.", "success")
    else:
        if(isPubblico):
            flash("Errore: impossibile rimuovere la serie '"+serie["titolo"]+"' di @"+autore["username"]+" dal tuo profilo pubblico, riprova.", "danger")
        else:
            flash("Errore: impossibile aggiungere la serie '"+serie["titolo"]+"' di @"+autore["username"]+" al tuo profilo pubblico, riprova.", "danger")

    return redirect(url_for("listaSerieSeguite", username=utente["username"]))

@app.route("/account/")
@login_required
def account():
    return render_template("account.html", utente=current_user)

@app.route("/switchPrivacy", methods=["POST"])
@login_required
def switchPrivacy():
    utente=dao.getUtenteByUsername(request.form.get("username"))
    if not utente:
        flash("Errore, pagina non trovata.", "danger")
        return render_template("home")

    if(current_user.username!=utente["username"]):
        flash("Accesso negato.", "danger")
        return render_template("home")

    privato=utente["privato"]
    if(privato==1):
        s="pubblico"
        a="success"
    else:
        s="privato"
        a="primary"
    if(dao.switchPrivacyAccount(current_user.username)):
        flash("Privacy dell'account cambiata correttamente: il tuo profilo è adesso "+s+".", a)
    else:
        flash("Errore: impossibile cambiare la privacy del profilo", "danger")

    return redirect(url_for("account"))

@app.route("/db")
@login_required
def mostraDB():
    if(not current_user.is_authenticated or current_user.codU!=ADMIN):
        flash("Accesso negato.", "danger")
        return redirect(url_for("home"))

    return render_template("db.html", db=dao.getDB(ADMIN))

def cambiaPassword(username, psw):
    dao.cambiaPsw(generate_password_hash(psw, method='sha256'), username)


def resetPsw():
    for u in dao.getUtenti():
        cambiaPassword(u["username"], "12345")

#cambiaPassword("artorias", "manusmiopadre")







