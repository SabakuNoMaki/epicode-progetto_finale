"""
StudIAmo — Assistente per lo Studio Universitario.

Carichi i tuoi materiali (PDF, PowerPoint, Word, testo) e puoi:
  - fare domande, ottenendo risposte con la citazione della fonte
  - generare quiz a risposta multipla per ripassare

Avvio:
    streamlit run app.py
"""

import time

import numpy as np
import streamlit as st

import rag
import stile

st.set_page_config(page_title="StudIAmo — Assistente per lo Studio",
                   page_icon="📚", layout="wide")

SEZ_DOMANDE = "Domande"
SEZ_QUIZ = "Ripasso a quiz"


# ---------------------------------------------------------------------------
# Memoria della sessione
# Streamlit riesegue lo script a ogni interazione, quindi quello che vogliamo
# conservare va messo in st.session_state.
# ---------------------------------------------------------------------------
INIZIALI = {
    "chunk": [], "matrice": None, "nomi_file": [], "chat": [],
    "quiz": None, "quiz_corretto": False, "indice_caricato": False,
    "mostra_stat": False,
    # Ultima ricerca: alimenta il pannello delle fonti sulla destra
    "fonti": [], "modalita": None, "documenti": [], "durata": None,
    # Modelli davvero disponibili sulla chiave inserita
    "modelli": [], "chiave_dei_modelli": None,
}
for chiave, valore in INIZIALI.items():
    if chiave not in st.session_state:
        st.session_state[chiave] = valore

# Il tema non va azzerato quando si svuota il materiale, quindi sta a parte
if "tema" not in st.session_state:
    st.session_state.tema = "scuro"

# Il foglio di stile dipende dal tema scelto: va iniettato per primo
st.markdown(stile.css(st.session_state.tema), unsafe_allow_html=True)

# Al primo avvio recuperiamo l'indice salvato su disco
if not st.session_state.indice_caricato:
    c, m, n = rag.carica_indice()
    if c is not None:
        st.session_state.chunk, st.session_state.matrice, st.session_state.nomi_file = c, m, n
    st.session_state.indice_caricato = True


@st.cache_resource(show_spinner="Carico il modello di embedding (solo la prima volta)…")
def modello_embedding():
    """@st.cache_resource carica il modello UNA volta, non a ogni interazione."""
    return rag.carica_modello()


def salva():
    """Riscrive l'indice su disco, o lo cancella se non e' rimasto nulla."""
    if st.session_state.chunk:
        rag.salva_indice(st.session_state.chunk, st.session_state.matrice,
                         st.session_state.nomi_file)
    else:
        rag.cancella_indice()


