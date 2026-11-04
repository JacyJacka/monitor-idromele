"""Hook PreToolUse: chiede conferma all'utente prima di ogni `git push`.

Mostra i commit che stanno per essere inviati e i file toccati, poi lascia
decidere all'utente. Se qualcosa va storto, chiede comunque conferma: in
caso di dubbio il push non parte mai da solo.
"""

import json
import subprocess
import sys

MAX_RIGHE = 30


def git(*argomenti, cartella):
    risultato = subprocess.run(
        ["git", *argomenti],
        cwd=cartella,
        capture_output=True,
        text=True,
        timeout=10,
    )
    if risultato.returncode != 0:
        raise RuntimeError(risultato.stderr.strip())
    return risultato.stdout.rstrip()


def base_di_confronto(cartella):
    """Il punto da cui contare i commit da inviare."""
    try:
        return git("rev-parse", "--abbrev-ref", "@{u}", cartella=cartella)
    except RuntimeError:
        pass  # ramo nuovo, senza corrispondente remoto
    try:
        git("rev-parse", "--verify", "origin/main", cartella=cartella)
        return "origin/main"
    except RuntimeError:
        return None


def accorcia(testo):
    righe = testo.splitlines()
    if len(righe) > MAX_RIGHE:
        righe = righe[:MAX_RIGHE] + [f"... e altre {len(righe) - MAX_RIGHE} righe"]
    return "\n".join(righe)


def riepilogo(cartella):
    ramo = git("branch", "--show-current", cartella=cartella)
    base = base_di_confronto(cartella)
    if base is None:
        commit = git("log", "--oneline", "-5", cartella=cartella)
        return f"Ramo: {ramo}\nUltimi commit:\n{commit}"
    commit = git("log", "--oneline", f"{base}..HEAD", cartella=cartella)
    if not commit:
        return f"Ramo: {ramo}\nNessun commit nuovo rispetto a {base}."
    file = git("diff", "--stat", f"{base}...HEAD", cartella=cartella)
    return (
        f"Ramo: {ramo} (confronto con {base})\n"
        f"Commit da inviare:\n{accorcia(commit)}\n\n"
        f"File toccati:\n{accorcia(file)}"
    )


def main():
    try:
        dati = json.load(sys.stdin)
        cartella = dati.get("cwd") or "."
        testo = riepilogo(cartella)
    except Exception as errore:  # in caso di dubbio, si chiede sempre
        testo = f"Impossibile preparare il riepilogo ({errore})."

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": "Conferma il push su GitHub.\n\n" + testo,
        }
    }))


if __name__ == "__main__":
    main()
