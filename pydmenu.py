#!/usr/bin/env python3
import sys, gi

gi.require_version("Gtk", "3.0")
gi.require_version("GtkLayerShell", "0.1")
from gi.repository import Gtk, Gdk, GtkLayerShell, Pango

items = [l.rstrip("\n") for l in sys.stdin]
matches, sel = items[:], 0


def match_from(q, s, start):
    """Greedy match of q inside s, forced to begin at index `start`.
    Returns a score (lower is better) or None if q can't be completed."""
    pos, gaps = start, 0
    for ch in q[1:]:
        nxt = s.find(ch, pos + 1)
        if nxt == -1:
            return None
        gaps += nxt - pos - 1  # characters skipped between matches
        pos = nxt
    return gaps * 2 + start


def score(query, item):
    """Lower is better. None means no match."""
    if not query:
        return 0  # everything ties, original order kept
    q, s = query.lower(), item.lower()

    # Fast path: a contiguous substring has zero gaps, so score = its index.
    idx = s.find(q)
    if idx != -1:
        return idx

    # Slow path: try every position of the first character as a start point.
    best = None
    for i, ch in enumerate(s):
        if ch != q[0]:
            continue
        sc = match_from(q, s, i)
        if sc is None:
            break  # later starts have even less room left
        if best is None or sc < best:
            best = sc
    return best


win = Gtk.Window()
GtkLayerShell.init_for_window(win)
GtkLayerShell.set_layer(win, GtkLayerShell.Layer.TOP)
GtkLayerShell.set_keyboard_mode(win, GtkLayerShell.KeyboardMode.EXCLUSIVE)
for edge in (GtkLayerShell.Edge.TOP, GtkLayerShell.Edge.LEFT, GtkLayerShell.Edge.RIGHT):
    GtkLayerShell.set_anchor(win, edge, True)

css = Gtk.CssProvider()
css.load_from_data(b"""
window, entry { background: #222; color: #eee; border: none; box-shadow: none; }
label { color: #8f8; }
""")
Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)

box = Gtk.Box(spacing=12)
entry = Gtk.Entry(width_chars=20)
out = Gtk.Label(xalign=0, ellipsize=Pango.EllipsizeMode.END)
box.pack_start(entry, False, False, 4)
box.pack_start(out, True, True, 0)
win.add(box)


def render():
    shown = matches[sel : sel + 10]
    out.set_text("  ".join(f"[{m}]" if i == 0 else m for i, m in enumerate(shown)))


def refresh(*_):
    global matches, sel
    q = entry.get_text()
    scored = [(sc, i) for i in items if (sc := score(q, i)) is not None]
    scored.sort(key=lambda t: t[0])  # stable sort: ties keep input order
    matches = [i for _, i in scored]
    sel = 0
    render()


def move(d):
    global sel
    if matches:
        sel = (sel + d) % len(matches)
        render()


def on_key(_, ev):
    k = Gdk.keyval_name(ev.keyval)
    if k == "Escape":
        Gtk.main_quit()
    elif k in ("Return", "KP_Enter"):
        if matches:
            print(matches[sel], flush=True)
        Gtk.main_quit()
    elif k in ("Right", "Tab"):
        move(1)
    elif k in ("Left", "ISO_Left_Tab"):
        move(-1)
    else:
        return False
    return True


entry.connect("changed", refresh)
win.connect("key-press-event", on_key)
win.connect("destroy", Gtk.main_quit)
refresh()
win.show_all()
Gtk.main()
