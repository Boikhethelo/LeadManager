
from textual.app import App, ComposeResult
from textual.widgets import(
Header, Footer, DataTable, Button, Input, Label, Select, Static, TabbedContent, TabPane
)

from textual.containers import Horizontal, Vertical, ScrollableContainer
from textual.screen import ModalScreen
from textual.binding import Binding
from textual import on

from database.csv_repository import CsvLeadRepository, LeadFileHandler, LeadConfig
from models.cli_commands import Controller, CLIConfig
from models.commands import Commands

def build_commands() -> Commands:
    handler = LeadFileHandler()
    config = LeadConfig()
    repo = CsvLeadRepository(handler, config)
    return Commands(repo)


CATEGORIES = ["leads", "contacts", "companies", "interactions"]


class DetailScreen(ModalScreen):
    """Shows all data for a searched ID across all categories."""

    BINDINGS = [Binding("escape,q", "dismiss", "Close")]

    def __init__(self, result: dict):
        super().__init__()
        self.result = result

    def compose(self) -> ComposeResult:
        with Vertical(id="detail-box"):
            yield Label("── Search Result ──", id="detail-title")
            for category, rows in self.result.items():
                yield Label(f"[bold]{category.upper()}[/bold]", classes="cat-label")
                if not rows:
                    yield Label("  (no records)", classes="empty-label")
                else:
                    for row in rows:
                        for k, v in row.items():
                            yield Label(f"  {k}: {v or '—'}", classes="field-label")
            yield Button("Close", id="close-btn", variant="primary")

    @on(Button.Pressed, "#close-btn")
    def close(self):
        self.dismiss()


class ConfirmDeleteScreen(ModalScreen):
    """Confirmation dialog before deleting a lead."""

    BINDINGS = [Binding("escape", "dismiss", "Cancel")]

    def __init__(self, lead_id: str):
        super().__init__()
        self.lead_id = lead_id

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-box"):
            yield Label(f"Delete all records for ID [bold]{self.lead_id}[/bold]?", id="confirm-msg")
            with Horizontal(id="confirm-buttons"):
                yield Button("Delete", id="confirm-yes", variant="error")
                yield Button("Cancel", id="confirm-no", variant="default")

    @on(Button.Pressed, "#confirm-yes")
    def confirm(self):
        self.dismiss(True)

    @on(Button.Pressed, "#confirm-no")
    def cancel(self):
        self.dismiss(False)


