from copy import deepcopy
from datetime import UTC, datetime
from io import StringIO
from re import sub
from shutil import get_terminal_size as tsize
from threading import current_thread
from typing import Any

from colorama import Style

from ..utils import strip_ansi, wrap
from .template import TemplateEngine


class Ruleset:
    def __init__(self, rules: dict[str, Any], defaults: dict[str, Any]):
        self._rules = self._merge_with_defaults(deepcopy(rules), deepcopy(defaults))
        self.dict = self.Dict(self._rules)
        for category, settings in self._rules.items():
            setattr(
                self,
                category,
                type(
                    f"{category.title().replace('_', '')}Rules", (), deepcopy(settings)
                )(),
            )

    def _merge_with_defaults(self, rules: dict[str, Any], defaults: dict[str, Any]):
        merged = defaults.copy()
        for category, settings in rules.items():
            if category in merged:
                merged[category].update(settings)
            else:
                merged[category] = settings
        return merged

    class Dict:
        def __init__(self, rules):
            self.all = rules
            for category, settings in rules.items():
                setattr(self, category, deepcopy(settings))


class BaseHandler:
    def __init__(self, defaults: dict[str, Any]):
        self.output_streams = []
        self.stream_rulesets = {}
        self.template_engine = TemplateEngine()
        self.previous_timestamp = None
        self.defaults = deepcopy(defaults)

    def add(self, stream: str | object, ruleset: dict[str, Any] = None):
        if stream not in self.output_streams:
            self.output_streams.append(stream)
            if ruleset:
                self.stream_rulesets[stream] = Ruleset(deepcopy(ruleset), self.defaults)
            else:
                self.stream_rulesets[stream] = Ruleset({}, self.defaults)
        return stream

    def remove(self, stream: str | object):
        if stream in self.output_streams:
            self.output_streams.remove(stream)
            if stream in self.stream_rulesets:
                del self.stream_rulesets[stream]

    def modify(
        self, stream: str | object, ruleset: dict[str, Any], use_original: bool = False
    ):
        if stream not in self.stream_rulesets:
            raise ValueError(f"Stream {stream} not found in handler.")

        if use_original:
            new_rules = deepcopy(self.defaults)
            new_rules.update(deepcopy(ruleset))
            self.stream_rulesets[stream] = Ruleset(new_rules, self.defaults)
        else:
            current_rules = deepcopy(self.stream_rulesets[stream]._rules)
            current_rules.update(deepcopy(ruleset))
            self.stream_rulesets[stream] = Ruleset(current_rules, self.defaults)

    def process_message(
        self,
        message: str,
        level: dict[str, str | int],
        metadata: dict[str, Any],
        ruleset: dict[str, Any],
    ):
        terminal_width = tsize().columns

        context = {
            "timestamp": self._define_timestamp(ruleset),
            "filename": metadata.get("file_name", ""),
            "wrapfunc": metadata.get("wrapping_func", ""),
            "linenum": metadata.get("line_number", ""),
            "level": level["name"],
        }

        log_line = self.template_engine.process(
            ruleset.log_line.format, context, level["name"]
        )
        log_line = sub(r"\x1b\[(\d+)C", lambda m: " " * int(m.group(1)), log_line)
        log_line = log_line if ruleset.formatting.ansi else strip_ansi(log_line)

        message_space = terminal_width - self.template_engine.processed.length
        message_indent = self.template_engine.processed.length

        log_metadata = self._generate_metadata(
            metadata, ruleset, message_space, terminal_width
        )

        formatted_message = message if ruleset.formatting.ansi else strip_ansi(message)

        log_line += log_metadata

        lines = wrap(formatted_message, message_space)

        log_output = StringIO()

        log_output.write(
            f"{log_line}{''.join([f'{line}\n' if i == 0 else f'\x1b[{message_indent}C{line}{Style.RESET_ALL}\n' for i, line in enumerate(lines)])}"
        )

        return log_output.getvalue()

    def _define_timestamp(self, ruleset: dict[str, Any]):
        now = datetime.now(UTC if ruleset.timestamps.use_utc else None)
        timestamp = now.strftime("%H:%M:%S")
        if timestamp == self.previous_timestamp and not ruleset.timestamps.always_show:
            return f"\x1b[{len(timestamp)}C"
        self.previous_timestamp = timestamp
        return timestamp

    def _generate_metadata(
        self,
        metadata: dict[str, Any],
        ruleset: dict[str, Any],
        message_space: int,
        terminal_width: int,
    ):
        if not ruleset.metadata.show_metadata:
            return ""

        metadata_items = []
        if ruleset.metadata.include_timestamp:
            metadata_items.append(f"[tms: {self._define_timestamp(ruleset)}]")
        if ruleset.metadata.include_level_name:
            metadata_items.append(f"[lvl: {metadata['level']}]")
        if ruleset.metadata.include_thread_name:
            metadata_items.append(f"[thr: {current_thread().name}]")
        if ruleset.metadata.include_file_name:
            metadata_items.append(f"[fl: {metadata['file_name']}]")
        if ruleset.metadata.include_wrapping_function:
            metadata_items.append(f"[wfc: {metadata['wrapping_func']}]")
        if ruleset.metadata.include_function:
            metadata_items.append(f"[fnc: {metadata['function']}]")
        if ruleset.metadata.include_line_number:
            metadata_items.append(f"[ln: {metadata['line_number']}]")
        if ruleset.metadata.include_value_count:
            metadata_items.append(f"[vlc: {metadata['value_count']}]")

        metadata_str = " ".join(metadata_items)
        metadata_space = terminal_width - message_space - len(strip_ansi(metadata_str))
        return f"{Style.RESET_ALL}{Style.DIM}{metadata_str.rjust(metadata_space)}{Style.RESET_ALL}"


