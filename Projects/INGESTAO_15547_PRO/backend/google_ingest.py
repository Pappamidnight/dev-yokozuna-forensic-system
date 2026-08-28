#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
google_ingest.py - Módulo de Ingestão e Sincronização Google (Gmail + Google Drive)
Descarrega e reorganiza localmente processos, anexos e provas do tribunal.
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
from typing import Any, Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [GOOGLE-INGEST] - %(levelname)s - %(message)s"
)
logger = logging.getLogger("google_ingest")

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
]

DEFAULT_GMAIL_LABELS = [
    "3719/25.0T8LSB",
    "ANALISTA",
    "CENTENARIO",
    "Finpartner"
]

DEFAULT_GDRIVE_FOLDERS = [
    "1 TRIBUNAL",
    "MAPA PROVAS",
    "SPARK 2926",
    "02 Assuntos Jurídicos Críticos: Foco total na documentação",
    "01 Negócio/Projeto Principal: Estrutura, Processos, Ferramen",
    "_KB"
]


def sanitize_filename(name: str) -> str:
    clean = re.sub(r'[\\/*?:"<>|]', "_", name)
    clean = re.sub(r'\s+', '_', clean.strip())
    return clean[:120]


def get_file_hash(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


class GoogleIngestor:
    def __init__(self, base_output_dir: Path, credentials_path: Optional[Path] = None):
        self.base_output_dir = Path(base_output_dir)
        self.gmail_dir = self.base_output_dir / "gmail"
        self.gdrive_dir = self.base_output_dir / "gdrive"
        self.index_dir = self.base_output_dir / "_index"

        for d in [self.gmail_dir, self.gdrive_dir, self.index_dir]:
            d.mkdir(parents=True, exist_ok=True)

        self.credentials_path = credentials_path or (self.base_output_dir.parent / "config" / "credentials.json")
        self.token_path = self.base_output_dir.parent / "config" / "token.json"
        self.creds = None
        self.gmail_service = None
        self.drive_service = None

    def authenticate(self) -> bool:
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
        except ImportError:
            logger.error("❌ Bibliotecas da Google não instaladas!")
            logger.info("Por favor instale: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
            return False

        if self.token_path.exists():
            try:
                self.creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)
            except Exception as e:
                logger.warning(f"Erro ao carregar token existente: {e}")

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    logger.info("🔄 A atualizar token expirado...")
                    self.creds.refresh(Request())
                except Exception as e:
                    logger.warning(f"Falha ao renovar token: {e}")
                    self.creds = None

            if not self.creds:
                if not self.credentials_path.exists():
                    logger.error(f"❌ Ficheiro de credenciais não encontrado em: {self.credentials_path}")
                    logger.info("📋 Como obter em 2 passos:")
                    logger.info("1. Aceda a https://console.cloud.google.com/apis/credentials")
                    logger.info("2. Crie um 'OAuth Client ID' (Desktop App), descarregue o JSON e guarde como:")
                    logger.info(f"   {self.credentials_path}")
                    return False

                logger.info("🌐 A abrir navegador para autorização Google OAuth...")
                flow = InstalledAppFlow.from_client_secrets_file(str(self.credentials_path), SCOPES)
                self.creds = flow.run_local_server(port=0)

            self.token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.token_path, "w") as token:
                token.write(self.creds.to_json())
            logger.info(f"✅ Token guardado com sucesso em: {self.token_path}")

        try:
            self.gmail_service = build("gmail", "v1", credentials=self.creds)
            self.drive_service = build("drive", "v3", credentials=self.creds)
            logger.info("✅ Autenticação Google API concluída com sucesso.")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar serviços Google: {e}")
            return False

    def ingest_gmail_label(self, label_name: str) -> List[Dict[str, Any]]:
        if not self.gmail_service:
            logger.error("Gmail service não autenticado.")
            return []

        logger.info(f"📥 A processar label do Gmail: {label_name}")
        results = []
        safe_label = sanitize_filename(label_name)
        target_dir = self.gmail_dir / safe_label
        target_dir.mkdir(parents=True, exist_ok=True)

        query = f'label:"{label_name}"'
        try:
            response = self.gmail_service.users().messages().list(userId="me", q=query).execute()
            messages = response.get("messages", [])

            while "nextPageToken" in response:
                page_token = response["nextPageToken"]
                response = self.gmail_service.users().messages().list(userId="me", q=query, pageToken=page_token).execute()
                messages.extend(response.get("messages", []))

            logger.info(f"Encontradas {len(messages)} mensagens para a label '{label_name}'.")

            for msg_summary in messages:
                msg_id = msg_summary["id"]
                msg = self.gmail_service.users().messages().get(userId="me", id=msg_id, format="full").execute()
                
                payload = msg.get("payload", {})
                headers = {h["name"].lower(): h["value"] for h in payload.get("headers", [])}
                subject = headers.get("subject", "Sem_Assunto")
                sender = headers.get("from", "Desconhecido")
                date_str = headers.get("date", "")
                
                safe_subject = sanitize_filename(subject)
                email_folder = target_dir / f"{msg_id}_{safe_subject[:40]}"
                email_folder.mkdir(parents=True, exist_ok=True)

                body_content = self._extract_body(payload)
                email_meta = {
                    "id": msg_id,
                    "label": label_name,
                    "subject": subject,
                    "from": sender,
                    "date": date_str,
                    "attachments": []
                }

                email_md_path = email_folder / "email_body.md"
                with open(email_md_path, "w", encoding="utf-8") as f:
                    f.write(f"# {subject}\n\n")
                    f.write(f"- **De:** {sender}\n")
                    f.write(f"- **Data:** {date_str}\n")
                    f.write(f"- **Label:** {label_name}\n")
                    f.write(f"- **ID:** {msg_id}\n\n---\n\n")
                    f.write(body_content)

                self._download_attachments(msg_id, payload, email_folder, email_meta)
                results.append(email_meta)

        except Exception as e:
            logger.error(f"Erro ao processar label '{label_name}': {e}")

        return results

    def _extract_body(self, payload: Dict[str, Any]) -> str:
        body = ""
        if "parts" in payload:
            for part in payload["parts"]:
                mime_type = part.get("mimeType", "")
                if mime_type == "text/plain" and "data" in part.get("body", {}):
                    data = part["body"]["data"]
                    return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
                elif mime_type == "text/html" and "data" in part.get("body", {}):
                    data = part["body"]["data"]
                    body = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        elif "body" in payload and "data" in payload["body"]:
            data = payload["body"]["data"]
            body = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        return body

    def _download_attachments(self, msg_id: str, payload: Dict[str, Any], email_folder: Path, email_meta: Dict[str, Any]):
        if "parts" not in payload:
            return

        for part in payload["parts"]:
            filename = part.get("filename")
            if filename and "attachmentId" in part.get("body", {}):
                att_id = part["body"]["attachmentId"]
                att = self.gmail_service.users().messages().attachments().get(
                    userId="me", messageId=msg_id, id=att_id
                ).execute()

                file_data = base64.urlsafe_b64decode(att["data"])
                safe_name = sanitize_filename(filename)
                file_path = email_folder / safe_name

                with open(file_path, "wb") as f:
                    f.write(file_data)

                sha256 = get_file_hash(file_path)
                logger.info(f"  📎 Anexo guardado: {safe_name} ({len(file_data)} bytes)")
                email_meta["attachments"].append({
                    "filename": safe_name,
                    "path": str(file_path),
                    "size_bytes": len(file_data),
                    "sha256": sha256
                })

            if "parts" in part:
                self._download_attachments(msg_id, part, email_folder, email_meta)

    def ingest_gdrive_folder(self, folder_name: str) -> List[Dict[str, Any]]:
        if not self.drive_service:
            logger.error("Drive service não autenticado.")
            return []

        logger.info(f"📂 A pesquisar pasta no Google Drive: {folder_name}")
        results = []
        try:
            query = f"mimeType = 'application/vnd.google-apps.folder' and name = '{folder_name}' and trashed = false"
            res = self.drive_service.files().list(q=query, fields="files(id, name)").execute()
            folders = res.get("files", [])

            if not folders:
                logger.warning(f"Pasta '{folder_name}' não encontrada no Google Drive.")
                return []

            folder_id = folders[0]["id"]
            safe_folder_name = sanitize_filename(folder_name)
            target_dir = self.gdrive_dir / safe_folder_name
            target_dir.mkdir(parents=True, exist_ok=True)

            self._download_drive_children(folder_id, target_dir, results)

        except Exception as e:
            logger.error(f"Erro ao processar pasta Drive '{folder_name}': {e}")

        return results

    def _download_drive_children(self, parent_id: str, current_dir: Path, results: List[Dict[str, Any]]):
        from googleapiclient.http import MediaIoBaseDownload
        import io

        query = f"'{parent_id}' in parents and trashed = false"
        res = self.drive_service.files().list(q=query, fields="files(id, name, mimeType, size)").execute()
        items = res.get("files", [])

        for item in items:
            item_id = item["id"]
            item_name = item["name"]
            mime_type = item["mimeType"]

            if mime_type == "application/vnd.google-apps.folder":
                sub_dir = current_dir / sanitize_filename(item_name)
                sub_dir.mkdir(parents=True, exist_ok=True)
                self._download_drive_children(item_id, sub_dir, results)
            else:
                safe_name = sanitize_filename(item_name)
                file_path = current_dir / safe_name

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
                else:
                    request = self.drive_service.files().get_media(fileId=item_id)

                logger.info(f"  ⬇️ A descarregar da Drive: {safe_name}")
                fh = io.FileIO(str(file_path), "wb")
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()

                sha256 = get_file_hash(file_path)
                results.append({
                    "id": item_id,
                    "name": safe_name,
                    "path": str(file_path),
                    "size_bytes": file_path.stat().st_size,
                    "sha256": sha256
                })

    def generate_manifest(self, gmail_data: List[Any], drive_data: List[Any]):
        manifest_path = self.index_dir / "GOOGLE_INGEST_MANIFEST.json"
        manifest = {
            "total_emails_processed": len(gmail_data),
            "total_drive_files_downloaded": len(drive_data),
            "gmail_records": gmail_data,
            "drive_records": drive_data
        }
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        logger.info(f"📄 Manifesto de ingestão gerado em: {manifest_path}")


