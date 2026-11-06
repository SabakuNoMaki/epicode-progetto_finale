"""
Foglio di stile dell'applicazione.

Impostazione grafica "Officina": strumento professionale, scuro e denso.
Tipografia IBM Plex (Sans per il testo, Mono per i metadati), accento
verde-acqua, superfici piatte separate da bordi sottili.

Due temi: scuro (quello nativo) e chiaro, che ne conserva struttura e
densita'. Tutti i colori sono variabili CSS: cambiare tema significa
iniettare un blocco di variabili diverso, le regole restano identiche.
"""

# ===========================================================================
# 1. Le due tavolozze
# ===========================================================================

VARIABILI_SCURO = """
:root {
    --sfondo:
        radial-gradient(900px 500px at 82% -12%, #10262B 0%, rgba(16,38,43,0) 60%),
        linear-gradient(180deg, #0F1219 0%, #0B0E14 100%);
    --sfondo-piatto: #0D1017;

    --superficie:   #12161E;
    --superficie-2: #10151D;
    --superficie-3: #0A0D13;
    --bordo:        #1E2530;
    --bordo-forte:  #2A3745;

    --testo:   #E6E9EF;
    --testo-2: #A9B3C1;
    --testo-3: #7D8899;

    --accento:        #2DD4BF;
    --accento-tenue:  #0C2E2A;
    --accento-bordo:  #17554D;
    --accento-solido: #2DD4BF;
    --su-accento:     #05231F;

    --ambra-fondo: #2B2410; --ambra-bordo: #6B5518; --ambra-testo: #FBCB5C;
    --verde-fondo: #0D2A20; --verde-bordo: #1E5C44; --verde-testo: #6EE7A8;
    --rosso-fondo: #2E1519; --rosso-bordo: #6B2830; --rosso-testo: #FCA5A5;

    --ombra-1: 0 1px 2px rgba(0,0,0,.32);
    --ombra-2: 0 8px 24px -12px rgba(0,0,0,.60);
}
"""

VARIABILI_CHIARO = """
:root {
    --sfondo:
        radial-gradient(900px 500px at 82% -12%, #E2F4F1 0%, rgba(226,244,241,0) 62%),
        linear-gradient(180deg, #FBFDFD 0%, #F3F6F7 100%);
    --sfondo-piatto: #F7F9FA;

    --superficie:   #FFFFFF;
    --superficie-2: #F2F6F7;
    --superficie-3: #FAFCFC;
    --bordo:        #E0E8EA;
    --bordo-forte:  #C9D6D9;

    --testo:   #0F1720;
    --testo-2: #47565F;
    --testo-3: #56626B;   /* scurito: con #67757E i metadati stavano a 3,8 */

    --accento:        #0F766E;
    --accento-tenue:  #E4F3F1;
    --accento-bordo:  #A3D6D0;
    --accento-solido: #0F766E;
    --su-accento:     #FFFFFF;

    --ambra-fondo: #FFFBEB; --ambra-bordo: #FDE68A; --ambra-testo: #92620B;
    --verde-fondo: #F0FDF4; --verde-bordo: #BBF7D0; --verde-testo: #15803D;
    --rosso-fondo: #FEF2F2; --rosso-bordo: #FECACA; --rosso-testo: #B91C1C;

    --ombra-1: 0 1px 2px rgba(15,23,32,.05);
    --ombra-2: 0 8px 22px -12px rgba(15,23,32,.14);
}
"""

# ===========================================================================
# 2. Le regole (identiche nei due temi: usano solo var(...))
# ===========================================================================

