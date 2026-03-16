"""
LiveBlocks - plugin for Sublime Text 4
=======================================
Kuda klast':
  Mac:     ~/Library/Application Support/Sublime Text/Packages/User/live_blocks.py
  Windows: %APPDATA%\\Sublime Text\\Packages\\User\\live_blocks.py
  Linux:   ~/.config/sublime-text/Packages/User/live_blocks.py

Kak pol'zovat'sya:
  1. Polozhi oba fayla v papku User (sm. vyshe)
  2. Sublime podkhvatit avtomaticheski
  3. Dlya testa vstavte vruchnuyu:
       [[block:abc123]]
       Lyuboy tekst zdes
       [[/block:abc123]]
  4. Posle sokhraneniya markery ischeznut vizualno
  5. Pravyy klik -> LiveBlock: Edit / Info / Regen / Insert

Goryachie klavishi (dobav v Key Bindings):
  { "keys": ["ctrl+shift+b"], "command": "live_block_insert" }
  { "keys": ["ctrl+shift+r"], "command": "live_block_regen_cursor" }

Marker format:  [[block:UUID]] ... content ... [[/block:UUID]]
"""

import datetime
import os
import re
import sqlite3
import threading
import uuid

import sublime
import sublime_plugin

# ── Constants ─────────────────────────────────────────────────────────────────

MARKER_RE = re.compile(r'\[\[block:([a-zA-Z0-9_-]+)\]\](.*?)\[\[/block:\1\]\]', re.DOTALL)
OPEN_RE = re.compile(r'\[\[block:([a-zA-Z0-9_-]+)\]\]')
CLOSE_RE = re.compile(r'\[\[/block:([a-zA-Z0-9_-]+)\]\]')

PHANTOM_KEY = 'live_blocks_markers'
REGION_KEY = 'live_blocks_regions'
BLOCK_SCOPE = 'comment'

PHANTOM_HTML = '<body style="margin:0;padding:0;font-size:0;line-height:0"> </body>'


# ── Database ──────────────────────────────────────────────────────────────────


def get_db_path(file_path: str) -> str:
    dirname = os.path.dirname(file_path) or '.'
    basename = os.path.basename(file_path)
    return os.path.join(dirname, f'.{basename}.liveblocks.db')


