//! acervo-gateway — API HTTP + SSE

use axum::{
    extract::{Path, State},
    http::StatusCode,
    response::{IntoResponse, Json, Sse},
    routing::get,
    Router,
};
use axum::response::sse::{Event, KeepAlive};
use acervo_db::DbPool;
use acervo_events::EventBus;
use acervo_files::FilesService;
use serde_json::json;
use std::{convert::Infallible, net::SocketAddr, sync::Arc, time::Duration};
use tokio_stream::wrappers::BroadcastStream;
use tokio_stream::StreamExt;
use tower_http::cors::{Any, CorsLayer};
use tower_http::trace::TraceLayer;

#[derive(Clone)]
struct AppState {
    files: Arc<FilesService>,
    bus: EventBus,
    pool: DbPool,
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    dotenvy::from_path("C:/ACERVO/.env").ok();

    tracing_subscriber::fmt().with_env_filter("info").init();

    tracing::info!("Iniciando ACERVO Gateway...");

    let pool = acervo_db::init("C:/ACERVO/db/acervo.db")?;
    tracing::info!("DB ligada");

    let bus = EventBus::novo(1000);
    tracing::info!("Bus criado");

    let files = FilesService::novo(pool.clone(), bus.clone(), "C:/ACERVO/storage");
    tracing::info!("Files Service pronto");

    let state = AppState {
        files: Arc::new(files),
        bus,
        pool,
    };

    let app = Router::new()
        .route("/api/health", get(health))
        .route("/api/status", get(status))
        .route("/api/files", get(listar_files))
        .route("/api/files/:id", get(obter_file))
        .route("/api/events", get(sse_events))
        .layer(CorsLayer::new().allow_origin(Any).allow_methods(Any).allow_headers(Any))
        .layer(TraceLayer::new_for_http())
        .with_state(state);

    let addr = SocketAddr::from(([127, 0, 0, 1], 8081));
    tracing::info!("Servidor em http://{}", addr);

    let listener = tokio::net::TcpListener::bind(addr).await?;
    axum::serve(listener, app).await?;

    Ok(())
}

async fn health() -> impl IntoResponse {
    Json(json!({"status": "healthy", "versao": env!("CARGO_PKG_VERSION")}))
}

async fn status(State(state): State<AppState>) -> impl IntoResponse {
    let total = state.pool.get().ok().and_then(|conn| {
        conn.query_row("SELECT COUNT(*) FROM ficheiros", [], |r| r.get::<_, i64>(0)).ok()
    }).unwrap_or(0);
    Json(json!({"status": "ONLINE", "total_ficheiros": total}))
}

async fn listar_files(State(state): State<AppState>) -> impl IntoResponse {
    match state.files.listar() {
        Ok(lista) => Json(json!({"total": lista.len(), "files": lista})).into_response(),
        Err(e) => (StatusCode::INTERNAL_SERVER_ERROR, Json(json!({"erro": e.to_string()}))).into_response(),
    }
}

async fn obter_file(
    State(state): State<AppState>,
    Path(id): Path<i64>,
) -> impl IntoResponse {
    let conn = match state.pool.get() {
        Ok(c) => c,
        Err(e) => return (StatusCode::INTERNAL_SERVER_ERROR, Json(json!({"erro": e.to_string()}))).into_response(),
    };
    let result = conn.query_row(
        "SELECT id, nome, hash_sha256, tamanho, s3_key FROM ficheiros WHERE id = ?1",
        [id],
        |row| Ok(json!({
            "id": row.get::<_, i64>(0)?,
            "nome": row.get::<_, String>(1)?,
            "hash_sha256": row.get::<_, String>(2)?,
            "tamanho": row.get::<_, i64>(3)?,
            "s3_key": row.get::<_, String>(4)?
        })),
    );
    match result {
        Ok(f) => Json(f).into_response(),
        Err(_) => (StatusCode::NOT_FOUND, Json(json!({"erro": "não encontrado"}))).into_response(),
    }
}

async fn sse_events(State(state): State<AppState>) -> Sse<impl tokio_stream::Stream<Item = Result<Event, Infallible>>> {
    let rx = state.bus.subscrever();
    let stream = BroadcastStream::new(rx).filter_map(|msg| {
        msg.ok().map(|ev| {
            Ok(Event::default().event(&ev.tipo).json_data(&ev.dados).unwrap_or_else(|_| Event::default().data("erro")))
        })
    });
    Sse::new(stream).keep_alive(KeepAlive::new().interval(Duration::from_secs(15)))
}

