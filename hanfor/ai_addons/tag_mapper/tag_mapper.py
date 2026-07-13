import itertools
import logging

from ai_addons.ai_addon_abstract_class import AiAddonAbstractClass
from ai_addons.threading_ai_socketio import SendUpdateThreadingAndAi
from ai_request.ai_core_requests import AiRequest
from json_db_connector.json_db import JsonDatabase
from lib_core.data import Tag, Requirement
from thread_handling.thread_function_decorator import thread_function, is_stopped, set_status
from thread_handling.threading_core import ThreadTask, ThreadGroup, SchedulingClass, TaskResult, ThreadHandler


class TagMapperAddon(AiAddonAbstractClass):
    """Assigns tags to requirements based on an AI YES/NO answer to a per-tag prompt.

    Mappings (tag <-> prompt) live in memory and are persisted to
    `hanfor/ai_addons/tag_mapper/prompts_to_tags_config.py` on demand via `save_configuration()`.
    """

    required_dependencies = ["send_update_threading_and_ai", "thread_handler", "ai_request", "db"]

    send_update_threading_and_ai: SendUpdateThreadingAndAi
    db: JsonDatabase
    thread_handler: ThreadHandler
    ai_request: AiRequest

    @property
    def addon_name(self) -> str:
        return "Tag Mapper"

    @property
    def addon_description(self) -> str:
        return "Assign tags to requirements automatically based on AI-evaluated prompts"

    def _do_initialize(self):
        self._mapping_id_counter = itertools.count(1)
        self._mappings: dict[int, dict] = {}
        self._load_mappings_from_config()

        # AI provider/model used when running mappings. Defaults to the catalogs default.
        self._selected_provider: str | None = None
        self._selected_model: str | None = None
        self._apply_default_provider_and_model()

    def _get_all_requirements(self) -> dict[str, str]:
        return {req.rid: req.description for req in self.db.get_objects(Requirement).values()}

    def _broadcast_mappings_now(self):
        self.send_update_threading_and_ai.send_ai_update(
            self.get_mappings(),
            "socket_tag_mapper_mappings_updated",
        )

    # -------------------------------------------------------------------
    # AI provider / model selection
    # -------------------------------------------------------------------

    def _apply_default_provider_and_model(self):
        """Pick the catalogs default provider/model as the initial selection."""
        providers = self.ai_request.catalog_to_frontend().get("providers", [])
        if not providers:
            return

        default_provider = next((p for p in providers if p.get("default")), providers[0])
        self._selected_provider = default_provider["name"]

        models = default_provider.get("models", [])
        default_model = next((m for m in models if m.get("default")), models[0] if models else None)
        self._selected_model = default_model["name"] if default_model else None

    @AiAddonAbstractClass.requires_enabled
    def get_selected_provider_model(self) -> dict:
        return {"provider": self._selected_provider, "model": self._selected_model}

    @AiAddonAbstractClass.requires_enabled
    def set_selected_provider_model(self, provider: str | None, model: str | None) -> dict:
        """Set the provider/model used for all future ask_ai calls from this addon.
        Falls back to the catalog default if the given provider/model is invalid.
        Broadcasts the resulting selection to all connected clients."""
        providers = {p["name"]: p for p in self.ai_request.catalog_to_frontend().get("providers", [])}

        if not provider or provider not in providers:
            self._apply_default_provider_and_model()
        else:
            self._selected_provider = provider
            provider_models = {m["name"] for m in providers[provider].get("models", [])}
            self._selected_model = model if model in provider_models else None

        selection = self.get_selected_provider_model()
        self.send_update_threading_and_ai.send_ai_update(selection, "socket_tag_mapper_selection_updated")
        return selection

    # -------------------------------------------------------------------
    # Configuration persistence
    # -------------------------------------------------------------------

    def _load_mappings_from_config(self):
        """Load mapping definitions from the plain-Python configuration file."""
        try:
            from ai_addons.tag_mapper import prompts_to_tags_config
        except ImportError:
            logging.warning(
                "[tag_mapper] WARNING: hanfor/ai_addons/tag_mapper/prompts_to_tags_config.py not found - starting with no mappings."
            )
            self._mappings = {}
            return

        for entry in getattr(prompts_to_tags_config, "MAPPINGS", []):
            mapping_id = next(self._mapping_id_counter)
            self._mappings[mapping_id] = {
                "id": mapping_id,
                "tag": entry.get("tag", ""),
                "prompt": entry.get("prompt", ""),
                "running": False,
                "assigned_requirements": [],
                "progress": {"processed": 0, "total": 0},
                "last_event": "",
            }

        self._ensure_tags_exist({mapping["tag"] for mapping in self._mappings.values()})

    def _ensure_tags_exist(self, tag_names: set[str]):
        """Auto-create any tag referenced by a loaded mapping that doesn't exist
        in the Tag store yet."""
        existing_names = {tag.name for tag in self.db.get_objects(Tag).values()}
        for name in tag_names:
            if name and name not in existing_names:
                self.db.add_object(Tag(name, self._NEW_TAG_COLOR, self._NEW_TAG_INTERNAL, self._NEW_TAG_DESCRIPTION))
                existing_names.add(name)

    @AiAddonAbstractClass.requires_enabled
    def save_configuration(self):
        """Persist the current in-memory mappings to hanfor/ai_addons/tag_mapper/prompts_to_tags_config.py."""
        lines = [
            "# Tag <-> AI prompt mappings for the AI Tag Mapper addon.\n",
            "# Auto-generated via 'Save Configuration' in the addon UI.\n\n",
            "MAPPINGS = [\n",
        ]
        for mapping in self._mappings.values():
            lines.append("    {\n")
            lines.append(f"        \"tag\": {mapping['tag']!r},\n")
            lines.append(f"        \"prompt\": {mapping['prompt']!r},\n")
            lines.append("    },\n")
        lines.append("]\n")

        with open("hanfor/ai_addons/tag_mapper/prompts_to_tags_config.py", "w", encoding="utf-8") as f:
            f.writelines(lines)

    # -------------------------------------------------------------------
    # Mapping
    # -------------------------------------------------------------------

    @AiAddonAbstractClass.requires_enabled
    def get_mappings(self) -> list[dict]:
        return list(self._mappings.values())

    @AiAddonAbstractClass.requires_enabled
    def add_mapping(self, tag: str = "", prompt: str = "") -> dict:
        mapping_id = next(self._mapping_id_counter)
        mapping = {
            "id": mapping_id,
            "tag": tag,
            "prompt": prompt,
            "running": False,
            "assigned_requirements": [],
            "progress": {"processed": 0, "total": 0},
            "last_event": "",
        }
        self._mappings[mapping_id] = mapping
        self._broadcast_mappings_now()
        return mapping

    @AiAddonAbstractClass.requires_enabled
    def update_mapping(self, mapping_id: int, tag: str, prompt: str) -> dict | None:
        """Update a single mappings tag/prompt in-memory. Called continuously
        (debounced) from the frontend as the user types"""
        mapping = self._mappings.get(mapping_id)
        if mapping is None:
            return None
        mapping["tag"] = tag
        mapping["prompt"] = prompt
        self._broadcast_mappings_now()
        return mapping

    @AiAddonAbstractClass.requires_enabled
    def delete_mapping(self, mapping_id: int):
        self._mappings.pop(mapping_id, None)
        self._broadcast_mappings_now()

    # -------------------------------------------------------------------
    # Tags
    # -------------------------------------------------------------------

    # Default color/description/internal used when a tag is quick-created
    # from the tag selector (which only asks for a name).
    _NEW_TAG_COLOR = "#9633A1"
    _NEW_TAG_INTERNAL = False
    _NEW_TAG_DESCRIPTION = ""

    @AiAddonAbstractClass.requires_enabled
    def get_available_tags(self) -> list[dict]:
        return [{"name": tag.name, "color": tag.color} for tag in self.db.get_objects(Tag).values()]

    @AiAddonAbstractClass.requires_enabled
    def create_tag(self, name: str) -> dict:
        if not name:
            return {"tag": name, "created": False}

        existing_names = {tag.name for tag in self.db.get_objects(Tag).values()}
        if name in existing_names:
            return {"tag": name, "created": False}

        tag = Tag(name, self._NEW_TAG_COLOR, self._NEW_TAG_INTERNAL, self._NEW_TAG_DESCRIPTION)
        self.db.add_object(tag)

        self.send_update_threading_and_ai.send_ai_update(
            self.get_available_tags(),
            "socket_tag_mapper_tags_updated",
        )
        return {"tag": name, "created": True}

    # -------------------------------------------------------------------
    # Requirement access
    # -------------------------------------------------------------------

    def _requirement_has_tag(self, rid: str, tag: str) -> bool:
        requirement = self.db.get_objects(Requirement)[rid]
        return any(t.name == tag for t in requirement.tags)

    def _assign_tag_to_requirement(self, rid: str, tag_name: str):
        requirement = self.db.get_objects(Requirement)[rid]
        tag = next(tag for tag in self.db.get_objects(Tag).values() if tag.name == tag_name)
        requirement.tags[tag] = "Tag_Mapper generated with AI"

    # -------------------------------------------------------------------
    # Running mappings
    # -------------------------------------------------------------------

    @AiAddonAbstractClass.requires_enabled
    def run_mapping(self, mapping_id: int):
        mapping = self._mappings.get(mapping_id)
        if mapping is None:
            return

        self.thread_handler.submit(
            ThreadTask(
                thread_function=self._run_mappings_task,
                scheduling_class=SchedulingClass.CALLER_DEPTH_1,
                group=ThreadGroup("TAG_MAPPER"),
                semaphore=None,
                callback=None,
                args=(mapping,),
                kwargs={},
                info_text=f"tag_mapper / run / {mapping['tag']}",
            )
        )

    @AiAddonAbstractClass.requires_enabled
    def run_all(self):
        for mapping_id in self._mappings.keys():
            self.run_mapping(mapping_id)

    @thread_function
    def _run_mappings_task(self, mapping: dict):
        mapping["assigned_requirements"] = []
        tag = mapping["tag"]
        prompt = mapping["prompt"]
        requirements = self._get_all_requirements()
        total = len(requirements)
        processed = 0

        mapping["running"] = True
        mapping["progress"] = {"processed": 0, "total": total}
        mapping["last_event"] = ""
        self._broadcast_mappings_now()

        set_status(f"running '{tag}' on {total} requirements")

        spawned: list[tuple[str, TaskResult]] = []

        for rid, desc in requirements.items():
            if is_stopped():
                break

            if self._requirement_has_tag(rid, tag):
                processed += 1
                mapping["progress"]["processed"] = processed
                mapping["last_event"] = f"Skipped {rid} (already tagged)"
                self._broadcast_mappings_now()
                continue

            full_prompt = (
                f"{prompt}\n"
                "\n"
                "Requirement:\n"
                f"{desc}\n"
                "\n"
                "Answer with exactly one word, YES or NO, and nothing else."
            )

            task_result = self.ai_request.ask_ai(
                prompt=full_prompt,
                provider=self._selected_provider,
                model_name=self._selected_model,
                info_text=f"tag_mapper / {tag} / {rid}",
            )
            spawned.append((rid, task_result))

        if is_stopped():
            for _, task_result in spawned:
                self.thread_handler.cancel_task(task_result.task_id())
            mapping["running"] = False
            self._broadcast_mappings_now()
            return

        assigned_any = False

        for rid, task_result in spawned:
            if is_stopped():
                self.thread_handler.cancel_task(task_result.task_id())
                continue

            try:
                response, status = task_result.result(timeout=60)
            except Exception:
                processed += 1
                mapping["progress"]["processed"] = processed
                mapping["last_event"] = f"Error checking {rid}"
                self._broadcast_mappings_now()
                continue

            processed += 1
            mapping["progress"]["processed"] = processed

            logging.debug(f"AI Response: {response}")
            if response and response.strip().upper().startswith("YES"):
                if not self._requirement_has_tag(rid, tag):
                    self._assign_tag_to_requirement(rid, tag)
                    assigned_any = True
                    if rid not in mapping["assigned_requirements"]:
                        mapping["assigned_requirements"].append(rid)
                    mapping["last_event"] = f"Assigned {rid}"
                else:
                    mapping["last_event"] = f"Already tagged {rid}"
            else:
                mapping["last_event"] = f"No match: {rid}"

            self._broadcast_mappings_now()

        if assigned_any:
            self.db.update()

        mapping["running"] = False
        self._broadcast_mappings_now()
