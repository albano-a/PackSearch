from ulauncher.api.client.EventListener import EventListener # type: ignore
from ulauncher.api.client.Extension import Extension # type: ignore
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction  # type: ignore
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem # type: ignore
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction # type: ignore
from ulauncher.api.shared.event import KeywordQueryEvent # type: ignore
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction # type: ignore


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
                for package_name, repo, desc in results:
                    # Create install command based on backend
                    if extension.backend == "pacman":
                        install_cmd = f"sudo pacman -S {package_name}"
                    elif extension.backend == "pamac":
                        install_cmd = f"pamac install {package_name}"
                    elif extension.backend == "yay":
                        install_cmd = f"yay -S {package_name}"
                    
                    # Create terminal command to open terminal and run install command
                    terminal_cmd = f"gnome-terminal -- bash -c '{install_cmd}; echo \"Press Enter to close...\"; read'"
                    
                    items.append(
                        ExtensionResultItem(
                            name=f"[{repo}] {package_name}",
                            description=f"{desc} (Press Enter to install)",
                            on_enter=RunScriptAction(terminal_cmd)
                        )
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
    results = []
    
    if tool == "pacman":
        cmd = ["pacman", "-Ss", query]
        results = _parse_pacman_output(cmd, query)
        
    elif tool == "pamac":
        cmd = ["pamac", "search", query]
        results = _parse_pamac_output(cmd, query)
        
    elif tool == "yay":
        # First search official repos
        cmd = ["yay", "-Ss", query, "--repo"]
        results = _parse_pacman_output(cmd, query)
        
        # If we have less than 5 results, also search AUR
        if len(results) < 5:
            cmd_aur = ["yay", "-Ss", query, "--aur"]
            aur_results = _parse_pacman_output(cmd_aur, query)
            results.extend(aur_results)
    else:
        raise ValueError("Unsupported backend")

    # Sort by priority and return top 10
    results.sort(key=lambda x: x[0], reverse=True)
    return [(name, repo, desc) for priority, name, repo, desc in results[:10]]


def _parse_pacman_output(cmd, query):
    try:
        proc = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10
        )
    except Exception:
        return []
    
    lines = proc.stdout.splitlines()
    results = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            i += 1
            continue
            
        if "/" in line and not line.startswith(" "):
            parts = line.split()
            if len(parts) >= 1:
                package_info = parts[0].split("/")
                if len(package_info) == 2:
                    repo = package_info[0]
                    name = package_info[1]
                    
                    desc = "No description"
                    if i + 1 < len(lines) and lines[i + 1].startswith("    "):
                        desc = lines[i + 1].strip()
                        i += 1
                    
                    priority = _calculate_priority(name, repo, query)
                    results.append((priority, name, repo, desc))
        
        i += 1
    
    return results


def _parse_pamac_output(cmd, query):
    try:
        proc = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10
        )
    except Exception:
        return []
    
    lines = proc.stdout.splitlines()
    results = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if "(" in line and ")" in line:
            repo_start = line.rfind("(")
            repo_end = line.rfind(")")
            if repo_start != -1 and repo_end != -1 and repo_end > repo_start:
                repo = line[repo_start + 1:repo_end]
                package_part = line[:repo_start].strip()
                parts = package_part.split()
                if len(parts) >= 1:
                    name = parts[0]
                    desc = " ".join(parts[1:]) if len(parts) > 1 else "No description"
                    priority = _calculate_priority(name, repo, query)
                    results.append((priority, name, repo, desc))
    
    return results


def _calculate_priority(name, repo, query):
    priority = 0
    
    # Exact match gets highest priority
    if name.lower() == query.lower():
        priority = 1000
    # Package name starts with query
    elif name.lower().startswith(query.lower()):
        priority = 750
    # Query is in package name
    elif query.lower() in name.lower():
        priority = 500
    
    # Boost official repos
    if repo in ["core", "extra", "community", "multilib"]:
        priority += 100
    
    return priority


if __name__ == "__main__":
    PackageSearchExtension().run()