class StreamHandler(BaseHandler):
    def __init__(self, defaults: dict[str, Any]):
        super().__init__(defaults)
        self.output_streams = []
        self.stream_rulesets = {}

    def add(self, stream: object, ruleset: dict[str, Any] = None):
        if stream not in self.output_streams:
            self.output_streams.append(stream)
            if ruleset:
                self.stream_rulesets[stream] = Ruleset(deepcopy(ruleset), self.defaults)
            else:
                self.stream_rulesets[stream] = Ruleset({}, self.defaults)
        return stream

    def modify(
        self, stream: object, ruleset: dict[str, Any], use_original: bool = False
    ):
        if stream not in self.stream_rulesets:
            raise ValueError(f"Stream {stream} not found in handler.")

        if use_original:
            new_rules = deepcopy(self.defaults)
            new_rules.update(deepcopy(ruleset))
            self.stream_rulesets[stream] = Ruleset(new_rules, self.defaults)
        else:
            current_rules = deepcopy(self.stream_rulesets[stream].dict.all)
            current_rules.update(deepcopy(ruleset))
            self.stream_rulesets[stream] = Ruleset(current_rules, self.defaults)

    def write(
        self, message: str, level_dict: dict[str, str | int], metadata: dict[str, Any]
    ):
        for stream in self.output_streams:
            ruleset = self.stream_rulesets.get(stream)
            if ruleset:
                if not self._should_log(message, level_dict["level"], ruleset):
                    continue
                processed_message = self.process_message(
                    message, level_dict, metadata, ruleset
                )
                stream.write(processed_message)
            else:
                stream.write(message)
            stream.flush()

    def _should_log(self, message: str, level: int, ruleset: dict[str, Any]):
        if level < ruleset.filtering.min_level:
            return False
        if any(
            substring in message for substring in ruleset.filtering.exclude_messages
        ):
            return False
        if ruleset.filtering.include_only_messages and not any(
            substring in message
            for substring in ruleset.filtering.include_only_messages
        ):
            return False
        return True


