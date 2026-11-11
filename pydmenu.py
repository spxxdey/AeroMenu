#!/usr/bin/env python3
import sys, gi

gi.require_version("Gtk", "3.0")
gi.require_version("GtkLayerShell", "0.1")
from gi.repository import Gtk, Gdk, Gio, GtkLayerShell, Pango

items = [l.rstrip("\n") for l in sys.stdin]
matches, sel = items[:], 0


def build_icon_map():
    icons = {}
    for app in Gio.AppInfo.get_all():
        icon = app.get_icon()
        if icon is None:
            continue
        items.append(app.get_name())
        keys = {app.get_name().lower()}
        exe = app.get_executable()
        if exe and exe != "flatpak":  # flatpak apps all share this
            keys.add(exe.rsplit("/", 1)[-1].lower())
        for k in keys:
            icons.setdefault(k, icon)  # first app wins on duplicates
    return icons


# need to set the correct icon theme
ICONS = build_icon_map()
theme = Gtk.IconTheme.get_default()
theme.append_search_path("~/.local/share/icons/")
theme.set_custom_theme("aero")


def icon_for(name):
    n = name.lower()
    if n in ICONS:
        return Gtk.Image.new_from_gicon(ICONS[n], Gtk.IconSize.LARGE_TOOLBAR)
    if theme.has_icon(n):  # fallback: item text IS an icon name
        return Gtk.Image.new_from_icon_name(n, Gtk.IconSize.LARGE_TOOLBAR)
    return None


CSS = b"""
* { font-family: "Segoe UI", "Open Sans", "Noto Sans", sans-serif; font-size: 11pt; }

window {
  background: linear-gradient(to bottom, rgba(96,106,120,0.62), rgba(52,58,68,0.72));
  border: 1px solid rgba(255,255,255,0.45);
  border-radius: 8px;
  box-shadow: inset 0 0 0 1px rgba(0,0,0,0.40),
              inset 0 1px 0 1px rgba(255,255,255,0.18);
}

entry {
  background: rgba(255,255,255,0.18);
  color: #fff;
  caret-color: #fff;
  border: 1px solid rgba(255,255,255,0.35);
  border-radius: 4px;
  box-shadow: none;
  padding: 6px 8px;
}
entry:focus { border-color: rgba(255,255,255,0.65); }

list { background: transparent; }

row {
  background: transparent;
  border-top: 1px ridge rgba(255, 255, 255, 0.3);
  border-bottom: 1px ridge rgba(0, 0, 0, 0.8);
  border-radius: 3px;
  padding: 7px 10px;
  outline-style: none;
}
row label { color: #fff; text-shadow: 0 1px 2px rgba(0,0,0,0.60); }

row:hover {
  background: linear-gradient(to bottom,
      rgba(255,255,255,0.40) 0%,
      rgba(255,255,255,0.20) 50%,
      rgba(255,255,255,0.04) 50%,
      rgba(255,255,255,0.16) 100%);
  border-color: rgba(255,255,255,0.55);
}
row:selected {
  background: linear-gradient(to bottom,
      rgba(255,255,255,0.52) 0%,
      rgba(255,255,255,0.28) 50%,
      rgba(255,255,255,0.06) 50%,
      rgba(255,255,255,0.22) 100%);
  border-color: rgba(255,255,255,0.80);
  box-shadow: inset 0 0 0 1px rgba(0,0,0,0.30);
}
row:selected label { color: #fff; }
"""


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
win.set_size_request(800, 600)  # no anchors = centered on screen

# Ask for an RGBA visual so the translucent CSS background actually shows.
visual = win.get_screen().get_rgba_visual()
if visual:
    win.set_visual(visual)
# win.set_app_paintable(True)

css = Gtk.CssProvider()
css.load_from_data(CSS)
Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)

box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
box.set_border_width(8)
entry = Gtk.Entry()
listbox = Gtk.ListBox()
listbox.set_can_focus(False)  # keep keyboard focus in the entry
box.pack_start(entry, False, False, 0)
box.pack_start(listbox, True, True, 0)
win.add(box)


def render():
    for child in listbox.get_children():
        listbox.remove(child)
    start = max(0, sel - 14)  # scroll so the selection stays visible
    for m in matches[start : start + 15]:
        row = Gtk.ListBoxRow()
        row.set_can_focus(False)
        row.item = m  # remember the full text on the row

        img = icon_for(m) or Gtk.Image()  # empty placeholder if no icon
        img.set_pixel_size(24)
        img.set_size_request(24, 24)  # keeps text aligned either way

        hbox = Gtk.Box(spacing=10)
        hbox.pack_start(img, False, False, 0)
        hbox.pack_start(
            Gtk.Label(label=m, xalign=0, ellipsize=Pango.EllipsizeMode.END),
            True,
            True,
            0,
        )
        row.add(hbox)
        listbox.add(row)
    listbox.show_all()
    rows = listbox.get_children()
    if rows:
        listbox.select_row(rows[sel - start])


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


def on_row_activated(_, row):
    print(row.item, flush=True)
    Gtk.main_quit()


def on_key(_, ev):
    k = Gdk.keyval_name(ev.keyval)
    if k == "Escape":
        Gtk.main_quit()
    elif k in ("Return", "KP_Enter"):
        if matches:
            print(matches[sel], flush=True)
        Gtk.main_quit()
    elif k in ("Down", "Tab"):
        move(1)
    elif k in ("Up", "ISO_Left_Tab"):
        move(-1)
    else:
        return False
    return True


entry.connect("changed", refresh)
listbox.connect("row-activated", on_row_activated)
win.connect("key-press-event", on_key)
win.connect("destroy", Gtk.main_quit)
refresh()
win.show_all()
Gtk.main()
