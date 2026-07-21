import logging
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError
from urllib.parse import quote
import ssl
import certifi

from app.classes.web.base_api_handler import BaseApiHandler

logger = logging.getLogger(__name__)

MODRINTH_API = "https://api.modrinth.com/v2"
USER_AGENT = "CraftyController/4.0"

PROJECT_TYPE_MAP = {
    "mod": "mod",
    "plugin": "plugin",
    "datapack": "datapack",
    "shader": "shader",
    "resourcepack": "resourcepack",
    "modpack": "modpack",
}


def _fetch_json(url, ssl_context):
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, context=ssl_context, timeout=15) as resp:
        return json.loads(resp.read().decode())


class ApiServersServerModsSearchHandler(BaseApiHandler):
    def get(self, server_id: str):
        auth_data = self.authenticate_user()
        if not auth_data:
            return

        if server_id not in [str(x["server_id"]) for x in auth_data[0]]:
            return self.finish_json(
                400,
                {
                    "status": "error",
                    "error": "NOT_AUTHORIZED",
                },
            )

        query = self.get_query_argument("query", "").strip()
        mod_type = self.get_query_argument("type", "mod")
        version = self.get_query_argument("version", "").strip()

        if not query:
            return self.finish_json(200, {"status": "ok", "data": []})

        project_type = PROJECT_TYPE_MAP.get(mod_type, "mod")

        facets = [[f"project_type:{project_type}"]]
        if version:
            facets.append([f"versions:{version}"])

        facets_json = quote(json.dumps(facets), safe="")
        encoded_query = quote(query, safe="")

        url = (
            f"{MODRINTH_API}/search?query={encoded_query}"
            f"&facets={facets_json}"
            f"&limit=25&index=relevance"
        )

        try:
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            data = _fetch_json(url, ssl_context)

            results = []
            for hit in data.get("hits", []):
                results.append(
                    {
                        "slug": hit.get("slug"),
                        "project_id": hit.get("project_id"),
                        "title": hit.get("title"),
                        "description": hit.get("description"),
                        "author": hit.get("author"),
                        "icon_url": hit.get("icon_url"),
                        "project_type": hit.get("project_type"),
                        "downloads": hit.get("downloads"),
                        "follows": hit.get("follows"),
                        "latest_version": hit.get("latest_version"),
                        "versions": hit.get("versions", []),
                        "categories": hit.get("categories", []),
                        "display_categories": hit.get("display_categories", []),
                        "date_created": hit.get("date_created"),
                        "date_modified": hit.get("date_modified"),
                        "license": hit.get("license"),
                        "client_side": hit.get("client_side"),
                        "server_side": hit.get("server_side"),
                        "color": hit.get("color"),
                    }
                )

            return self.finish_json(200, {"status": "ok", "data": results})

        except URLError as e:
            logger.error(f"Modrinth search error: {e}")
            return self.finish_json(
                502,
                {
                    "status": "error",
                    "error": "UPSTREAM_ERROR",
                    "error_data": "Cannot connect to Modrinth API",
                },
            )


class ApiServersServerModsProjectHandler(BaseApiHandler):
    def get(self, server_id: str, project_slug: str):
        auth_data = self.authenticate_user()
        if not auth_data:
            return

        if server_id not in [str(x["server_id"]) for x in auth_data[0]]:
            return self.finish_json(
                400,
                {
                    "status": "error",
                    "error": "NOT_AUTHORIZED",
                },
            )

        ssl_context = ssl.create_default_context(cafile=certifi.where())

        try:
            project_url = (
                f"{MODRINTH_API}/project/{quote(project_slug, safe='')}"
            )
            project = _fetch_json(project_url, ssl_context)

            versions_url = (
                f"{MODRINTH_API}/project/{quote(project_slug, safe='')}/version"
            )
            versions_raw = _fetch_json(versions_url, ssl_context)

            versions = []
            for v in versions_raw:
                versions.append(
                    {
                        "id": v.get("id"),
                        "version_number": v.get("version_number"),
                        "game_versions": v.get("game_versions", []),
                        "loaders": v.get("loaders", []),
                        "date_published": v.get("date_published"),
                        "downloads": v.get("downloads"),
                        "changelog": v.get("changelog", ""),
                        "files": [
                            {
                                "url": f.get("url"),
                                "filename": f.get("filename"),
                                "size": f.get("size"),
                            }
                            for f in v.get("files", [])
                        ],
                    }
                )

            gallery = []
            for g in project.get("gallery", []):
                gallery.append(
                    {
                        "url": g.get("url"),
                        "raw_url": g.get("raw_url"),
                        "description": g.get("description", ""),
                    }
                )

            return self.finish_json(
                200,
                {
                    "status": "ok",
                    "data": {
                        "slug": project.get("slug"),
                        "project_id": project.get("project_id"),
                        "title": project.get("title"),
                        "description": project.get("description"),
                        "body": project.get("body", ""),
                        "author": project.get("author"),
                        "icon_url": project.get("icon_url"),
                        "project_type": project.get("project_type"),
                        "downloads": project.get("downloads"),
                        "follows": project.get("follows"),
                        "categories": project.get("categories", []),
                        "display_categories": project.get("display_categories", []),
                        "versions": project.get("versions", []),
                        "game_versions": project.get("game_versions", []),
                        "loaders": project.get("loaders", []),
                        "license": project.get("license", {}),
                        "date_created": project.get("date_created"),
                        "date_modified": project.get("date_modified"),
                        "client_side": project.get("client_side"),
                        "server_side": project.get("server_side"),
                        "issues_url": project.get("issues_url"),
                        "source_url": project.get("source_url"),
                        "wiki_url": project.get("wiki_url"),
                        "discord_url": project.get("discord_url"),
                        "donation_urls": project.get("donation_urls", []),
                        "gallery": gallery,
                        "color": project.get("color"),
                        "version_list": versions,
                    },
                },
            )

        except URLError as e:
            logger.error(f"Modrinth project error: {e}")
            return self.finish_json(
                502,
                {
                    "status": "error",
                    "error": "UPSTREAM_ERROR",
                    "error_data": "Cannot connect to Modrinth API",
                },
            )


