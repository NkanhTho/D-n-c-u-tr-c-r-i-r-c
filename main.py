"""
main.py
=======
Chuong trinh demo tong hop cac thuat toan do thi
"""

import os
import sys
from collections import defaultdict
from graph import Graph


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def fmt_num(x):
    """In so nguyen cho gon: 95.0 -> 95, con so thuc giu nguyen (lam tron 4 chu so)."""
    try:
        return int(x) if float(x).is_integer() else round(float(x), 4)
    except (TypeError, ValueError):
        return x


# ======================================================================
# PHAN CO BAN (muc 1-6 trong menu)
# ======================================================================

def input_graph_from_file():
    print_header("NHAP DO THI TU FILE")
    filepath = input("Nhap duong dan file (vi du: graph.txt): ").strip()
    
    if not os.path.exists(filepath):
        print(f"Khong tim thay file: {filepath}")
        return None
    
    directed = input("Do thi co huong? (y/n): ").strip().lower() == 'y'
    
    try:
        g = Graph.from_file(filepath, directed=directed)
        print(f"\nDa doc thanh cong! So dinh: {len(g.nodes)}, So canh: {len(g.to_edge_list())}")
        return g
    except Exception as e:
        print(f"Loi khi doc file: {e}")
        return None


def input_graph_manual():
    print_header("NHAP DO THI THU CONG")
    print("Chon dang nhap:")
    print("  1. Danh sach canh (edge list)")
    print("  2. Danh sach ke (adjacency list)")
    print("  3. Ma tran ke (adjacency matrix)")
    mode = input("Chon (1-3, mac dinh 1): ").strip() or "1"

    directed = input("Do thi co huong? (y/n): ").strip().lower() == 'y'

    if mode == "2":
        g = Graph(directed=directed)
        print("\nNhap danh sach ke (moi dong: u v1 v2:w2 v3 ...)")
        print("Vi du: A B C:5 D  nghia la A noi B (w=1), A noi C (w=5), A noi D (w=1)")
        print("Nhap dong trong de ket thuc")
        edges = []
        while True:
            line = input("> ").strip()
            if not line:
                break
            parts = line.split()
            if len(parts) < 1:
                continue
            u = parts[0]
            g.nodes.add(u)
            for token in parts[1:]:
                if ":" in token:
                    v, w = token.split(":", 1)
                    try:
                        w = float(w)
                        edges.append((u, v, int(w) if w.is_integer() else w))
                    except ValueError:
                        print(f"Trong so khong hop le trong '{token}', bo qua.")
                else:
                    edges.append((u, token, 1))
        # Do thi vo huong: neu nguoi dung khai bao ca chieu A->B lan B->A thi chi giu 1 canh
        if not directed:
            edges = Graph._merge_symmetric(edges)
        for u, v, w in edges:
            g.add_edge(u, v, w)
        print(f"\nDa them thanh cong! So dinh: {len(g.nodes)}, So canh: {len(g.to_edge_list())}")
        return g

    elif mode == "3":
        try:
            n = int(input("So dinh: ").strip())
        except ValueError:
            print("So dinh khong hop le!")
            return None
        labels_raw = input(f"Nhan cua {n} dinh (cach nhau boi dau cach, Enter de dung 0..{n-1}): ").strip()
        node_labels = labels_raw.split() if labels_raw else [str(i) for i in range(n)]
        if len(node_labels) != n:
            print("So luong nhan khong khop so dinh!")
            return None

        print(f"Nhap {n} dong, moi dong {n} so cach nhau boi dau cach (0 = khong co canh):")
        matrix = []
        for i in range(n):
            row = input(f"Dong {i+1} ({node_labels[i]}): ").strip().split()
            try:
                row = [float(x) if float(x) != int(float(x)) else int(float(x)) for x in row]
            except ValueError:
                print("Gia tri khong hop le!")
                return None
            if len(row) != n:
                print(f"Can nhap dung {n} gia tri!")
                return None
            matrix.append(row)

        g = Graph.from_adjacency_matrix(matrix, node_labels=node_labels, directed=directed)
        print(f"\nDa them thanh cong! So dinh: {len(g.nodes)}, So canh: {len(g.to_edge_list())}")
        return g

    else:
        g = Graph(directed=directed)
        print("\nNhap cac canh (moi dong: u v [weight])")
        print("Nhap dong trong de ket thuc")

        while True:
            line = input("> ").strip()
            if not line:
                break
            parts = line.split()
            if len(parts) == 2:
                u, v = parts
                g.add_edge(u, v)
            elif len(parts) == 3:
                u, v, w = parts
                try:
                    g.add_edge(u, v, float(w))
                except ValueError:
                    print("Trong so khong hop le!")
            else:
                print("Sai dinh dang! Can: u v hoac u v weight")

        print(f"\nDa them thanh cong! So dinh: {len(g.nodes)}, So canh: {len(g.to_edge_list())}")
        return g