REGOLE = """
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

:root { --raggio: 9px; --raggio-s: 6px;
        --sans: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        --mono: 'IBM Plex Mono', ui-monospace, SFMono-Regular, Menlo, monospace; }

/* --------------------------- Impianto generale --------------------------- */
body { background-color: var(--sfondo-piatto) !important; }

.stApp {
    background-color: var(--sfondo-piatto);
    background-image: var(--sfondo);
    background-attachment: fixed;
    color: var(--testo);
}

.block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; max-width: 1280px; }

html, body, [class*="css"] { font-family: var(--sans); -webkit-font-smoothing: antialiased; }
h1, h2, h3, h4 { letter-spacing: -0.015em; color: var(--testo) !important; font-weight: 600; }
p, li, span, label, .stMarkdown { color: var(--testo-2); }
[data-testid="stCaptionContainer"], .stCaption, small { color: var(--testo-3) !important; }
code { font-family: var(--mono) !important; color: var(--accento) !important;
       background: var(--accento-tenue) !important; font-size: .84em !important; }
hr { border-color: var(--bordo) !important; }
a { color: var(--accento) !important; }

/* ----------------------------- Barra superiore --------------------------- */
.barra-alta {
    display: flex; align-items: center; gap: 14px;
    padding: 11px 16px; margin-bottom: 16px;
    background: var(--superficie);
    border: 1px solid var(--bordo);
    border-radius: var(--raggio);
    box-shadow: var(--ombra-1);
}
.barra-alta .marchio {
    display: flex; align-items: center; gap: 9px;
    font-size: 14.5px; font-weight: 600; color: var(--testo);
}
.barra-alta .tessera {
    width: 28px; height: 28px; border-radius: var(--raggio-s);
    background: linear-gradient(150deg, var(--accento), var(--accento-bordo));
    display: grid; place-items: center; flex: 0 0 auto;
}
.barra-alta .spazio { flex-grow: 1; }

.chip {
    font-family: var(--mono); font-size: 11px; color: var(--testo-3);
    border: 1px solid var(--bordo-forte); border-radius: var(--raggio-s);
    padding: 3px 8px; white-space: nowrap;
}
.chip.acceso { color: var(--accento); border-color: var(--accento-bordo);
               background: var(--accento-tenue); }
.pallino { width: 6px; height: 6px; border-radius: 50%; background: var(--accento);
           display: inline-block; margin-right: 5px; vertical-align: middle; }

/* -------------------------- Etichette dei metadati ----------------------- */
.riga-meta { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 11px; }
.meta {
    font-family: var(--mono); font-size: 10.5px; text-transform: uppercase;
    letter-spacing: .06em; padding: 3px 8px; border-radius: var(--raggio-s);
    border: 1px solid var(--bordo-forte); color: var(--testo-3);
}
.meta.evidenza { background: var(--accento-tenue); color: var(--accento);
                 border-color: var(--accento-bordo); }
.meta.panoramica { background: var(--ambra-fondo); color: var(--ambra-testo);
                   border-color: var(--ambra-bordo); }

/* ------------------------------ Riquadri stat ---------------------------- */
.riga-stat { display: flex; gap: 8px; margin-bottom: 14px; flex-wrap: wrap; }
.stat {
    flex: 1 1 120px; background: var(--superficie); border: 1px solid var(--bordo);
    border-radius: var(--raggio-s); padding: 10px 12px;
}
.stat .numero { font-family: var(--mono); font-size: 20px; font-weight: 600;
                color: var(--testo); line-height: 1.15; font-variant-numeric: tabular-nums; }
.stat .etichetta { font-family: var(--mono); font-size: 10px; text-transform: uppercase;
                   letter-spacing: .09em; color: var(--testo-3); margin-top: 3px; }

/* -------------------------- Pannello delle fonti ------------------------- */
.rail-titolo {
    display: flex; align-items: center; justify-content: space-between;
    font-family: var(--mono); font-size: 10.5px; text-transform: uppercase;
    letter-spacing: .1em; color: var(--testo-3); margin-bottom: 10px;
}
.fonte {
    background: var(--superficie-2); border: 1px solid var(--bordo);
    border-left: 2px solid var(--accento-bordo);
    border-radius: var(--raggio-s); padding: 10px 11px; margin-bottom: 8px;
}
.fonte.prima { border-left-color: var(--accento); }
.fonte .riga1 { display: flex; justify-content: space-between; align-items: baseline; gap: 8px; }
.fonte .nome { font-size: 12px; font-weight: 600; color: var(--testo); overflow: hidden;
               text-overflow: ellipsis; white-space: nowrap; }
.fonte .punteggio { font-family: var(--mono); font-size: 11px; color: var(--accento);
                    font-variant-numeric: tabular-nums; flex: 0 0 auto; }
.fonte .posizione { font-family: var(--mono); font-size: 10.5px; color: var(--testo-3);
                    margin: 5px 0 6px; }
.fonte .estratto { font-size: 12px; line-height: 1.6; color: var(--testo-2); }
.rail-scorri {
    max-height: 58vh; overflow-y: auto; padding-right: 4px;
    scrollbar-width: thin; scrollbar-color: var(--bordo-forte) transparent;
}
.rail-scorri::-webkit-scrollbar { width: 6px; }
.rail-scorri::-webkit-scrollbar-thumb { background: var(--bordo-forte); border-radius: 3px; }

.rail-vuoto {
    border: 1px dashed var(--bordo-forte); border-radius: var(--raggio-s);
    padding: 16px 13px; font-size: 12.5px; line-height: 1.6; color: var(--testo-3);
}
.rail-nota {
    font-family: var(--mono); font-size: 10px; color: var(--testo-3);
    line-height: 1.7; padding-top: 10px; margin-top: 10px; border-top: 1px solid var(--bordo);
}

/* ----------------------------------- Chat -------------------------------- */
[data-testid="stChatMessage"] {
    background: var(--superficie); border: 1px solid var(--bordo);
    border-radius: var(--raggio); padding: 14px 16px; margin-bottom: 8px;
    box-shadow: none;
}
[data-testid="stChatMessage"] p { line-height: 1.72; color: var(--testo-2); font-size: 14.5px; }
[data-testid="stChatMessage"] strong { color: var(--testo); }

/* Avatar della chat: Streamlit li colora di rosso e arancione di serie */
[data-testid="stChatMessageAvatarUser"] {
    background: var(--bordo-forte) !important; color: var(--testo-2) !important;
    border-radius: var(--raggio-s) !important;
}
[data-testid="stChatMessageAvatarAssistant"] {
    background: var(--accento-solido) !important; color: var(--su-accento) !important;
    border-radius: var(--raggio-s) !important;
}
[data-testid^="stChatMessageAvatar"] svg { fill: currentColor !important; }
/* L'icona dentro l'avatar deve ereditare, altrimenti la regola generica
   sulle icone la lascia grigia su fondo verde-acqua (contrasto 1,14). */
[data-testid^="stChatMessageAvatar"] [data-testid="stIconMaterial"],
[data-testid^="stChatMessageAvatar"] * { color: inherit !important; }

/* Indicatore di attesa: di serie ha un riquadro bianco */
[data-testid="stSpinner"] {
    background: var(--superficie) !important;
    border: 1px solid var(--bordo) !important;
    border-radius: var(--raggio-s) !important;
}
[data-testid="stSpinner"] * { color: var(--testo-2) !important; }

/* Riferimento alla fonte dentro la risposta */
[data-testid="stChatMessage"] code {
    font-size: .8em !important; padding: 1px 5px; border-radius: 3px;
}

/* Barra di scrittura, fissata in fondo */
[data-testid="stBottomBlockContainer"], [data-testid="stBottom"],
[data-testid="stBottom"] > div, [data-testid="stChatInput"] > div,
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stBottomBlockContainer"] { padding-top: .4rem !important; padding-bottom: .9rem !important; }
[data-testid="stChatInput"] {
    background: var(--superficie) !important;
    border: 1px solid var(--bordo-forte) !important;
    border-radius: var(--raggio) !important;
    box-shadow: var(--ombra-2) !important;
}
[data-testid="stChatInput"] textarea {
    field-sizing: content; height: auto !important;
    min-height: 1.5rem !important; max-height: 9rem !important;
    color: var(--testo) !important; font-size: 14.5px !important;
}
@supports not (field-sizing: content) {
    [data-testid="stChatInput"] textarea { height: 2.5rem !important; }
}
[data-testid="stChatInput"] textarea::placeholder { color: var(--testo-3) !important; }

/* --------------------------------- Controlli ----------------------------- */
button[data-testid^="stBaseButton"],
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {
    border-radius: var(--raggio-s) !important; font-weight: 500; font-size: 13.5px;
    background: var(--superficie) !important; color: var(--testo) !important;
    border: 1px solid var(--bordo-forte) !important;
    transition: border-color .15s ease, background .15s ease;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    border-color: var(--accento-bordo) !important; background: var(--superficie-2) !important;
}
button[data-testid="stBaseButton-primary"],
button[data-testid="stBaseButton-primaryFormSubmit"] {
    background: var(--accento-solido) !important; color: var(--su-accento) !important;
    border-color: var(--accento-solido) !important; font-weight: 600;
}
/* L'etichetta dei pulsanti sta in un <p>: deve ereditare il colore */
button p, button span, button div, button label,
[role="radio"] p, [role="radio"] span, [role="radio"] div { color: inherit !important; }

.stTextInput input, .stTextArea textarea, [data-testid="stTextInputRootElement"],
[data-testid="stSelectbox"] > div > div {
    background: var(--superficie-2) !important; color: var(--testo) !important;
    border-color: var(--bordo) !important; border-radius: var(--raggio-s) !important;
}
.stTextInput input::placeholder { color: var(--testo-3) !important; }
[data-testid="stSelectbox"] input { color: var(--testo) !important; }
[data-baseweb="popover"] div, [role="listbox"] {
    background: var(--superficie) !important; color: var(--testo) !important;
}
[data-testid="stIconMaterial"], [data-baseweb="input"] button { color: var(--testo-2) !important; }

[data-testid="stSlider"] input { background: transparent !important; }
[data-testid="stSliderThumbValue"] {
    background: var(--accento-solido) !important; color: var(--su-accento) !important;
    padding: .05rem .38rem !important; border-radius: 4px !important;
    font-family: var(--mono) !important; font-weight: 600 !important;
}
[data-testid="stSliderThumbValue"] * { color: var(--su-accento) !important; }

/* Selettore di sezione: sono button[role="radio"], senza data-testid */
[role="radiogroup"] button[role="radio"] {
    background: var(--superficie) !important; color: var(--testo-2) !important;
    border-color: var(--bordo) !important; font-size: 13px !important;
}
[role="radiogroup"] button[role="radio"][aria-checked="true"] {
    background: var(--accento-tenue) !important; color: var(--accento) !important;
    border-color: var(--accento-bordo) !important;
}

/* Expander: da aperto Streamlit gli mette un fondo bianco pieno */
[data-testid="stExpander"] {
    border: 1px solid var(--bordo) !important; border-radius: var(--raggio) !important;
    box-shadow: none !important; background: var(--superficie);
}
[data-testid="stExpander"] details summary { background: transparent !important; }
[data-testid="stExpander"] details summary:hover { background: var(--superficie-2) !important; }
[data-testid="stExpander"] details summary,
[data-testid="stExpander"] details summary * { color: var(--testo) !important; }
[data-testid="stExpander"] details { background: transparent !important; }

[data-testid="stFileUploader"] section, [data-testid="stFileUploaderDropzone"] {
    background: var(--superficie-2) !important;
    border: 1px dashed var(--bordo-forte) !important;
}
[data-testid="stFileUploader"] span, [data-testid="stFileUploader"] div,
[data-testid="stFileUploader"] small { color: var(--testo-3) !important; }

[data-testid="stAlert"] {
    background: var(--superficie-2) !important; border: 1px solid var(--bordo) !important;
    border-radius: var(--raggio-s) !important; color: var(--testo) !important;
}

/* ------------------------------ Barra laterale --------------------------- */
[data-testid="stSidebar"] {
    background: var(--superficie-3); border-right: 1px solid var(--bordo);
}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    font-family: var(--mono); font-size: 10.5px !important; text-transform: uppercase;
    letter-spacing: .11em; color: var(--testo-3) !important; font-weight: 500;
}
[data-testid="stSidebar"] .block-container { padding-top: 1.4rem; }

.stButton > button[kind="secondary"]:has(+ *), 
[data-testid="stSidebar"] .stColumn:last-child button {
    padding: 0 !important; min-height: 32px !important; height: 32px !important;
    color: var(--testo-3) !important;
}
[data-testid="stSidebar"] .stColumn:last-child button:hover {
    color: var(--rosso-testo) !important; border-color: var(--rosso-bordo) !important;
}

.pillola-file {
    background: var(--superficie-2); border: 1px solid var(--bordo);
    border-radius: var(--raggio-s); padding: .34rem .55rem;
    font-size: 12.5px; color: var(--testo-2);
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

/* --------------------------- Quiz ---------------------------------------- */
.domanda-quiz {
    background: var(--superficie); border: 1px solid var(--bordo);
    border-radius: var(--raggio); padding: 14px 16px .4rem; margin-bottom: 8px;
}
.domanda-quiz b { color: var(--testo); font-weight: 600; }
.numero-domanda {
    display: inline-grid; place-items: center; width: 20px; height: 20px;
    border-radius: 4px; background: var(--accento-tenue); color: var(--accento);
    border: 1px solid var(--accento-bordo);
    font-family: var(--mono); font-size: 11px; font-weight: 600;
    margin-right: 9px; vertical-align: middle;
}
.esito { border-radius: var(--raggio); padding: 13px 15px; margin-bottom: 8px; }
.esito.giusta    { background: var(--verde-fondo); border: 1px solid var(--verde-bordo); }
.esito.sbagliata { background: var(--rosso-fondo); border: 1px solid var(--rosso-bordo); }
.esito .testo-domanda { font-weight: 600; margin-bottom: 8px; color: var(--testo); font-size: 14px; }
.esito .riga { font-size: 13.5px; margin: .16rem 0; color: var(--testo-2); }
.esito .riga b { color: var(--testo); }
.esito .nota { font-size: 12.5px; color: var(--testo-3); margin-top: 7px; line-height: 1.55; }

/* ------------------- Elementi di Streamlit da nascondere ----------------- */
footer, #MainMenu, [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }
"""


