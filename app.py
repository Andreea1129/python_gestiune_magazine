from flask import Flask, render_template, request, redirect, url_for, flash
from mysql.connector import Error

from db import fetch_all_dict, fetch_one_dict, execute

app = Flask(__name__)
app.secret_key = "secret123"


# ---------- Helpers ----------

def _first_selected_id(name: str):
    # In Flask, pentru compatibilitate, luam primul selectat.
    vals = request.form.getlist(name)
    if vals:
        return vals[0]
    return request.values.get(name)


# ---------- Index ----------
@app.get("/")
def index():
    return render_template("index.html")


@app.get("/index.html")
def index_html():
    return render_template("index.html")


# ---------- MAGAZINE ----------
@app.get("/tabela_Magazine.html")
def tabela_magazine():
    magazine = fetch_all_dict(
        "SELECT idmagazin, Nume, Adresa, Email FROM magazine ORDER BY idmagazin"
    )
    return render_template("tabela_Magazine.html", magazine=magazine)


@app.route("/nou_Magazin.html", methods=["GET", "POST"])
def nou_magazin():
    if request.method == "POST":
        nume = (request.form.get("Nume") or "").strip()
        adresa = (request.form.get("Adresa") or "").strip()
        email = (request.form.get("Email") or "").strip()

        if not nume or not adresa or not email:
            return render_template("nou_Magazin.html", error="Toate campurile sunt obligatorii!", form=request.form)

        try:
            execute(
                "INSERT INTO magazine (Nume, Adresa, Email) VALUES (%s, %s, %s)",
                (nume, adresa, email),
            )
        except Error as e:
            return render_template("nou_Magazin.html", error=f"Eroare la adaugare: {e}", form=request.form)

        return render_template("nou_Magazin.html", success=True)

    return render_template("nou_Magazin.html", form={})


@app.post("/sterge_Magazin.html")
def sterge_magazin():
    ids = request.form.getlist("primarykey")
    if not ids:
        return render_template("sterge_Magazin.html", deleted=False)

    # stergere in bulk
    try:
        placeholders = ",".join(["%s"] * len(ids))
        # Daca exista FK fara CASCADE in DB, trebuie sa stergi intai din stoc.
        execute(f"DELETE FROM stoc WHERE idmagazin IN ({placeholders})", ids)
        execute(f"DELETE FROM magazine WHERE idmagazin IN ({placeholders})", ids)
    except Error as e:
        return render_template("sterge_Magazin.html", deleted=False, error=str(e))

    return render_template("sterge_Magazin.html", deleted=True)


@app.get("/modifica_Magazin.html")
def modifica_magazin_lista():
    magazine = fetch_all_dict(
        "SELECT idmagazin, Nume, Adresa, Email FROM magazine ORDER BY idmagazin"
    )
    return render_template("modifica_Magazin.html", magazine=magazine)


@app.route("/m1_Magazin.html", methods=["GET", "POST"])
def m1_magazin():
    # ia primul magazin selectat
    id_raw = _first_selected_id("primarykey")
    if not id_raw:
        return render_template("m1_Magazin.html", missing=True)

    try:
        mid = int(id_raw)
    except ValueError:
        return render_template("m1_Magazin.html", missing=True)

    magazin = fetch_one_dict(
        "SELECT idmagazin, Nume, Adresa, Email FROM magazine WHERE idmagazin=%s",
        (mid,),
    )
    if not magazin:
        return render_template("m1_Magazin.html", missing=True)

    return render_template("m1_Magazin.html", magazin=magazin)


@app.post("/m2_Magazin.html")
def m2_magazin():
    try:
        mid = int(request.form.get("idmagazin"))
    except (TypeError, ValueError):
        return render_template("m2_Magazin.html", error="ID magazin invalid")

    nume = (request.form.get("Nume") or "").strip()
    adresa = (request.form.get("Adresa") or "").strip()
    email = (request.form.get("Email") or "").strip()

    if not nume or not adresa or not email:
        return render_template("m2_Magazin.html", error="Toate campurile sunt obligatorii!")

    try:
        execute(
            "UPDATE magazine SET Nume=%s, Adresa=%s, Email=%s WHERE idmagazin=%s",
            (nume, adresa, email, mid),
        )
    except Error as e:
        return render_template("m2_Magazin.html", error=str(e))

    return render_template("m2_Magazin.html", success=True)