def demo_graph_representation(g):
    print_header("BIEU DIEN DO THI")
    
    print("\n--- DANH SACH KE (Adjacency List) ---")
    for node in sorted(g.nodes, key=lambda x: str(x)):
        neighbors = g.adj[node]
        if neighbors:
            neighbor_str = ", ".join([f"{v}({w})" for v, w in neighbors])
            print(f"  {node} -> {neighbor_str}")
        else:
            print(f"  {node} -> []")
    
    print("\n--- DANH SACH CANH (Edge List) ---")
    edges = g.to_edge_list()
    for u, v, w in edges:
        arrow = "->" if g.directed else "--"
        print(f"  {u} {arrow} {v} (w={w})")
    
    print("\n--- MA TRAN KE (Adjacency Matrix) ---")
    nodes, matrix = g.to_adjacency_matrix()
    n = len(nodes)
    print("     " + " ".join(f"{str(n):>5}" for n in nodes))
    for i in range(n):
        row = " ".join(f"{matrix[i][j]:>5}" for j in range(n))
        print(f"{str(nodes[i]):>5} {row}")
    
    save = input("\nBan co muon luu hinh do thi? (y/n): ").strip().lower() == 'y'
    if save:
        filename = input("Nhap ten file (mac dinh: graph.png): ").strip() or "graph.png"
        g.draw(filename)


def demo_bfs_dfs(g):
    print_header("DUYET DO THI BFS & DFS")
    
    if not g.nodes:
        print("Do thi rong!")
        return
    
    start = input(f"Nhap dinh bat dau (cac dinh: {sorted(g.nodes)}): ").strip()
    if start not in g.nodes:
        print(f"Dinh '{start}' khong ton tai!")
        return
    
    print("\n--- BFS ---")
    bfs_result = g.bfs(start)
    print(f"Thu tu duyet BFS tu {start}: {' -> '.join(map(str, bfs_result))}")
    
    print("\n--- DFS ---")
    dfs_result = g.dfs(start)
    print(f"Thu tu duyet DFS tu {start}: {' -> '.join(map(str, dfs_result))}")


def demo_bipartite(g):
    print_header("KIEM TRA DO THI HAI PHIA (BIPARTITE)")
    
    is_bip, parts = g.is_bipartite()
    
    if is_bip:
        print("Do thi LA do thi hai phia (Bipartite)!")
        set_a, set_b = parts
        print(f"\nTap A: {sorted(set_a)}")
        print(f"Tap B: {sorted(set_b)}")
    else:
        print("Do thi KHONG PHAI la do thi hai phia (Bipartite)!")


