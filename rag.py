
import io
import re

import numpy as np


# ---------------------------------------------------------------------------
# 1. LETTURA DEI DOCUMENTI
# ---------------------------------------------------------------------------

def leggi_pdf(file):
    """Estrae il testo da un PDF, pagina per pagina."""
    from pypdf import PdfReader

    reader = PdfReader(file)
    pagine = []
    for numero, pagina in enumerate(reader.pages, start=1):
        testo = pagina.extract_text() or ""
        if testo.strip():
            pagine.append((f"pagina {numero}", testo))
    return pagine


def leggi_pptx(file):
    """Estrae il testo da una presentazione PowerPoint, slide per slide."""
    from pptx import Presentation

    prs = Presentation(file)
    slides = []
    for numero, slide in enumerate(prs.slides, start=1):
        pezzi = []
        for shape in slide.shapes:
            if shape.has_text_frame:
                pezzi.append(shape.text_frame.text)
            # Anche il testo dentro le tabelle
            if getattr(shape, "has_table", False) and shape.has_table:
                for riga in shape.table.rows:
                    pezzi.append(" | ".join(cella.text for cella in riga.cells))
        testo = "\n".join(p for p in pezzi if p.strip())
        if testo.strip():
            slides.append((f"slide {numero}", testo))
    return slides


def leggi_docx(file):
    """Estrae il testo da un documento Word."""
    from docx import Document

    doc = Document(file)
    testo = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    return [("documento", testo)] if testo.strip() else []


def leggi_testo(file):
    """Estrae il testo da un file .txt o .md."""
    dati = file.read()
    if isinstance(dati, bytes):
        dati = dati.decode("utf-8", errors="ignore")
    return [("documento", dati)] if dati.strip() else []


def leggi_documento(file, nome_file):
    nome = nome_file.lower()
    if nome.endswith(".pdf"):
        return leggi_pdf(file)
    if nome.endswith(".pptx"):
        return leggi_pptx(file)
    if nome.endswith(".docx"):
        return leggi_docx(file)
    if nome.endswith((".txt", ".md")):
        return leggi_testo(file)
    raise ValueError(f"Formato non supportato: {nome_file}")


# ---------------------------------------------------------------------------
# 2. SPEZZETTAMENTO IN CHUNK
# ---------------------------------------------------------------------------

def pulisci(testo):
    """Toglie spazi e a capo di troppo."""
    testo = re.sub(r"[ \t]+", " ", testo)
    testo = re.sub(r"\n{3,}", "\n\n", testo)
    return testo.strip()