def get_db(file_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path(file_path))
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS blocks (
            uuid        TEXT PRIMARY KEY,
            source_file TEXT,
            prompt      TEXT DEFAULT '',
            generator   TEXT DEFAULT 'static',
            schedule    TEXT DEFAULT NULL,
            created_at  TEXT,
            updated_at  TEXT
        )
    """
    )
    conn.commit()
    return conn


def db_get_block(file_path: str, block_uuid: str):
    with get_db(file_path) as conn:
        row = conn.execute(
            'SELECT uuid, prompt, generator, schedule, created_at, updated_at FROM blocks WHERE uuid=?',
            (block_uuid,),
        ).fetchone()
    if row:
        return dict(zip(['uuid', 'prompt', 'generator', 'schedule', 'created_at', 'updated_at'], row))
    return None


def db_save_block(file_path: str, block_uuid: str, prompt: str = '', generator: str = 'static', schedule=None):
    now = datetime.datetime.now().isoformat()
    with get_db(file_path) as conn:
        conn.execute(
            """
            INSERT INTO blocks (uuid, source_file, prompt, generator, schedule, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(uuid) DO UPDATE SET
                prompt=excluded.prompt,
                generator=excluded.generator,
                schedule=excluded.schedule,
                updated_at=excluded.updated_at
            """,
            (block_uuid, file_path, prompt, generator, schedule, now, now),
        )


def db_delete_block(file_path: str, block_uuid: str):
    with get_db(file_path) as conn:
        conn.execute('DELETE FROM blocks WHERE uuid=?', (block_uuid,))


# ── Utilities ─────────────────────────────────────────────────────────────────


def make_uuid() -> str:
    return uuid.uuid4().hex[:8]


def find_blocks_in_text(text: str) -> list:
    blocks = []
    for m in MARKER_RE.finditer(text):
        bid = m.group(1)
        open_tag = f'[[block:{bid}]]'
        close_tag = f'[[/block:{bid}]]'
        blocks.append(
            {
                'uuid': bid,
                'content': m.group(2),
                'full_start': m.start(),
                'full_end': m.end(),
                'open_end': m.start() + len(open_tag),
                'close_start': m.end() - len(close_tag),
            }
        )
    return blocks


def block_at_cursor(view):
    text = view.substr(sublime.Region(0, view.size()))
    cursor = view.sel()[0].begin()
    for block in find_blocks_in_text(text):
        if block['full_start'] <= cursor <= block['full_end']:
            return block
    return None


# ── Phantom rendering ─────────────────────────────────────────────────────────


def hide_markers(view):
    text = view.substr(sublime.Region(0, view.size()))
    phantoms = []

    for m in OPEN_RE.finditer(text):
        phantoms.append(sublime.Phantom(sublime.Region(m.start(), m.end()), PHANTOM_HTML, sublime.LAYOUT_INLINE))
    for m in CLOSE_RE.finditer(text):
        phantoms.append(sublime.Phantom(sublime.Region(m.start(), m.end()), PHANTOM_HTML, sublime.LAYOUT_INLINE))

    if not hasattr(view, '_lb_phantom_set'):
        view._lb_phantom_set = sublime.PhantomSet(view, PHANTOM_KEY)
    view._lb_phantom_set.update(phantoms)

    block_regions = [sublime.Region(b['open_end'], b['close_start']) for b in find_blocks_in_text(text)]
    view.add_regions(REGION_KEY, block_regions, scope=BLOCK_SCOPE, flags=sublime.DRAW_NO_OUTLINE | sublime.DRAW_NO_FILL)


# ── Listeners ─────────────────────────────────────────────────────────────────


class LiveBlocksListener(sublime_plugin.EventListener):
    def on_load(self, view):
        sublime.set_timeout(lambda: hide_markers(view), 100)

    def on_activated(self, view):
        sublime.set_timeout(lambda: hide_markers(view), 50)

    def on_post_save(self, view):
        hide_markers(view)

    def on_modified(self, view):
        if hasattr(view, '_lb_timer'):
            view._lb_timer.cancel()

        def refresh():
            sublime.set_timeout(lambda: hide_markers(view), 0)

        view._lb_timer = threading.Timer(0.4, refresh)
        view._lb_timer.start()


# ── Commands ──────────────────────────────────────────────────────────────────


class LiveBlockInsertCommand(sublime_plugin.TextCommand):
    """Ctrl+Shift+B -- insert new block at cursor."""

    def run(self, edit):
        file_path = self.view.file_name()
        if not file_path:
            sublime.error_message('Save the file first!')
            return

        bid = make_uuid()
        snippet = f'[[block:{bid}]]\nNew block -- enter text here\n[[/block:{bid}]]'

        for region in self.view.sel():
            self.view.insert(edit, region.begin(), snippet)

        db_save_block(file_path, bid)
        hide_markers(self.view)
        sublime.status_message(f'LiveBlock created: {bid}')


class LiveBlockRegenCursorCommand(sublime_plugin.TextCommand):
    """Ctrl+Shift+R -- regenerate block under cursor."""

    def run(self, edit):
        file_path = self.view.file_name()
        if not file_path:
            return

        block = block_at_cursor(self.view)
        if not block:
            sublime.status_message('Cursor is not inside a block')
            return

        meta = db_get_block(file_path, block['uuid'])
        generator = meta['generator'] if meta else 'static'
        prompt = meta['prompt'] if meta else ''

        new_content = self._generate(generator, prompt, block['uuid'])
        content_region = sublime.Region(block['open_end'], block['close_start'])
        self.view.replace(edit, content_region, f'\n{new_content}\n')

        hide_markers(self.view)
        sublime.status_message(f'Block {block["uuid"]} regenerated')

    def _generate(self, generator: str, prompt: str, block_uuid: str) -> str:
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if generator == 'datetime':
            return f'Updated: {now}'
        if generator == 'static':
            return prompt if prompt else f'[static block {block_uuid}]'
        # extend here: 'llm', 'script', etc.
        return f'[{generator}] {now}'


class LiveBlockEditCommand(sublime_plugin.TextCommand):
    """Right-click -> LiveBlock: Edit"""

    def run(self, edit):
        file_path = self.view.file_name()
        if not file_path:
            return

        block = block_at_cursor(self.view)
        if not block:
            sublime.status_message('Cursor is not inside a block')
            return

        meta = db_get_block(file_path, block['uuid'])
        items = [
            f'UUID:      {block["uuid"]}',
            f'Generator: {meta["generator"] if meta else "static"}',
            f'Prompt:    {(meta["prompt"] or "(empty)") if meta else "(not in DB)"}',
            '── Actions ──────────────',
            'Edit prompt',
            'Change generator',
            'Regenerate now',
            'Delete block',
        ]

        def on_select(idx):
            if idx == 4:
                self._edit_prompt(file_path, block['uuid'], meta)
            elif idx == 5:
                self._edit_generator(file_path, block['uuid'], meta)
            elif idx == 6:
                self.view.run_command('live_block_regen_cursor')
            elif idx == 7:
                self._delete_block(file_path, block['uuid'], block)

        self.view.window().show_quick_panel(items, on_select)

    def _edit_prompt(self, file_path, block_uuid, meta):
        current = meta['prompt'] if meta else ''
        self.view.window().show_input_panel(
            'Prompt / text:',
            current,
            lambda val: self._save_prompt(file_path, block_uuid, val, meta),
            None,
            None,
        )

    def _save_prompt(self, file_path, block_uuid, prompt, meta):
        generator = meta['generator'] if meta else 'static'
        db_save_block(file_path, block_uuid, prompt=prompt, generator=generator)
        sublime.status_message(f'Prompt saved for {block_uuid}')

    def _edit_generator(self, file_path, block_uuid, meta):
        generators = ['static', 'datetime', 'script', 'llm']
        current = meta['generator'] if meta else 'static'

        def on_select(idx):
            if idx >= 0:
                prompt = meta['prompt'] if meta else ''
                db_save_block(file_path, block_uuid, prompt=prompt, generator=generators[idx])
                sublime.status_message(f'Generator -> {generators[idx]}')

        self.view.window().show_quick_panel(
            [f'{"-> " if g == current else "   "}{g}' for g in generators],
            on_select,
        )

    def _delete_block(self, file_path, block_uuid, block):
        self.view.run_command(
            'live_block_delete_region',
            {'start': block['full_start'], 'end': block['full_end'], 'uuid': block_uuid},
        )


class LiveBlockDeleteRegionCommand(sublime_plugin.TextCommand):
    def run(self, edit, start, end, uuid):
        file_path = self.view.file_name()
        self.view.erase(edit, sublime.Region(start, end))
        if file_path:
            db_delete_block(file_path, uuid)
        hide_markers(self.view)
        sublime.status_message(f'Block {uuid} deleted')


class LiveBlockInfoCommand(sublime_plugin.TextCommand):
    """Right-click -> LiveBlock: Info"""

    def run(self, edit):
        file_path = self.view.file_name()
        if not file_path:
            return

        block = block_at_cursor(self.view)
        if not block:
            sublime.status_message('Cursor is not inside a block')
            return

        meta = db_get_block(file_path, block['uuid'])
        if meta:
            info = (
                f'<b>Block</b> <code>{meta["uuid"]}</code><br>'
                f'Generator: <code>{meta["generator"]}</code><br>'
                f'Prompt: {meta["prompt"] or "(empty)"}<br>'
                f'Updated: {meta["updated_at"] or "-"}'
            )
        else:
            info = f'<b>Block</b> <code>{block["uuid"]}</code><br><i>Not in DB</i>'

        self.view.show_popup(f'<body style="padding:8px">{info}</body>', max_width=400)