# ---------------------------------------------------------------------------
# BARRA LATERALE
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Modello")
    chiave_api = st.text_input(
        "API key OpenAI", type="password", placeholder="sk-…",
        label_visibility="collapsed",
        help=f"La prendi da {rag.DOVE_PRENDERE_LA_CHIAVE}")
    if not chiave_api:
        st.caption(f"[→ Ottieni una chiave]({rag.DOVE_PRENDERE_LA_CHIAVE})")
        modello_scelto = rag.MODELLO_DI_RISERVA
    else:
        # Chiediamo a OpenAI quali modelli ha questa chiave: il catalogo
        # cambia da account ad account, quindi non possiamo darlo per scontato.
        # Lo facciamo una volta sola per chiave, non a ogni interazione.
        if st.session_state.chiave_dei_modelli != chiave_api:
            try:
                with st.spinner("Leggo i modelli disponibili…"):
                    st.session_state.modelli = rag.modelli_disponibili(chiave_api)
                st.session_state.chiave_dei_modelli = chiave_api
            except Exception as e:
                st.session_state.modelli = []
                st.error(rag.spiega_errore(e))

        if st.session_state.modelli:
            modello_scelto = st.selectbox(
                "Modello", st.session_state.modelli, index=0,
                help="Sono i modelli che la tua chiave può davvero usare. "
                     "I più economici sono in cima.")
        else:
            modello_scelto = rag.MODELLO_DI_RISERVA

    st.divider()
    st.header("Aspetto")
    st.segmented_control("Tema", ["scuro", "chiaro"], key="tema",
                         format_func=str.capitalize, label_visibility="collapsed")

    st.divider()
    st.header("Materiale")
    if st.session_state.nomi_file:
        # Ogni documento ha il suo pulsante per essere rimosso singolarmente
        for nome in list(st.session_state.nomi_file):
            col_nome, col_x = st.columns([5, 1], vertical_alignment="center")
            with col_nome:
                st.markdown(f'<div class="pillola-file" title="{nome}">{nome}</div>',
                            unsafe_allow_html=True)
            with col_x:
                if st.button("✕", key=f"togli__{nome}", help=f"Rimuovi {nome}"):
                    (st.session_state.chunk,
                     st.session_state.matrice,
                     st.session_state.nomi_file) = rag.rimuovi_documento(
                        st.session_state.chunk, st.session_state.matrice,
                        st.session_state.nomi_file, nome)
                    salva()
                    st.session_state.fonti = []
                    st.rerun()

        if st.button("Svuota tutto", use_container_width=True):
            rag.cancella_indice()
            for chiave, valore in INIZIALI.items():
                st.session_state[chiave] = valore
            st.session_state.indice_caricato = True
            st.rerun()
    else:
        st.caption("Nessun documento caricato.")


# ---------------------------------------------------------------------------
# BARRA SUPERIORE
# ---------------------------------------------------------------------------
chips = [f"{len(st.session_state.nomi_file)} documenti",
         f"{len(st.session_state.chunk)} passaggi",
         modello_scelto]