def demo_shortest_path(g):
    print_header("DUONG DI NGAN NHAT")
    
    if not g.nodes:
        print("Do thi rong!")
        return
    
    nodes = sorted(g.nodes, key=lambda x: str(x))
    print(f"Cac dinh: {nodes}")
    
    start = input("Nhap dinh bat dau: ").strip()
    if start not in g.nodes:
        print(f"Dinh '{start}' khong ton tai!")
        return
    
    end = input("Nhap dinh ket thuc: ").strip()
    if end not in g.nodes:
        print(f"Dinh '{end}' khong ton tai!")
        return
    
    if start == end:
        print("Diem bat dau va ket thuc trung nhau!")
        return
    
    print("\n--- DIJKSTRA ---")
    dijkstra_result = None
    try:
        result = g.dijkstra(start, end)
        if result["distance"] == float("inf"):
            print(f"Khong co duong di tu {start} den {end}")
        else:
            print(f"Duong di: {' -> '.join(result['path'])}")
            print(f"Khoang cach: {result['distance']}")
            dijkstra_result = result
    except ValueError as e:
        print(f"Loi: {e}")
    
    print("\n--- BELLMAN-FORD ---")
    bf_result = None
    try:
        result = g.bellman_ford(start, end)
        if result["distance"] == float("inf"):
            print(f"Khong co duong di tu {start} den {end}")
        else:
            print(f"Duong di: {' -> '.join(result['path'])}")
            print(f"Khoang cach: {result['distance']}")
            bf_result = result
    except ValueError as e:
        print(f"Loi: {e}")

    if dijkstra_result or bf_result:
        if input("\nLuu hinh truc quan hoa duong di ngan nhat? (y/n): ").strip().lower() == 'y':
            if dijkstra_result:
                filename = input("Ten file cho Dijkstra (mac dinh: dijkstra.png): ").strip() or "dijkstra.png"
                g.draw_shortest_path(dijkstra_result["path"], algo_name="Dijkstra",
                                      distance=dijkstra_result["distance"], save_path=filename)
            if bf_result:
                filename = input("Ten file cho Bellman-Ford (mac dinh: bellman_ford.png): ").strip() or "bellman_ford.png"
                g.draw_shortest_path(bf_result["path"], algo_name="Bellman-Ford",
                                      distance=bf_result["distance"], save_path=filename)


# ======================================================================
# PHAN NANG CAO (muc 7-10 trong menu)
# ======================================================================

def demo_euler(g):
    print_header("CHU TRINH / DUONG DI EULER")
    
    print("\n--- FLEURY ---")
    try:
        result = g.fleury()
        if result is None:
            print("Khong ton tai duong di/chu trinh Euler!")
        else:
            print(f"Duong di Euler: {' -> '.join(map(str, result))}")
            if input("Luu hinh truc quan hoa Fleury? (y/n): ").strip().lower() == 'y':
                filename = input("Ten file (mac dinh: fleury.png): ").strip() or "fleury.png"
                g.draw_euler_path(result, algo_name="Fleury", save_path=filename)
    except Exception as e:
        print(f"Loi: {e}")
    
    print("\n--- HIERHOLZER ---")
    try:
        result = g.hierholzer()
        if result is None:
            print("Khong ton tai duong di/chu trinh Euler!")
        else:
            print(f"Duong di Euler: {' -> '.join(map(str, result))}")
            if input("Luu hinh truc quan hoa Hierholzer? (y/n): ").strip().lower() == 'y':
                filename = input("Ten file (mac dinh: hierholzer.png): ").strip() or "hierholzer.png"
                g.draw_euler_path(result, algo_name="Hierholzer", save_path=filename)
    except Exception as e:
        print(f"Loi: {e}")


def demo_mst(g):
    print_header("CAY KHUNG NHO NHAT (MST)")
    
    if g.directed:
        print("MST chi ap dung cho do thi VO HUONG!")
        return
    
    # Chon dinh bat dau co dinh (nho nhat theo thu tu chu cai) de ket qua lap lai duoc
    # moi lan chay (set cua Python khong dam bao thu tu duyet giua cac lan chay).
    start = min(g.nodes, key=lambda x: str(x)) if g.nodes else None

    print(f"\n--- PRIM (bat dau tu dinh {start}) ---")
    try:
        result = g.prim(start)
        if result is None:
            print("Do thi khong lien thong, khong co MST!")
        else:
            print("Cac canh cua MST:")
            total = 0
            for u, v, w in result:
                print(f"  {u} --({w})-- {v}")
                total += w
            print(f"Tong trong so: {total}")
            if input("Luu hinh truc quan hoa Prim? (y/n): ").strip().lower() == 'y':
                filename = input("Ten file (mac dinh: prim.png): ").strip() or "prim.png"
                g.draw_mst(result, algo_name="Prim", save_path=filename)
    except Exception as e:
        print(f"Loi: {e}")
    
    print("\n--- KRUSKAL ---")
    try:
        result = g.kruskal()
        if result is None:
            print("Do thi khong lien thong, khong co MST!")
        else:
            print("Cac canh cua MST:")
            total = 0
            for u, v, w in result:
                print(f"  {u} --({w})-- {v}")
                total += w
            print(f"Tong trong so: {total}")
            if input("Luu hinh truc quan hoa Kruskal? (y/n): ").strip().lower() == 'y':
                filename = input("Ten file (mac dinh: kruskal.png): ").strip() or "kruskal.png"
                g.draw_mst(result, algo_name="Kruskal", save_path=filename)
    except Exception as e:
        print(f"Loi: {e}")


