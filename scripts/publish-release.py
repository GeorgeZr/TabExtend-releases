"""Publish validated attachments, resuming drafts without replacing a release."""
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

spec = importlib.util.spec_from_file_location("verify_package", Path(__file__).with_name("verify-package.py"))
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)
tag = sys.argv[1]
metadata = validator.verify(tag)
repository = os.environ.get("GITHUB_REPOSITORY", "GeorgeZr/TabExtend-releases")
if repository != "GeorgeZr/TabExtend-releases":
    raise ValueError("Unexpected release repository")


def gh(*args):
    return subprocess.check_output(["gh", *args], text=True, stderr=subprocess.PIPE)


def api_or_none(endpoint):
    try:
        return json.loads(gh("api", endpoint))
    except subprocess.CalledProcessError as error:
        if "HTTP 404" in error.stderr:
            return None
        raise


archive = metadata["archive"]
endpoint = f"repos/{repository}/releases"
release = api_or_none(f"{endpoint}/tags/{tag}")
if release and not release["draft"]:
    assets = {asset["name"]: asset for asset in release["assets"]}
    if assets.get(archive, {}).get("digest") != f"sha256:{metadata['sha256']}" or f"{archive}.sha256" not in assets:
        raise ValueError("Published release differs from this package; create a new version instead")
    print(f"Already published: {release['html_url']}")
else:
    notes = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "tabextend-release-notes.md"
    notes.write_text(f"""下载 **`{archive}`** 并解压，然后在 `chrome://extensions` 开启开发者模式，选择「加载已解压的扩展程序」。选中直接包含 `manifest.json` 的目录。

更新时将新版文件替换到原安装目录，再点击扩展的重新加载按钮。建议先导出备份，无需卸载旧扩展。

请下载上述 ZIP 附件，GitHub 自动生成的 `Source code` 附件不是安装包。

[详细安装说明](https://github.com/{repository}#安装)

SHA-256: `{metadata['sha256']}`
""")
    if release is None:
        gh("release", "create", tag, "--repo", repository, "--verify-tag", "--draft", "--title", f"TabExtend {tag}", "--notes-file", str(notes))
    gh("release", "upload", tag, str(Path(".release") / archive), str(Path(".release") / f"{archive}.sha256"), "--repo", repository, "--clobber")
    latest = api_or_none(f"{endpoint}/latest")
    current_version = tuple(map(int, metadata["version"].split(".")))
    previous_tag = latest["tag_name"] if latest else "v0.0.0"
    if not re.fullmatch(r"v\d+\.\d+\.\d+", previous_tag):
        raise ValueError("Cannot compare latest release version")
    is_latest = current_version >= tuple(map(int, previous_tag[1:].split(".")))
    gh("release", "edit", tag, "--repo", repository, "--draft=false", f"--latest={str(is_latest).lower()}", "--notes-file", str(notes))
    print(f"Published: https://github.com/{repository}/releases/tag/{tag}")
