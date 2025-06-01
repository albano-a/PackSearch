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
        try:
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

            results = run_search(extension.backend, query)
            if not results:
                items.append(
                    ExtensionResultItem(
                        name="No packages found",
                        description=f"No packages matching '{query}'",
                        on_enter=None
                    )
                )
            else:
                for name, desc in results:
                    items.append(
                        ExtensionResultItem(name=name, description=desc, on_enter=None)
                    )

        except Exception as e:
            items = [
                ExtensionResultItem(
                    name="Extension Error",
                    description=f"Error: {str(e)}",
                    on_enter=None
                )
            ]

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

    try:
        proc = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )
    except subprocess.CalledProcessError:
        return []  # Return empty list if command fails
    
    lines = proc.stdout.splitlines()
    results = []

    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue
            
        # For pacman/yay output format: "repo/package-name version"
        if tool in ["pacman", "yay"] and "/" in line and not line.startswith(" "):
            parts = line.split()
            if len(parts) >= 1:
                package_info = parts[0].split("/")
                if len(package_info) == 2:
                    name = package_info[1]
                    # Get description from next line if it starts with spaces
                    desc = parts[1] if len(parts) > 1 else "No description"
                    results.append((name, desc))
        
        # For pamac output format (adjust based on actual pamac output)
        elif tool == "pamac" and not line.startswith(" "):
            parts = line.split()
            if len(parts) >= 1:
                name = parts[0]
                desc = " ".join(parts[1:]) if len(parts) > 1 else "No description"
                results.append((name, desc))

    return results[:10]  # Limit to 10 results


if __name__ == "__main__":
    PackageSearchExtension().run()
