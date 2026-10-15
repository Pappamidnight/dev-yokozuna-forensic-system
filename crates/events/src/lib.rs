//! acervo-events — Bus de eventos interno

use acervo_core::Evento;
use tokio::sync::broadcast;

#[derive(Clone)]
pub struct EventBus {
    tx: broadcast::Sender<Evento>,
}

impl EventBus {
    pub fn novo(capacidade: usize) -> Self {
        let (tx, _) = broadcast::channel(capacidade);
        Self { tx }
    }

    pub fn emitir(&self, evento: Evento) {
        let _ = self.tx.send(evento);
    }

    pub fn subscrever(&self) -> broadcast::Receiver<Evento> {
        self.tx.subscribe()
    }
}
