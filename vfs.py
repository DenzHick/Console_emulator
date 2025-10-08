import csv
import base64
import stat

class VFSNode:
    """базовый узел в vfs (файл или папка)"""

    def __init__(self, name, permissions=0o755):
        self.name = name
        self.parent = None
        self.permissions = permissions # добавляем права


class VFSFile(VFSNode):
    """узел-файл"""

    def __init__(self, name, content="", permissions=0o644):
        super().__init__(name, permissions)
        self.content = content

    def __repr__(self):
        return f"File('{self.name}')"


class VFSDirectory(VFSNode):
    """узел-папка"""

    def __init__(self, name, permissions=0o755):
        super().__init__(name, permissions)
        self.children = {}  # {'имя': VFSNode}

    def add_child(self, node):
        node.parent = self
        self.children[node.name] = node

    def __repr__(self):
        return f"Dir('{self.name}')"


class VFS:
    """обертка для управления vfs"""
    def __init__(self):
        self.vfs_root = VFSDirectory('/')
        self.current_dir = self.vfs_root

    def load_vfs(self, vfs_path):
        """загружает vfs из csv файла в память"""
        self.vfs_root = VFSDirectory('/')
        self.current_dir = self.vfs_root

        try:
            with open(vfs_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # пропускаем заголовок
                for row in reader:
                    path_str, type, content, permissions_str = row
                    permissions = int(permissions_str, 8) if permissions_str else (0o755 if type == 'dir' else 0o644)
                    path_parts = [part for part in path_str.split('/') if part]

                    node = self.vfs_root
                    for part in path_parts[:-1]:
                        if part not in node.children:
                            new_dir = VFSDirectory(part)
                            node.add_child(new_dir)
                        node = node.children[part]

                    name = path_parts[-1]
                    if type == 'dir':
                        if name not in node.children:
                            new_node = VFSDirectory(name, permissions)
                            node.add_child(new_node)
                    elif type == 'file':
                        decoded_content = base64.b64decode(content).decode('utf-8')
                        new_node = VFSFile(name, decoded_content, permissions)
                        node.add_child(new_node)

        except FileNotFoundError:
            print(f"warning: vfs file '{vfs_path}' not found. Using empty VFS.")
        except Exception as e:
            print(f"error loading vfs: {e}")

    def get_node_from_path(self, path):
        """находит узел по абсолютному или относительному пути"""
        if not path:
            return self.current_dir

        if path.startswith('/'):
            start_node = self.vfs_root
            path_parts = [part for part in path.split('/') if part]
        else:
            start_node = self.current_dir
            path_parts = [part for part in path.split('/') if part]

        node = start_node
        for part in path_parts:
            if part == '.':
                continue
            if part == '..':
                if node.parent:
                    node = node.parent
                continue
            if isinstance(node, VFSDirectory) and part in node.children:
                node = node.children[part]
            else:
                return None
        return node

    def get_current_path(self):
        """возвращает строковое представление текущего пути в vfs"""
        if self.current_dir == self.vfs_root:
            return "/"

        path = []
        node = self.current_dir
        while node.parent:
            path.append(node.name)
            node = node.parent
        return '/' + '/'.join(reversed(path))