def spezza(testo, dimensione=800, sovrapposizione=150):
    testo = pulisci(testo)
    if not testo:
        return []

    pezzi = []
    inizio = 0
    while inizio < len(testo):
        fine = inizio + dimensione

        # Cerchiamo di tagliare a fine frase invece che a meta' parola
        if fine < len(testo):
            taglio = testo.rfind(". ", inizio + dimensione // 2, fine)
            if taglio != -1:
                fine = taglio + 1

        pezzo = testo[inizio:fine].strip()
        if pezzo:
            pezzi.append(pezzo)

        if fine >= len(testo):
            break
        inizio = fine - sovrapposizione

    return pezzi


def prepara_chunk(file, nome_file):
    chunk = []
    for posizione, testo in leggi_documento(file, nome_file):
        for pezzo in spezza(testo):
            chunk.append({"testo": pezzo, "file": nome_file, "posizione": posizione})
    return chunk


# ---------------------------------------------------------------------------
# 3. EMBEDDINGS E RICERCA
# ---------------------------------------------------------------------------
MODELLO_EMBEDDING = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def carica_modello():
    """Carica il modello che trasforma il testo in vettori."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODELLO_EMBEDDING)


def calcola_embeddings(modello, testi):
    return modello.encode(testi, normalize_embeddings=True, show_progress_bar=False)


def cerca(modello, domanda, matrice, chunk, quanti=4):
    v_domanda = calcola_embeddings(modello, [domanda])[0]
    similarita = matrice @ v_domanda            # prodotto scalare = coseno
    migliori = np.argsort(similarita)[::-1][:quanti]
    return [(chunk[i], float(similarita[i])) for i in migliori]

SPIE_PANORAMICA = [
    "elenca", "elencami", "elenco", "lista", "tutti", "tutte", "tutt'",
    "quali", "quante", "quanti", "esistono", "tipi di",
    "riassumi", "riassunto", "riepiloga", "panoramica", "sintetizza", "sintesi",
    "in generale", "argomenti", "indice", "parla", "sommario",
    "schema", "mappa", "ripasso", "ripassa", "ogni",
]


def e_panoramica(domanda):
    """Riconosce se la domanda chiede una visione d'insieme invece di un dettaglio."""
    d = domanda.lower()
    return any(spia in d for spia in SPIE_PANORAMICA)
BONUS_NOME_FILE = 0.20


def parole_del_nome(nome_file):
    """Estrae le parole significative dal nome del file (senza estensione)."""
    base = nome_file.rsplit(".", 1)[0].lower()
    return {p for p in re.split(r"[_\-\s.]+", base) if len(p) >= 4}


def cerca_panoramica(modello, domanda, matrice, chunk,
                     max_chunk=20, max_documenti=2, soglia_relativa=0.85):
    v_domanda = calcola_embeddings(modello, [domanda])[0]
    similarita = matrice @ v_domanda

    # Punteggio di ogni documento = il migliore tra i suoi passaggi
    punteggio_doc = {}
    for i, c in enumerate(chunk):
        s = float(similarita[i])
        if s > punteggio_doc.get(c["file"], -1):
            punteggio_doc[c["file"]] = s

    # Bonus per il nome del file citato nella domanda
    d = domanda.lower()
    for nome in punteggio_doc:
        if any(parola in d for parola in parole_del_nome(nome)):
            punteggio_doc[nome] += BONUS_NOME_FILE

    ordinati = sorted(punteggio_doc.items(), key=lambda x: x[1], reverse=True)
    massimo = ordinati[0][1]
    scelti = [nome for nome, p in ordinati[:max_documenti]
              if p >= massimo * soglia_relativa]

    risultati = []
    for nome in scelti:
        for i, c in enumerate(chunk):
            if c["file"] == nome:
                risultati.append((c, float(similarita[i])))
    return risultati[:max_chunk], scelti


# Quanti passaggi passare all'LLM per una domanda puntuale.
PASSAGGI_PUNTUALI = 4

# Tetto dei passaggi in ricerca panoramica: li' serve tutto il documento,
# ma senza un limite il contesto diventerebbe enorme.
MAX_PASSAGGI_PANORAMICA = 20


def recupera(modello, domanda, matrice, chunk,
             quanti=PASSAGGI_PUNTUALI, max_chunk_panoramica=MAX_PASSAGGI_PANORAMICA):
    if e_panoramica(domanda):
        risultati, documenti = cerca_panoramica(
            modello, domanda, matrice, chunk, max_chunk=max_chunk_panoramica)
        return risultati, "panoramica", documenti

    risultati = cerca(modello, domanda, matrice, chunk, quanti=quanti)
    documenti = list(dict.fromkeys(c["file"] for c, _ in risultati))
    return risultati, "puntuale", documenti


# ---------------------------------------------------------------------------
# 4. RISPOSTA DELL'LLM
# ---------------------------------------------------------------------------

DOVE_PRENDERE_LA_CHIAVE = "https://platform.openai.com/api-keys"

# Quali modelli preferiamo, dal piu' economico in su. Non sono scritti nel
# codice come scelta definitiva: sono solo l'ordine di preferenza con cui
# scegliamo FRA QUELLI che la chiave dell'utente ha davvero a disposizione.
# Il catalogo di OpenAI cambia nel tempo e varia da account ad account, quindi
# fissarne uno solo significa prima o poi trovarsi un "modello non disponibile".
PREFERENZE_MODELLI = [
    "gpt-4.1-nano", "gpt-4o-mini", "gpt-4.1-mini",
    "gpt-5-nano", "gpt-5-mini", "gpt-4.1", "gpt-4o",
]

MODELLO_DI_RISERVA = "gpt-4o-mini"


def client_llm(chiave):
    """Crea il client OpenAI con la chiave inserita dall'utente."""
    from openai import OpenAI

    return OpenAI(api_key=chiave)


def modelli_disponibili(chiave):
    """
    Chiede a OpenAI l'elenco dei modelli accessibili con questa chiave.

    Ritorna i modelli di chat, con i piu' economici in cima: cosi' l'utente
    sceglie fra cose che esistono davvero sul suo account, invece di scoprire
    a posteriori che quello scritto nel codice non c'e'.
    """
    nomi = {m.id for m in client_llm(chiave).models.list().data}

    # Scartiamo i modelli che non servono a generare testo
    def utile(n):
        if not (n.startswith("gpt") or n.startswith("o1") or n.startswith("o3")):
            return False
        return not any(x in n for x in
                       ("audio", "realtime", "transcribe", "tts", "image",
                        "search", "instruct", "vision-preview"))

    preferiti = [n for n in PREFERENZE_MODELLI if n in nomi]
    altri = sorted(n for n in nomi if utile(n) and n not in preferiti)
    return preferiti + altri


def formatta_matematica(testo):
    r"""
    Porta le formule nei delimitatori che Streamlit sa disegnare.

    I modelli di OpenAI scrivono la matematica con \( ... \) e \[ ... \],
    che Streamlit mostra come testo grezzo: "( a_n )" invece della formula.
    Il motore che usa (KaTeX) riconosce invece $ ... $ e $$ ... $$.
    Glielo chiediamo nelle istruzioni, ma convertiamo comunque: i modelli
    tornano spesso alla notazione a cui sono abituati.
    """
    if not testo:
        return testo
    testo = re.sub(r"\\\[(.+?)\\\]", r"$$\1$$", testo, flags=re.S)
    testo = re.sub(r"\\\((.+?)\\\)", r"$\1$", testo, flags=re.S)
    return testo


ISTRUZIONI = r"""Sei un assistente che aiuta uno studente universitario a studiare.

Rispondi alla domanda usando ESCLUSIVAMENTE il CONTESTO che ti viene fornito.

Regole importanti:
- Se la risposta non e' nel contesto, scrivi esattamente: "Non trovo questa informazione nei documenti caricati." Non inventare nulla.
- Cita sempre le fonti che hai usato, indicandole tra parentesi quadre cosi': [nomefile.pdf, pagina 4]
- Per le formule usa LaTeX con i dollari: $ ... $ in mezzo al testo e
  $$ ... $$ per una formula su riga propria. Non usare mai \( \) o \[ \].
- Rispondi in italiano, in modo chiaro e ordinato.
- Se la domanda e' vaga, rispondi comunque con quello che trovi di piu' pertinente."""


def costruisci_contesto(risultati):
    """Mette insieme i chunk trovati in un unico testo da dare all'LLM."""
    parti = []
    for chunk, punteggio in risultati:
        parti.append(f"[{chunk['file']}, {chunk['posizione']}]\n{chunk['testo']}")
    return "\n\n---\n\n".join(parti)


ISTRUZIONI_PANORAMICA = r"""Sei un assistente che aiuta uno studente universitario a studiare.

Lo studente ti ha fatto una domanda d'insieme: vuole un quadro completo, non un
singolo dettaglio. Ti viene fornito il CONTESTO, che contiene i passaggi dei
documenti piu' pertinenti, in ordine di lettura.

Regole importanti:
- Sii ESAUSTIVO: elenca TUTTI gli elementi pertinenti che trovi nel contesto,
  senza fermarti ai primi due o tre e senza omettere nulla.
- Organizza la risposta in un elenco puntato, con una riga di spiegazione per
  ogni voce.
- Usa esclusivamente il contesto fornito: non aggiungere elementi che conosci
  ma che non sono presenti nei documenti.
- Indica la fonte tra parentesi quadre cosi': [nomefile.pdf, pagina 4]
- Se nel contesto non c'e' nulla di pertinente, scrivi: "Non trovo questa
  informazione nei documenti caricati."
- Per le formule usa LaTeX con i dollari: $ ... $ in mezzo al testo e
  $$ ... $$ per una formula su riga propria. Non usare mai \( \) o \[ \].
- Rispondi in italiano."""


def rispondi(domanda, risultati, chiave, modalita="puntuale",
             modello=MODELLO_DI_RISERVA):
    client = client_llm(chiave)
    contesto = costruisci_contesto(risultati)
    istruzioni = ISTRUZIONI_PANORAMICA if modalita == "panoramica" else ISTRUZIONI

    risposta = client.chat.completions.create(
        model=modello,
        messages=[
            {"role": "system", "content": istruzioni},
            {"role": "user", "content": f"CONTESTO:\n{contesto}\n\nDOMANDA: {domanda}"},
        ],
        temperature=0.2,
    )
    return formatta_matematica(risposta.choices[0].message.content)


def rispondi_senza_contesto(domanda, chiave, modello=MODELLO_DI_RISERVA):
    client = client_llm(chiave)
    risposta = client.chat.completions.create(
        model=modello,
        messages=[
            {"role": "system", "content": "Rispondi in italiano, in modo conciso."},
            {"role": "user", "content": domanda},
        ],
        temperature=0.2,
    )
    return risposta.choices[0].message.content


# ---------------------------------------------------------------------------
# 5. GENERAZIONE DEI QUIZ
# ---------------------------------------------------------------------------

ISTRUZIONI_QUIZ = r"""Sei un docente universitario che prepara domande d'esame.

Ti viene fornito del MATERIALE di studio. Genera esattamente {n} domande a
risposta multipla basate SOLO su quel materiale.

Regole:
- Ogni domanda ha 4 opzioni, di cui una sola corretta.
- Le opzioni sbagliate devono essere plausibili, non assurde: servono a far
  ragionare, non a essere scartate a colpo d'occhio.
- La domanda deve poter essere risolta leggendo il materiale fornito.
- Nella spiegazione, chiarisci perche' la risposta corretta e' giusta.
- Per le formule usa LaTeX con i dollari: $ ... $ in mezzo al testo e
  $$ ... $$ per una formula su riga propria. Non usare mai \( \) o \[ \].
- Scrivi tutto in italiano.

Rispondi ESCLUSIVAMENTE con un oggetto JSON valido in questo formato,
senza testo prima o dopo e senza blocchi markdown:

{{"domande": [
  {{"domanda": "...",
   "opzioni": ["...", "...", "...", "..."],
   "indice_corretta": 0,
   "spiegazione": "...",
   "fonte": "nomefile.pdf, pagina 3"}}
]}}"""


def domanda_valida(d):
    return (isinstance(d, dict)
            and isinstance(d.get("domanda"), str) and d["domanda"].strip()
            and isinstance(d.get("opzioni"), list) and len(d["opzioni"]) == 4
            and all(isinstance(o, str) and o.strip() for o in d["opzioni"])
            and isinstance(d.get("indice_corretta"), int)
            and 0 <= d["indice_corretta"] <= 3)


def json_annidati(testo):
    import json

    trovati = []
    profondita = 0
    inizio = None
    for i, ch in enumerate(testo):
        if ch == "{":
            if profondita == 0:
                inizio = i
            profondita += 1
        elif ch == "}" and profondita > 0:
            profondita -= 1
            if profondita == 0 and inizio is not None:
                try:
                    trovati.append(json.loads(testo[inizio:i + 1]))
                except Exception:
                    pass
                inizio = None
    return trovati


def raccogli_domande(oggetto, trovate):
    if isinstance(oggetto, dict):
        if domanda_valida(oggetto):
            trovate.append(oggetto)
            return
        for chiave, valore in oggetto.items():
            raccogli_domande(chiave, trovate)     # anche le chiavi: vedi sopra
            raccogli_domande(valore, trovate)
    elif isinstance(oggetto, list):
        for valore in oggetto:
            raccogli_domande(valore, trovate)
    elif isinstance(oggetto, str):
        if "{" in oggetto and "domanda" in oggetto:
            for pezzo in json_annidati(oggetto):
                raccogli_domande(pezzo, trovate)


def genera_quiz(chunk_scelti, chiave, n_domande=5, tentativi=3,
                modello=MODELLO_DI_RISERVA):
    import json

    client = client_llm(chiave)
    materiale = costruisci_contesto([(c, 1.0) for c in chunk_scelti])

    valide = []
    viste = set()
    for _ in range(tentativi):
        risposta = client.chat.completions.create(
            model=modello,
            messages=[
                {"role": "system", "content": ISTRUZIONI_QUIZ.format(n=n_domande)},
                {"role": "user", "content": f"MATERIALE:\n{materiale}"},
            ],
            temperature=0.7,      # un po' di varieta': i quiz non devono essere identici
            response_format={"type": "json_object"},
        )
        testo = risposta.choices[0].message.content.strip()
        testo = testo.replace("```json", "").replace("```", "").strip()

        trovate = []
        try:
            raccogli_domande(json.loads(testo), trovate)
        except Exception:
            # JSON non interpretabile: proviamo a pescare i frammenti a mano
            for pezzo in json_annidati(testo):
                raccogli_domande(pezzo, trovate)

        for d in trovate:
            # Anche le domande possono contenere formule
            d["domanda"] = formatta_matematica(d["domanda"])
            d["opzioni"] = [formatta_matematica(o) for o in d["opzioni"]]
            if d.get("spiegazione"):
                d["spiegazione"] = formatta_matematica(d["spiegazione"])

            testo_domanda = d["domanda"].strip().lower()
            if testo_domanda not in viste:      # niente doppioni tra i tentativi
                viste.add(testo_domanda)
                valide.append(d)

        if len(valide) >= n_domande:
            break

    return valide[:n_domande]


def scegli_chunk_per_quiz(chunk, n_chunk=6, argomento=None, modello=None, matrice=None):
    if argomento and modello is not None and matrice is not None:
        risultati = cerca(modello, argomento, matrice, chunk, quanti=n_chunk)
        return [c for c, _ in risultati]

    if len(chunk) <= n_chunk:
        return list(chunk)
    # Prendiamo chunk equidistanti, per coprire tutto il materiale
    passo = len(chunk) / n_chunk
    return [chunk[int(i * passo)] for i in range(n_chunk)]


# ---------------------------------------------------------------------------
# 6. SALVATAGGIO SU DISCO
# ---------------------------------------------------------------------------

CARTELLA_INDICE = "indice"


def salva_indice(chunk, matrice, nomi_file, cartella=CARTELLA_INDICE):
    """Salva su disco i chunk (JSON) e gli embedding (formato numpy)."""
    import json
    import os

    os.makedirs(cartella, exist_ok=True)
    with open(os.path.join(cartella, "chunk.json"), "w", encoding="utf-8") as f:
        json.dump({"chunk": chunk, "nomi_file": nomi_file}, f, ensure_ascii=False)
    np.save(os.path.join(cartella, "embeddings.npy"), matrice)


def carica_indice(cartella=CARTELLA_INDICE):
    import json
    import os

    file_chunk = os.path.join(cartella, "chunk.json")
    file_emb = os.path.join(cartella, "embeddings.npy")
    if not (os.path.exists(file_chunk) and os.path.exists(file_emb)):
        return None, None, None

    try:
        with open(file_chunk, encoding="utf-8") as f:
            dati = json.load(f)
        matrice = np.load(file_emb)
        chunk = dati["chunk"]
        # Coerenza: il numero di righe della matrice deve pareggiare i chunk
        if len(chunk) != len(matrice):
            return None, None, None
        return chunk, matrice, dati.get("nomi_file", [])
    except Exception:
        return None, None, None


def rimuovi_documento(chunk, matrice, nomi_file, nome_da_togliere):
    tenere = [i for i, c in enumerate(chunk) if c["file"] != nome_da_togliere]

    nuovi_chunk = [chunk[i] for i in tenere]
    nuova_matrice = matrice[tenere] if len(tenere) else None
    nuovi_nomi = [n for n in nomi_file if n != nome_da_togliere]

    return nuovi_chunk, nuova_matrice, nuovi_nomi


def cancella_indice(cartella=CARTELLA_INDICE):
    """Cancella l'indice salvato su disco."""
    import shutil

    shutil.rmtree(cartella, ignore_errors=True)


# ---------------------------------------------------------------------------
# 7. MESSAGGI DI ERRORE
# ---------------------------------------------------------------------------

def spiega_errore(e):
    """Traduce gli errori dell'API in messaggi comprensibili."""
    testo = str(e)
    if "401" in testo or "invalid" in testo.lower() and "key" in testo.lower():
        return "La API key non e' valida. Ricontrolla di averla copiata per intero."
    if "429" in testo:
        return ("Troppe richieste o credito esaurito. Aspetta qualche secondo e riprova, "
                "oppure controlla il credito su platform.openai.com.")
    if "model" in testo.lower() and ("not" in testo.lower() or "does not exist" in testo.lower()):
        return ("Questo modello non e' disponibile sulla tua chiave. "
                "Scegline un altro dal menu 'Modello' nella barra laterale.\n\n"
                f"Messaggio di OpenAI: {testo[:200]}")
    return f"Errore nella chiamata all'LLM: {testo[:300]}"