st.markdown(stile.barra_alta("StudIAmo", chips,
                             acceso="pronto" if chiave_api else None),
            unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# CARICAMENTO
# ---------------------------------------------------------------------------
with st.expander("Carica materiale", expanded=not st.session_state.chunk):
    files = st.file_uploader(
        "Trascina qui i file — PDF, PowerPoint, Word o testo",
        type=["pdf", "pptx", "docx", "txt", "md"],
        accept_multiple_files=True, label_visibility="collapsed")

    if files and st.button("Indicizza i documenti", type="primary"):
        modello = modello_embedding()
        nuovi_chunk, problemi = [], []

        barra = st.progress(0.0, text="Leggo i documenti…")
        for i, f in enumerate(files):
            if f.name in st.session_state.nomi_file:
                continue                      # già caricato
            try:
                pezzi = rag.prepara_chunk(f, f.name)
                if not pezzi:
                    problemi.append(f"**{f.name}** — nessun testo estratto "
                                    "(può essere un PDF di sole immagini scansionate)")
                else:
                    nuovi_chunk += pezzi
                    st.session_state.nomi_file.append(f.name)
            except Exception as e:
                problemi.append(f"**{f.name}** — {e}")
            barra.progress((i + 1) / len(files), text=f"Letto {f.name}")

        if nuovi_chunk:
            barra.progress(1.0, text="Calcolo gli embedding…")
            nuova = rag.calcola_embeddings(modello, [c["testo"] for c in nuovi_chunk])
            if st.session_state.matrice is None:
                st.session_state.matrice = nuova
            else:
                st.session_state.matrice = np.vstack([st.session_state.matrice, nuova])
            st.session_state.chunk += nuovi_chunk
            salva()

        barra.empty()
        for p in problemi:
            st.warning(p)
        if nuovi_chunk:
            st.success(f"Indicizzati {len(nuovi_chunk)} nuovi passaggi · "
                       "il materiale resta salvato per le prossime volte")
            st.rerun()
        elif not problemi:
            st.info("Questi documenti erano già stati caricati.")


if not st.session_state.chunk:
    st.info("Carica almeno un documento per iniziare, dal pannello qui sopra.")
    st.stop()


# ---------------------------------------------------------------------------
# SELETTORE DI SEZIONE
# ---------------------------------------------------------------------------
riga_sel = st.columns([2, 1], vertical_alignment="center")
with riga_sel[0]:
    sezione = st.segmented_control("Sezione", [SEZ_DOMANDE, SEZ_QUIZ],
                                   default=SEZ_DOMANDE, label_visibility="collapsed")
    if sezione is None:
        sezione = SEZ_DOMANDE
with riga_sel[1]:
    etichetta = "Nascondi statistiche" if st.session_state.mostra_stat else "Statistiche"
    if st.button(etichetta, use_container_width=True):
        st.session_state.mostra_stat = not st.session_state.mostra_stat
        st.rerun()

if st.session_state.mostra_stat:
    st.markdown(stile.riga_stat([
        (len(st.session_state.nomi_file), "documenti"),
        (len(st.session_state.chunk), "passaggi"),
        (len([m for m in st.session_state.chat if m["ruolo"] == "user"]), "domande"),
    ]), unsafe_allow_html=True)


# ============================== DOMANDE ====================================
if sezione == SEZ_DOMANDE:
    col_chat, col_fonti = st.columns([2.15, 1], gap="medium")

    # ---- conversazione ----
    with col_chat:
        if not st.session_state.chat:
            st.caption("Puoi chiedere un dettaglio preciso (*“cosa fa la "
                       "backpropagation?”*) oppure un quadro d'insieme "
                       "(*“elencami tutti gli algoritmi di ordinamento”*): "
                       "la strategia di ricerca si adatta da sola.")

        for messaggio in st.session_state.chat:
            with st.chat_message(messaggio["ruolo"]):
                if messaggio.get("meta"):
                    st.markdown(stile.riga_meta(messaggio["meta"]),
                                unsafe_allow_html=True)
                st.markdown(messaggio["testo"])

    # ---- pannello delle fonti, sempre visibile ----
    with col_fonti:
        st.markdown(stile.pannello_fonti(st.session_state.fonti,
                                         st.session_state.modalita),
                    unsafe_allow_html=True)


# ================================ QUIZ =====================================
else:
    col_quiz, _ = st.columns([2.15, 1], gap="medium")
    with col_quiz:
        riga = st.columns([3, 1])
        with riga[0]:
            argomento = st.text_input(
                "Argomento", label_visibility="collapsed",
                placeholder="Argomento del quiz (vuoto = ripasso generale)")
        with riga[1]:
            n_domande = st.selectbox("Domande", [3, 5, 10], index=1,
                                     label_visibility="collapsed")

        if st.button("Genera il quiz", type="primary"):
            if not chiave_api:
                st.error("Inserisci la tua API key nella barra laterale.")
            else:
                try:
                    with st.spinner("Preparo le domande…"):
                        modello = modello_embedding()
                        scelti = rag.scegli_chunk_per_quiz(
                            st.session_state.chunk,
                            n_chunk=max(6, n_domande),
                            argomento=argomento or None,
                            modello=modello,
                            matrice=st.session_state.matrice)
                        quiz = rag.genera_quiz(scelti, chiave_api, n_domande,
                                            modello=modello_scelto)
                    if not quiz:
                        st.error("Non sono riuscito a generare domande valide. Riprova.")
                    else:
                        st.session_state.quiz = quiz
                        st.session_state.quiz_corretto = False
                        st.rerun()
                except Exception as e:
                    st.error(rag.spiega_errore(e))

        quiz = st.session_state.quiz
        if quiz:
            st.write("")
            if not st.session_state.quiz_corretto:
                with st.form("modulo_quiz"):
                    for i, d in enumerate(quiz):
                        st.markdown(
                            f'<div class="domanda-quiz">'
                            f'<span class="numero-domanda">{i + 1}</span>'
                            f'<b>{d["domanda"]}</b></div>', unsafe_allow_html=True)
                        # index=None per non suggerire una risposta di default
                        st.radio("Scegli:", d["opzioni"], key=f"risposta_{i}",
                                 index=None, label_visibility="collapsed")
                    if st.form_submit_button("Correggi", type="primary",
                                             use_container_width=True):
                        st.session_state.quiz_corretto = True
                        st.rerun()
            else:
                giuste = 0
                for i, d in enumerate(quiz):
                    scelta = st.session_state.get(f"risposta_{i}")
                    corretta = d["opzioni"][d["indice_corretta"]]
                    esatta = scelta == corretta
                    giuste += esatta

                    righe = [f'<div class="testo-domanda">'
                             f'<span class="numero-domanda">{i + 1}</span>'
                             f'{d["domanda"]}</div>']
                    if esatta:
                        righe.append(f'<div class="riga">✅ <b>{corretta}</b></div>')
                    else:
                        data = scelta if scelta is not None else "nessuna risposta"
                        righe.append(f'<div class="riga">❌ Tua risposta: {data}</div>')
                        righe.append(f'<div class="riga">✅ Corretta: <b>{corretta}</b></div>')
                    if d.get("spiegazione"):
                        righe.append(f'<div class="nota">{d["spiegazione"]}</div>')
                    if d.get("fonte"):
                        righe.append(f'<div class="nota">Da ripassare: {d["fonte"]}</div>')

                    st.markdown(f'<div class="esito {"giusta" if esatta else "sbagliata"}">'
                                + "".join(righe) + "</div>", unsafe_allow_html=True)

                percentuale = giuste / len(quiz) * 100
                st.markdown(stile.riga_stat([
                    (f"{giuste}/{len(quiz)}", "risposte giuste"),
                    (f"{percentuale:.0f}%", "punteggio"),
                ]), unsafe_allow_html=True)

                if percentuale == 100:
                    st.balloons()
                elif percentuale < 60:
                    st.info("Sotto il 60%: conviene ripassare gli argomenti segnalati sopra.")

                if st.button("Nuovo quiz"):
                    st.session_state.quiz = None
                    st.session_state.quiz_corretto = False
                    st.rerun()


# ---------------------------------------------------------------------------
# BARRA DI SCRITTURA
# ---------------------------------------------------------------------------
if sezione == SEZ_DOMANDE:
    domanda = st.chat_input("Chiedi qualcosa ai tuoi documenti…")

    if domanda:
        modello = modello_embedding()
        risultati, modalita, documenti = rag.recupera(
            modello, domanda, st.session_state.matrice, st.session_state.chunk)

        st.session_state.chat.append({"ruolo": "user", "testo": domanda})
        st.session_state.fonti = risultati
        st.session_state.modalita = modalita
        st.session_state.documenti = documenti

        meta = [(modalita, "panoramica" if modalita == "panoramica" else "evidenza"),
                (f"{len(risultati)} passaggi", "")]

        if not chiave_api:
            st.session_state.chat.append({
                "ruolo": "assistant", "meta": meta,
                "testo": "Inserisci la tua API key nella barra laterale per ottenere "
                         "la risposta scritta. I passaggi trovati sono già elencati "
                         "nel pannello a destra."})
        else:
            try:
                with st.spinner("Leggo i documenti e preparo la risposta…"):
                    inizio = time.time()
                    testo = rag.rispondi(domanda, risultati, chiave_api, modalita,
                                         modello=modello_scelto)
                    durata = time.time() - inizio
                meta.append((f"{durata:.1f} s", ""))
                st.session_state.chat.append(
                    {"ruolo": "assistant", "meta": meta, "testo": testo})
            except Exception as e:
                st.session_state.chat.append(
                    {"ruolo": "assistant", "meta": meta,
                     "testo": f"⚠️ {rag.spiega_errore(e)}"})

        st.rerun()