def print_flow_table(g, flow_edges):
    """In luong/tai trong tren tung canh cua mang, danh dau canh da bao hoa (luong = tai trong)."""
    capacity = defaultdict(float)
    for u, v, w in g.to_edge_list():
        capacity[(u, v)] += w

    print("\nLuong tren tung canh (luong/tai trong):")
    for (u, v) in sorted(capacity, key=lambda e: (str(e[0]), str(e[1]))):
        cap = fmt_num(capacity[(u, v)])
        flow = flow_edges.get((u, v), 0)
        mark = "   <- bao hoa (dung het tai trong)" if cap > 0 and flow == cap else ""
        print(f"  {u} -> {v}: {flow}/{cap}{mark}")


def demo_maxflow(g):
    print_header("LUONG CUC DAI (FORD-FULKERSON)")

    if not g.directed:
        print("Ford-Fulkerson chi ap dung cho do thi CO HUONG (trong so = kha nang thong qua)!")
        print("Vui long nap lai do thi va chon 'co huong'.")
        return

    if not g.nodes:
        print("Do thi rong!")
        return

    if any(w < 0 for _u, _v, w in g.to_edge_list()):
        print("Kha nang thong qua (trong so) cua canh khong duoc am!")
        return

    nodes = sorted(g.nodes, key=lambda x: str(x))
    print(f"Cac dinh: {nodes}")

    source = input("Nhap dinh nguon (source): ").strip()
    if source not in g.nodes:
        print(f"Dinh '{source}' khong ton tai!")
        return

    sink = input("Nhap dinh dich (sink): ").strip()
    if sink not in g.nodes:
        print(f"Dinh '{sink}' khong ton tai!")
        return

    if source == sink:
        print("Dinh nguon va dinh dich trung nhau!")
        return

    try:
        max_flow, flow_edges = g.ford_fulkerson(source, sink, return_flow_edges=True)
    except ValueError as e:
        print(f"Loi: {e}")
        return

    max_flow = fmt_num(max_flow)
    flow_edges = {edge: fmt_num(f) for edge, f in flow_edges.items()}

    print(f"\nLuong cuc dai tu {source} den {sink} = {max_flow}")
    print_flow_table(g, flow_edges)

    if input("\nLuu hinh truc quan hoa luong cuc dai? (y/n): ").strip().lower() == 'y':
        filename = input("Ten file (mac dinh: maxflow.png): ").strip() or "maxflow.png"
        g.draw_maxflow(flow_edges, source, sink, max_flow, save_path=filename)