# ---------- PRODUSE ----------
@app.get("/tabela_Produse.html")
def tabela_produse():
    produse = fetch_all_dict(
        "SELECT idprodus, Nume, Cod, Categorie FROM produse ORDER BY idprodus"
    )
    return render_template("tabela_Produse.html", produse=produse)


@app.route("/nou_Produs.html", methods=["GET", "POST"])
def nou_produs():
    if request.method == "POST":
        nume = (request.form.get("Nume") or "").strip()
        cod = (request.form.get("Cod") or "").strip()
        categorie = (request.form.get("Categorie") or "").strip()

        if not nume or not cod or not categorie:
            return render_template("nou_Produs.html", error="Toate campurile sunt obligatorii!", form=request.form)

        try:
            execute(
                "INSERT INTO produse (Nume, Cod, Categorie) VALUES (%s, %s, %s)",
                (nume, cod, categorie),
            )
        except Error as e:
            return render_template("nou_Produs.html", error=f"Eroare la adaugare: {e}", form=request.form)

        return render_template("nou_Produs.html", success=True)

    return render_template("nou_Produs.html", form={})


@app.post("/sterge_Produs.html")
def sterge_produs():
    ids = request.form.getlist("primarykey")
    if not ids:
        return render_template("sterge_Produs.html", deleted=False)

    try:
        placeholders = ",".join(["%s"] * len(ids))
        execute(f"DELETE FROM stoc WHERE idprodus IN ({placeholders})", ids)
        execute(f"DELETE FROM produse WHERE idprodus IN ({placeholders})", ids)
    except Error as e:
        return render_template("sterge_Produs.html", deleted=False, error=str(e))

    return render_template("sterge_Produs.html", deleted=True)


@app.get("/modifica_Produs.html")
def modifica_produs_lista():
    produse = fetch_all_dict(
        "SELECT idprodus, Nume, Cod, Categorie FROM produse ORDER BY idprodus"
    )
    return render_template("modifica_Produs.html", produse=produse)


@app.route("/m1_Produs.html", methods=["GET", "POST"])
def m1_produs():
    id_raw = _first_selected_id("primarykey")
    if not id_raw:
        return render_template("m1_Produs.html", missing=True)

    try:
        pid = int(id_raw)
    except ValueError:
        return render_template("m1_Produs.html", missing=True)

    produs = fetch_one_dict(
        "SELECT idprodus, Nume, Cod, Categorie FROM produse WHERE idprodus=%s",
        (pid,),
    )
    if not produs:
        return render_template("m1_Produs.html", missing=True)

    return render_template("m1_Produs.html", produs=produs)


@app.post("/m2_Produs.html")
def m2_produs():
    try:
        pid = int(request.form.get("idprodus"))
    except (TypeError, ValueError):
        return render_template("m2_Produs.html", error="ID produs invalid")

    nume = (request.form.get("Nume") or "").strip()
    cod = (request.form.get("Cod") or "").strip()
    categorie = (request.form.get("Categorie") or "").strip()

    if not nume or not cod or not categorie:
        return render_template("m2_Produs.html", error="Toate campurile sunt obligatorii!")

    try:
        execute(
            "UPDATE produse SET Nume=%s, Cod=%s, Categorie=%s WHERE idprodus=%s",
            (nume, cod, categorie, pid),
        )
    except Error as e:
        return render_template("m2_Produs.html", error=str(e))

    return render_template("m2_Produs.html", success=True)


# ---------- STOC ----------
@app.get("/tabela_Stoc.html")
def tabela_stoc():
    stocuri = fetch_all_dict(
        """
        SELECT
          s.idstoc,
          s.idmagazin AS idmagazin_stoc,
          m.Nume AS NumeMagazin,
          m.Adresa AS Adresa,
          m.Email AS Email,
          s.idprodus AS idprodus_stoc,
          p.Nume AS NumeProdus,
          p.Cod AS Cod,
          p.Categorie AS Categorie,
          s.Cantitate AS Cantitate,
          s.pret_vanzare AS pret_vanzare
        FROM stoc s
        JOIN magazine m ON m.idmagazin = s.idmagazin
        JOIN produse p ON p.idprodus = s.idprodus
        ORDER BY s.idstoc
        """
    )
    return render_template("tabela_Stoc.html", stocuri=stocuri)