def css(tema="scuro"):
    """Restituisce il blocco <style> completo per il tema richiesto."""
    variabili = VARIABILI_CHIARO if tema == "chiaro" else VARIABILI_SCURO
    return f"<style>{variabili}{REGOLE}</style>"


# ===========================================================================
# 3. Componenti HTML
# ===========================================================================

LIBRO = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" '
         'stroke="var(--su-accento)" stroke-width="2.2" stroke-linecap="round" '
         'stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>'
         '<path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>')


def barra_alta(nome, chips, acceso=None):
    """Barra superiore: marchio a sinistra, metadati a destra."""
    pezzi = "".join(f'<span class="chip">{c}</span>' for c in chips)
    stato = (f'<span class="chip acceso"><span class="pallino"></span>{acceso}</span>'
             if acceso else "")
    return (f'<div class="barra-alta">'
            f'<div class="marchio"><span class="tessera">{LIBRO}</span>{nome}</div>'
            f'<span class="spazio"></span>{pezzi}{stato}</div>')


def riga_meta(voci):
    """voci: lista di (testo, classe) dove classe e' '', 'evidenza' o 'panoramica'."""
    pezzi = "".join(f'<span class="meta {c}">{t}</span>' for t, c in voci)
    return f'<div class="riga-meta">{pezzi}</div>'