def demo_practical_problem():
    """
    Bai toan giao hang: click chon diem dau/dich tren cung 1 cua so.
    Truc quan sinh dong: KHO (S) = 🏭, DIEM GIAO (T) = 📦, giao lo = 🚚
    """
    import matplotlib
    matplotlib.rcParams['font.family'] = 'Segoe UI Emoji'   # Windows
    import matplotlib.pyplot as plt
    import networkx as nx

    print_header("BAI TOAN THUC TE: GIAO HANG - TIM DUONG NGAN NHAT")

    print("""
HUONG DAN:
- Click dinh 1 -> chon KHO / DIEM XUAT PHAT
- Click dinh 2 -> chon DIEM GIAO HANG -> tu dong chay Dijkstra
- Click tiep   -> reset, chon cap moi
- Dong cua so  -> thoat

Y NGHIA ICON:
  🏭  = Kho hang trung tam (S)
  📦  = Diem giao hang (T)
  🚚  = Giao lo trung gian (A..P)
  🟢  = Diem dau dang chon
  🔴  = Diem dich dang chon
""")

    edges = [
        ("S", "A", 4), ("S", "B", 6), ("S", "C", 2), ("S", "D", 7),
        ("A", "E", 3), ("A", "F", 6), ("A", "C", 2),
        ("B", "F", 2), ("B", "G", 5), ("B", "H", 7),
        ("C", "E", 4), ("C", "G", 8),
        ("D", "H", 3), ("D", "I", 6),
        ("E", "J", 5), ("E", "K", 7),
        ("F", "J", 3), ("F", "G", 2),
        ("G", "K", 4), ("G", "L", 6),
        ("H", "L", 5), ("H", "M", 8),
        ("I", "M", 4), ("I", "N", 6),
        ("J", "O", 6), ("J", "K", 2),
        ("K", "P", 4), ("K", "O", 5),
        ("L", "P", 3), ("L", "O", 7),
        ("M", "P", 6), ("N", "P", 5),
        ("O", "T", 4), ("P", "T", 3),
    ]
    g = Graph.from_edge_list(edges, directed=False)

    G = nx.Graph()
    for u, v, w in g.to_edge_list():
        G.add_edge(u, v, weight=w)

    pos = nx.spring_layout(G, seed=42, k=1.8 / (len(G.nodes) ** 0.5), iterations=200)

    fig, ax = plt.subplots(figsize=(13, 10))
    fig.patch.set_facecolor('#eef2ff')
    ax.set_facecolor('#eef2ff')

    state = {"start": None, "end": None}

    # ---- Icon theo TRANG THAI cua dinh ----
    ICON_CHUA_CHON   = "🏢"   # toa nha: chua chon hoac dang chon lam DAU
    ICON_DANG_CHON_DICH = "📍"  # ghim vi tri: dang chon lam DICH
    ICON_DA_CO_DICH  = "🚦"   # giao lo: cac dinh con lai sau khi da co ca dau + dich

    def redraw():
        ax.clear()
        ax.set_facecolor('#eef2ff')
        ax.axis('off')

        # ---- 1. Ve canh nen (xam nhat) ----
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color='#c8ced8', width=1.4)

        # ---- 2. Neu da co start + end -> ve duong di ngan nhat ----
        title = "🏭 Click chon KHO (diem xuat phat)"
        if state["start"] and not state["end"]:
            title = f"🚚 Da chon diem dau: {state['start']}. Click chon DIEM GIAO HANG"
        elif state["start"] and state["end"]:
            res = g.dijkstra(state["start"], state["end"])
            if res["distance"] == float("inf"):
                title = f"❌ Khong co duong di tu {state['start']} den {state['end']}"
            else:
                path = res["path"]
                seq_edges = list(zip(path[:-1], path[1:]))

                # Ve halo (quang sang) duong di
                nx.draw_networkx_edges(
                    G, pos, ax=ax, edgelist=seq_edges,
                    edge_color='#90caf9', width=9, alpha=0.55
                )
                # Ve duong di chinh
                nx.draw_networkx_edges(
                    G, pos, ax=ax, edgelist=seq_edges,
                    edge_color='#1565c0', width=4.0
                )

                # Ve mui ten chi huong tung chang (tinh trung diem)
                for (u, v) in seq_edges:
                    x1, y1 = pos[u]
                    x2, y2 = pos[v]
                    # Ve mui ten tai 65% doan
                    dx, dy = x2 - x1, y2 - y1
                    L = (dx * dx + dy * dy) ** 0.5
                    if L > 0:
                        ux, uy = dx / L, dy / L
                        mx = x1 + ux * L * 0.65
                        my = y1 + uy * L * 0.65
                        ax.annotate(
                            "", xy=(mx + ux * 0.02, my + uy * 0.02),
                            xytext=(mx, my),
                            arrowprops=dict(arrowstyle='-|>', color='#0d47a1',
                                            lw=2.5, mutation_scale=20),
                            zorder=5
                        )

                # Nhan km tren tung chang
                weight_map = {(u, v): w for u, v, w in g.to_edge_list()}
                for (u, v) in seq_edges:
                    w = weight_map.get((u, v), weight_map.get((v, u), ''))
                    mx = (pos[u][0] + pos[v][0]) / 2
                    my = (pos[u][1] + pos[v][1]) / 2
                    ax.text(mx, my + 0.035, f"{w}km",
                            fontsize=9, fontweight='bold', color='#0d47a1',
                            ha='center', va='bottom', zorder=6,
                            bbox=dict(boxstyle='round,pad=0.25',
                                      fc='#e3f2fd', ec='#1565c0', alpha=0.95))

                title = (f"🚚 Tuyen giao hang: {' → '.join(path)}   "
                         f"|   Tong: {fmt_num(res['distance'])} km")

        # ---- 3. Ve node (vong tron + icon) ----
        for n in G.nodes():
            x, y = pos[n]

            # ---- Xac dinh icon theo TRANG THAI ----
            if n == state["end"]:
                # Dinh dang chon lam DICH -> ghim vi tri
                icon = ICON_DANG_CHON_DICH
            elif state["start"] is not None and state["end"] is not None:
                # Da co ca dau + dich -> cac dinh con lai thanh giao lo
                # (tru 2 dinh dau/dich)
                if n == state["start"]:
                    icon = ICON_CHUA_CHON   # dau van la toa nha
                else:
                    icon = ICON_DA_CO_DICH
            else:
                # Chua chon gi, hoac chi moi chon dau -> toa nha
                icon = ICON_CHUA_CHON

            # ---- Mau vien ----
            if n == state["start"]:
                ring_color, ring_w = '#2e7d32', 5.0
                bg = '#c8e6c9'
            elif n == state["end"]:
                ring_color, ring_w = '#c62828', 5.0
                bg = '#ffcdd2'
            else:
                ring_color, ring_w = '#7986cb', 2.0
                bg = '#e8eaf6'

            # ---- Ve vong tron nen + icon + ten ----
            ax.scatter(x, y, s=1400, c=bg, edgecolors=ring_color,
                       linewidths=ring_w, zorder=3)
            ax.text(x, y, icon, fontsize=22,
                    ha='center', va='center', zorder=4)
            ax.text(x, y - 0.085, str(n), fontsize=10, fontweight='bold',
                    color='#2b2b3d', ha='center', va='top', zorder=4,
                    bbox=dict(boxstyle='round,pad=0.15', fc='white',
                              ec='#b0bec5', alpha=0.9))

        ax.set_title(title, fontsize=13, fontweight='bold',
                     color='#1a237e', pad=14)
        fig.canvas.draw_idle()

    def onclick(event):
        if event.inaxes != ax or event.xdata is None:
            return
        x, y = event.xdata, event.ydata
        node = min(pos, key=lambda n: (pos[n][0] - x) ** 2 + (pos[n][1] - y) ** 2)

        if state["start"] is None:
            state["start"] = node
            state["end"] = None
            print(f"\n>> 🏭 Diem dau = {node}")
        elif state["end"] is None:
            if node == state["start"]:
                print("!! Trung diem dau, click dinh khac.")
                return
            state["end"] = node
            print(f">> 📦 Diem giao = {node}")

            print("\n--- DIJKSTRA ---")
            res = g.dijkstra(state["start"], state["end"])
            if res["distance"] == float("inf"):
                print(f"❌ Khong co duong di tu {state['start']} den {state['end']}")
            else:
                print(f"🚚 Tuyen: {' -> '.join(res['path'])}")
                print(f"📏 Tong: {fmt_num(res['distance'])} km")
                bf = g.bellman_ford(state["start"], state["end"])
                print(f"🔁 Bellman-Ford doi chieu: {fmt_num(bf['distance'])} km")
        else:
            state["start"] = node
            state["end"] = None
            print(f"\n>> Reset. Diem dau moi = {node}")

        redraw()

    fig.canvas.mpl_connect('button_press_event', onclick)
    redraw()
    plt.tight_layout()
    print("\n>> Cua so do thi mo ra. Click chon diem dau / diem giao.")
    print(">> Dong cua so de ket thuc.\n")
    plt.show()
    print("Da dong bai toan thuc te.")