def main():
    parser = argparse.ArgumentParser(description="Ingestão de Dados Google (Gmail & Google Drive)")
    parser.add_argument("--output", "-o", default=r"C:\Users\Yokozuna\Dev\Projects\INGESTAO_15547_PRO\raw\google_ingest",
                        help="Diretório de destino para os ficheiros descarregados")
    parser.add_argument("--credentials", "-c", default=None,
                        help="Caminho para o ficheiro credentials.json do Google Cloud")
    parser.add_argument("--labels", nargs="+", default=DEFAULT_GMAIL_LABELS,
                        help="Lista de labels do Gmail para descarregar")
    parser.add_argument("--folders", nargs="+", default=DEFAULT_GDRIVE_FOLDERS,
                        help="Lista de pastas do Google Drive para descarregar")
    parser.add_argument("--skip-gmail", action="store_true", help="Ignorar Gmail")
    parser.add_argument("--skip-drive", action="store_true", help="Ignorar Google Drive")

    args = parser.parse_args()

    ingestor = GoogleIngestor(
        base_output_dir=Path(args.output),
        credentials_path=Path(args.credentials) if args.credentials else None
    )

    if not ingestor.authenticate():
        sys.exit(1)

    gmail_results = []
    if not args.skip_gmail:
        for lbl in args.labels:
            res = ingestor.ingest_gmail_label(lbl)
            gmail_results.extend(res)

    drive_results = []
    if not args.skip_drive:
        for folder in args.folders:
            res = ingestor.ingest_gdrive_folder(folder)
            drive_results.extend(res)

    ingestor.generate_manifest(gmail_results, drive_results)
    logger.info("🎉 Ingestão Google concluída com sucesso!")


if __name__ == "__main__":
    main()