class ApiServersServerModsInstallHandler(BaseApiHandler):
    def post(self, server_id: str):
        auth_data = self.authenticate_user()
        if not auth_data:
            return

        if server_id not in [str(x["server_id"]) for x in auth_data[0]]:
            return self.finish_json(
                400,
                {
                    "status": "error",
                    "error": "NOT_AUTHORIZED",
                },
            )

        try:
            data = json.loads(self.request.body)
        except json.decoder.JSONDecodeError as e:
            return self.finish_json(
                400,
                {"status": "error", "error": "INVALID_JSON", "error_data": str(e)},
            )

        project_id = data.get("project_id") or data.get("slug")
        version_id = data.get("version_id", "")
        mod_type = data.get("type", "mod")

        if not project_id:
            return self.finish_json(
                400,
                {"status": "error", "error": "MISSING_PROJECT_ID"},
            )

        try:
            server_path = self.controller.servers.get_server_data_by_id(server_id)["path"]

            if mod_type == "plugin":
                target_dir = Path(server_path, "plugins")
            else:
                target_dir = Path(server_path, "mods")

            os.makedirs(target_dir, exist_ok=True)

            ssl_context = ssl.create_default_context(cafile=certifi.where())

            SERVER_LOADERS = {
                "plugin": ["paper", "spigot", "purpur", "bukkit", "folia", "pufferfish"],
                "mod": ["fabric", "forge", "quilt", "neoforge"],
            }

            if version_id:
                versions_url = (
                    f"{MODRINTH_API}/project/{quote(project_id, safe='')}"
                    f"/version/{quote(version_id, safe='')}"
                )
                version_data = _fetch_json(versions_url, ssl_context)
            else:
                versions_url = (
                    f"{MODRINTH_API}/project/{quote(project_id, safe='')}/version"
                )
                versions = _fetch_json(versions_url, ssl_context)
                if not versions:
                    return self.finish_json(
                        404,
                        {"status": "error", "error": "NO_VERSIONS"},
                    )
                compatible = SERVER_LOADERS.get(mod_type, [])
                matched = [v for v in versions if
                    any(l in [x.lower() for x in v.get("loaders", [])] for l in compatible)]
                if matched:
                    version_data = matched[0]
                else:
                    version_data = versions[0]

            files = version_data.get("files", [])
            if not files:
                return self.finish_json(
                    404,
                    {"status": "error", "error": "NO_FILES"},
                )

            file_info = files[0]
            download_url = file_info.get("url")
            filename = file_info.get("filename", f"{project_id}.jar")

            if not download_url:
                return self.finish_json(
                    404,
                    {"status": "error", "error": "NO_DOWNLOAD_URL"},
                )

            out_file = Path(target_dir, filename)

            dl_req = Request(download_url, headers={"User-Agent": USER_AGENT})
            with urlopen(dl_req, context=ssl_context, timeout=120) as resp:
                with open(out_file, "wb") as f:
                    while True:
                        chunk = resp.read(1024 * 1024)
                        if not chunk:
                            break
                        f.write(chunk)

            return self.finish_json(
                200,
                {
                    "status": "ok",
                    "data": {
                        "filename": filename,
                        "path": str(out_file),
                        "version_number": version_data.get("version_number", ""),
                        "game_versions": version_data.get("game_versions", []),
                        "loaders": version_data.get("loaders", []),
                    },
                },
            )

        except URLError as e:
            logger.error(f"Modrinth download error: {e}")
            return self.finish_json(
                502,
                {
                    "status": "error",
                    "error": "DOWNLOAD_FAILED",
                    "error_data": f"Download failed: {e}",
                },
            )
        except json.decoder.JSONDecodeError as e:
            logger.error(f"Modrinth API returned invalid JSON: {e}")
            return self.finish_json(
                502,
                {
                    "status": "error",
                    "error": "UPSTREAM_ERROR",
                    "error_data": "Modrinth API returned invalid response",
                },
            )
        except Exception as e:
            logger.error(f"Modrinth install error: {e}")
            return self.finish_json(
                500,
                {
                    "status": "error",
                    "error": "INSTALL_ERROR",
                    "error_data": str(e),
                },
            )
