#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
google_ingest.py - Extrator e Sincronizador TOTAL Google (Drive Completo + Gmail Completo)
Descarrega TODAS as pastas/ficheiros da Google Drive e TODOS os emails/anexos do Gmail.
"""

import os
import re
import sys
import json
import base64
import hashlib
import argparse
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Configuração de Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [TOTAL-INGEST] - %(levelname)s - %(message)s"
)
logger = logging.getLogger("total_ingest")

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/gmail.readonly"
]


def load_env_file(env_path: Path) -> Dict[str, str]:
    """Lê variáveis do ficheiro .env."""
    env_vars = {}
    if not env_path.exists():
        return env_vars
    with open(env_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env_vars[k.strip()] = v.strip().strip('"').strip("'")
            os.environ[k.strip()] = v.strip().strip('"').strip("'")
    return env_vars


def sanitize_filename(name: str) -> str:
    """Remove caracteres inválidos para nomes de ficheiros no Windows."""
    clean = re.sub(r'[\\/*?:"<>|]', "_", name)
    clean = re.sub(r'\s+', '_', clean.strip())
    return clean[:120]


def get_file_hash(filepath: Path) -> str:
    """Calcula o hash SHA-256 de um ficheiro local."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


class GoogleTotalIngestor:
    def __init__(self, base_output_dir: Path, env_path: Optional[Path] = None):
        self.base_output_dir = Path(base_output_dir)
        self.gdrive_dir = self.base_output_dir / "gdrive_completo"
        self.gmail_dir = self.base_output_dir / "gmail_completo"
        self.index_dir = self.base_output_dir / "_index"

        for d in [self.gdrive_dir, self.gmail_dir, self.index_dir]:
            d.mkdir(parents=True, exist_ok=True)

        package_dir = Path(__file__).resolve().parent
        self.env_path = env_path or (package_dir / ".env")
        self.env_vars = load_env_file(self.env_path)

        self.credentials_path = package_dir / "config" / "credentials.json"
        self.token_path = package_dir / "config" / "token.json"
        self.creds = None
        self.drive_service = None
        self.gmail_service = None

    def authenticate(self) -> bool:
        """Autentica via Tokens do .env, API Key, token.json ou OAuth."""
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
        except ImportError:
            logger.error("❌ Bibliotecas da Google não instaladas!")
            logger.info("Instale com: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
            return False

        # 1. Tentar autenticar com GOOGLE_ACCESS_TOKEN e REFRESH_TOKEN do .env
        access_token = self.env_vars.get("GOOGLE_ACCESS_TOKEN") or os.environ.get("GOOGLE_ACCESS_TOKEN")
        refresh_token = self.env_vars.get("GOOGLE_REFRESH_TOKEN") or os.environ.get("GOOGLE_REFRESH_TOKEN")

        if access_token:
            logger.info("🔑 A inicializar com Tokens do .env...")
            try:
                self.creds = Credentials(
                    token=access_token,
                    refresh_token=refresh_token,
                    token_uri="https://oauth2.googleapis.com/token",
                    scopes=SCOPES
                )
                self.drive_service = build("drive", "v3", credentials=self.creds)
                self.gmail_service = build("gmail", "v1", credentials=self.creds)
                logger.info("✅ Conectado com sucesso ao Google Drive e Gmail via Token!")
                return True
            except Exception as e:
                logger.warning(f"Aviso ao inicializar credenciais: {e}")

        # 2. Tentar token.json existente
        if self.token_path.exists():
            try:
                self.creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)
                self.drive_service = build("drive", "v3", credentials=self.creds)
                self.gmail_service = build("gmail", "v1", credentials=self.creds)
                logger.info("✅ Autenticado via token.json!")
                return True
            except Exception as e:
                logger.warning(f"Erro no token.json: {e}")

        # 3. Fallback para credentials.json (OAuth)
        if self.credentials_path.exists():
            try:
                from google_auth_oauthlib.flow import InstalledAppFlow
                flow = InstalledAppFlow.from_client_secrets_file(str(self.credentials_path), SCOPES)
                self.creds = flow.run_local_server(port=0)
                with open(self.token_path, "w") as token:
                    token.write(self.creds.to_json())
                self.drive_service = build("drive", "v3", credentials=self.creds)
                self.gmail_service = build("gmail", "v1", credentials=self.creds)
                logger.info("✅ Autenticado via OAuth!")
                return True
            except Exception as e:
                logger.error(f"Erro OAuth: {e}")

        # 4. Fallback para GOOGLE_API_KEY (Apenas Drive público)
        api_key = self.env_vars.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if api_key and not api_key.startswith("AIzaSyA_SUA_CHAVE"):
            logger.info("🔑 A utilizar GOOGLE_API_KEY do .env...")
            try:
                self.drive_service = build("drive", "v3", developerKey=api_key)
                logger.info("✅ Conectado ao Google Drive via API Key!")
                return True
            except Exception as e:
                logger.warning(f"Erro API Key: {e}")

        logger.error("❌ Nenhuma credencial válida encontrada.")
        return False

    # =========================================================================
    # EXTRAÇÃO TOTAL DA GOOGLE DRIVE
    # =========================================================================
    def sync_all_drive(self) -> List[Dict[str, Any]]:
        """Varre e descarrega TODA a Google Drive a partir da raiz."""
        if not self.drive_service:
            logger.error("Drive service indisponível.")
            return []

        logger.info("🚀 A INICIAR EXTRAÇÃO TOTAL DO GOOGLE DRIVE...")
        results = []
        try:
            self._download_drive_folder_recursive("root", self.gdrive_dir, results)
        except Exception as e:
            logger.error(f"Erro durante extração total da Drive: {e}")
        logger.info(f"✅ Extração do Drive concluída! Total de ficheiros: {len(results)}")
        return results

    def _download_drive_folder_recursive(self, folder_id: str, current_dir: Path, results: List[Dict[str, Any]]):
        from googleapiclient.http import MediaIoBaseDownload
        import io

        current_dir.mkdir(parents=True, exist_ok=True)
        page_token = None

        while True:
            query = f"'{folder_id}' in parents and trashed = false"
            res = self.drive_service.files().list(
                q=query,
                pageSize=100,
                pageToken=page_token,
                fields="nextPageToken, files(id, name, mimeType, size, modifiedTime)"
            ).execute()

            items = res.get("files", [])
            for item in items:
                item_id = item["id"]
                item_name = item["name"]
                mime_type = item["mimeType"]

                if mime_type == "application/vnd.google-apps.folder":
                    sub_dir = current_dir / sanitize_filename(item_name)
                    logger.info(f"📁 Entrando na pasta: {sub_dir.relative_to(self.gdrive_dir)}")
                    self._download_drive_folder_recursive(item_id, sub_dir, results)
                else:
                    safe_name = sanitize_filename(item_name)
                    file_path = current_dir / safe_name

                    try:
                        if mime_type == "application/vnd.google-apps.document":
                            safe_name = f"{Path(safe_name).stem}.pdf"
                            file_path = current_dir / safe_name
                            request = self.drive_service.files().export_media(fileId=item_id, mimeType="application/pdf")
                        elif mime_type == "application/vnd.google-apps.spreadsheet":
                            safe_name = f"{Path(safe_name).stem}.xlsx"
                            file_path = current_dir / safe_name
                            request = self.drive_service.files().export_media(
                                fileId=item_id,
                                mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                        elif mime_type == "application/vnd.google-apps.presentation":
                            safe_name = f"{Path(safe_name).stem}.pdf"
                            file_path = current_dir / safe_name
                            request = self.drive_service.files().export_media(fileId=item_id, mimeType="application/pdf")
                        else:
                            request = self.drive_service.files().get_media(fileId=item_id)

                        # Evita descarregar novamente se o ficheiro já existir localmente
                        if not file_path.exists():
                            logger.info(f"  ⬇️ A descarregar ficheiro: {safe_name}")
                            fh = io.FileIO(str(file_path), "wb")
                            downloader = MediaIoBaseDownload(fh, request)
                            done = False
                            while not done:
                                status, done = downloader.next_chunk()
                        else:
                            logger.info(f"  ⚡ Já existe localmente: {safe_name}")

                        sha256 = get_file_hash(file_path)
                        results.append({
                            "id": item_id,
                            "name": safe_name,
                            "path": str(file_path),
                            "size_bytes": file_path.stat().st_size,
                            "sha256": sha256,
                            "modified": item.get("modifiedTime", "")
                        })
                    except Exception as e:
                        logger.error(f"  ❌ Erro ao transferir '{item_name}': {e}")

            page_token = res.get("nextPageToken")
            if not page_token:
                break

    # =========================================================================
    # EXTRAÇÃO TOTAL DO GMAIL (TODAS AS LABELS E EMAILS)
    # =========================================================================
    def sync_all_gmail(self) -> List[Dict[str, Any]]:
        """Varre e descarrega TODOS os emails e anexos de todas as labels."""
        if not self.gmail_service:
            logger.warning("Gmail service não disponível. A ignorar Gmail.")
            return []

        logger.info("🚀 A INICIAR EXTRAÇÃO TOTAL DO GMAIL...")
        results = []
        try:
            # Obter todas as labels da conta
            labels_res = self.gmail_service.users().labels().list(userId="me").execute()
            user_labels = labels_res.get("labels", [])
            logger.info(f"📋 Encontradas {len(user_labels)} labels no Gmail.")

            for lbl in user_labels:
                lbl_name = lbl["name"]
                # Ignorar categorias automáticas spam/trash
                if lbl_name in ["SPAM", "TRASH", "DRAFT", "CHAT"]:
                    continue

                safe_label = sanitize_filename(lbl_name)
                lbl_dir = self.gmail_dir / safe_label
                lbl_dir.mkdir(parents=True, exist_ok=True)

                query = f'label:"{lbl_name}"'
                page_token = None
                logger.info(f"📥 A extrair emails da label: '{lbl_name}'")

                while True:
                    res = self.gmail_service.users().messages().list(
                        userId="me", q=query, pageToken=page_token, maxResults=100
                    ).execute()
                    messages = res.get("messages", [])

                    for msg_ref in messages:
                        msg_id = msg_ref["id"]
                        try:
                            msg = self.gmail_service.users().messages().get(
                                userId="me", id=msg_id, format="full"
                            ).execute()

                            payload = msg.get("payload", {})
                            headers = {h["name"].lower(): h["value"] for h in payload.get("headers", [])}
                            subject = headers.get("subject", "Sem_Assunto")
                            sender = headers.get("from", "Desconhecido")
                            date_str = headers.get("date", "")

                            safe_subject = sanitize_filename(subject)
                            email_folder = lbl_dir / f"{msg_id}_{safe_subject[:40]}"
                            email_folder.mkdir(parents=True, exist_ok=True)

                            body_content = self._extract_body(payload)
                            email_meta = {
                                "id": msg_id,
                                "label": lbl_name,
                                "subject": subject,
                                "from": sender,
                                "date": date_str,
                                "attachments": []
                            }

                            email_md_path = email_folder / "email_body.md"
                            if not email_md_path.exists():
                                with open(email_md_path, "w", encoding="utf-8") as f:
                                    f.write(f"# {subject}\n\n")
                                    f.write(f"- **De:** {sender}\n")
                                    f.write(f"- **Data:** {date_str}\n")
                                    f.write(f"- **Label:** {lbl_name}\n")
                                    f.write(f"- **ID:** {msg_id}\n\n---\n\n")
                                    f.write(body_content)

                            self._download_attachments(msg_id, payload, email_folder, email_meta)
                            results.append(email_meta)
                        except Exception as em_err:
                            logger.error(f"Erro no email ID {msg_id}: {em_err}")

                    page_token = res.get("nextPageToken")
                    if not page_token:
                        break

        except Exception as e:
            logger.error(f"Erro na extração do Gmail: {e}")

        logger.info(f"✅ Extração do Gmail concluída! Total de emails processados: {len(results)}")
        return results

    def _extract_body(self, payload: Dict[str, Any]) -> str:
        body = ""
        if "parts" in payload:
            for part in payload["parts"]:
                mime_type = part.get("mimeType", "")
                if mime_type == "text/plain" and "data" in part.get("body", {}):
                    return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
                elif mime_type == "text/html" and "data" in part.get("body", {}):
                    body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
        elif "body" in payload and "data" in payload["body"]:
            body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")
        return body

    def _download_attachments(self, msg_id: str, payload: Dict[str, Any], email_folder: Path, email_meta: Dict[str, Any]):
        if "parts" not in payload:
            return

        for part in payload["parts"]:
            filename = part.get("filename")
            if filename and "attachmentId" in part.get("body", {}):
                att_id = part["body"]["attachmentId"]
                safe_name = sanitize_filename(filename)
                file_path = email_folder / safe_name

                if not file_path.exists():
                    try:
                        att = self.gmail_service.users().messages().attachments().get(
                            userId="me", messageId=msg_id, id=att_id
                        ).execute()

                        file_data = base64.urlsafe_b64decode(att["data"])
                        with open(file_path, "wb") as f:
                            f.write(file_data)
                        logger.info(f"    📎 Anexo guardado: {safe_name}")
                    except Exception as e:
                        logger.error(f"    ❌ Erro anexo {safe_name}: {e}")

                if file_path.exists():
                    sha256 = get_file_hash(file_path)
                    email_meta["attachments"].append({
                        "filename": safe_name,
                        "path": str(file_path),
                        "size_bytes": file_path.stat().st_size,
                        "sha256": sha256
                    })

            if "parts" in part:
                self._download_attachments(msg_id, part, email_folder, email_meta)

    def generate_manifest(self, drive_data: List[Any], gmail_data: List[Any]):
        """Gera o manifesto JSON consolidado de toda a sincronização."""
        manifest_path = self.index_dir / "FULL_GOOGLE_INGEST_MANIFEST.json"
        manifest = {
            "total_drive_files": len(drive_data),
            "total_gmail_emails": len(gmail_data),
            "drive_files": drive_data,
            "gmail_emails": gmail_data
        }
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        logger.info(f"📄 Manifesto Total de Ingestão guardado em: {manifest_path}")


def main():
    package_dir = Path(__file__).resolve().parent
    default_out = package_dir / "data" / "raw"

    parser = argparse.ArgumentParser(description="Extração e Sincronização TOTAL Google (Drive + Gmail)")
    parser.add_argument("--output", "-o", default=str(default_out),
                        help="Diretório de destino local para os ficheiros")
    parser.add_argument("--skip-drive", action="store_true", help="Não extrair Google Drive")
    parser.add_argument("--skip-gmail", action="store_true", help="Não extrair Gmail")

    args = parser.parse_args()

    ingestor = GoogleTotalIngestor(base_output_dir=Path(args.output))

    if not ingestor.authenticate():
        sys.exit(1)

    drive_results = []
    if not args.skip_drive:
        drive_results = ingestor.sync_all_drive()

    gmail_results = []
    if not args.skip_gmail:
        gmail_results = ingestor.sync_all_gmail()

    ingestor.generate_manifest(drive_results, gmail_results)
    logger.info("🎉 EXTRAÇÃO TOTAL CONCLUÍDA COM SUCESSO!")


if __name__ == "__main__":
    main()