def riga_stat(voci):
    celle = "".join(f'<div class="stat"><div class="numero">{n}</div>'
                    f'<div class="etichetta">{e}</div></div>' for n, e in voci)
    return f'<div class="riga-stat">{celle}</div>'


def titolo_rail(testo, contatore=""):
    return (f'<div class="rail-titolo"><span>{testo}</span>'
            f'<span style="color: var(--accento)">{contatore}</span></div>')


def blocco_fonte(chunk, punteggio, prima=False, lunghezza=190):
    estratto = chunk["testo"][:lunghezza].replace("<", "&lt;").strip()
    return (f'<div class="fonte{" prima" if prima else ""}">'
            f'<div class="riga1"><span class="nome">{chunk["file"]}</span>'
            f'<span class="punteggio">{punteggio:.2f}</span></div>'
            f'<div class="posizione">{chunk["posizione"]}</div>'
            f'<div class="estratto">«{estratto}…»</div></div>')


def pannello_fonti(fonti, modalita=None):
    """
    Costruisce l'intero pannello di destra in un solo blocco HTML.

    Le fonti stanno in un contenitore a scorrimento con altezza massima: in
    modalita' panoramica possono essere anche venti, e senza questo il
    pannello diventerebbe una colonna lunghissima.
    """
    if not fonti:
        corpo = ('<div class="rail-vuoto">Qui compariranno i passaggi dei tuoi '
                 'documenti da cui è stata ricavata la risposta, con il loro '
                 'punteggio di somiglianza.</div>')
        conteggio = ""
    else:
        carte = "".join(blocco_fonte(c, p, prima=(i == 0))
                        for i, (c, p) in enumerate(fonti))
        corpo = f'<div class="rail-scorri">{carte}</div>'
        conteggio = str(len(fonti))

    nota_modalita = ""
    if modalita == "panoramica":
        nota_modalita = ('<div class="rail-nota" style="border-top: none; '
                         'padding-top: 0; margin-top: 0; margin-bottom: 8px;">'
                         'ricerca panoramica: l\'intero documento</div>')

    return (f'<div class="rail-titolo"><span>Fonti consultate</span>'
            f'<span style="color: var(--accento)">{conteggio}</span></div>'
            f'{nota_modalita}{corpo}'
            f'<div class="rail-nota">embedding calcolati in locale<br>'
            f'MiniLM multilingue · 384 dimensioni</div>')