@app.route("/nou_Stoc.html", methods=["GET", "POST"])
def nou_stoc():
    magazine = fetch_all_dict("SELECT idmagazin, Nume, Adresa, Email FROM magazine ORDER BY idmagazin")
    produse = fetch_all_dict("SELECT idprodus, Nume, Cod, Categorie FROM produse ORDER BY idprodus")

    if request.method == "POST":
        idmagazin = request.form.get("idmagazin")
        idprodus = request.form.get("idprodus")
        cantitate = (request.form.get("Cantitate") or "").strip()
        pret = (request.form.get("PretVanzare") or "").strip()

        if not idmagazin or not idprodus or not cantitate or not pret:
            return render_template(
                "nou_Stoc.html",
                error="Toate campurile sunt obligatorii!",
                magazine=magazine,
                produse=produse,
                form=request.form,
            )

        try:
            execute(
                "INSERT INTO stoc (idmagazin, idprodus, Cantitate, pret_vanzare) VALUES (%s, %s, %s, %s)",
                (int(idmagazin), int(idprodus), int(cantitate), float(pret)),
            )
        except Exception as e:
            return render_template(
                "nou_Stoc.html",
                error=f"Eroare la adaugare: {e}",
                magazine=magazine,
                produse=produse,
                form=request.form,
            )

        return render_template("nou_Stoc.html", success=True, magazine=magazine, produse=produse)

    return render_template("nou_Stoc.html", magazine=magazine, produse=produse, form={})


@app.post("/sterge_Stoc.html")
def sterge_stoc():
    ids = request.form.getlist("primarykey")
    if not ids:
        return render_template("sterge_Stoc.html", deleted=False)

    try:
        placeholders = ",".join(["%s"] * len(ids))
        execute(f"DELETE FROM stoc WHERE idstoc IN ({placeholders})", ids)
    except Error as e:
        return render_template("sterge_Stoc.html", deleted=False, error=str(e))

    return render_template("sterge_Stoc.html", deleted=True)


@app.get("/modifica_Stoc.html")
def modifica_stoc_lista():
    stocuri = fetch_all_dict(
        """
        SELECT
          s.idstoc,
          s.idmagazin AS idmagazin_stoc,
          m.Nume AS NumeMagazin,
          m.Adresa AS Adresa,
          m.Email AS Email,
          s.idprodus AS idprodus_stoc,
          p.Nume AS NumeProdus,
          p.Cod AS Cod,
          p.Categorie AS Categorie,
          s.Cantitate AS Cantitate,
          s.pret_vanzare AS pret_vanzare
        FROM stoc s
        JOIN magazine m ON m.idmagazin = s.idmagazin
        JOIN produse p ON p.idprodus = s.idprodus
        ORDER BY s.idstoc
        """
    )
    return render_template("modifica_Stoc.html", stocuri=stocuri)


@app.route("/m1_Stoc.html", methods=["GET", "POST"])
def m1_stoc():
    id_raw = _first_selected_id("primarykey")
    if not id_raw:
        return render_template("m1_Stoc.html", missing=True)

    try:
        sid = int(id_raw)
    except ValueError:
        return render_template("m1_Stoc.html", missing=True)

    stoc = fetch_one_dict(
        "SELECT idstoc, idmagazin, idprodus, Cantitate, pret_vanzare FROM stoc WHERE idstoc=%s",
        (sid,),
    )
    if not stoc:
        return render_template("m1_Stoc.html", missing=True)

    magazine = fetch_all_dict("SELECT idmagazin, Nume, Adresa, Email FROM magazine ORDER BY idmagazin")
    produse = fetch_all_dict("SELECT idprodus, Nume, Cod, Categorie FROM produse ORDER BY idprodus")

    return render_template("m1_Stoc.html", stoc=stoc, magazine=magazine, produse=produse)


@app.post("/m2_Stoc.html")
def m2_stoc():
    try:
        sid = int(request.form.get("idstoc"))
        idmagazin = int(request.form.get("idmagazin"))
        idprodus = int(request.form.get("idprodus"))
        cantitate = int(request.form.get("Cantitate"))
        pret = float(request.form.get("PretVanzare"))
    except Exception:
        return render_template("m2_Stoc.html", error="Date invalide (verifica toate campurile)")

    try:
        execute(
            "UPDATE stoc SET idmagazin=%s, idprodus=%s, Cantitate=%s, pret_vanzare=%s WHERE idstoc=%s",
            (idmagazin, idprodus, cantitate, pret, sid),
        )
    except Error as e:
        return render_template("m2_Stoc.html", error=str(e))

    return render_template("m2_Stoc.html", success=True)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