def main():
    g = None
    
    while True:
        clear_screen()
        print("=" * 70)
        print("  CHUONG TRINH DEMO THUAT TOAN DO THI")
        print("=" * 70)
        print("\n--- PHAN CO BAN ---")
        print("1. Nhap do thi tu file")
        print("2. Nhap do thi thu cong")
        print("3. Bieu dien do thi (List <-> Matrix <-> Edge list, ve & luu hinh)")
        print("4. Duyet do thi (BFS & DFS)")
        print("5. Kiem tra do thi hai phia (Bipartite)")
        print("6. Duong di ngan nhat (Dijkstra & Bellman-Ford)")
        print("\n--- PHAN NANG CAO ---")
        print("7. Chu trinh / Duong di Euler (Fleury & Hierholzer)")
        print("8. Cay khung nho nhat (Prim & Kruskal)")
        print("9. Luong cuc dai (Ford-Fulkerson)")
        print("10. Bai toan thuc te (giao hang - Dijkstra)")
        print("\n0. Thoat")
        print("-" * 70)
        
        if g is not None:
            print(f"Trang thai: Da nap do thi voi {len(g.nodes)} dinh, {len(g.to_edge_list())} canh")
            print(f"Loai: {'Co huong' if g.directed else 'Vo huong'}")
        else:
            print("Trang thai: Chua nap do thi")
        print("-" * 70)
        
        choice = input("Chon chuc nang (0-10): ").strip()
        
        if choice == "0":
            print("\nCam on ban da su dung chuong trinh!")
            break
        
        elif choice == "1":
            g = input_graph_from_file()
            input("\nNhan Enter de tiep tuc...")
        
        elif choice == "2":
            g = input_graph_manual()
            input("\nNhan Enter de tiep tuc...")
        
        elif choice == "3":
            if g is None:
                print("Vui long nap do thi truoc!")
                input("\nNhan Enter de tiep tuc...")
                continue
            demo_graph_representation(g)
            input("\nNhan Enter de tiep tuc...")
        
        elif choice == "4":
            if g is None:
                print("Vui long nap do thi truoc!")
                input("\nNhan Enter de tiep tuc...")
                continue
            demo_bfs_dfs(g)
            input("\nNhan Enter de tiep tuc...")
        
        elif choice == "5":
            if g is None:
                print("Vui long nap do thi truoc!")
                input("\nNhan Enter de tiep tuc...")
                continue
            demo_bipartite(g)
            input("\nNhan Enter de tiep tuc...")
        
        elif choice == "6":
            if g is None:
                print("Vui long nap do thi truoc!")
                input("\nNhan Enter de tiep tuc...")
                continue
            demo_shortest_path(g)
            input("\nNhan Enter de tiep tuc...")
        
        elif choice == "7":
            if g is None:
                print("Vui long nap do thi truoc!")
                input("\nNhan Enter de tiep tuc...")
                continue
            demo_euler(g)
            input("\nNhan Enter de tiep tuc...")
        
        elif choice == "8":
            if g is None:
                print("Vui long nap do thi truoc!")
                input("\nNhan Enter de tiep tuc...")
                continue
            demo_mst(g)
            input("\nNhan Enter de tiep tuc...")
        
        elif choice == "9":
            if g is None:
                print("Vui long nap do thi truoc!")
                input("\nNhan Enter de tiep tuc...")
                continue
            demo_maxflow(g)
            input("\nNhan Enter de tiep tuc...")

        elif choice == "10":
            demo_practical_problem()
            input("\nNhan Enter de tiep tuc...")
        
        else:
            print("Lua chon khong hop le!")
            input("\nNhan Enter de tiep tuc...")


if __name__ == "__main__":
    main()