class LeadManagerApp(App):
    CSS = """
    Screen {
        background: #0d1117;
    }

    Header {
        background: #161b22;
        color: #58a6ff;
    }

    Footer {
        background: #161b22;
        color: #8b949e;
    }

    TabbedContent {
        height: 1fr;
    }

    TabPane {
        padding: 1 2;
    }

    DataTable {
        height: 1fr;
        border: solid #30363d;
        background: #0d1117;
    }

    DataTable > .datatable--header {
        background: #161b22;
        color: #58a6ff;
    }

    DataTable > .datatable--cursor {
        background: #1f6feb;
        color: #ffffff;
    }

    .form-row {
        height: auto;
        margin-bottom: 1;
    }

    .form-label {
        width: 20;
        color: #8b949e;
        padding-top: 1;
    }

    Input {
        background: #161b22;
        border: solid #30363d;
        color: #e6edf3;
        width: 40;
    }

    Input:focus {
        border: solid #58a6ff;
    }

    Select {
        background: #161b22;
        border: solid #30363d;
        color: #e6edf3;
        width: 40;
    }

    Button {
        margin: 0 1;
    }

    Button.action-btn {
        background: #1f6feb;
        color: #ffffff;
        border: none;
    }

    Button.danger-btn {
        background: #da3633;
        color: #ffffff;
        border: none;
    }

    .status-bar {
        height: 1;
        color: #3fb950;
        padding: 0 2;
    }

    .status-bar.error {
        color: #f85149;
    }

    #detail-box {
        background: #161b22;
        border: solid #58a6ff;
        padding: 2 3;
        width: 60;
        height: auto;
        margin: 4 auto;
    }

    #detail-title {
        color: #58a6ff;
        text-align: center;
        margin-bottom: 1;
    }

    .cat-label {
        color: #f0883e;
        margin-top: 1;
    }

    .field-label {
        color: #e6edf3;
    }

    .empty-label {
        color: #484f58;
    }

    #confirm-box {
        background: #161b22;
        border: solid #f85149;
        padding: 2 3;
        width: 50;
        height: auto;
        margin: 8 auto;
    }

    #confirm-msg {
        color: #e6edf3;
        margin-bottom: 2;
    }

    #confirm-buttons {
        height: auto;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh_view", "Refresh"),
    ]

    TITLE = "Lead Manager"
    SUB_TITLE = "CRM"

    def __init__(self):
        super().__init__()
        self._commands = build_commands()
        # Wire the controller with the TUI display callback — same pattern as App
        self._controller = Controller(CLIConfig(), self._commands, self.display)



    def display(self, result: dict | list | str | None) -> None:
        """
        Receives any result from Commands and decides how to surface it in the TUI.
        Handlers call this; the TUI decides what to show.
        """
        if result is None:
            return

        # dict = search-by-id result → open detail modal
        if isinstance(result, dict):
            self.push_screen(DetailScreen(result))

        # list = get_all / get_by_key results → refresh the view table
        elif isinstance(result, list):
            self._populate_table(result)

        # str = new lead ID returned by create_new_lead
        elif isinstance(result, str):
            self._set_status("new-status", f"✓ Created new lead with ID: {result}")



    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent():
            # ── VIEW ──────────────────────────────────────────────────────
            with TabPane("View", id="tab-view"):
                with Vertical():
                    with Horizontal(id="view-controls"):
                        yield Select(
                            [(c.capitalize(), c) for c in CATEGORIES],
                            value="leads",
                            id="category-select",
                        )
                        yield Button("Load", id="load-btn", classes="action-btn")
                    yield DataTable(id="main-table")
                    yield Static("", id="view-status", classes="status-bar")

            # ── SEARCH ────────────────────────────────────────────────────
            with TabPane("Search", id="tab-search"):
                with Vertical():
                    with Horizontal(classes="form-row"):
                        yield Label("Search by ID:", classes="form-label")
                        yield Input(placeholder="e.g. 1", id="search-input")
                        yield Button("Search", id="search-btn", classes="action-btn")
                    yield Static("", id="search-status", classes="status-bar")

            # ── NEW LEAD ──────────────────────────────────────────────────
            with TabPane("New Lead", id="tab-new"):
                with Vertical():
                    yield Label("Creates a blank record across all categories with a shared ID.")
                    yield Static("", id="new-status", classes="status-bar")
                    yield Button("Create New Lead", id="new-btn", classes="action-btn")

            # ── MODIFY ────────────────────────────────────────────────────
            with TabPane("Modify", id="tab-modify"):
                with ScrollableContainer():
                    with Horizontal(classes="form-row"):
                        yield Label("Lead ID:", classes="form-label")
                        yield Input(placeholder="e.g. 1", id="modify-id")
                    with Horizontal(classes="form-row"):
                        yield Label("Category:", classes="form-label")
                        yield Select(
                            [(c.capitalize(), c) for c in CATEGORIES],
                            value="leads",
                            id="modify-category",
                        )
                    with Horizontal(classes="form-row"):
                        yield Label("Field:", classes="form-label")
                        yield Input(placeholder="e.g. Status", id="modify-key")
                    with Horizontal(classes="form-row"):
                        yield Label("New Value:", classes="form-label")
                        yield Input(placeholder="e.g. Closed Won", id="modify-value")
                    yield Button("Apply Change", id="modify-btn", classes="action-btn")
                    yield Static("", id="modify-status", classes="status-bar")

            # ── DELETE ────────────────────────────────────────────────────
            with TabPane("Delete", id="tab-delete"):
                with Vertical():
                    with Horizontal(classes="form-row"):
                        yield Label("Lead ID to delete:", classes="form-label")
                        yield Input(placeholder="e.g. 1", id="delete-input")
                        yield Button("Delete", id="delete-btn", classes="danger-btn")
                    yield Static("", id="delete-status", classes="status-bar")

        yield Footer()


    def _set_status(self, widget_id: str, msg: str, error: bool = False) -> None:
        w = self.query_one(f"#{widget_id}", Static)
        w.update(msg)
        w.set_class(error, "error")

    def _populate_table(self, rows: list[dict]) -> None:
        """Populate the view table with an arbitrary list of row dicts."""
        table = self.query_one("#main-table", DataTable)
        table.clear(columns=True)
        if not rows:
            self._set_status("view-status", "No records found.")
            return
        headers = list(rows[0].keys())
        table.add_columns(*headers)
        for row in rows:
            table.add_row(*[row.get(h, "") for h in headers])
        self._set_status("view-status", f"{len(rows)} record(s) loaded.")


    @on(Button.Pressed, "#load-btn")
    def load_category(self) -> None:
        category = self.query_one("#category-select", Select).value
        # routes through Controller → Commands.search → display callback
        self._controller.run(f"search {category} category")

    @on(Button.Pressed, "#search-btn")
    def search_by_id(self) -> None:
        lead_id = self.query_one("#search-input", Input).value.strip()
        if not lead_id:
            self._set_status("search-status", "Please enter an ID.", error=True)
            return
        self._controller.run(f"search {lead_id} id")

    @on(Button.Pressed, "#new-btn")
    def create_new_lead(self) -> None:
        self._controller.run("new")

    @on(Button.Pressed, "#modify-btn")
    def modify_lead(self) -> None:
        lead_id = self.query_one("#modify-id", Input).value.strip()
        category = self.query_one("#modify-category", Select).value
        key = self.query_one("#modify-key", Input).value.strip()
        change = self.query_one("#modify-value", Input).value.strip()

        if not all([lead_id, category, key, change]):
            self._set_status("modify-status", "All fields are required.", error=True)
            return

        self._controller.run(f"modify {lead_id} {category} {key} {change}")
        self._set_status("modify-status", f"✓ Updated '{key}' on ID {lead_id}.")

    @on(Button.Pressed, "#delete-btn")
    def delete_lead(self) -> None:
        lead_id = self.query_one("#delete-input", Input).value.strip()
        if not lead_id:
            return

        def handle_confirm(confirmed: bool) -> None:
            if confirmed:
                self._controller.run(f"delete {lead_id}")
                self._set_status("delete-status", f"✓ Deleted all records for ID {lead_id}.")

        self.push_screen(ConfirmDeleteScreen(lead_id), handle_confirm)


    def action_refresh_view(self) -> None:
        category = self.query_one("#category-select", Select).value
        self._controller.run(f"search {category} category")


if __name__ == "__main__":
    LeadManagerApp().run()