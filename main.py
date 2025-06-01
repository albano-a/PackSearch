from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.model import ExtensionResultItem, RenderResultListAction
from ulauncher.api.shared.event import KeywordQueryEvent

import subprocess
import shutil


class PackageSearchExtension(Extension):
    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.backend = self.detect_backend()

    def detect_backend(self):
        for cmd in ["yay", "pamac", "pacman"]:
            if shutil.which(cmd):
                return cmd
        return None


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        query = event.get_argument()
        items = []

        if not query:
            return RenderResultListAction(
                [
                    ExtensionResultItem(
                        name="Enter a package name to search",
                        description="e.g., pack neovim",
                        on_enter=None,
                    )
                ]
            )

        if not extension.backend:
            return RenderResultListAction(
                [
                    ExtensionResultItem(
                        name="No supported package manager found",
                        description="Install yay, pamac or pacman",
                        on_enter=None,
                    )
                ]
            )

        try:
            results = run_search(extension.backend, query)
            for name, desc in results:
                items.append(
                    ExtensionResultItem(name=name, description=desc, on_enter=None)
                )
        except Exception as e:
            items.append(
                ExtensionResultItem(name="Error", description=str(e), on_enter=None)
            )

        return RenderResultListAction(items)


def run_search(tool, query):
    if tool == "pacman":
        cmd = ["pacman", "-Ss", query]
    elif tool == "pamac":
        cmd = ["pamac", "search", query]
    elif tool == "yay":
        cmd = ["yay", "-Ss", query]
    else:
        raise ValueError("Unsupported backend")

    proc = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=True
    )
    lines = proc.stdout.splitlines()

    results = []
    name = ""
    desc = ""

    for line in lines:
        if line.startswith(tool):
            parts = line.split("/", 1)[-1].split(" ", 1)
            name = parts[0].strip()
            desc = parts[1].strip() if len(parts) > 1 else ""
            results.append((name, desc))

    return results[:10]  # Limit to 10 results


if __name__ == "__main__":
    PackageSearchExtension().run()