class FileHandler(BaseHandler):
    def __init__(self, defaults: dict[str, Any]):
        super().__init__(defaults)
        self.file_streams = {}
        self.file_rulesets = {}

    def add(
        self, file_path: str, ruleset: dict[str, Any] | None = None, reset: bool = False
    ):
        if file_path not in self.file_streams or reset:
            mode = "w" if reset else "a"
            self.file_streams[file_path] = open(file_path, mode)
            if ruleset:
                self.file_rulesets[file_path] = Ruleset(
                    deepcopy(ruleset), self.defaults
                )
            else:
                self.file_rulesets[file_path] = Ruleset({}, self.defaults)
        return file_path

    def remove(self, file_path: str):
        if file_path in self.file_streams:
            self.file_streams[file_path].close()
            del self.file_streams[file_path]
            if file_path in self.file_rulesets:
                del self.file_rulesets[file_path]

    def modify(
        self, file_path: str, ruleset: dict[str, Any], use_original: bool = False
    ):
        if file_path in self.file_rulesets:
            if use_original:
                new_rules = deepcopy(self.defaults)
                new_rules.update(deepcopy(ruleset))
                self.file_rulesets[file_path] = Ruleset(new_rules, self.defaults)
            else:
                current_rules = deepcopy(self.file_rulesets[file_path]._rules)
                current_rules.update(deepcopy(ruleset))
                self.file_rulesets[file_path] = Ruleset(current_rules, self.defaults)

    def write(
        self, message: str, level_dict: dict[str, str | int], metadata: dict[str, Any]
    ):
        for file_path, file_stream in self.file_streams.items():
            ruleset = self.file_rulesets.get(file_path)
            if ruleset:
                if not self._should_log(message, level_dict["level"], ruleset):
                    continue
                processed_message = self.process_message(
                    message, level_dict, metadata, ruleset
                )
                file_stream.write(strip_ansi(processed_message))
            else:
                file_stream.write(strip_ansi(message))
            file_stream.flush()

    def _should_log(self, message: str, level: int, ruleset: dict[str, Any]):
        if level < ruleset.filtering.min_level:
            return False
        if any(
            substring in message for substring in ruleset.filtering.exclude_messages
        ):
            return False
        if ruleset.filtering.include_only_messages and not any(
            substring in message
            for substring in ruleset.filtering.include_only_messages
        ):
            return False
        return True

    def reset(self, file_path: str):
        if file_path in self.file_streams:
            self.remove(file_path)
            self.add(file_path, reset=True)


class Streams:
    def __init__(self, defaults: dict[str, Any]):
        self.file = FileHandler(defaults)
        self.normal = StreamHandler(defaults)


class FHGroup:
    def __init__(self, file_handler: FileHandler, *items):
        self.file_handler = file_handler
        self.file_paths = []
        self.add(*items)

    def unwrap_fhgroups(self, items):
        new = []
        for item in items:
            if isinstance(item, str):
                new.append(item)
            elif isinstance(item, FHGroup):
                new.extend(self.unwrap_fhgroups(item.file_paths))
        return new

    def add(self, *items):
        items = self.unwrap_fhgroups(items)
        for item in items:
            if item not in self.file_paths:
                self.file_paths.append(item)
                self.file_handler.add(item)
        return [*items]

    def remove(self, *items: str):
        items = self.unwrap_fhgroups(items)
        for file_path in items:
            if file_path in self.file_paths:
                self.file_paths.remove(file_path)
                self.file_handler.remove(file_path)
        return [*items]

    def reset(self):
        for file_path in self.file_paths:
            self.file_handler.remove(file_path)
            self.file_handler.add(file_path, reset=True)

    def modify(self, ruleset: dict[str, Any], use_original: bool = False):
        for file_path in self.file_paths:
            self.file_handler.modify(file_path, ruleset, use_original)

    def remove_all(self):
        for file_path in self.file_paths:
            self.file_handler.remove(file_path)
        self.file_paths.clear()


class SHGroup:
    def __init__(self, stream_handler: StreamHandler, *items):
        self.stream_handler = stream_handler
        self.streams = []
        self.add(*items)

    def unwrap_shgroups(self, items):
        new = []
        for item in items:
            if isinstance(item, SHGroup):
                new.extend(item.streams)
            else:
                new.append(item)
        return new

    def add(self, *items):
        items = self.unwrap_shgroups(items)
        for item in items:
            if item not in self.streams:
                self.streams.append(item)
                self.stream_handler.add(item)
        return [*items]

    def remove(self, *items: str):
        items = self.unwrap_shgroups(items)
        for item in items:
            if item in self.streams:
                self.streams.remove(item)
                self.stream_handler.remove(item)
        return [*items]

    def modify(self, ruleset: dict[str, Any], use_original: bool = False):
        for stream in self.streams:
            self.stream_handler.modify(stream, ruleset, use_original)

    def remove_all(self):
        for stream in self.streams:
            self.stream_handler.remove(stream)
        self.streams.clear()
