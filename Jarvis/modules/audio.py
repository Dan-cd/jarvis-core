from safe.safe_execution import safe_execute

@safe_execute(origin="plugin", sensitive=True)
def audio_plugin():
    raise RuntimeError("Microfone não encontrado")
    