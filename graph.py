"""
graph.py
========
KHUNG DUNG CHUNG CHO CA NHOM
"""

from collections import defaultdict, deque
import heapq


class Graph:
    def __init__(self, directed: bool = False):
        self.directed = directed
        self.adj = defaultdict(list)
        self.nodes = set()

    # ------------------------------------------------------------------
    # NGUOI 1: Input & bieu dien do thi
    # ------------------------------------------------------------------
    def add_edge(self, u, v, weight: float = 1):
        self.nodes.add(u)
        self.nodes.add(v)
        self.adj[u].append((v, weight))
        if not self.directed:
            self.adj[v].append((u, weight))

    @staticmethod
    def _merge_symmetric(edges):
        """
        Voi do thi VO HUONG: neu nguoi dung liet ke ca (u, v) lan (v, u) (cung trong so)
        thi chi giu lai 1 canh, tranh them canh 2 lan (lam bac cac dinh tang gap doi).
        Canh lap lai cung chieu (u, v), (u, v) van duoc coi la 2 canh song song.
        """
        pending = defaultdict(int)
        merged = []
        for e in edges:
            u, v = e[0], e[1]
            w = e[2] if len(e) == 3 else 1
            if u != v and pending[(v, u, w)] > 0:
                pending[(v, u, w)] -= 1
                continue
            pending[(u, v, w)] += 1
            merged.append(e)
        return merged

    @classmethod
    def from_edge_list(cls, edges, directed: bool = False):
        g = cls(directed=directed)
        for e in edges:
            if len(e) == 2:
                u, v = e
                g.add_edge(u, v)
            else:
                u, v, w = e
                g.add_edge(u, v, w)
        return g

    @classmethod
    def from_adjacency_list(cls, adjacency: dict, directed: bool = False):
        """
        Xay dung do thi truc tiep tu danh sach ke.
        adjacency: {u: [v1, v2, ...]} hoac {u: [(v1, w1), (v2, w2), ...]}
        Voi do thi vo huong, moi canh chi can khai bao 1 chieu (add_edge tu lo them chieu con lai).
        """
        g = cls(directed=directed)
        for u in adjacency:
            g.nodes.add(u)
        edges = []
        for u, neighbors in adjacency.items():
            for item in neighbors:
                if isinstance(item, (tuple, list)):
                    v, w = item
                else:
                    v, w = item, 1
                edges.append((u, v, w))
        if not directed:
            edges = cls._merge_symmetric(edges)
        for u, v, w in edges:
            g.add_edge(u, v, w)
        return g

    @classmethod
    def from_adjacency_matrix(cls, matrix, node_labels=None, directed: bool = False):
        """
        Xay dung do thi truc tiep tu ma tran ke.
        matrix[i][j] != 0 nghia la co canh tu node_labels[i] den node_labels[j], trong so = matrix[i][j].
        Neu khong truyen node_labels, mac dinh danh so 0..n-1.
        """
        n = len(matrix)
        if node_labels is None:
            node_labels = list(range(n))
        if len(node_labels) != n:
            raise ValueError("So luong nhan dinh (node_labels) phai bang kich thuoc ma tran")

        g = cls(directed=directed)
        for label in node_labels:
            g.nodes.add(label)

        if directed:
            for i in range(n):
                for j in range(n):
                    if matrix[i][j]:
                        g.add_edge(node_labels[i], node_labels[j], matrix[i][j])
        else:
            # Chi duyet nua tren cua ma tran de tranh them canh 2 lan
            for i in range(n):
                for j in range(i, n):
                    if matrix[i][j]:
                        g.add_edge(node_labels[i], node_labels[j], matrix[i][j])
        return g

    @classmethod
    def from_file(cls, filepath: str, directed: bool = None):
        edges = []
        with open(filepath, "r", encoding="utf-8") as f:
            for line_number, raw_line in enumerate(f, start=1):
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                if len(parts) == 2:
                    u, v = parts
                    edges.append((u, v))
                elif len(parts) == 3:
                    u, v, w = parts
                    try:
                        w = float(w)
                        if w.is_integer():
                            w = int(w)
                    except ValueError:
                        raise ValueError(f"Dong {line_number} co trong so khong hop le: '{w}'")
                    edges.append((u, v, w))
                else:
                    raise ValueError(f"Dong {line_number} sai dinh dang: '{line}'")
        
        if directed is None:
            directed = cls._detect_directed(edges)
        if not directed:
            edges = cls._merge_symmetric(edges)
        return cls.from_edge_list(edges, directed=directed)

    @classmethod
    def _detect_directed(cls, edges):
        edge_set = set()
        for e in edges:
            if len(e) == 2:
                u, v = e
                edge_set.add((u, v))
            else:
                u, v, w = e
                edge_set.add((u, v))
        
        for u, v in edge_set:
            if (v, u) not in edge_set:
                return True
        return False

    def to_adjacency_matrix(self):
        list_nodes = sorted(self.nodes, key=lambda x: str(x))
        index = {node: i for i, node in enumerate(list_nodes)}
        n = len(list_nodes)
        matrix = [[0] * n for _ in range(n)]
        for u in self.adj:
            for (v, w) in self.adj[u]:
                i, j = index[u], index[v]
                matrix[i][j] = w
        return list_nodes, matrix

    def to_edge_list(self):
        edges = []
        seen = set()
        for u in self.adj:
            for (v, w) in self.adj[u]:
                if self.directed:
                    edges.append((u, v, w))
                else:
                    key = frozenset((u, v)) if u != v else (u, v)
                    pair_id = (key, w)
                    if pair_id in seen:
                        continue
                    seen.add(pair_id)
                    edges.append((u, v, w))
        return edges

    def draw(self, save_path: str = "graph.png"):
        try:
            import networkx as nx
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import matplotlib.patheffects as pe
        except ImportError:
            print("Loi: Thieu thu vien networkx hoac matplotlib!")
            print("Vui long cai dat: pip install networkx matplotlib")
            return None

        G = nx.DiGraph() if self.directed else nx.Graph()
        for node in self.nodes:
            G.add_node(node)
        for (u, v, w) in self.to_edge_list():
            G.add_edge(u, v, weight=w)

        n_nodes = max(len(G.nodes), 1)
        # Kich thuoc hinh tu dong co dan theo so dinh, toi thieu 10x8
        side = max(10, 1.1 * (n_nodes ** 0.5) + 6)
        fig, ax = plt.subplots(figsize=(side, side * 0.82))
        fig.patch.set_facecolor('#f4f6fb')
        ax.set_facecolor('#f4f6fb')

        try:
            pos = nx.spring_layout(G, seed=42, k=2.2 / (n_nodes ** 0.5), iterations=200)
        except Exception:
            pos = nx.spring_layout(G, seed=42)

        # To mau node theo bac (degree): bac cao hon -> mau dam hon, tao chieu sau truc quan
        degrees = dict(G.degree())
        max_deg = max(degrees.values()) if degrees else 1
        cmap = plt.cm.get_cmap('viridis')
        node_colors = [cmap(0.25 + 0.65 * (degrees[n] / max_deg if max_deg else 0)) for n in G.nodes]
        node_sizes = [900 + 250 * degrees[n] / max_deg if max_deg else 900 for n in G.nodes]

        # Bong mo nhe duoi node de tao chieu sau
        nx.draw_networkx_nodes(
            G, pos, ax=ax, node_color='#00000022', node_size=node_sizes,
            linewidths=0
        )
        nodes_artist = nx.draw_networkx_nodes(
            G, pos, ax=ax, node_color=node_colors, node_size=node_sizes,
            edgecolors='white', linewidths=2.2
        )
        nodes_artist.set_zorder(3)

        if self.directed:
            nx.draw_networkx_edges(
                G, pos, ax=ax, edge_color='#7a8291', arrows=True,
                arrowstyle='-|>', arrowsize=18, width=1.8,
                connectionstyle='arc3,rad=0.08', node_size=node_sizes,
                alpha=0.85
            )
        else:
            nx.draw_networkx_edges(
                G, pos, ax=ax, edge_color='#7a8291', width=1.8, alpha=0.85
            )

        labels = nx.draw_networkx_labels(
            G, pos, ax=ax, font_size=12, font_weight='bold', font_color='white'
        )
        for txt in labels.values():
            txt.set_path_effects([pe.withStroke(linewidth=2.5, foreground='#2b2b3d')])
            txt.set_zorder(4)

        edge_labels = nx.get_edge_attributes(G, 'weight')
        if edge_labels:
            nx.draw_networkx_edge_labels(
                G, pos, ax=ax, edge_labels=edge_labels, font_size=10,
                font_color='#333333',
                bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#cccccc', alpha=0.9)
            )

        ax.set_title(
            f"{'Do thi co huong' if self.directed else 'Do thi vo huong'}"
            f"  ({n_nodes} dinh, {len(G.edges)} canh)",
            fontsize=15, fontweight='bold', color='#2b2b3d', pad=14
        )
        ax.axis('off')

        try:
            plt.savefig(save_path, dpi=180, bbox_inches='tight', facecolor=fig.get_facecolor())
            plt.close(fig)
            print(f"Da luu hinh do thi vao: {save_path}")
            return save_path
        except Exception as e:
            print(f"Loi khi luu hinh: {e}")
            plt.close(fig)
            return None

    # ------------------------------------------------------------------
    # Cac ham dung chung de ve do thi nen + highlight ket qua thuat toan
    # ------------------------------------------------------------------
    def _build_nx_and_pos(self):
        import networkx as nx
        G = nx.DiGraph() if self.directed else nx.Graph()
        for node in self.nodes:
            G.add_node(node)
        for (u, v, w) in self.to_edge_list():
            G.add_edge(u, v, weight=w)
        n_nodes = max(len(G.nodes), 1)
        try:
            pos = nx.spring_layout(G, seed=42, k=2.2 / (n_nodes ** 0.5), iterations=200)
        except Exception:
            pos = nx.spring_layout(G, seed=42)
        return G, pos

    def _new_figure(self, n_nodes):
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        side = max(10, 1.1 * (max(n_nodes, 1) ** 0.5) + 6)
        fig, ax = plt.subplots(figsize=(side, side * 0.82))
        fig.patch.set_facecolor('#f4f6fb')
        ax.set_facecolor('#f4f6fb')
        return plt, fig, ax

    def _draw_base_graph(self, G, pos, ax, highlight_edges=None, dim_non_highlighted=True):
        """Ve node + tat ca canh nen (mau xam), highlight_edges se duoc ve de ('#e74c3c') o buoc sau."""
        import networkx as nx
        import matplotlib.patheffects as pe

        nx.draw_networkx_nodes(
            G, pos, ax=ax, node_color='#00000022', node_size=950, linewidths=0
        )
        nodes_artist = nx.draw_networkx_nodes(
            G, pos, ax=ax, node_color='#4c6ef5', node_size=950,
            edgecolors='white', linewidths=2.2
        )
        nodes_artist.set_zorder(3)

        highlight_set = set()
        if highlight_edges:
            for e in highlight_edges:
                u, v = e[0], e[1]
                highlight_set.add((u, v))
                if not self.directed:
                    highlight_set.add((v, u))

        base_edges = [(u, v) for u, v in G.edges() if (u, v) not in highlight_set]
        edge_alpha = 0.35 if (highlight_edges and dim_non_highlighted) else 0.85
        if self.directed:
            nx.draw_networkx_edges(
                G, pos, ax=ax, edgelist=base_edges, edge_color='#9aa1ad', arrows=True,
                arrowstyle='-|>', arrowsize=16, width=1.5,
                connectionstyle='arc3,rad=0.08', node_size=950, alpha=edge_alpha
            )
        else:
            nx.draw_networkx_edges(
                G, pos, ax=ax, edgelist=base_edges, edge_color='#9aa1ad', width=1.5, alpha=edge_alpha
            )

        labels = nx.draw_networkx_labels(
            G, pos, ax=ax, font_size=12, font_weight='bold', font_color='white'
        )
        for txt in labels.values():
            txt.set_path_effects([pe.withStroke(linewidth=2.5, foreground='#2b2b3d')])
            txt.set_zorder(4)

    def draw_mst(self, mst_edges, algo_name="MST", save_path="mst.png"):
        """
        Ve do thi goc voi cac canh thuoc cay khung nho nhat (MST) duoc to dam mau do.
        mst_edges: list (u, v, w) tra ve tu prim()/kruskal()
        """
        try:
            import networkx as nx
        except ImportError:
            print("Loi: Thieu thu vien networkx hoac matplotlib!")
            return None
        if not mst_edges:
            print("Khong co MST de ve (do thi khong lien thong hoac rong).")
            return None

        G, pos = self._build_nx_and_pos()
        plt, fig, ax = self._new_figure(len(G.nodes))

        self._draw_base_graph(G, pos, ax, highlight_edges=mst_edges)

        nx.draw_networkx_edges(
            G, pos, ax=ax, edgelist=[(u, v) for u, v, w in mst_edges],
            edge_color='#e74c3c', width=3.2, alpha=0.95
        )
        edge_labels = {(u, v): w for u, v, w in mst_edges}
        nx.draw_networkx_edge_labels(
            G, pos, ax=ax, edge_labels=edge_labels, font_size=10, font_color='#c0392b',
            bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#e74c3c', alpha=0.9)
        )

        total = sum(w for u, v, w in mst_edges)
        ax.set_title(f"{algo_name}: Cay khung nho nhat (tong trong so = {total})",
                      fontsize=15, fontweight='bold', color='#2b2b3d', pad=14)
        ax.axis('off')

        plt.savefig(save_path, dpi=180, bbox_inches='tight', facecolor=fig.get_facecolor())
        plt.close(fig)
        print(f"Da luu hinh {algo_name} vao: {save_path}")
        return save_path

    def draw_euler_path(self, path, algo_name="Euler", save_path="euler.png"):
        """
        Ve do thi goc va danh so thu tu cac canh theo duong di/chu trinh Euler.
        path: danh sach dinh theo thu tu di qua, vd [A, B, C, A]
        """
        try:
            import networkx as nx
        except ImportError:
            print("Loi: Thieu thu vien networkx hoac matplotlib!")
            return None
        if not path or len(path) < 2:
            print("Khong co duong di Euler de ve.")
            return None

        seq_edges = list(zip(path[:-1], path[1:]))
        G, pos = self._build_nx_and_pos()
        plt, fig, ax = self._new_figure(len(G.nodes))

        self._draw_base_graph(G, pos, ax, highlight_edges=seq_edges)

        import matplotlib.cm as cm
        n_steps = len(seq_edges)
        cmap = cm.get_cmap('autumn')
        for i, (u, v) in enumerate(seq_edges):
            color = cmap(i / max(n_steps - 1, 1))
            if self.directed:
                nx.draw_networkx_edges(
                    G, pos, ax=ax, edgelist=[(u, v)], edge_color=[color], width=3.0,
                    arrows=True, arrowstyle='-|>', arrowsize=18,
                    connectionstyle='arc3,rad=0.08', node_size=950
                )
            else:
                nx.draw_networkx_edges(
                    G, pos, ax=ax, edgelist=[(u, v)], edge_color=[color], width=3.0
                )
            # Nhan so thu tu buoc di tai trung diem canh
            mx, my = (pos[u][0] + pos[v][0]) / 2, (pos[u][1] + pos[v][1]) / 2
            ax.text(mx, my, str(i + 1), fontsize=9, fontweight='bold', color='#7a3e00',
                    ha='center', va='center', zorder=5,
                    bbox=dict(boxstyle='circle,pad=0.15', fc='#fff3cd', ec='#e0a800', alpha=0.95))

        ax.set_title(f"{algo_name}: Duong di Euler ({n_steps} canh, danh so thu tu di qua)",
                      fontsize=15, fontweight='bold', color='#2b2b3d', pad=14)
        ax.axis('off')

        plt.savefig(save_path, dpi=180, bbox_inches='tight', facecolor=fig.get_facecolor())
        plt.close(fig)
        print(f"Da luu hinh {algo_name} vao: {save_path}")
        return save_path

    def draw_shortest_path(self, path, algo_name="Dijkstra", distance=None, save_path="shortest_path.png"):
        """
        Ve do thi goc, tô đậm màu xanh duong di ngan nhat tim duoc.
        path: danh sach dinh theo thu tu di qua, vd [S, A, D, T]
        distance: tong khoang cach/chi phi cua duong di (chi de hien thi tren tieu de)
        """
        try:
            import networkx as nx
        except ImportError:
            print("Loi: Thieu thu vien networkx hoac matplotlib!")
            return None
        if not path or len(path) < 2:
            print("Khong co duong di de ve.")
            return None

        seq_edges = list(zip(path[:-1], path[1:]))
        G, pos = self._build_nx_and_pos()
        plt, fig, ax = self._new_figure(len(G.nodes))

        self._draw_base_graph(G, pos, ax, highlight_edges=seq_edges)

        if self.directed:
            nx.draw_networkx_edges(
                G, pos, ax=ax, edgelist=seq_edges, edge_color='#1565c0', width=3.5,
                arrows=True, arrowstyle='-|>', arrowsize=18,
                connectionstyle='arc3,rad=0.08', node_size=950
            )
        else:
            nx.draw_networkx_edges(
                G, pos, ax=ax, edgelist=seq_edges, edge_color='#1565c0', width=3.5
            )

        weight_of = {(u, v): w for u, v, w in self.to_edge_list()}
        if not self.directed:
            for (u, v), w in list(weight_of.items()):
                weight_of[(v, u)] = w
        edge_labels = {(u, v): weight_of.get((u, v), '') for (u, v) in seq_edges}
        nx.draw_networkx_edge_labels(
            G, pos, ax=ax, edge_labels=edge_labels, font_size=10, font_color='#0d47a1',
            bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#1565c0', alpha=0.9)
        )

        # To mau rieng cho diem dau/cuoi
        start_node, end_node = path[0], path[-1]
        nx.draw_networkx_nodes(G, pos, ax=ax, nodelist=[start_node], node_color='#2e7d32',
                                node_size=1050, edgecolors='white', linewidths=2.5).set_zorder(4)
        nx.draw_networkx_nodes(G, pos, ax=ax, nodelist=[end_node], node_color='#c62828',
                                node_size=1050, edgecolors='white', linewidths=2.5).set_zorder(4)
        for txt in nx.draw_networkx_labels(G, pos, ax=ax, labels={start_node: start_node, end_node: end_node},
                                            font_size=12, font_weight='bold', font_color='white').values():
            txt.set_zorder(5)

        title = f"{algo_name}: Duong di ngan nhat tu {start_node} den {end_node}"
        if distance is not None:
            title += f" (tong = {distance})"
        ax.set_title(title, fontsize=14, fontweight='bold', color='#2b2b3d', pad=14)
        ax.axis('off')

        plt.savefig(save_path, dpi=180, bbox_inches='tight', facecolor=fig.get_facecolor())
        plt.close(fig)
        print(f"Da luu hinh {algo_name} vao: {save_path}")
        return save_path

    def draw_maxflow(self, flow_edges, source, sink, max_flow, save_path="maxflow.png"):
        """
        Ve do thi goc va hien thi flow/capacity tren moi canh: vd '7/10'.
        flow_edges: dict {(u, v): flow_value} - luong thuc te di qua canh (u, v) trong ket qua cuoi.
        """
        try:
            import networkx as nx
        except ImportError:
            print("Loi: Thieu thu vien networkx hoac matplotlib!")
            return None

        G, pos = self._build_nx_and_pos()
        plt, fig, ax = self._new_figure(len(G.nodes))

        used_edges = [(u, v) for (u, v), f in flow_edges.items() if f > 0]
        self._draw_base_graph(G, pos, ax, highlight_edges=used_edges)

        nx.draw_networkx_edges(
            G, pos, ax=ax, edgelist=used_edges, edge_color='#2e7d32', width=3.0,
            arrows=self.directed, arrowstyle='-|>', arrowsize=18,
            connectionstyle='arc3,rad=0.08', node_size=950
        )

        capacity = {(u, v): w for u, v, w in self.to_edge_list()}
        edge_labels = {}
        for (u, v) in G.edges():
            cap = capacity.get((u, v), 0)
            flow = flow_edges.get((u, v), 0)
            edge_labels[(u, v)] = f"{flow}/{cap}"
        nx.draw_networkx_edge_labels(
            G, pos, ax=ax, edge_labels=edge_labels, font_size=9, font_color='#1b5e20',
            bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#2e7d32', alpha=0.9)
        )

        # To mau rieng cho source/sink
        nx.draw_networkx_nodes(G, pos, ax=ax, nodelist=[source], node_color='#f39c12',
                                node_size=1050, edgecolors='white', linewidths=2.5).set_zorder(4)
        nx.draw_networkx_nodes(G, pos, ax=ax, nodelist=[sink], node_color='#8e44ad',
                                node_size=1050, edgecolors='white', linewidths=2.5).set_zorder(4)
        for txt in nx.draw_networkx_labels(G, pos, ax=ax, labels={source: source, sink: sink},
                                            font_size=12, font_weight='bold', font_color='white').values():
            txt.set_zorder(5)

        ax.set_title(f"Ford-Fulkerson: Luong cuc dai tu {source} den {sink} = {max_flow}\n"
                      f"(nhan canh: luong/tai trong)",
                      fontsize=14, fontweight='bold', color='#2b2b3d', pad=14)
        ax.axis('off')

        plt.savefig(save_path, dpi=180, bbox_inches='tight', facecolor=fig.get_facecolor())
        plt.close(fig)
        print(f"Da luu hinh Max Flow vao: {save_path}")
        return save_path

    # ------------------------------------------------------------------
    # NGUOI 2: BFS, DFS, Bipartite
    # ------------------------------------------------------------------
    def bfs(self, start):
        if start not in self.nodes:
            raise ValueError(f"Dinh '{start}' khong ton tai")
        visited = {start}
        order = []
        queue = deque([start])
        while queue:
            u = queue.popleft()
            order.append(u)
            for v, _w in self.adj[u]:
                if v not in visited:
                    visited.add(v)
                    queue.append(v)
        return order

    def dfs(self, start):
        if start not in self.nodes:
            raise ValueError(f"Dinh '{start}' khong ton tai")
        visited = set()
        order = []
        stack = [start]
        while stack:
            u = stack.pop()
            if u in visited:
                continue
            visited.add(u)
            order.append(u)
            for v, _w in reversed(self.adj[u]):
                if v not in visited:
                    stack.append(v)
        return order

    def is_bipartite(self):
        # Bipartite duoc dinh nghia tren tinh lien thong VO HUONG cua do thi.
        # Voi do thi co huong, phai gop ca canh vao (in-edge) va canh ra (out-edge)
        # thi moi duyet dung cac thanh phan lien thong - neu chi dung self.adj (out-edge)
        # se bo sot canh "nguoc" va suy ra ket qua sai.
        undirected_adj = defaultdict(set)
        for u in self.adj:
            for v, _w in self.adj[u]:
                undirected_adj[u].add(v)
                undirected_adj[v].add(u)

        color = {}
        for source in sorted(self.nodes, key=lambda x: str(x)):
            if source in color:
                continue
            color[source] = 0
            queue = deque([source])
            while queue:
                u = queue.popleft()
                for v in undirected_adj[u]:
                    if v not in color:
                        color[v] = 1 - color[u]
                        queue.append(v)
                    elif color[v] == color[u]:
                        return False, None
        set_a = {n for n, c in color.items() if c == 0}
        set_b = {n for n, c in color.items() if c == 1}
        return True, (set_a, set_b)

    # ------------------------------------------------------------------
    # NGUOI 3: Dijkstra, Bellman-Ford, Fleury, Hierholzer
    # ------------------------------------------------------------------
    def dijkstra(self, start, end=None):
        if start not in self.nodes:
            raise ValueError(f"Dinh '{start}' khong ton tai")
        if end is not None and end not in self.nodes:
            raise ValueError(f"Dinh '{end}' khong ton tai")
        dist = {node: float("inf") for node in self.nodes}
        prev = {node: None for node in self.nodes}
        dist[start] = 0
        visited = set()
        heap = [(0, start)]
        while heap:
            d, u = heapq.heappop(heap)
            if u in visited:
                continue
            visited.add(u)
            for v, w in self.adj[u]:
                if w < 0:
                    raise ValueError("Dijkstra khong xu ly trong so am")
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(heap, (nd, v))
        if end is None:
            return dist
        if dist[end] == float("inf"):
            return {"distance": float("inf"), "path": []}
        path = []
        node = end
        while node is not None:
            path.append(node)
            node = prev[node]
        path.reverse()
        return {"distance": dist[end], "path": path}

    def bellman_ford(self, start, end=None):
        if start not in self.nodes:
            raise ValueError(f"Dinh '{start}' khong ton tai")
        if end is not None and end not in self.nodes:
            raise ValueError(f"Dinh '{end}' khong ton tai")
        dist = {node: float("inf") for node in self.nodes}
        prev = {node: None for node in self.nodes}
        dist[start] = 0
        edges = []
        for u in self.adj:
            for v, w in self.adj[u]:
                edges.append((u, v, w))
        n = len(self.nodes)
        for _ in range(max(n - 1, 0)):
            updated = False
            for u, v, w in edges:
                if dist[u] != float("inf") and dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    prev[v] = u
                    updated = True
            if not updated:
                break
        for u, v, w in edges:
            if dist[u] != float("inf") and dist[u] + w < dist[v]:
                raise ValueError("Do thi co chu trinh am")
        if end is None:
            return dist
        if dist[end] == float("inf"):
            return {"distance": float("inf"), "path": []}
        path = []
        node = end
        while node is not None:
            path.append(node)
            node = prev[node]
        path.reverse()
        return {"distance": dist[end], "path": path}

    def fleury(self):
        """
        Tim duong di/chu trinh Euler bang thuat toan Fleury.
        Ho tro ca do thi vo huong va co huong (dong bo voi hierholzer()).
        Nguyen tac: tai moi buoc, uu tien di qua canh KHONG PHAI cau (bridge) -
        tuc la canh ma neu bo di se lam giam so dinh con lai co the tiep can duoc
        tu dinh hien tai (voi do thi co huong, "tiep can duoc" tinh theo chieu canh).
        """
        if not self.nodes:
            return []

        if self.directed:
            out_deg = {node: 0 for node in self.nodes}
            in_deg = {node: 0 for node in self.nodes}
            for u in self.adj:
                for v, w in self.adj[u]:
                    out_deg[u] += 1
                    in_deg[v] += 1

            start_candidates = [n for n in self.nodes if out_deg[n] - in_deg[n] == 1]
            end_candidates = [n for n in self.nodes if in_deg[n] - out_deg[n] == 1]
            for n in self.nodes:
                diff = out_deg[n] - in_deg[n]
                if diff not in (0, 1, -1):
                    return None

            if start_candidates or end_candidates:
                if len(start_candidates) == 1 and len(end_candidates) == 1:
                    start = start_candidates[0]
                else:
                    return None
            else:
                start = next((n for n in self.nodes if out_deg[n] > 0), next(iter(self.nodes)))

            edges = []
            out_edge_ids_of = defaultdict(list)
            for u in self.adj:
                for v, w in self.adj[u]:
                    idx = len(edges)
                    edges.append([u, v, w, True])
                    out_edge_ids_of[u].append(idx)

            def other_end(idx, node):
                # co huong: chi di theo dung chieu u -> v
                return edges[idx][1]

            def active_edges(node):
                return [idx for idx in out_edge_ids_of[node] if edges[idx][3]]

            def count_reachable(node):
                visited = {node}
                stack = [node]
                while stack:
                    cur = stack.pop()
                    for idx in active_edges(cur):
                        nxt = other_end(idx, cur)
                        if nxt not in visited:
                            visited.add(nxt)
                            stack.append(nxt)
                return len(visited)

        else:
            degree = {node: len(self.adj[node]) for node in self.nodes}
            odd_nodes = [node for node, d in degree.items() if d % 2 != 0]

            if len(odd_nodes) not in (0, 2):
                return None

            if odd_nodes:
                start = odd_nodes[0]
            else:
                start = next((n for n in self.nodes if degree[n] > 0), next(iter(self.nodes)))

            edges = []
            edge_ids_of = defaultdict(list)
            seen = set()

            for u in self.adj:
                for v, w in self.adj[u]:
                    if (v, u, w) in seen:
                        continue
                    seen.add((u, v, w))
                    idx = len(edges)
                    edges.append([u, v, w, True])
                    edge_ids_of[u].append(idx)
                    edge_ids_of[v].append(idx)

            def other_end(idx, node):
                u, v, w, active = edges[idx]
                return v if u == node else u

            def active_edges(node):
                return [idx for idx in edge_ids_of[node] if edges[idx][3]]

            def count_reachable(node):
                visited = {node}
                stack = [node]
                while stack:
                    cur = stack.pop()
                    for idx in active_edges(cur):
                        nxt = other_end(idx, cur)
                        if nxt not in visited:
                            visited.add(nxt)
                            stack.append(nxt)
                return len(visited)

        def reachable_from(node):
            visited = {node}
            stack = [node]
            while stack:
                cur = stack.pop()
                for idx in active_edges(cur):
                    nxt = other_end(idx, cur)
                    if nxt not in visited:
                        visited.add(nxt)
                        stack.append(nxt)
            return visited

        def is_bridge(idx, node):
            if self.directed:
                # Co huong: sau khi di qua canh idx (node -> nxt), moi canh con lai phai
                # van tiep can duoc tu nxt; neu co canh bi "bo roi" thi canh idx la cau.
                nxt = other_end(idx, node)
                edges[idx][3] = False
                reach = reachable_from(nxt)
                stranded = any(e[3] and e[0] not in reach for e in edges)
                edges[idx][3] = True
                return stranded
            reach_with = count_reachable(node)
            edges[idx][3] = False
            reach_without = count_reachable(node)
            edges[idx][3] = True
            return reach_without < reach_with

        path = [start]
        current = start

        while True:
            avail = active_edges(current)
            if not avail:
                break

            if len(avail) == 1:
                chosen = avail[0]
            else:
                chosen = None
                for idx in avail:
                    if not is_bridge(idx, current):
                        chosen = idx
                        break
                if chosen is None:
                    chosen = avail[0]

            edges[chosen][3] = False
            current = other_end(chosen, current)
            path.append(current)

        if any(e[3] for e in edges):
            return None

        return path

    def hierholzer(self):
        if not self.nodes:
            return []
        if self.directed:
            out_deg = {node: 0 for node in self.nodes}
            in_deg = {node: 0 for node in self.nodes}
            for u in self.adj:
                for v, w in self.adj[u]:
                    out_deg[u] += 1
                    in_deg[v] += 1
            start_candidates = [n for n in self.nodes if out_deg[n] - in_deg[n] == 1]
            end_candidates = [n for n in self.nodes if in_deg[n] - out_deg[n] == 1]
            for n in self.nodes:
                diff = out_deg[n] - in_deg[n]
                if diff not in (0, 1, -1):
                    return None
            if len(start_candidates) == 1 and len(end_candidates) == 1:
                start = start_candidates[0]
            elif not start_candidates and not end_candidates:
                start = next((n for n in self.nodes if out_deg[n] > 0), next(iter(self.nodes)))
            else:
                return None
        else:
            odd_nodes = [n for n in self.nodes if len(self.adj[n]) % 2 != 0]
            if len(odd_nodes) not in (0, 2):
                return None
            start = odd_nodes[0] if odd_nodes else next((n for n in self.nodes if self.adj[n]), next(iter(self.nodes)))

        local_adj = {node: list(self.adj[node]) for node in self.nodes}

        def get_next_edge(node):
            while local_adj[node]:
                v, w = local_adj[node].pop()
                if not self.directed:
                    for i, (n2, w2) in enumerate(local_adj[v]):
                        if n2 == node and w2 == w:
                            local_adj[v].pop(i)
                            break
                return v
            return None

        stack = [start]
        circuit = []
        while stack:
            node = stack[-1]
            nxt = get_next_edge(node)
            if nxt is not None:
                stack.append(nxt)
            else:
                circuit.append(stack.pop())
        circuit.reverse()
        total_edges = sum(len(v) for v in self.adj.values())
        if not self.directed:
            total_edges //= 2
        if len(circuit) - 1 != total_edges:
            return None
        return circuit

    def check_euler_condition(self):
        """
        Kiem tra dieu kien ton tai chu trinh/duong di Euler
        Tra ve: (co_ton_tai, loai, chi_tiet)
        """
        if not self.nodes:
            return False, "Do thi rong", "Khong co dinh nao"
        
        if self.directed:
            in_deg = {v: 0 for v in self.nodes}
            out_deg = {v: 0 for v in self.nodes}
            
            for u in self.adj:
                for v, w in self.adj[u]:
                    out_deg[u] += 1
                    in_deg[v] += 1
            
            start_nodes = []
            end_nodes = []
            for v in self.nodes:
                diff = out_deg[v] - in_deg[v]
                if diff == 1:
                    start_nodes.append(v)
                elif diff == -1:
                    end_nodes.append(v)
                elif diff != 0:
                    return False, "Khong co", f"Dinh {v} chenh lech bac {diff} (khong hop le)"
            
            if len(start_nodes) == 0 and len(end_nodes) == 0:
                return True, "Chu trinh Euler", "Moi dinh co bac vao = bac ra"
            elif len(start_nodes) == 1 and len(end_nodes) == 1:
                return True, "Duong di Euler", f"Tu {start_nodes[0]} den {end_nodes[0]}"
            else:
                return False, "Khong co", f"So dinh bat dau: {len(start_nodes)}, so dinh ket thuc: {len(end_nodes)}"
        
        else:
            odd_deg = []
            for v in self.nodes:
                if len(self.adj[v]) % 2 == 1:
                    odd_deg.append(v)
            
            if len(odd_deg) == 0:
                return True, "Chu trinh Euler", "Moi dinh co bac chan"
            elif len(odd_deg) == 2:
                return True, "Duong di Euler", f"Hai dinh bac le: {odd_deg[0]}, {odd_deg[1]}"
            else:
                return False, "Khong co", f"Co {len(odd_deg)} dinh bac le (can 0 hoac 2)"

    # ------------------------------------------------------------------
    # NGUOI 4: Prim, Kruskal
    # ------------------------------------------------------------------
    def prim(self, start=None):
        if self.directed:
            raise ValueError("Prim chi ap dung cho do thi vo huong")
        if not self.nodes:
            return []
        if start is None:
            start = min(self.nodes, key=lambda x: str(x))
        if start not in self.nodes:
            raise ValueError(f"Dinh '{start}' khong ton tai")
        visited = {start}
        mst_edges = []
        heap = []
        for neighbor, weight in self.adj[start]:
            heapq.heappush(heap, (weight, neighbor, start))
        while heap and len(visited) < len(self.nodes):
            w, v, u = heapq.heappop(heap)
            if v in visited:
                continue
            visited.add(v)
            mst_edges.append((u, v, w))
            for next_neighbor, next_weight in self.adj[v]:
                if next_neighbor not in visited:
                    heapq.heappush(heap, (next_weight, next_neighbor, v))
        if len(visited) < len(self.nodes):
            return None
        return mst_edges

    def kruskal(self):
        if self.directed:
            raise ValueError("Kruskal chi ap dung cho do thi vo huong")
        edges = []
        seen = set()
        for u in self.adj:
            for v, w in self.adj[u]:
                key = frozenset((u, v))
                if key not in seen:
                    seen.add(key)
                    edges.append((u, v, w))
        edges.sort(key=lambda x: x[2])
        parent = {node: node for node in self.nodes}
        rank = {node: 0 for node in self.nodes}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(x, y):
            rx, ry = find(x), find(y)
            if rx == ry:
                return False
            if rank[rx] < rank[ry]:
                parent[rx] = ry
            elif rank[rx] > rank[ry]:
                parent[ry] = rx
            else:
                parent[ry] = rx
                rank[rx] += 1
            return True

        mst_edges = []
        for u, v, w in edges:
            if union(u, v):
                mst_edges.append((u, v, w))
                if len(mst_edges) == len(self.nodes) - 1:
                    break
        if len(mst_edges) != len(self.nodes) - 1:
            return None
        return mst_edges

    # ------------------------------------------------------------------
    # NGUOI 5: Ford-Fulkerson
    # ------------------------------------------------------------------
    def ford_fulkerson(self, source, sink, return_flow_edges=False):
        if not self.directed:
            raise ValueError("Ford-Fulkerson chi ap dung cho do thi co huong")
        if source not in self.nodes or sink not in self.nodes:
            raise ValueError("source hoac sink khong ton tai")
        if source == sink:
            return (0, {}) if return_flow_edges else 0

        capacity = defaultdict(float)
        residual = defaultdict(lambda: defaultdict(float))
        for u in self.adj:
            for v, w in self.adj[u]:
                capacity[(u, v)] += w
                residual[u][v] += w
                if v not in residual:
                    residual[v] = defaultdict(float)

        def bfs_residual():
            parent = {source: None}
            queue = deque([source])
            visited = {source}
            while queue:
                u = queue.popleft()
                if u == sink:
                    break
                for v in residual[u]:
                    if v not in visited and residual[u][v] > 0:
                        visited.add(v)
                        parent[v] = u
                        queue.append(v)
            return sink in parent, parent

        max_flow = 0.0
        while True:
            found_path, parent = bfs_residual()
            if not found_path:
                break
            path_flow = float("inf")
            v = sink
            while v != source:
                u = parent[v]
                path_flow = min(path_flow, residual[u][v])
                v = u
            v = sink
            while v != source:
                u = parent[v]
                residual[u][v] -= path_flow
                residual[v][u] += path_flow
                v = u
            max_flow += path_flow

        if not return_flow_edges:
            return max_flow

        # Luong thuc te tren canh goc (u, v) = capacity - phan con lai trong residual
        flow_edges = {}
        for (u, v), cap in capacity.items():
            used = cap - residual[u][v]
            if used > 1e-9:
                flow_edges[(u, v)] = used
        return max_flow, flow_edges